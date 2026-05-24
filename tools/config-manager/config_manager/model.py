from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Literal


Method = Literal["copy", "link"]


@dataclass(frozen=True)
class Entry:
    id: str
    source: str
    method: Method
    targets: tuple[str, ...]


@dataclass(frozen=True)
class ResolvedTarget:
    id: str
    source: Path
    target: Path
    method: Method


class ConfigError(Exception):
    pass


def load_entries(config_path: Path) -> list[Entry]:
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("config root must be an object")

    schema_version = raw.get("schemaVersion")
    if schema_version != 1:
        raise ConfigError(f"unsupported schemaVersion: {schema_version!r}")

    entries_raw = raw.get("entries")
    if not isinstance(entries_raw, list):
        raise ConfigError("entries must be an array")

    entries: list[Entry] = []
    seen: set[str] = set()
    for index, item in enumerate(entries_raw):
        entries.append(_parse_entry(index, item, seen))
    return entries


def _parse_entry(index: int, item: Any, seen: set[str]) -> Entry:
    if not isinstance(item, dict):
        raise ConfigError(f"entries[{index}] must be an object")

    entry_id = _required_string(item, "id", index)
    if entry_id in seen:
        raise ConfigError(f"duplicate entry id: {entry_id}")
    seen.add(entry_id)

    source = _required_string(item, "source", index)
    method_raw = _required_string(item, "method", index)
    if method_raw not in {"copy", "link"}:
        raise ConfigError(f"entries[{index}].method must be 'copy' or 'link'")

    targets_raw = item.get("targets")
    if not isinstance(targets_raw, list) or not targets_raw:
        raise ConfigError(f"entries[{index}].targets must be a non-empty array")

    targets: list[str] = []
    for target_index, target in enumerate(targets_raw):
        if not isinstance(target, str) or not target:
            raise ConfigError(
                f"entries[{index}].targets[{target_index}] must be a non-empty string"
            )
        targets.append(target)

    return Entry(
        id=entry_id,
        source=source,
        method=method_raw,  # type: ignore[arg-type]
        targets=tuple(targets),
    )


def _required_string(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"entries[{index}].{key} must be a non-empty string")
    return value
