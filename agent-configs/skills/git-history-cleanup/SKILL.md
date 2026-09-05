---
name: git-history-cleanup
description: >-
  Use only when the user explicitly asks to rebuild a feature branch as a clean
  commit series: reorder or split commits, fold fixups, verify each commit, or
  prove tree equivalence. Rebuild on a new branch without modifying the source
  branch. Do not use for ordinary implementation, in-place history rewrites,
  or commit-message-only changes.
---

# Git History Cleanup

Rebuild a feature branch as a clean, independently valid commit series while
preserving the original branch and its final tree.

## Scope

Own history analysis and reconstruction on a new branch; do not modify the
source branch or change the feature's final contents.

- Do not use for an in-place rewrite unless the user explicitly expands scope.
- Do not use for ordinary implementation or a commit-message-only change.

## Trigger

Use this skill only for an explicit request to clean, reorder, split, or
otherwise rebuild a feature branch's commit history.

## Inputs and outcome

Identify the source, base, destination, and repository constraints, then
produce a new branch whose final tree equals the source branch's final tree.

- Input: source branch, base branch, destination branch name, and any commit
  convention such as signed-off commits.
- Input: repository instructions and documentation defining setup, validation,
  and maintainer expectations.
- Outcome: an approved commit plan, a clean destination series, per-commit
  validation results, and final tree-equivalence evidence.

## Procedure

Analyze the existing branch, obtain approval for the new series, then rebuild
it in isolated worktrees according to `AGENTS.md`.

### Analyze history

1. Inspect the graph, commits, and final diff for `base..source`.
2. Identify mixed concerns, fixups, premature file introduction, and commits
   that cannot plausibly validate in isolation.
3. Map dependencies between code, build configuration, documentation, and
   interfaces before deciding commit boundaries.
4. Propose the destination commit series in order. State each commit's purpose,
   files or logical changes, dependencies, and validation boundary.
5. Obtain the user's approval before creating the destination branch or commits.

### Rebuild commits

1. Create the isolated destination worktree and branch using the general
   worktree rules in `AGENTS.md`. Keep the source available for reference
   without switching or committing to it.
2. Reconstruct each approved commit intentionally from the base state. Stage
   selected source states, files, or hunks; do not blindly replay the original
   commit order.
3. Keep every commit narrowly scoped and logically coherent. If a split exposes
   a dependency or validation failure, revise that boundary rather than carry a
   broken intermediate commit forward.
4. Commit with the repository's required convention, including sign-off only
   when required.
5. Before each commit, inspect the staged result with `git diff --cached
   --stat` and `git diff --cached --check`, then run the validation appropriate
   to that commit's scope when practical.

## Completion

Finish only after the destination series is valid and its final tree matches
the source branch.

1. Run the repository's relevant final build or tests in the destination
   worktree.
2. Compare the destination and source tree objects, for example:

   ```bash
   git rev-parse <destination-branch>^{tree} <source-branch>^{tree}
   git diff --stat <destination-branch>..<source-branch>
   ```

   The tree IDs must match and the diff must be empty.
3. Report the destination branch, ordered commit list, validation performed,
   tree-equivalence result, and any non-obvious split decision.
4. Leave worktrees in place unless the user asks to remove them.
