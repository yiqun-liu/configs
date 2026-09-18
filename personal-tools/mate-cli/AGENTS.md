# AGENTS

Conventions for AI agents working in this directory.

## Invariants

- `mate` is a stdlib-only, platform-neutral Python 3 wrapper over
  `opencode run`. All intelligence lives in `agents/mate.md` (ask/do) and
  `agents/lingo.md` (one-shot language help); do not move logic into the
  wrapper that the agent or opencode already provides.
- The wrapper sets `OPENCODE_CONFIG_DIR` to its own directory at startup
  (unless already set in the environment), making `agents/` beside the
  wrapper the agent source for mate calls. The deployed wrapper must
  resolve (symlink) into this directory — a copied wrapper has no
  `agents/` beside it (on Windows, link `mate.py`, don't copy it).
  Scoping also relies on `~/.config/opencode/agents` staying absent:
  opencode merges config sources, so agents there would load too. No
  agent deploy entry exists.
- opencode writes runtime artifacts (`node_modules/`, `package.json`,
  `package-lock.json`, `bun.lock`) into that directory; `.gitignore`
  keeps them out of the repo.
- Keep the tagged protocol (`[ASK]`, `[DO]`, `[REWORK]`, `[RESULT]`) in sync:
  change the wrapper's `cmd_*` functions and the protocol section of
  `agents/mate.md` together. `[DO]`/`[REWORK]` replies are prose plus
  exactly one fenced command block — `bash` on macOS/Linux, `powershell` on
  Windows (`split_do_cmd_reply` splits; first fence pair wins). `[ASK]`
  must contain no command fence.
- Agents never execute; execution happens only in `cmd_do` after user
  confirmation. Do not loosen the `bash`/`edit` denies.
- `print_section`, `paint`, `print_answer_marker` must stay TTY-gated.
- State is limited to `~/.local/state/mate/session.id` and the server port
  file (`/tmp/mate_server_port`, `MATE_PORT_FILE` to override; `-1` marks a
  failed boot until `mate stop` clears it). A missing session triggers
  the single-retry recreate in `run_turn`. `lingo` runs with
  `persist=False` and must not disturb the shared session.
- The server is reached via `--port` (not `--attach`, which drops assistant
  text events in opencode 1.18.x). Keep the one-shot fallback and
  `MATE_SERVER=0`.

## Docs

- `README.md` documents usage, design, env vars, and the verification
  checklist; update it when the interface changes.
