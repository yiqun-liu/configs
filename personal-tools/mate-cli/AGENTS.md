# AGENTS

Conventions for AI agents working in this directory.

## What this is

- `mate` is a thin stdlib-only Python 3 wrapper over `opencode run`; all
  intelligence lives in the agents (repo: `agent-configs/opencode/agents/`:
  `mate.md` for ask/do, `lingo.md` for one-shot language help) and the
  opencode session. Do not move logic into the wrapper that the agent or
  opencode already provides.
- The same `mate` file runs on macOS, Linux, and Windows (via `mate.cmd`);
  keep it stdlib-only and platform-neutral.
- Deployment goes through the repo config manager (`mate-cli` and the
  `mate-agent` directory entry, plus `mate-cmd` on Windows); there is no
  installer script.

## Interface contracts

- The tagged message protocol (`[ASK]`, `[DO]`, `[REWORK]`, `[RESULT]`) is the
  contract between `mate` and the mate agent. Change both sides together: the
  wrapper's `cmd_*` functions and the protocol section of `mate.md`.
- `[DO]`/`[REWORK]` replies are short optional prose (shown to the user)
  followed by exactly one fenced bash block (`split_reply` returns both
  parts; the first fence pair wins); `[ASK]` replies must contain no bash
  fence. Keep this stated in the agent file.
- `lingo` has no tags: the raw user input is the prompt to the `lingo`
  agent, which infers the intent. Keep its output formats (dictionary
  entry, grammar answer, rewrite + `[NOTE]`) stated in `lingo.md`.
- The agents never execute: execution happens only in `cmd_do` after
  explicit user confirmation. Do not loosen the `bash`/`edit` denies.
- Terminal styling (`section`, `paint`, `answer_marker`) must stay
  TTY-gated: piped output stays plain and marker-free.

## State and sessions

- Persistent state is limited to `~/.local/state/mate/session.id`. All ask/do
  turns use `--dir "$MATE_DIR"` so one global session exists; session capture
  reads `sessionID` from the NDJSON stream, and a missing session must
  trigger the single-retry recreate in `run_turn`.
- `lingo` runs with `persist=False`: it must never read or write the session
  state, and it must not disturb an existing mate session.
- The opencode server is lazily started and reached via `--port` (prefer it
  over `--attach`: same target, but `--attach` drops assistant text events
  in opencode 1.18.x). The port in use (or the `-1` boot-failure marker)
  persists in the port file (`MATE_PORT_FILE`, default
  `/tmp/mate_server_port`); a `-1` record makes runs skip the server until
  `mate stop` clears the file. Keep the one-shot fallback for a server that
  cannot start, and the `MATE_SERVER=0` escape hatch.

## Docs

- `README.md` documents usage, design, env vars, and the verification
  checklist; update it when the interface changes.
