---
name: structural-review
description: "Inspect code for structural quality before or outside merge-readiness work. Use when the user asks to review, inspect, assess, or clean up a specific code area for ownership leaks (modeling responsibility leaks), abstraction mismatches, naming problems, duplication, refactoring opportunities, or whether logic should move. Also use when the user asks for an opinion on API shape, naming, or helper placement. Do not use for merge-preparation reviews — use code-review instead."
---

# Structural Review

Use this skill when the user asks to review, inspect, assess, or clean up a specific code area and the primary goal is structural quality rather than merge preparation.

Typical triggers:

- "review this file/directory"
- "any cleanup opportunities here?"
- "does this helper belong in common?"
- "is this a good API/name?"
- "should this logic move into a shared module?"

Do not use this skill for generic post-implementation wrap-up. For test verification, diff summaries, commit messages, or merge-readiness checklists, use the separate `code-review` skill.

## Review Focus

Inspect for:

- ownership and abstraction boundaries
- helper placement and module responsibility
- duplication and missed shared helpers
- naming quality and API shape
- unnecessary state, wrappers, or indirection
- local complexity that can be reduced without changing behavior
- inconsistencies between related files after recent refactors

Structural review may mention correctness risks, but maintainability and design are the default focus unless the user asks for a bug hunt.

## Process

### 1. Inspect First

Read the relevant files before suggesting changes.

- Start with the narrowest area the user named.
- Read nearby shared helpers or docs only when needed to judge ownership.
- Build a concrete picture of how the code is used before proposing moves or renames.

### 2. Identify Findings

Present findings first.

- Prioritize real issues over style preferences.
- Prefer concrete findings with file and line references.
- Distinguish clearly between:
  - bugs or regressions
  - design or abstraction issues
  - optional cleanup opportunities

If no meaningful findings exist, say so explicitly instead of inventing nits.

### 3. Recommend the Right Abstraction Level

When suggesting cleanup, prefer the smallest shared abstraction that matches existing usage.

- Keep low-level helpers when they are already useful.
- Add higher-level wrappers only when callers are repeatedly rebuilding the same operation.
- Do not move logic into shared code if it is still test-local or introduces knobs only one caller needs.

### 4. Change Only If Requested

If the user asked for review only, stop after findings and recommendations.

If the user asked to implement the cleanup:

- preserve behavior unless a behavior change is explicitly requested
- keep edits local and consistent with current naming
- reuse existing shared helpers when possible
- verify the affected build/tests after changes when feasible

### 5. Report Verification Separately

Verification status is separate from review findings.

- Structural review can still be useful even before verification.
- If changes were made, report what was verified and what was not.

## Output Shape

Default response order:

1. findings, ordered by severity
2. open questions or assumptions
3. brief recommendation or change summary

When the user asks for an opinion rather than a formal review, a short conclusion is fine, but still anchor it in code references.

## Review Heuristics

The heuristics below take C/C++/Rust projects as an example; the same reasoning applies to other paradigms with analogous concepts.

- If a leaf file repeatedly resolves shared topology or formatting details, consider a higher-level helper in the shared module.
- If a shared header starts parsing environment variables or policy strings, question whether configuration ownership is leaking into modeling code.
- If a struct or helper name is technically correct but vague, prefer names that reveal scope and responsibility.
- If two call sites build the same object shape independently, consider a constructor/helper.
- If a field or temporary exists only to feed one nearby statement, inline or remove it unless it improves clarity.

## Verification Guidance

After implementing a structural cleanup:

- run the smallest relevant build or test step first
- prefer project-local verification commands from repo docs
- if verification cannot be run, say so plainly

## Boundaries

- Do not force a commit-message or diff-summary workflow into structural review.
- Do not require tests to pass before presenting inspection findings.
- Do not dispatch subagents unless the user explicitly asks for delegation.
