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
        return CompareResult("OK", entry.id, entry.target, (f"{entry.target} links to {entry.source}",))
    if info.kind == "missing":
        return CompareResult("ERROR", entry.id, entry.target, (f"target missing: {entry.target}",))
    return CompareResult(
        "WARN",
        entry.id,
        entry.target,
        (f"{entry.target} is {info.kind}, not a link to {entry.source}",),
    )


def compare_paths(entry_id: str, source: Path, target: Path) -> CompareResult:
    if not source.exists():
        return CompareResult("ERROR", entry_id, target, (f"source missing: {source}",))
    if not target.exists():
        return CompareResult("ERROR", entry_id, target, (f"target missing: {target}",))
    if source.is_file() and target.is_file():
        if filecmp.cmp(source, target, shallow=False):
            return CompareResult("OK", entry_id, target, (f"same: {source} == {target}",))
        return CompareResult("DIFF", entry_id, target, tuple(compare_files(source, target)))
    if source.is_dir() and target.is_dir():
        lines = tuple(compare_dirs(source, target))
        if not lines:
            return CompareResult("OK", entry_id, target, (f"same: {source} == {target}",))
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


def compare_to_operation(result: CompareResult) -> OperationResult:
    return OperationResult(result.level, result.id, result.target, "\n".join(result.lines))
