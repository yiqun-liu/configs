from __future__ import annotations

import json
import sys
from typing import Literal, TextIO

from .compare import OnelineResult
from .deps import CheckResult, Status
from .model import ResolvedTarget
from .operations import OperationResult

ColorMode = Literal["auto", "always", "never"]
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"


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


STATUS_COLORS: dict[Status, str] = {
    "ok": GREEN,
    "missing": RED,
    "blocked": YELLOW,
    "manual": DIM,
    "skip": DIM,
}

_UNICODE_SYMBOLS: dict[Status, str] = {
    "ok": "\u2713",
    "missing": "\u2717",
    "blocked": "\u23f8",
    "manual": "\u2014",
    "skip": "\u00b7",
}

_ASCII_SYMBOLS: dict[Status, str] = {
    "ok": "+",
    "missing": "x",
    "blocked": "!",
    "manual": "-",
    "skip": ".",
}


def _status_symbols(stream: TextIO) -> dict[Status, str]:
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        for symbol in _UNICODE_SYMBOLS.values():
            symbol.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return _ASCII_SYMBOLS
    return _UNICODE_SYMBOLS


def print_check_results(
    results: list[CheckResult],
    *,
    as_json: bool,
    stream: TextIO | None = None,
) -> None:
    output = stream if stream is not None else sys.stdout
    if as_json:
        payload = [
            {
                "type": result.kind,
                "id": result.id,
                "name": result.name,
                "tier": result.tier,
                "status": result.status,
                "blocked_by": list(result.blocked_by),
            }
            for result in results
        ]
        print(json.dumps(payload, indent=2), file=output)
        return

    use_color = output.isatty()
    symbols = _status_symbols(output)
    print(f"{'STATUS':<14} {'TIER':<12} {'KIND':<7} NAME", file=output)

    missing = 0
    blocked = 0
    skipped = 0
    for result in results:
        plain = f"{symbols[result.status]} {result.status}".ljust(14)
        status_text = colored(plain, STATUS_COLORS[result.status]) if use_color else plain
        kind = "env" if result.kind == "env_var" else "tool"
        line = f"{status_text} {result.tier:<12} {kind:<7} {result.name}"
        if result.blocked_by:
            line += f"  (blocked by: {', '.join(result.blocked_by)})"
        print(line, file=output)
        if result.status == "missing":
            missing += 1
        elif result.status == "blocked":
            blocked += 1
        elif result.status == "skip":
            skipped += 1

    parts = []
    if missing:
        parts.append(f"{missing} missing")
    if blocked:
        parts.append(f"{blocked} blocked")
    if skipped:
        parts.append(f"{skipped} skipped")
    if parts:
        print(f"\n{', '.join(parts)}", file=output)
    else:
        print("\nAll prerequisites satisfied.", file=output)


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
