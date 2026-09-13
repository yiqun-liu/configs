# mate-cli

A lightweight personal-assistant CLI backed by opencode. Three commands, one
persistent session:

- `mate ask "..."` — the agent answers in the shared session.
- `mate do "..."` — the agent explains and proposes a shell command; `mate`
  shows both, executes on `Y`, regenerates on `rework: <feedback>`, and
  reports the exit status and output tail back into the session so the agent
  self-corrects.
- `mate reset` — forget the session; the next run starts fresh.

The wrapper is a single stdlib-only Python 3 script; the same file runs on
macOS, Linux, and Windows.

## Files

| File       | Installs to                         | Role                       |
| ---------- | ----------------------------------- | -------------------------- |
| `mate`     | `~/.local/bin/mate`                 | python wrapper             |
| `mate.cmd` | `%USERPROFILE%\.local\bin\mate.cmd` | cmd/PowerShell shim (Win)  |

Both deploy through the repo config manager (`tracked-configs.json` entries
`mate-cli`, `mate-agent`, and on Windows `mate-cmd`); there is no separate
installer. The agent definition lives at `agent-configs/opencode/agents/mate.md`
in the repo (deployed to opencode's global agents dir) and changes in lockstep
with the wrapper's tagged message protocol.

State: `~/.local/state/mate/session.id` holds the shared session id.

## Usage

```sh
mate ask "what did I use git worktree for last week?"
mate do "find the 10 largest files under ~/Downloads"
mate reset           # start a fresh session next run
```

## Design notes

- **One global session.** All turns run with `--dir "$HOME"`, so the session
  belongs to the home project regardless of the invoking directory. The first
  run captures the session id from the NDJSON stream (`opencode run
  --format json` puts `sessionID` on every event line) and persists it; later
  runs pass `--session`. A dead session id is detected (empty output) and
  recreated once.
- **One-shot turns.** Each invocation is a plain `opencode run`; the wrapper
  manages no background processes. This trades ~1s of per-turn startup for
  simplicity (no ports, no orphaned servers, no fallback paths).
- **Persistent instructions.** The agent body in `mate.md` and the user-level
  `~/.config/opencode/AGENTS.md` are injected as system prompt on every
  request (assembled per call in opencode's `prompt.ts`), so they survive
  autocompaction by construction. Turn history that autocompaction summarizes
  is never deleted from storage.
- **Safety split.** The agent may inspect (`read`/`glob`/`grep` allowed,
  including outside the project dir) but never executes: `bash`, `edit`,
  `task`, `question`, `skill` are denied. Execution happens only in `mate`
  after explicit `Y` confirmation, via `bash -c`.
- **Python, stdlib only.** No third-party deps and no `jq`; NDJSON parsing
  uses the `json` module. Python 3 is already a required repo prerequisite.

## Configuration

| Env var                  | Default    | Meaning                                                        |
| ------------------------ | ---------- | -------------------------------------------------------------- |
| `MATE_MODEL`             | unset      | passed as `--model provider/x`                                 |
| `MATE_DIR`               | home dir   | session directory                                              |
| `MATE_DEBUG`             | unset      | copy last turn's NDJSON here                                   |
| `OPENCODE_BIN`           | `opencode` | opencode binary path                                           |
| `OPENCODE_GIT_BASH_PATH` | `bash`     | bash used to run `do` commands (Windows: point at Git Bash)    |

## Windows

Requirements: Python 3 on PATH (`python`), opencode (`npm install -g
opencode-ai`), and Git Bash (the `do` executor; set
`OPENCODE_GIT_BASH_PATH` if `bash` on PATH resolves to WSL).

`tracked-configs.json` entries on a Windows machine (method `copy`; native
opencode reads `%USERPROFILE%\.config\opencode`):

```json
{ "id": "mate-cli",   "source": "personal-tools/mate-cli/mate",     "method": "copy", "targets": [ "C:/Users/<you>/.local/bin/mate.py" ] },
{ "id": "mate-cmd",   "source": "personal-tools/mate-cli/mate.cmd", "method": "copy", "targets": [ "C:/Users/<you>/.local/bin/mate.cmd" ] },
{ "id": "mate-agent", "source": "agent-configs/opencode/agents/mate.md", "method": "copy", "targets": [ "C:/Users/<you>/.config/opencode/agents/mate.md" ] }
```

Add `%USERPROFILE%\.local\bin` to PATH once, then `mate` works from cmd and
PowerShell via the shim. `.gitattributes` keeps `mate` LF-only and `mate.cmd`
CRLF-only so both platforms' checkouts stay runnable.

## Verification checklist

Offline tests (no LLM calls):

```sh
python3 tests/test_mate.py        # parsing unit tests + fake-opencode flow
```

(The integration cases need a POSIX shell for the fake binary and skip on
Windows; run the live checklist there instead.)

After deploying via `./manage.sh deploy --id mate-cli --id mate-agent`:

1. `mate ask "2+2?"` twice, then `opencode session list` shows one "mate"
   session with both turns.
2. `mate do "list the 3 biggest files in ~/.local/share"` — read the
   explanation, inspect the proposed command, `Y`, check the `[RESULT]`
   feedback turn with `opencode export <session-id>`.
3. `rework: make it human-readable sizes` path regenerates via `[REWORK]`.
4. `mate reset` then a fresh turn recreates the session.

## Evolution

Removed during the ask/do simplification, candidates to revisit if needs
change:

- **Lazy server + `--attach`** — `opencode serve` started on demand to avoid
  per-turn cold boot, plus a `mate stop` to dispose it. Dropped for
  simplicity; reintroduce behind a flag if per-turn latency matters.
- **`mate export` / `mate session`** — passthroughs to `opencode export` and
  the stored id. Use those directly when needed.
