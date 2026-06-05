from __future__ import annotations

import json
import sys
from typing import Literal, TextIO

from .compare import OnelineResult
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


MINUS = "\u2212"


def _format_fd(fd: FileDiff, width: int) -> str:
    if fd.kind == "diff":
        return f"{fd.path:<{width}} +{fd.added}/{MINUS}{fd.removed}"
    return f"{fd.path:<{width}} {fd.kind}"


def _file_path_width(files: tuple[FileDiff, ...]) -> int:
    if not files:
        return 0
    return max(len(fd.path) for fd in files) + 2


def print_oneline_results(
    results: list[OnelineResult],
    *,
    stream: TextIO | None = None,
) -> None:
    output = stream if stream is not None else sys.stdout
    total_added = 0
    total_removed = 0
    diff_count = 0
    miss_count = 0

    for result in results:
        if result.level == "SAME":
            print(f"SAME  {result.id} → {result.target}", file=output)
        elif result.level == "DIFF":
            diff_count += 1
            width = _file_path_width(result.files)
            print(f"DIFF  {result.id} → {result.target}:", file=output)
            for fd in result.files:
                total_added += fd.added
                total_removed += fd.removed
                print(f"        {_format_fd(fd, width)}", file=output)
        elif result.level == "MISS":
            miss_count += 1
            print(f"MISS  {result.id} → {result.target}: {result.message}", file=output)
        elif result.level == "WARN":
            print(f"WARN  {result.id} → {result.target}: {result.message}", file=output)

    parts: list[str] = []
    if diff_count:
        parts.append(f"+{total_added}/{MINUS}{total_removed} across {diff_count} entries")
    if miss_count:
        suffix = "s" if miss_count > 1 else ""
        parts.append(f"{miss_count} miss{suffix}")
    if parts:
        print(f"\n{', '.join(parts)}", file=output)
