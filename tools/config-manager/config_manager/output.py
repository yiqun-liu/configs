from __future__ import annotations

import json
import sys
from typing import Literal, TextIO

from .model import ResolvedTarget
from .operations import OperationResult

ColorMode = Literal["auto", "always", "never"]
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"


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


def print_results(
    results: list[OperationResult],
    *,
    color: ColorMode = "auto",
    stream: TextIO | None = None,
) -> None:
    output = stream if stream is not None else sys.stdout
    use_color = should_color(color, output)
    for result in results:
        message = colorize_unified_diff(result.message, enabled=use_color)
        if "\n" in message:
            indented = "\n".join(f"      {line}" for line in message.split("\n"))
            print(f"{result.level:<5} {result.id}:\n{indented}", file=output)
        else:
            print(f"{result.level:<5} {result.id}: {message}", file=output)


def should_color(mode: ColorMode, stream: TextIO) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    return stream.isatty()


def colorize_unified_diff(message: str, *, enabled: bool) -> str:
    if not enabled:
        return message
    return "\n".join(colorize_unified_diff_line(line) for line in message.split("\n"))


def colorize_unified_diff_line(line: str) -> str:
    if line.startswith("--- "):
        return colored(line, RED)
    if line.startswith("+++ "):
        return colored(line, GREEN)
    if line.startswith("@@"):
        return colored(line, CYAN)
    if line.startswith("-"):
        return colored(line, RED)
    if line.startswith("+"):
        return colored(line, GREEN)
    return line


def colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"
