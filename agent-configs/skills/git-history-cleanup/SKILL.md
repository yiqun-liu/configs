---
name: git-history-cleanup
description: "Review a feature branch against a base branch and rebuild it as a clean, buildable commit series on a new branch without modifying the original branch. Uses git worktrees for physical isolation between source and destination. Use when commits need reordering, scope cleanup, per-commit verification, or final tree-equivalence checks."
---

# Git History Cleanup

Use this skill when the user wants a messy branch rewritten into a clean commit stack.

## Scope

This skill is for:
- reviewing a branch against its base branch
- proposing a cleaned commit plan before rewriting
- rebuilding history on a new branch instead of rewriting the original branch
- ensuring each rewritten commit does one thing and builds cleanly
- ending at the same contents as the original branch tip

This skill is not for:
- in-place history rewrites unless the user explicitly asks
- ordinary implementation work where no history cleanup is requested

## Core Rules

- Do not overwrite the source branch unless the user explicitly asks.
- Prefer creating a new branch from the chosen base branch.
- Use git worktrees for physical isolation between the source and destination branches, so the source tree is always available for reference without branch switching.
- Present the planned cleaned history before creating branches or committing.
- Keep each commit narrowly scoped and logically coherent.
- If a file is introduced and then repeatedly reworked, prefer introducing it once in the final commit that has all required dependencies.
- Every rewritten commit should build without warnings when practical.
- The final rewritten branch must end at the same tree as the original source branch.

## First Steps

1. Read repository instructions first.
   Start with `README.md`.
   Read `AGENTS.md`.
   If present, read `AGENTS.local.md`.
2. Read repository docs that define verification or maintainer expectations.
3. Identify:
   - source branch
   - base branch
   - destination branch name
   - commit hygiene requirements such as `git commit -sm`

## Analysis Workflow

1. Inspect the branch graph and commit list from `base..source`.
2. Inspect the final tree diff from `base..source`.
3. Identify bad history patterns:
   - mixed concerns in one commit
   - fixup commits that should fold earlier
   - docs mixed with code when they can stand alone
   - files added too early and then repeatedly reshaped
   - commits that likely fail to build in isolation
4. Map dependencies between changes before proposing a new order.
   Watch especially for:
   - build-system references to files that should land later
   - helper APIs used before they are introduced
   - docs that rely on later names or behavior
5. Present the proposed cleaned history to the user before rewriting.

## Worktree Setup

After the analysis plan is approved and before rewriting:

1. Locate or create the worktree directory.
   Check in priority order:
   - `.worktrees/` (preferred, hidden)
   - `worktrees/` (alternative)
   If neither exists, ask the user where to create worktrees.

2. Verify the worktree directory is gitignored.
   ```bash
   git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
   ```
   If not ignored, add it to `.gitignore` and commit before proceeding.

3. Create a worktree for the destination branch.
   ```bash
   git worktree add .worktrees/<destination-branch> -b <destination-branch> <base-branch>
   ```

4. Optionally create a worktree for the source branch if you need frequent file-level reference.
   ```bash
   git worktree add .worktrees/<source-branch> <source-branch>
   ```

5. Run project setup in the destination worktree and verify a clean baseline.
   ```bash
   cd .worktrees/<destination-branch>
   # Auto-detect and run appropriate setup (npm install, cargo build, etc.)
   # Run tests to confirm baseline is clean
   ```

The source branch worktree is read-only reference — never commit to it.
The destination branch worktree is where all rewrite work happens.

## Rewrite Workflow

Work is done inside the destination branch worktree (e.g. `.worktrees/<destination-branch>`).

1. From the base branch state in the destination worktree, reconstruct each commit intentionally.
   Prefer staging selected file states from the source worktree instead of blindly replaying the original order.
   For example, to grab a file at a specific historical state:
   ```bash
   # From inside the destination worktree:
   git checkout <historical-commit> -- path/to/file
   # Or, if a source worktree exists, copy directly:
   cp /path/to/.worktrees/<source-branch>/path/to/file path/to/file
   git add path/to/file
   ```
2. If one historical commit contains multiple concerns, split it by staging only the files or hunks that belong in the current commit.
3. If an early staged state causes a build failure due to a later dependency, fix the split now rather than carrying the bad boundary forward.
4. Commit each step with a specific message.
   Use `git commit -sm` when the user asks for signed-off commits.
5. After each commit, build and verify (see Verification section) inside the destination worktree.

## Verification

After staging each rewritten commit:
- run `git diff --cached --stat`
- run `git diff --cached --check`
- run the repository's relevant build command

If stronger maintainer verification is required by repo docs and feasible, run that too.

## Final Validation

At the end:
1. Build the rewritten branch tip again (in the destination worktree).
2. Compare the rewritten branch against the original source branch.
3. Verify exact tree equivalence, for example with:

```bash
git rev-parse <destination-branch>^{tree} <source-branch>^{tree}
git diff --stat <destination-branch>..<source-branch>
```

The tree hashes should match and the diff should be empty.

4. Clean up worktrees.
   ```bash
   git worktree remove .worktrees/<destination-branch>
   git worktree remove .worktrees/<source-branch>  # if created
   ```

## Output Expectations

When reporting completion:
- give the new branch name
- list the cleaned commit history in order
- state that the original branch was not modified
- state what verification was run
- state whether the rewritten branch matches the original source tree exactly
- mention any non-obvious split decisions that were needed to keep commits buildable

## Integration

**Calls:**
- **using-git-worktrees** — REQUIRED for setting up the destination (and optionally source) worktree before the rewrite phase begins

**Called by:**
- Any skill or workflow that needs a messy branch cleaned before merging, reviewing, or continuing work