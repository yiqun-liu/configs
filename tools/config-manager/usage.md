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

Options:

| Option | Applies To | Meaning |
| --- | --- | --- |
| `--id ID` | all commands | Operate on one entry id; may be repeated |
| `--dry-run` | `deploy`, `collect` | Validate and print planned changes without prompting or modifying files |
| `--json` | `list` | Print machine-readable JSON |

Examples:

```powershell
python tools/config-manager/manage.py list
python tools/config-manager/manage.py deploy --dry-run
python tools/config-manager/manage.py deploy --id agent-skills
python tools/config-manager/manage.py compare --id opencode-config --id codex-agents
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
