---
name: write-coding-plan
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Write Coding Plan

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. Each task should only do one thing but do it well. DRY. YAGNI. TDD.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the write-coding-plan skill to create the implementation plan."

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Initial evaluation

- Read README.md and design documents in docs/ if not have done so already.
- Evaluate whether the task can be automatically compiled and tested.
  - For example, some projects which require priviledged operation cannot be tested by agents. If so, ask human partner to test when a task has been done

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
  - if some existing tests are affected, update and include them as failing tests
- "Run failing to make sure it fails" - step
  - if the task cannot be run directly by agent, ask them to do so
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
  - if the task cannot be run directly by agent, ask them to do so
- "Present to them and let them do the commit"

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> An implementation plan which is friendly to execute-coding-plans skill.

[design documents (relative path) this plan is based on]

**Goal:** [One sentence describing what this builds]

**Prerequisite**
[bullet points about the dependences / prerequisite]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- One-sentence description (commit message): implement / refactor xxx
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write / Update the failing test**

[test objects: which aspects the function / interface to test (e.g. basic function, boundaries, for function foo)]
[optional, include only core test code for demonstration]

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

[the interface and behavior description (or changes in descriptions), one for each function]

[implementation draft with pseudocode and file references (do what change in what files)]

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

Present to your human partner and let user do the commit
```

## Remember
- Exact file paths always
- pseudocode code in plan to reduce potential cross-session handoff loss
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Execution Handoff

After saving the plan, list the one-line commit message for each task and ask for refinement instructions.

When they approve the task decomposition, offer execution choice:

**"Plan complete and saved to `docs/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with execute-coding-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**
- Guide them to open new session
- **REQUIRED SUB-SKILL:** New session uses execute-coding-plans
