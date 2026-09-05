---
name: serious-code-review
description: >-
  Use for source-code review when the user explicitly requests a serious,
  thorough, formal, deep, or independent review, or when the review target is
  a large rewrite or feature (about 500 changed source lines). Produce an
  evidence-backed review with explicit coverage; use independent review only
  when the user selects it. Do not use for casual feedback, plans, standing
  instructions, general prose, or commit-history review.
---

# Serious Code Review

Review source code thoroughly while keeping findings evidence-based and low-noise.

## Scope

Own an in-depth source-code review; do not review plans, prose, or commit
history, and do not change the reviewed source.

## Trigger

Use this workflow when the user asks for an in-depth review, including an
equivalent natural-language request, or when a requested source review covers
a large rewrite or feature (about 500 changed source lines). The user need not
name the skill.

- Do not use it for casual feedback, design plans, standing instructions,
  general prose, or commit-history review.
- Do not start a review solely because implementation work exceeds the size
  threshold; a source-review request and reviewable code or diff are required.
- Ask for scope or desired depth only when the target or review goal is unclear.

## Inputs and outcome

Establish the review target and deliver an evidence-backed, severity-ranked
report with its coverage and limits made explicit.

- Identify the files, directories, or source diff. Include only direct
  dependencies needed for evidence.
- Estimate changed source lines for size-triggered reviews. Exclude generated,
  vendored, lock, and formatting-only files; use the feature's affected scope
  when a rewrite's line count is misleading.
- Read repository guidance and directly relevant documentation.
- Record the requested focus and fixed project decisions. Treat those
  decisions as constraints, not defects.

## Procedure

Apply the selected review coverage, then inspect and report only supported
findings.

### Establish coverage

Select the lenses and conditional concerns that fit the target. Use
[the review record](references/review-record.md) to mark each as applied or
not applicable.

- **Implementation quality** — behavior, failures, boundaries, resource use,
  local efficiency, readability, and tests. Use for every source review.
- **Structure** — responsibilities, interfaces, cohesion, local dependencies,
  and component-level naming. Use when a cohesive module is in scope.
- **Architecture** — module boundaries, dependency direction, cross-module
  protocols, and system constraints. Use when the target spans modules.
- **Conditional concerns** — concurrency, performance, and testing when the
  target or its documented context makes them relevant.

A finding in one lens may limit confidence in another. State that condition
and its evidence.

### Select review mode

Choose the mode the user requested; direct review is the default.

- **Direct** — inspect the target and report the selected coverage. Use when
  the user wants one thorough review.
- **Independent** — ask a fresh subagent to review from a self-contained
  brief, then verify its claims. Use only when the user explicitly requests
  independent or generative review.

For independent review:

- Give the subagent the target, scope, selected coverage, user focus, and
  documentation needed to understand the target. Do not give it parent
  conclusions.
- Require it to complete the independent portion of
  [the review record](references/review-record.md): limited alternative
  generation, adversarial inputs and relevant scheduling interleavings,
  self-containedness, and evidence-backed results.
- Verify every reported claim against the target before presenting it. Report
  disagreements as questions or omit them.

### Inspect

Inspect the selected coverage against the target, direct dependencies, and
documented conventions.

- Distinguish confirmed findings from questions, assumptions, and strengths.
- Do not invent requirements, recommend unrelated refactoring, or infer a
  defect merely from absent documentation.
- Prefer a clean result over speculative nits. A review with no meaningful
  findings is valid when it says what was checked and what was not covered.

### Report

Present results in severity order using
[the review record](references/review-record.md).

- Every finding names its location, impact, evidence, and a concise suggested
  direction.
- Use severity for impact: Critical must be fixed; High should be fixed;
  Medium merits tracking or fixing; Low is optional and never blocks.
- Separate confirmed findings from questions, assumptions, strengths, and
  omitted coverage.

## Completion

Finish when the user has the review report and its known limitations.

- Do not change source, create commits, or start another workflow as part of
  the review.

## References

Use [the review record](references/review-record.md) to enforce coverage and
the finding format.
