from __future__ import annotations

from dataclasses import dataclass
import difflib
import filecmp
from pathlib import Path

from .model import ResolvedTarget
from .operations import OperationResult
from .platform import PlatformOps, normalize_path


@dataclass(frozen=True)
class CompareResult:
    level: str
    id: str
    target: Path
    lines: tuple[str, ...]


def compare_entry(entry: ResolvedTarget, platform: PlatformOps) -> CompareResult:
    if entry.method == "link":
        return compare_link(entry, platform)
    return compare_paths(entry.id, entry.source, entry.target)


def compare_link(entry: ResolvedTarget, platform: PlatformOps) -> CompareResult:
    info = platform.inspect_link(entry.target)
    expected = normalize_path(entry.source)
    if info.target is not None and normalize_path(info.target) == expected:
        return CompareResult("SAME", entry.id, entry.target, (f"{entry.target} links to {entry.source}",))
    if info.kind == "missing":
        return CompareResult("MISS", entry.id, entry.target, (f"target missing: {entry.target}",))
    return CompareResult(
        "WARN",
        entry.id,
        entry.target,
        (f"{entry.target} is {info.kind}, not a link to {entry.source}",),
    )


def compare_paths(entry_id: str, source: Path, target: Path) -> CompareResult:
    if not source.exists():
        return CompareResult("MISS", entry_id, target, (f"source missing: {source}",))
    if not target.exists():
        return CompareResult("MISS", entry_id, target, (f"target missing: {target}",))
    if source.is_file() and target.is_file():
        if filecmp.cmp(source, target, shallow=False):
            return CompareResult("SAME", entry_id, target, (f"same: {source} == {target}",))
        return CompareResult("DIFF", entry_id, target, tuple(compare_files(source, target)))
    if source.is_dir() and target.is_dir():
        lines = tuple(compare_dirs(source, target))
        if not lines:
            return CompareResult("SAME", entry_id, target, (f"same: {source} == {target}",))
        return CompareResult("DIFF", entry_id, target, lines)
    return CompareResult("DIFF", entry_id, target, (f"type differs: {source} vs {target}",))


def compare_dirs(source: Path, target: Path) -> list[str]:
    source_paths = _relative_paths(source)
    target_paths = _relative_paths(target)
    lines: list[str] = []

    for rel in sorted(source_paths - target_paths):
        lines.append(f"only in source: {rel}")
    for rel in sorted(target_paths - source_paths):
        lines.append(f"only in target: {rel}")
    for rel in sorted(source_paths & target_paths):
        left = source / rel
        right = target / rel
        if left.is_file() and right.is_file():
            if not filecmp.cmp(left, right, shallow=False):
                lines.extend(compare_files(left, right))
        elif left.is_dir() != right.is_dir():
            lines.append(f"type differs: {rel}")
    return lines


def compare_files(source: Path, target: Path) -> list[str]:
    source_text = read_text_for_diff(source)
    target_text = read_text_for_diff(target)
    if source_text is None or target_text is None:
        return [f"binary files differ: {source} != {target}"]

    return list(
        difflib.unified_diff(
            source_text.splitlines(),
            target_text.splitlines(),
            fromfile=str(source),
            tofile=str(target),
            lineterm="",
        )
    )


def read_text_for_diff(path: Path) -> str | None:
    try:
        sample = path.read_bytes()[:8192]
        if b"\0" in sample:
            return None
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _relative_paths(root: Path) -> set[Path]:
    result: set[Path] = set()
    for path in root.rglob("*"):
        result.add(path.relative_to(root))
    return result


@dataclass(frozen=True)
class FileDiff:
    path: str
    added: int
    removed: int
    kind: str


@dataclass(frozen=True)
class OnelineResult:
    level: str
    id: str
    target: Path
    files: tuple[FileDiff, ...]
    message: str


def compare_entry_oneline(entry: ResolvedTarget, platform: PlatformOps) -> OnelineResult:
    if entry.method == "link":
        return _compare_link_oneline(entry, platform)
    return _compare_paths_oneline(entry.id, entry.source, entry.target)


def _compare_link_oneline(entry: ResolvedTarget, platform: PlatformOps) -> OnelineResult:
    info = platform.inspect_link(entry.target)
    expected = normalize_path(entry.source)
    if info.target is not None and normalize_path(info.target) == expected:
        return OnelineResult("SAME", entry.id, entry.target, (), f"{entry.target} links to {entry.source}")
    if info.kind == "missing":
        return OnelineResult("MISS", entry.id, entry.target, (), f"target missing: {entry.target}")
    return OnelineResult("WARN", entry.id, entry.target, (), f"{entry.target} is {info.kind}, not a link to {entry.source}")


def _compare_paths_oneline(entry_id: str, source: Path, target: Path) -> OnelineResult:
    if not source.exists():
        return OnelineResult("MISS", entry_id, target, (), f"source missing: {source}")
    if not target.exists():
        return OnelineResult("MISS", entry_id, target, (), f"target missing: {target}")
    if source.is_file() and target.is_file():
        if filecmp.cmp(source, target, shallow=False):
            return OnelineResult("SAME", entry_id, target, (), f"same: {source} == {target}")
        fd = _file_diff_stats(source.name, source, target)
        return OnelineResult("DIFF", entry_id, target, (fd,), "")
    if source.is_dir() and target.is_dir():
        files = _dir_diff_stats(source, target)
        if not files:
            return OnelineResult("SAME", entry_id, target, (), f"same: {source} == {target}")
        return OnelineResult("DIFF", entry_id, target, tuple(files), "")
    fd = FileDiff(source.name, 0, 0, "type-differs")
    return OnelineResult("DIFF", entry_id, target, (fd,), f"type differs: {source} vs {target}")


def _dir_diff_stats(source: Path, target: Path) -> list[FileDiff]:
    source_paths = _relative_paths(source)
    target_paths = _relative_paths(target)
    results: list[FileDiff] = []

    for rel in sorted(source_paths - target_paths):
        results.append(FileDiff(str(rel), 0, 0, "only-in-source"))
    for rel in sorted(target_paths - source_paths):
        results.append(FileDiff(str(rel), 0, 0, "only-in-target"))
    for rel in sorted(source_paths & target_paths):
        left = source / rel
        right = target / rel
        if left.is_file() and right.is_file():
            if not filecmp.cmp(left, right, shallow=False):
                fd = _file_diff_stats(str(rel), left, right)
                if fd is not None:
                    results.append(fd)
        elif left.is_dir() != right.is_dir():
            results.append(FileDiff(str(rel), 0, 0, "type-differs"))

    return results


def _file_diff_stats(rel_path: str, source: Path, target: Path) -> FileDiff | None:
    source_text = read_text_for_diff(source)
    target_text = read_text_for_diff(target)
    if source_text is None or target_text is None:
        return FileDiff(rel_path, 0, 0, "binary")
    added = 0
    removed = 0
    for line in difflib.unified_diff(
        source_text.splitlines(),
        target_text.splitlines(),
        lineterm="",
    ):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return FileDiff(rel_path, added, removed, "diff")


def compare_to_operation(result: CompareResult) -> OperationResult:
    return OperationResult(result.level, result.id, result.target, "\n".join(result.lines))
