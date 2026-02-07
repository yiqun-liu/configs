---
name: code-review
description: "Verify tests, propose commit messages, and optionally dispatch code review subagent after completing tasks"
---

# Code Review

## Overview

Prepare completed work for review and merge with commit message proposal and optional code review dispatch.

## When to Use

After implementing a task, before moving to the next task or wrapping up.

## The Process

### Step 1: Verify Tests

```bash
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before proceeding:

[Show failures]
```

Stop. Cannot proceed with review until tests pass.

**If tests pass:** Continue to Step 2.

### Step 2: Show Changes Summary

```bash
git diff --stat HEAD~1..HEAD
```

Brief summary of files touched and changes made.

### Step 3: Propose Commit Message

Format with conventional commits style:

```
<type>: <short description>

- Detail 1
- Detail 2

Refs: #<issue-id>
```

Types: feat, fix, refactor, docs, test, chore

### Step 4: Code Review Option

Present review findings (from previous reviews if any) and ask:

```
Tests: ✅ PASSED
Changes: <N> files changed

[1] Request code review and continue
[2] Skip review, I'm confident
```

**If [1]:** Dispatch `@capture-knowledge` subagent with changes summary, then dispatch `@code-review/code-reviewer` subagent.

**If [2]:** Continue to next task.

## Example

```
Tests: ✅ 12/12 PASSED

Changes:
 src/auth.ts    +87/-12
 tests/auth_test +42/-0

Proposed commit:
---
feat: add JWT authentication with RS256

- Implement token generation with 24h expiry
- Add refresh token rotation
- Store tokens in httpOnly cookie

Refs: #42
---

[1] Request code review and continue
[2] Skip review, I'm confident

Which?
```

## Integration

**Called by:**
- `@subagent-driven-development` - After each task

**Calls:**
- `@capture-knowledge` - Optional, when user confirms
- `@code-review/code-reviewer` - For detailed code review
