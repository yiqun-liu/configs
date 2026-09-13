# AGENTS

Conventions for AI agents working in this directory.

## What this is

- `mate` is a thin stdlib-only Python 3 wrapper over `opencode run`; all
  intelligence lives in the mate agent (repo:
  `agent-configs/opencode/agents/mate.md`, deployed to opencode's global
  agents dir) and the opencode session. Do not move logic into the wrapper
  that the agent or opencode already provides.
- The same `mate` file runs on macOS, Linux, and Windows (via `mate.cmd`);
  keep it stdlib-only and platform-neutral.
- Deployment goes through the repo config manager (`mate-cli`, `mate-agent`,
  and `mate-cmd` on Windows); there is no installer script.

## Interface contracts

- The tagged message protocol (`[ASK]`, `[DO]`, `[REWORK]`, `[RESULT]`) is the
  contract between `mate` and the agent. Change both sides together: the
  wrapper's `cmd_*` functions and the protocol section of the agent file.
- `[DO]`/`[REWORK]` replies are short optional prose (shown to the user)
  followed by exactly one fenced bash block (`split_reply` returns both
  parts; the first fence pair wins); `[ASK]` replies must contain no bash
  fence. Keep this stated in the agent file.
- The agent never executes: execution happens only in `cmd_do` after explicit
  user confirmation. Do not loosen the agent's `bash`/`edit` denies.

## State and sessions

- Persistent state is limited to `~/.local/state/mate/session.id`. All turns
  use `--dir "$MATE_DIR"` so one global session exists; session capture reads
  `sessionID` from the NDJSON stream, and a missing session must trigger the
  single-retry recreate in `run_turn`.
- Each turn is a one-shot `opencode run`; keep the wrapper free of background
  server management.

## Docs

- `README.md` documents usage, design, env vars, and the verification
  checklist; update it when the interface changes.
