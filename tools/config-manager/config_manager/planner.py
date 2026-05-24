from __future__ import annotations

from .model import ResolvedTarget


def filter_by_id(entries: list[ResolvedTarget], ids: list[str] | None) -> list[ResolvedTarget]:
    if not ids:
        return entries

    available = {entry.id for entry in entries}
    missing = [entry_id for entry_id in ids if entry_id not in available]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"unknown id: {joined}")

    selected = set(ids)
    return [entry for entry in entries if entry.id in selected]
