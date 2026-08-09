---
name: capture-knowledge
description: "Create a Markdown memo only when the user explicitly asks to capture or memo information. Do not trigger proactively for information discovered during a workflow."
---

# Capture Knowledge

Create markdown documents to preserve valuable information, decisions, and knowledge discovered during the workflow — anything that would be useful to reference later (decisions and rationale, technical choices and trade-offs, API designs, domain knowledge, problem solutions, configuration details).

Create a memo only from an explicit user request. Do not suggest or create one proactively.

## Path & Format

Save to `docs/memos/YYYY-MM-DD-<topic>.md` (ask the user for the topic, or infer from context). Skeleton:

```markdown
# <Topic> - <Date>

## <Category 1>
[Content]

## <Category 2>
[Content]

## References
[Links, code references like `src/auth.ts:45-92`, or notes]
```

Structure categories based on the information itself — common ones: Context, Decision, Implementation Details, Open Questions, Trade-offs Considered.

## Commit

```bash
git add docs/memos/<filename>.md
git commit -sm "docs: add memo on <topic>"
```

## Tips

- Keep memos focused on one topic.
- Capture the "why" behind decisions, not just the what.
- Include code references (file:line) when relevant.
- Note open questions or pending items.
