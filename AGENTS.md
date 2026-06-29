# AGENTS — Repo Instructions

## What This Repo Is

Personal configuration files synced across machines. See `README.md` for full usage.

No build system, tests, CI, or package manager.

## Architecture

Top-level directories (`vim`, `git`, `nvim`, `tmux`, `clangd`, `aerc`, `mbsync`, `vscode`, `agent-configs`) are **independent config domains** — they don't cross-reference each other. When exploring a config issue, stay within the relevant directory; no need to peek into others.

## Key Gotchas

- **No build/test/CI commands exist** — don't try to run them.
- `tracked-configs.json` is **gitignored** (machine-specific). Edit `tracked-configs.example` as the template.
- `nvim/lazy-lock.json` is gitignored (Neovim plugin lockfile).
- `agent-configs/AGENTS.md` is a **global personal instructions file** deployed to `~/.config/opencode/AGENTS.md` — it is NOT repo-specific guidance.
- `agent-configs/skills` is symlinked (`method: link`) — edits in repo immediately affect `~/.agents/skills`.
- `link` entries: `collect` only validates, never copies back.
- After editing config files, follow the sate rules below to deploy to the system via config manager. See [`tools/config-manager/usage.md`](tools/config-manager/usage.md) for full deployment command reference.

### Deploy Safety Rules

1. **Compare before deploying.** Always run `./manage.sh compare --id <entry>` and review the diff before any `deploy`. This reveals whether the target has local changes not tracked in this repo.
2. **Never deploy without an explicit `--id`.** Running `./manage.sh deploy` without `--id` operates on every entry — never do this.
3. **Ask for explicit permission before `deploy`.** Do not run `./manage.sh deploy` unless the user explicitly says to.
4. **Watch for local-only changes.** If `compare` shows differences where the target has content the repo source lacks, those local changes will be overwritten by `deploy`. Ask the user for confirmation before proceeding.
- Windows: directory links fall back to junctions; file symlinks may need privilege elevation.
