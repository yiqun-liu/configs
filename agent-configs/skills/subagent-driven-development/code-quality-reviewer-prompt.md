# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent. **Only dispatch after spec compliance review passes.**

**Purpose:** verify the implementation is well-built (clean, tested, maintainable) on the task's diff range.

```text
Task tool (general-purpose):
  description: "Code quality review for Task N"
  prompt: |
    Review the code quality of one implemented task.

    ## Inputs

    - Task requirements: [full text of Task N from the plan]
    - What the implementer claims they built: [from implementer's report]
    - Working directory: [WORKDIR]
    - Diff range: [BASE_SHA]..[HEAD_SHA]

    ## What to Do

    Review this task-level change set directly; do not invoke the end-to-end code-review skill, which runs only after all plan tasks are complete. Inspect the full diff and any neighboring code needed to assess correctness, test adequacy, and maintainability.

    ## Report

    - Strengths
    - Findings ordered by Critical / High / Medium / Low, each with file:line, impact, and rationale
    - Verdict: Approved / Needs changes
```
