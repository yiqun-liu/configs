# Spec Compliance Reviewer Prompt Template

Use this template when dispatching a spec compliance reviewer subagent.

**Purpose:** verify the implementer built what was requested — nothing more, nothing less.

```text
Task tool (general-purpose):
  description: "Review spec compliance for Task N"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## What Was Requested

    [FULL TEXT of task requirements]

    ## Authoritative Change Set

    - Working directory: [WORKDIR]
    - Diff range: [BASE_SHA]..[HEAD_SHA]

    ## What Implementer Claims They Built

    [From implementer's report]

    ## CRITICAL: Do Not Trust the Report

    The implementer's report may be incomplete, inaccurate, or optimistic. In WORKDIR, inspect the authoritative diff and actual code independently; use the report only as a pointer. Do not take it as proof of completeness, scope, or interpretation.

    ## Your Job

    Read the implementation code and check:

    - **Missing requirements** — did they implement everything requested? Anything skipped, missed, or claimed-but-not-actually-done?
    - **Extra/unneeded work** — anything built that wasn't requested, over-engineered, or "nice to have"?
    - **Misunderstandings** — did they interpret requirements differently, solve the wrong problem, or implement the right feature the wrong way?

    Report:
    - ✅ Spec compliant (only if everything matches after code inspection)
    - ❌ Issues found: list specifically what's missing or extra, with file:line references
```
