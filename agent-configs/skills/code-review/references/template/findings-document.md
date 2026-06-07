# Findings Document Template

Each phase writes a findings document to
`.tmp/agent/reviews/{id}/{phase}-findings.md` using this structure.

---

```markdown
# {Phase} Findings

**Scope reviewed**: [modules/components/functions]

### Scope Model

This section provides structured context for downstream phases. The
downstream reviewer reads this section to understand what was inspected
— without re-deriving the map from findings prose.

**Downstream reviewers inspect all items in scope.** The maps provide
context (what exists, what each thing owns), not prioritization. A
module with clean inter-module boundaries may still have structural or
implementation issues that only deeper inspection reveals.

**Architecture phase** produces a **Module Map**:

| Module | Files | Ownership | Boundary health |
|--------|-------|-----------|----------------|
| [name] | [glob or file list] | [single-sentence responsibility] | ✅ Clean / ⚠ [issue summary] |

**Structural phase** produces a **Component Map** (one table per
module reviewed):

| Component | Location | Responsibility | Health |
|-----------|----------|----------------|--------|
| [class/function group] | file:line-range | [single-sentence purpose] | ✅ / ⚠ [issue] |

**Implementation phase** does not produce a Scope Model (leaf phase —
no downstream consumer).

### Checklist Coverage

Before writing findings, list which reference sections were applied and
which were N/A. This creates an audit trail — it forces the reviewer to
acknowledge every checklist section rather than silently skipping items.

```markdown
| Reference section | Applied | Notes |
|-------------------|---------|-------|
| SOLID § SRP | ✅ | [brief note on what was checked] |
| SOLID § OCP | ✅ | ... |
| SOLID § LSP | N/A | No inheritance in this codebase |
| ... | ... | ... |
```

### Findings

1. **[Category] [Severity] [rework-impact]** Brief title
   - **Location**: file:line
   - **Description**: what's wrong
   - **Why it matters**: impact on correctness/maintainability
   - **Suggested fix**: resolution (if not obvious)

2. ...

**Category** is one of:

| Category | When to use |
|----------|------------|
| Design | Architectural, structural, or organizational issues |
| Bug | Correctness defects, latent or active |
| Documentation | Missing, incorrect, or misleading docs |

**Suggested fix** guidance: consider both approaches and propose the
better one for the API's trust boundary:

- **Runtime guard**: add a check, return error, or assert at the call
  site. Appropriate for public APIs where callers cannot be trusted.
- **Settled by spec**: document the precondition in the API contract and
  trust callers to conform. Appropriate for internal APIs where the
  caller is within the same trust boundary and a runtime check adds
  unnecessary overhead. State the precondition explicitly in the fix.

### Blocking Assessment

- Finding #N is blocking: [reason — what downstream work it invalidates]
- Finding #M is not blocking: [reason — fix is local]

### Not Covered

- [Anything the reviewer couldn't assess without more context]
```
