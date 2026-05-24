from __future__ import annotations

import os
from pathlib import Path

from .model import Entry, ResolvedTarget


def resolve_entries(entries: list[Entry], repo_root: Path) -> list[ResolvedTarget]:
    resolved: list[ResolvedTarget] = []
    for entry in entries:
        source = (repo_root / entry.source).resolve()
        for target_raw in entry.targets:
            target = resolve_target(target_raw)
            resolved.append(
                ResolvedTarget(
                    id=entry.id,
                    source=source,
                    target=target,
                    method=entry.method,
                )
            )
    return resolved


def resolve_target(path: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(path))
    target = Path(expanded)
    if target.is_absolute():
        return target
    return target.absolute()
