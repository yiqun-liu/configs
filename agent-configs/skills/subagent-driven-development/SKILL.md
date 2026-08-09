---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session, using a dedicated implementation worktree and branch
---

# Subagent-Driven Development

Execute a plan by dispatching a fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review. Core principle: fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

- **Have an implementation plan?** No → manual execution or brainstorm first.
- **Tasks mostly independent?** No (tightly coupled) → manual execution or brainstorm first.
- **Stay in this session?** Yes → this skill. No (parallel session) → execute-coding-plans.

vs. execute-coding-plans: same session (no context switch), fresh subagent per task (no context pollution), automatic review checkpoints (no human-in-loop between tasks).

## The Process

1. **Read the plan once.** Extract all tasks with full text and surrounding context. Create a session task list with the available planning or TODO tool. Re-reading the plan later is wasteful — carry the full text forward into each subagent dispatch.

2. **Prepare an isolated branch.** Confirm `WORKDIR` is a dedicated worktree and branch assigned to this plan; otherwise create one with **using-git-worktrees**. All implementer subagents work and commit only there—never in the caller's worktree or branch. Record `PLAN_BASE_SHA` before the first task.

3. **Per task:**
   - Record a task context before implementation: `WORKDIR` and `BASE_SHA` (the current `HEAD`).
   - Dispatch an implementer subagent using `./implementer-prompt.md`. Provide the full task text + scene-setting context (where this task fits, dependencies, architectural context) — don't make the subagent read the plan file.
   - If the implementer asks questions, answer clearly and completely before letting them proceed. Don't rush them into implementation.
   - Once implemented and self-reviewed, resolve `HEAD_SHA` and dispatch a spec compliance reviewer using `./spec-reviewer-prompt.md`. Pass `WORKDIR`, the full task text, and `BASE_SHA..HEAD_SHA`; the reviewer must inspect that change set rather than trust the report.
   - Spec issues found → the same implementer fixes and commits them → refresh `HEAD_SHA` → the same reviewer re-reviews the updated range. Repeat until ✅.
   - Dispatch a code quality reviewer using `./code-quality-reviewer-prompt.md`. **Only after spec compliance is ✅** — wrong order defeats the two-stage gate.
   - Quality issues found → the same implementer fixes and commits them → refresh `HEAD_SHA` → the same reviewer re-reviews the updated range. Repeat until approved.
   - Mark the task complete in the session task list.

4. **After all tasks:** resolve `PLAN_HEAD_SHA` and dispatch a final `code-review` subagent with `WORKDIR`, the full plan requirements, and `PLAN_BASE_SHA..PLAN_HEAD_SHA`. Stop if the plan-wide range cannot be established.

## Advantages

- Same session (no handoff); continuous progress (no waiting between tasks).
- Fresh context per task — no context pollution, no confusion.
- Two-stage review catches both spec drift (over/under-building) and quality issues.
- Implementer can ask questions before AND during work — issues surface early.

## Red Flags

- **Never dispatch multiple implementer subagents in parallel** — they will conflict on the same files.
- **Never start code-quality review before spec compliance is ✅** — wrong order.
- **Never let implementer self-review replace actual review** — both are needed; self-review catches obvious issues, the two-stage review catches the rest.
- **Never skip the re-review loop** — reviewer found issues = implementer fixes = review again, until approved.
- **Never let a subagent commit outside the dedicated implementation worktree and branch.**

If a subagent fails a task, dispatch a fix subagent with specific instructions rather than fixing manually (avoids context pollution).

## Integration

**Required workflow skills:**

- **write-coding-plan** — creates the plan this skill executes.
- **using-git-worktrees** — provides the dedicated worktree and branch.
- **code-review** — completes development after all tasks.

**Subagents should use:**

- **test-driven-development** — subagents follow TDD for each task.

**Alternative workflow:**

- **execute-coding-plans** — use for parallel session instead of same-session execution.
