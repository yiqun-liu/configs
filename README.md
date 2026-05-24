# Configurations

A repo of Yiqun's personal configuration files. The goal is to:
- Make configurable software behave consistently across machines
- Enable fast syncing across Windows, macOS, and Linux machines

## Config Manager

The `manage.sh` and `manage.ps1` wrappers call the cross-platform Python config
manager at `tools/config-manager/manage.py`.

The tool syncs configuration files with these commands:

### Commands

| Command | Description |
|---------|-------------|
| `./manage.sh list` | Show configured mappings |
| `./manage.sh compare` | Show differences between repo and system |
| `./manage.sh deploy` | Sync configs from repo to system |
| `./manage.sh collect` | Sync copy-managed configs from system to repo |

### collect

Syncs machine configurations to the repository:

```bash
./manage.sh collect
```

For each copy-managed item, copies from the system path to the repo path. Link
entries are validated but not copied because the repo source is canonical.

### deploy

Deploys configurations from the repository to the system:

```bash
./manage.sh deploy
```

Prompts for confirmation before deploying each config. Use `y` to deploy, `n`
to skip. Use `--dry-run` to validate and preview actions without modifying
files.

### compare

Shows differences between repository and system configurations:

```bash
./manage.sh compare
```

- Handles both files (e.g., `.vimrc`) and directories (e.g., `.config/nvim`)
- Checks link targets for link-managed entries
- Shows missing or different paths

## Setup

```bash
# 1. Review tracked-configs.json and customize targets if needed
nvim tracked-configs.json

# 2. Preview deployment
./manage.sh deploy --dry-run

# 3. Deploy configs
./manage.sh deploy

# 4. After making changes on a machine, collect and commit
./manage.sh collect
git add -A && git commit -m "update configs"
```

## Notes

- Configurations may have external dependencies (e.g., plugin managers, LSP servers)
- Some files are filtered by `.gitignore` to avoid committing compiled or downloaded files
- Works on Windows, Linux, and macOS
