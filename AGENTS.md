# AGENTS — Repo Instructions

## What This Repo Is

Personal configuration files synced across machines. See `README.md` for full usage.

No build system, tests, CI, or package manager.

## Architecture

Top-level directories (`vim`, `git`, `nvim`, `tmux`, `clangd`, `aerc`, `mbsync`, `vscode`, `agent-configs`) are **independent config domains** — they don't cross-reference each other. When exploring a config issue, stay within the relevant directory; no need to peek into others.

## Key Gotchas

- **No test/lint/CI commands exist** — don't try to run them.
- `tracked-configs.json` is **gitignored** (machine-specific). Edit `tracked-configs.example` as the template.
- `nvim/lazy-lock.json` is gitignored (Neovim plugin lockfile).
- `agent-configs/AGENTS.md` is a **global personal instructions file** deployed to `~/.config/opencode/AGENTS.md` — it is NOT repo-specific guidance.
- `agent-configs/skills` is symlinked (`method: link`) — edits in repo immediately affect `~/.agents/skills`.
- `link` entries: `collect` only validates, never copies back.
- After editing config files, run `./manage.sh deploy` to apply to the system.
- Windows: directory links fall back to junctions; file symlinks may need privilege elevation.
