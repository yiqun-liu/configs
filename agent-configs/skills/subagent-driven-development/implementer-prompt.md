# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent.

```text
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name]

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## Worktree Ownership

    Work only in [WORKDIR] on [BRANCH], the dedicated worktree and branch assigned to this plan. You may commit there. Do not switch branches, modify another worktree, or commit anywhere else.

    ## Before You Begin

    If anything is unclear about the requirements, approach, dependencies, or assumptions, **ask now** — raise concerns before starting work. While working, if you encounter something unexpected, pause and ask; don't guess.

    ## Your Job

    1. Implement exactly what the task specifies (no more, no less — YAGNI).
    2. For a feature, bug fix, refactor, or behavior change, use the test-driven-development skill; follow its user-approved exceptions.
    3. Self-review with fresh eyes: completeness, naming clarity, overbuilding, and test quality. Fix every issue you find.
    4. Run the relevant verification again after self-review fixes.
    5. Commit the verified work in the assigned worktree and branch.
    6. Report back.

    Work from: [directory]

    ## Report Format

    - What you implemented
    - What you tested and test results
    - Files changed
    - Commit SHA
    - Self-review findings (if any)
    - Any issues or concerns
```
