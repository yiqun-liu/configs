---
name: capture-knowledge
description: "Create markdown memos documenting requested knowledge and information discovered during workflow"
---

# Capture Knowledge

## Overview

Create markdown documents to preserve valuable information, decisions, and knowledge discovered during the workflow.

## When to Use

**Trigger 1:** You notice valuable information worth documenting → ask user: "Memo this?"

**Trigger 2:** User says "memo this" or similar → create memo immediately

## Valuable Information to Capture

- Decisions made and their rationale
- Technical choices and trade-offs
- API designs or architecture decisions
- Domain knowledge discovered
- Problem solutions found
- Configuration details
- Any information that would be useful to reference later

## The Process

### Step 1: Confirm with User

Ask before creating:

```
Should I memo this? (y/n)

[Repeat back what would be captured]
```

If yes → Step 2. If no → stop.

### Step 2: Determine File Path

Use format: `docs/memos/YYYY-MM-DD-<topic>.md`

Ask user for topic or infer from context.

### Step 3: Create Memo

Format:
```markdown
# <Topic> - <Date>

## <Category 1>
[Content]

## <Category 2>
[Content]

## References
[Links, code snippets, or notes]
```

Structure categories based on the information itself. Common categories:
- Context
- Decision
- Implementation Details
- Open Questions
- Trade-offs Considered

### Step 4: Commit

```bash
git add docs/memos/<filename>.md
git commit -sm "docs: add memo on <topic>"
```

## Example

**User says:** "memo the API authentication strategy we decided on"

**You ask:** "Confirm: Document the JWT with RS256 decision, token expiry details, and refresh token approach?"

**User:** "yes"

**You create:**
```markdown
# API Authentication Strategy - 2026-02-06

## Decision
Use JWT with RS256 for API authentication.

## Implementation Details
- Token expires in 24 hours
- Refresh token rotation enabled
- Stored in httpOnly cookie

## References
src/auth.ts:45-92
tests/auth_test.js
```

**Then commit.**

## Tips

- Keep memos focused on one topic
- Include code references when relevant
- Capture the "why" behind decisions
- Note any open questions or pending items
- Use clear categories appropriate to the content
