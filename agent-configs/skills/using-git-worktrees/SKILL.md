---
name: using-git-worktrees
description: "Creates an isolated git worktree for multi-commit work. Trigger when a task is too large for a single well-scoped commit. Do not trigger for single-commit changes (bug fixes, config tweaks) or exploratory/throwaway work."
---

# Using Git Worktrees

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching. Use for multi-commit tasks; skip for single-commit changes or throwaway exploration.

## Directory Selection

Priority order:

1. Existing `.worktrees/` (preferred, hidden) or `worktrees/` — use whichever exists; `.worktrees/` wins if both.
2. Preference specified in `AGENTS.md` — `grep -i "worktree.*director" AGENTS.md` and use it without asking.
3. Default to `.worktrees/` (project-local, hidden) — no need to ask.

Bind the selected directory to `worktree_root`, then derive `path="$worktree_root/$BRANCH_NAME"`. Reuse these values for verification, creation, setup, and reporting.

## Safety: Verify Ignored Before Creating

If `worktree_root` is project-local, it MUST be gitignored before `git worktree add`:

```bash
git check-ignore -q "$worktree_root"
```

If it is not ignored, add that exact directory to `.gitignore` and ask the user to commit before proceeding. Do not create the worktree until the ignore rule is committed. Skipping this pollutes `git status` with worktree contents.

## Setup

1. Create the worktree: `git worktree add "$path" -b "$BRANCH_NAME"` (omit `-b` for an existing branch), then work inside `$path`.
2. Run project setup in the new worktree — auto-detect from `package.json` / `Cargo.toml` / `pyproject.toml` / `requirements.txt` / `go.mod` (or the project's documented setup). Skip if none applies.
3. Verify a clean baseline: run the project's test command. If tests fail, report failures and ask whether to proceed or investigate — you can't distinguish new failures from pre-existing ones if you silently continue.

The requesting workflow owns this worktree and branch. Agents assigned to it may commit there; they must not switch or commit in the caller's worktree or branch.

## Report

```text
Worktree ready at <absolute value of $path>
Tests: <pass/fail summary>
Ready to implement <feature-name>
```

## Common Mistakes

- **Skipping ignore verification** — worktree contents get tracked, polluting git status.
- **Proceeding with failing baseline tests** — can't tell new bugs from pre-existing ones. Report and ask.
- **Hardcoding directory location** — follow the priority order above; don't assume.
