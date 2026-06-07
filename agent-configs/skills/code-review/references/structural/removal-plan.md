# Removal Plan — Structural Review Lens

Identify dead, unused, or feature-flagged-off code and determine whether
it can be safely deleted now or should be deferred with a tracking plan.

---

## Classification

### Critical — Immediate Removal Needed

Code that poses a security risk, significant cost, or blocks other work.
Remove immediately after verification.

### High — Remove This Sprint

Code with active consumers that need a short migration window.
Plan removal within the current iteration.

### Medium — Backlog / Next Iteration

Code that can be deferred. No urgency, but should be tracked for
future cleanup.

### Safe to Delete Now

Code with **no active consumers** — no references, no tests, no config
that would activate it.

Evidence required before declaring "safe to delete":

- Searched codebase for all references (`rg`, `grep`)
- Checked for dynamic/reflection-based usage (string-based lookups,
  config-driven instantiation)
- Verified no external consumers (APIs, SDKs, public interfaces)
- Confirmed feature flag telemetry shows zero usage (if applicable)

### Defer with Plan

Code that **has active consumers** or requires migration before removal.

Cannot delete immediately because:

- Active callers still depend on it
- Needs stakeholder sign-off
- Requires a migration path for consumers
- Feature flag still on for some users

---

## Removal Template

### Safe to Delete Now

| Field | Details |
|-------|---------|
| **Location** | `path/to/file.ts:line` |
| **Rationale** | Why this should be removed |
| **Evidence** | Unused (no references found), dead feature flag, deprecated API |
| **Impact** | None / Low — no active consumers |
| **Deletion steps** | 1. Remove code, 2. Remove tests, 3. Remove config references |
| **Verification** | Run tests, check no runtime errors, monitor logs post-deletion |

### Defer Removal

| Field | Details |
|-------|---------|
| **Location** | `path/to/file.ts:line` |
| **Why defer** | Active consumers, needs migration, stakeholder sign-off required |
| **Preconditions** | Feature flag off for N weeks, telemetry shows 0 usage |
| **Breaking changes** | API/contract changes for consumers |
| **Migration plan** | Steps for consumers to migrate away |
| **Timeline** | Target date or sprint |
| **Validation** | Metrics to confirm safe removal (error rates, usage counts) |
| **Rollback plan** | How to restore if issues found |

---

## Checklist Before Removal

- [ ] Searched codebase for all references (`rg`, `grep`)
- [ ] Checked for dynamic/reflection-based usage
- [ ] Verified no external consumers (APIs, SDKs, docs)
- [ ] Feature flag telemetry reviewed (if applicable)
- [ ] Tests updated/removed
- [ ] Documentation updated
- [ ] Team notified (if shared code)