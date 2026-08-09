---
name: execute-coding-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Execute Coding Plans

Load a written plan, review it critically, execute tasks in batches, report between batches for architect review.

**Commit ownership:** create commits only in a dedicated worktree and branch assigned to this execution session. Otherwise stop at each commit boundary, report the proposed message, and let the user commit. Never commit in the caller's worktree or branch.

## The Loop

1. **Review the plan critically** — read the design and plan file. Raise questions or concerns before starting; if none, create a session task list with the available planning or TODO tool and proceed.
2. **Execute a batch (default: first 3 tasks)** — for each task: mark in_progress, follow the plan's steps exactly, run the verifications it specifies, mark completed.
3. **Report** — when the batch is done, show what was implemented and the verification output. Say "Ready for feedback." and wait.
4. **Continue** — apply local feedback, then execute the next batch. If feedback changes the plan or fundamental approach, return to plan review and synchronize the task list before continuing. Repeat until all tasks are complete.

## When to Stop

Stop executing immediately and ask for clarification when:

- a blocker appears mid-batch (missing dependency, test fails, instruction unclear),
- the plan has critical gaps preventing you from starting,
- verification fails repeatedly.

Ask rather than guess. Don't force through blockers.

## Completion

After all tasks are verified, use the **code-review** skill to verify the work end-to-end. Then propose a commit message for the completed work.
