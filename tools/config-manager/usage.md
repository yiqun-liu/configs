# Config Manager Usage

Config Manager is the cross-platform replacement for the shell-specific
`manage.sh` implementation. The repo stores the desired config state, and the
tool deploys that state to machine-specific target paths.

## Commands

Run from the repo root:

```powershell
python tools/config-manager/manage.py <command>
```

| Command | What It Does |
| --- | --- |
| `list` | Print configured entries with resolved source, target, and method |
| `compare` | Compare repo sources with deployed targets; text differences use unified diff format |
| `deploy` | Apply repo sources to targets |
| `collect` | Copy target state back into repo sources for copy-managed entries |
| `check-deps` | Verify declared prerequisites (tools and env vars) are present on this machine |

Options:

| Option | Applies To | Meaning |
| --- | --- | --- |
| `--id ID` | all commands | Operate on one entry id; may be repeated |
| `--color auto\|always\|never` | `compare` | Colorize unified diffs; defaults to `auto` |
| `--dry-run` | `deploy`, `collect` | Validate and print planned changes without prompting or modifying files |
| `--json` | `list`, `check-deps` | Print machine-readable JSON |
| `--oneline` | `compare` | Show per-file diff counts (`+N/−M`) instead of full unified diffs |

Examples:

```powershell
python tools/config-manager/manage.py list
python tools/config-manager/manage.py deploy --dry-run
python tools/config-manager/manage.py deploy --id agent-skills
python tools/config-manager/manage.py compare --color always --id tmux
python tools/config-manager/manage.py compare --id opencode-config --id codex-agents
python tools/config-manager/manage.py compare --oneline
python tools/config-manager/manage.py check-deps
python tools/config-manager/manage.py check-deps --json
```

## Entry Point

Use the Python entry point as the single portable interface:

```text
tools/config-manager/manage.py
```

Native shell wrappers may exist for convenience, but they cannot share one
extension across Unix shells and PowerShell. If wrappers are kept, they should be
thin pass-through files:

```text
manage.sh   -> python tools/config-manager/manage.py "$@"
manage.ps1  -> python tools/config-manager/manage.py @args
```

## Configuration

`deploy` and `collect` are interactive by default. Each selected target asks for
confirmation before changing files. Answer `y` to run the action or `n` to skip
that target.

Unchanged copy-managed entries are skipped automatically without prompting.

Use `tracked-configs.json` at the repo root:

```json
{
  "$schema": "./tools/config-manager/tracked-configs.schema.json",
  "schemaVersion": 1,
  "entries": [
    {
      "id": "agent-skills",
      "source": "agent-configs/skills",
      "method": "link",
      "targets": [
        "~/.agents/skills",
        "~/.claude/skills"
      ]
    },
    {
      "id": "opencode-config",
      "source": "agent-configs/opencode/opencode.json",
      "method": "copy",
      "targets": [
        "~/.config/opencode/opencode.json"
      ]
    }
  ]
}
```

Fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable name used in logs, prompts, and `--id` filters |
| `source` | Repo-relative source path |
| `method` | Deployment method: `copy` or `link` |
| `targets` | Installed paths; `~` expands to the user's home directory |

Use multiple `targets` when one source should deploy to several locations, such
as agent skills shared by OpenCode, Codex, and Claude.

### Windows Git Caveat

Different Windows Git distributions may resolve home/config paths differently.
For example, MSYS2 Git may read global config from an MSYS2 home such as:

```text
D:/software/MSYS2/home/yliu
```

while PowerShell and native Windows tools usually treat this as the home:

```text
C:/Users/yliu
```

If `git/ignore` is deployed only to `~/.config/git/ignore`, MSYS2 Git may not
use it. Add the MSYS2 Git config directory as another target for the same `git`
source when that Git build is used:

```json
{
  "id": "git",
  "source": "git",
  "method": "copy",
  "targets": [
    "~/.config/git",
    "D:/software/MSYS2/home/yliu/.config/git"
  ]
}
```

### Copy vs Link

`copy` manages two independent filesystem paths:

| Command | Behavior |
| --- | --- |
| `deploy` | Copy `source` to `target` |
| `collect` | Copy `target` to `source` |
| `compare` | Compare `source` and `target`; text file differences use unified diff format |

`link` makes the target point at the repo source:

| Command | Behavior |
| --- | --- |
| `deploy` | Create or repair a link from `target` to `source` |
| `collect` | Validate the link and skip copying |
| `compare` | Check link target, then compare if needed |

On Windows, directory links try a symbolic link first and fall back to a junction.
File links require symbolic-link support; otherwise use `copy`.

## Prerequisites

Config files in this repo depend on external tools (language runtimes, LSP
servers, CLI helpers) and environment variables (API keys). Declare them in
`prerequisites.json` at the repo root and verify them with `check-deps`.

```json
{
  "$schema": "./tools/config-manager/prerequisites.schema.json",
  "schemaVersion": 1,
  "dependencies": [
    {
      "id": "uv",
      "name": "uv",
      "description": "Python package and version manager; provides the uvx runner.",
      "tier": "required",
      "install": {
        "script": "curl -LsSf https://astral.sh/uv/install.sh | sh"
      },
      "check": ["uv --version", "uvx --version"]
    },
    {
      "id": "python",
      "name": "Python",
      "description": "Python runtime.",
      "tier": "required",
      "install": { "script": "uv python install" },
      "check": ["python --version", "python3 --version"]
    }
  ],
  "env_vars": [
    "MINIMAX_API_KEY"
  ]
}
```

### `dependencies` entries

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier; also the value referenced by `depend_on` |
| `name` | Display name |
| `description` | One-line purpose |
| `tier` | `required`, `recommended`, or `optional` |
| `manual` | `true` when no automatic installer exists (e.g. fonts, GUI apps). Optional, default `false` |
| `install` | Object mapping an install method to a full command string |
| `check` | Command string, or array of commands (any success counts). Omit when the entry cannot be auto-verified |
| `depend_on` | Array of prerequisite `id`s; the entry is reported blocked until all are satisfied |
| `platform` | Restrict to specific platforms: `windows`, `linux`, `macos`, or `unix` (or an array). Omit to apply on all platforms |

`install` keys are install methods. Package-manager keys include `winget`,
`scoop`, `choco`, `brew`, `apt`, `dnf`, `pacman`, `pip`, `npm`, `cargo`, and
`go`. The `script` key holds an OS-agnostic command such as
`curl -LsSf https://example.com/install.sh | sh`.

`check` runs each command via the shell and treats exit code 0 as present. Use an
array when the binary name differs across platforms, for example
`["python --version", "python3 --version"]`.

### `env_vars`

A flat list of environment variable names. Membership implies the variable is
required and must be set manually; `check-deps` verifies presence by reading the
process environment.

### `check-deps` behavior

- Each `check` command runs via the shell; exit 0 marks the entry `ok`,
  otherwise `missing`.
- An entry whose `depend_on` includes an unsatisfied entry is `blocked` and its
  own check is skipped.
- An entry without a `check` is `manual` and never fails the run.
- An entry whose `platform` does not match the current machine is `skip` and
  never fails the run.
- Each `env_var` is `ok` when set and `missing` when unset.
- Exit code is `1` when any `required` entry is `missing` or `blocked`, or when
  any `env_var` is unset; otherwise `0`.

`check-deps` only verifies; it never runs `install` commands. Install commands
are documentation until a future command renders or executes them.
