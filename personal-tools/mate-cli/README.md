# mate-cli

A lightweight personal-assistant CLI backed by opencode. Three commands, one
persistent session:

- `mate ask "..."` — the agent answers in the shared session.
- `mate do "..."` — the agent explains and proposes a shell command; `mate`
  shows both, executes on `Y`, regenerates on `rework: <feedback>`, and
  reports the exit status and output tail back into the session so the agent
  self-corrects.
- `mate lingo "..."` — one-shot language help, no shared session: pass a
  word (dictionary entry), a grammar question, or text to rewrite (stdin via
  `-`); the agent infers the intent.
- `mate reset` — forget the session; the next run starts fresh.

The wrapper is a single stdlib-only Python 3 script; the same file runs on
macOS, Linux, and Windows.

## Files

| File         | Installs to                             | Role                       |
| ------------ | --------------------------------------- | -------------------------- |
| `mate`       | `~/.local/bin/mate`                     | python wrapper             |
| `mate.cmd`   | `%USERPROFILE%\.local\bin\mate.cmd`     | cmd/PowerShell shim (Win)  |
| `agents/`    | `~/.config/opencode/agents/`            | mate + lingo agent prompts |

All deploy through the repo config manager (`tracked-configs.json` entries
`mate-cli`, `mate-agent` — the whole agents directory — and `mate-cmd` on
Windows); there is no separate installer. The agent definitions live at
`agent-configs/opencode/agents/` and change in lockstep with the wrapper's
tagged message protocol.

State: `~/.local/state/mate/session.id` holds the shared session id.

## Usage

```sh
mate ask "what did I use git worktree for last week?"
mate do "find the 10 largest files under ~/Downloads"
mate lingo slump                    # dictionary entry
mate lingo "affect vs effect"       # grammar
mate lingo - < draft.txt            # natural rewrite via stdin
mate reset                          # start a fresh session next run
mate stop                           # dispose the lazily started server
```

## Design notes

- **One global session.** All turns run with `--dir "$HOME"`, so the session
  belongs to the home project regardless of the invoking directory. The first
  run captures the session id from the NDJSON stream (`opencode run
  --format json` puts `sessionID` on every event line) and persists it; later
  runs pass `--session`. A dead session id is detected (empty output) and
  recreated once.
- **Lazy backend.** The first run starts `opencode serve` detached on a
  local port; later runs connect via `--port` (same target as `--attach`,
  but it also streams the full assistant event set), so boot and app init
  are paid once per server lifetime instead of per turn. With `MATE_PORT`
  unset, a free port is auto-picked and recorded in
  `/tmp/mate_server_port`; a failed boot writes `-1` there and later runs
  skip the server (one-shot) until `mate stop` clears the file. If the
  server cannot start at all, the run falls back to one-shot mode.
  `MATE_SERVER=0` disables the lazy server entirely.
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
- **One-shot lingo.** `mate lingo` runs `--agent lingo` with `persist=False`:
  the shared session is neither read nor written, and every call is
  independent. The agent infers the intent (word / grammar / rewrite) from
  the input.
- **Terminal-aware styling.** `do` output is structured into `─ section ─`
  rules; on an interactive terminal headers are colored, agent replies get a
  `─ mate ─` / `─ lingo ─` marker, errors are red. `NO_COLOR` disables all
  styling, and markers are TTY-only so piped output stays clean.

## Configuration

| Env var                  | Default    | Meaning                                                        |
| ------------------------ | ---------- | -------------------------------------------------------------- |
| `MATE_MODEL`             | unset      | passed as `--model provider/model`                             |
| `MATE_DIR`               | home dir   | session directory                                              |
| `MATE_DEBUG`             | unset      | copy last turn's NDJSON here                                   |
| `OPENCODE_BIN`           | `opencode` | opencode binary path                                           |
| `OPENCODE_GIT_BASH_PATH` | `bash`     | bash used to run `do` commands (Windows: point at Git Bash)    |
| `MATE_PORT`              | auto-pick  | fixed port for the lazy server                                 |
| `MATE_SERVER`            | `1`        | set `0` to force one-shot runs without a server                |

### Model selection

The model resolves in this order (first match wins):

1. `MATE_MODEL` env var (passed as `--model provider/model`)
2. The agent's frontmatter `model:` (see the commented line in
   `lingo.md`; `mate.md` leaves it unset)
3. Top-level `model` in `~/.config/opencode/opencode.json`
4. opencode's implicit default (first authenticated provider)

To pin a model per agent, set `model:` in its frontmatter; to override
per call, use `MATE_MODEL`.

### Latency notes

Per-turn cost = opencode boot + MCP server startup + model/network. The
first two can be reduced without touching the shared global config:

- MCP servers can be disabled per project. mate sessions run with
  `--dir $HOME`, so `~/.opencode/opencode.json` (tracked as the
  `opencode-home-project` entry) scopes MCP startup down to mate
  sessions only; set `"enabled": false` per server there.
- Runs attach to the lazily started server (see design notes), so the
  remaining per-turn cost is the `opencode run` CLI boot plus the model.

## Windows

Requirements: Python 3 on PATH (`python`), opencode (`npm install -g
opencode-ai`), and Git Bash (the `do` executor; set
`OPENCODE_GIT_BASH_PATH` if `bash` on PATH resolves to WSL).

`tracked-configs.json` entries on a Windows machine (method `copy`; native
opencode reads `%USERPROFILE%\.config\opencode`):

```json
{ "id": "mate-cli",   "source": "personal-tools/mate-cli/mate",     "method": "copy", "targets": [ "C:/Users/<you>/.local/bin/mate.py" ] },
{ "id": "mate-cmd",   "source": "personal-tools/mate-cli/mate.cmd", "method": "copy", "targets": [ "C:/Users/<you>/.local/bin/mate.cmd" ] },
{ "id": "mate-agent", "source": "agent-configs/opencode/agents",    "method": "copy", "targets": [ "C:/Users/<you>/.config/opencode/agents" ] }
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
5. `mate lingo slump` prints a dictionary entry; `mate lingo - < file`
   rewrites; the mate session id file is unchanged by lingo calls.
6. Cold start: `mate stop`, remove `/tmp/mate_server_port`, then `mate ask`
   boots the server and records the port; a second run attaches without
   booting; a forced failure (`MATE_START_TIMEOUT=0.1`) writes `-1` and
   later runs skip the server until `mate stop`.

## Evolution

Removed during the ask/do simplification, candidates to revisit if needs
change:

- **`mate export` / `mate session`** — passthroughs to `opencode export` and
  the stored id. Use those directly when needed.
