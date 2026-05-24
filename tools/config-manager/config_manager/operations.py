from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .model import ResolvedTarget
from .platform import PlatformOps, normalize_path, remove_path


@dataclass(frozen=True)
class OperationResult:
    level: str
    id: str
    target: Path
    message: str


def deploy_copy(entry: ResolvedTarget, *, dry_run: bool, prompt: bool) -> OperationResult:
    if not entry.source.exists():
        return OperationResult("ERROR", entry.id, entry.target, f"source missing: {entry.source}")

    if dry_run:
        return OperationResult("OK", entry.id, entry.target, f"would copy {entry.source} -> {entry.target}")

    if entry.target.exists() or entry.target.is_symlink():
        if prompt and not confirm_replace(entry.id, entry.target):
            return OperationResult("SKIP", entry.id, entry.target, "skipped by user")
        remove_path(entry.target)

    entry.target.parent.mkdir(parents=True, exist_ok=True)
    copy_path(entry.source, entry.target)
    return OperationResult("OK", entry.id, entry.target, f"copied {entry.source} -> {entry.target}")


def collect_copy(entry: ResolvedTarget, *, dry_run: bool, prompt: bool) -> OperationResult:
    if not entry.target.exists():
        return OperationResult("ERROR", entry.id, entry.target, f"target missing: {entry.target}")

    if dry_run:
        return OperationResult("OK", entry.id, entry.target, f"would copy {entry.target} -> {entry.source}")

    if entry.source.exists() or entry.source.is_symlink():
        if prompt and not confirm_replace(entry.id, entry.source):
            return OperationResult("SKIP", entry.id, entry.target, "skipped by user")
        remove_path(entry.source)

    entry.source.parent.mkdir(parents=True, exist_ok=True)
    copy_path(entry.target, entry.source)
    return OperationResult("OK", entry.id, entry.target, f"collected {entry.target} -> {entry.source}")


def ensure_link(
    entry: ResolvedTarget,
    *,
    dry_run: bool,
    prompt: bool,
    platform: PlatformOps,
) -> OperationResult:
    if not entry.source.exists():
        return OperationResult("ERROR", entry.id, entry.target, f"source missing: {entry.source}")

    info = platform.inspect_link(entry.target)
    expected = normalize_path(entry.source)

    if info.target is not None and normalize_path(info.target) == expected:
        return OperationResult("OK", entry.id, entry.target, f"{info.kind} already points to {entry.source}")

    if dry_run:
        if info.kind == "missing":
            return OperationResult("OK", entry.id, entry.target, f"would link {entry.target} -> {entry.source}")
        return OperationResult("WARN", entry.id, entry.target, f"would replace existing {info.kind}: {entry.target}")

    if info.kind != "missing":
        if prompt and not confirm_replace(entry.id, entry.target):
            return OperationResult("SKIP", entry.id, entry.target, "skipped by user")
        remove_path(entry.target)

    entry.target.parent.mkdir(parents=True, exist_ok=True)
    result = platform.create_link(entry.source, entry.target)
    return OperationResult("OK", entry.id, entry.target, f"{result.message}: {entry.target} -> {entry.source}")


def validate_link(entry: ResolvedTarget, platform: PlatformOps) -> OperationResult:
    info = platform.inspect_link(entry.target)
    expected = normalize_path(entry.source)
    if info.target is not None and normalize_path(info.target) == expected:
        return OperationResult("OK", entry.id, entry.target, f"{info.kind} points to {entry.source}")
    if info.kind == "missing":
        return OperationResult("ERROR", entry.id, entry.target, f"link target missing: {entry.target}")
    return OperationResult("WARN", entry.id, entry.target, f"{entry.target} is {info.kind}, not a link to {entry.source}")


def copy_path(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target, symlinks=True)
    else:
        shutil.copy2(source, target)


def confirm_replace(entry_id: str, path: Path) -> bool:
    answer = input(f"replace {entry_id} path {path}? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def confirm_action(action: str, entry: ResolvedTarget) -> bool:
    answer = input(
        f"{action} {entry.id}: {entry.source} -> {entry.target}? [y/N] "
    ).strip().lower()
    return answer in {"y", "yes"}
