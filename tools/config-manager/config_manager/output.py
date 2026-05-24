from __future__ import annotations

import json

from .model import ResolvedTarget
from .operations import OperationResult


def print_entries(entries: list[ResolvedTarget], *, as_json: bool) -> None:
    if as_json:
        payload = [
            {
                "id": entry.id,
                "source": str(entry.source),
                "target": str(entry.target),
                "method": entry.method,
            }
            for entry in entries
        ]
        print(json.dumps(payload, indent=2))
        return

    for entry in entries:
        print(f"{entry.id}: {entry.method} {entry.source} -> {entry.target}")


def print_results(results: list[OperationResult]) -> None:
    for result in results:
        message = result.message.replace("\n", "\n      ")
        print(f"{result.level:<5} {result.id}: {message}")
