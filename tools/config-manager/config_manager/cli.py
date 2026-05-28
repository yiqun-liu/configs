from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .compare import compare_entry, compare_to_operation
from .model import ConfigError, ResolvedTarget, load_entries
from .operations import (
    OperationResult,
    collect_copy,
    confirm_action,
    deploy_copy,
    ensure_link,
    validate_link,
)
from .output import print_entries, print_results
from .paths import resolve_entries
from .planner import filter_by_id
from .platform import PlatformOps, get_platform_ops


def main(repo_root: Path, argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config_path = repo_root / "tracked-configs.json"
        entries = load_entries(config_path)
        resolved = resolve_entries(entries, repo_root)
        selected = filter_by_id(resolved, args.id)
    except (ConfigError, ValueError) as exc:
        print(f"ERROR {exc}")
        return 2

    platform = get_platform_ops()

    if args.command == "list":
        print_entries(selected, as_json=args.json)
        return 0

    if args.command == "compare":
        results = [compare_to_operation(compare_entry(entry, platform)) for entry in selected]
        print_results(results, color=args.color)
        return exit_code(results)

    if args.command == "deploy":
        results = []
        for entry in selected:
            if unchanged_copy(entry, platform):
                results.append(no_difference_result(entry))
                continue
            if not args.dry_run and not confirm_action("deploy", entry):
                results.append(OperationResult("SKIP", entry.id, entry.target, "skipped by user"))
                continue
            if entry.method == "copy":
                results.append(deploy_copy(entry, dry_run=args.dry_run, prompt=False))
            else:
                results.append(
                    ensure_link(
                        entry,
                        dry_run=args.dry_run,
                        prompt=False,
                        platform=platform,
                    )
                )
        print_results(results)
        return exit_code(results)

    if args.command == "collect":
        results = []
        for entry in selected:
            if unchanged_copy(entry, platform):
                results.append(no_difference_result(entry))
                continue
            if not args.dry_run and not confirm_action("collect", entry):
                results.append(OperationResult("SKIP", entry.id, entry.target, "skipped by user"))
                continue
            if entry.method == "copy":
                results.append(collect_copy(entry, dry_run=args.dry_run, prompt=False))
            else:
                results.append(validate_link(entry, platform))
        print_results(results)
        return exit_code(results)

    parser.error(f"unknown command: {args.command}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage tracked config files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list resolved config entries")
    add_common_filters(list_parser)
    list_parser.add_argument("--json", action="store_true", help="print JSON")

    compare_parser = subparsers.add_parser("compare", help="compare sources and targets")
    add_common_filters(compare_parser)
    compare_parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="colorize unified diffs",
    )

    deploy_parser = subparsers.add_parser("deploy", help="deploy sources to targets")
    add_common_filters(deploy_parser)
    deploy_parser.add_argument("--dry-run", action="store_true", help="show planned changes")

    collect_parser = subparsers.add_parser("collect", help="collect targets back into sources")
    add_common_filters(collect_parser)
    collect_parser.add_argument("--dry-run", action="store_true", help="show planned changes")

    return parser


def add_common_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--id", action="append", help="operate on one entry id; may be repeated")


def unchanged_copy(entry: ResolvedTarget, platform: PlatformOps) -> bool:
    return entry.method == "copy" and compare_entry(entry, platform).level == "OK"


def no_difference_result(entry: ResolvedTarget) -> OperationResult:
    return OperationResult("SKIP", entry.id, entry.target, "no differences")


def exit_code(results) -> int:
    if any(result.level == "ERROR" for result in results):
        return 1
    return 0
