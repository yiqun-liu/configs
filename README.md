# Configurations

A repo of Yiqun's personal configuration files. The goal is to:
- Make configurable software behave consistently across machines
- Enable fast syncing across machines (Mac and Linux distributions)

## manage.sh

The `manage.sh` script syncs configuration files with three commands:

### Commands

| Command | Description |
|---------|-------------|
| `./manage.sh collect` | Sync configs from system to repo |
| `./manage.sh deploy` | Sync configs from repo to system |
| `./manage.sh compare` | Show differences between repo and system |

### collect

Syncs current system configurations to the repository:

```bash
./manage.sh collect
```

For each configured item, copies from the system path to the repo path.

### deploy

Deploys configurations from the repository to the system:

```bash
./manage.sh deploy
```

Prompts for confirmation before overwriting each config. Use `y` to deploy, `n` to skip.

### compare

Shows differences between repository and system configurations:

```bash
./manage.sh compare
```

- Uses `diff -u -r` with `--color=auto` for colored output
- Respects `.gitignore` to skip ignored files
- Handles both files (e.g., `.vimrc`) and directories (e.g., `.config/nvim`)
- Shows "Only in system" or "Only in repo" for missing items

## Setup

```bash
# 1. Copy example to create working tracked-configs
cp tracked-configs.example tracked-configs

# 2. Customize paths if needed
nvim tracked-configs

# 3. Deploy configs to system
./manage.sh deploy

# 4. After making changes on a machine, collect and commit
./manage.sh collect
git add -A && git commit -m "update configs"
```

## Notes

- Configurations may have external dependencies (e.g., plugin managers, LSP servers)
- Some files are filtered by `.gitignore` to avoid committing compiled or downloaded files
- Works on both Linux and macOS
