#!/usr/bin/env python3
from pathlib import Path
import sys


def main() -> int:
    tool_dir = Path(__file__).resolve().parent
    repo_root = tool_dir.parent.parent
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(tool_dir))

    from config_manager.cli import main as cli_main

    return cli_main(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
