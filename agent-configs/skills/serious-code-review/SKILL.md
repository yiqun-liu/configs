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
- Before inspection, ask the user to choose **Direct** or
  **Independent/generative** review unless they already selected one. For a
  target too broad for one coherent pass, also offer optional partitioned
  coverage. Do not assume the user knows these forms exist.

## Procedure

Apply the selected review coverage, then inspect and report only supported
findings.

### Select review mode

Ask the user to choose a review form before inspection unless they already
selected one. Do not silently default to a form.

- **Direct** — one reviewer inspects the target and reports the selected
  coverage; no subagent is used.
- **Independent/generative** — ask a fresh subagent to review from a
  self-contained brief, then verify its claims. Explain that it adds limited
  alternative generation, adversarial conditions, and a self-containedness
  check.

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

### Establish coverage

Select the lenses and conditional concerns that fit the target. Use
[the review record](references/review-record.md) to mark each as applied or
not applicable.

- **Implementation quality** — behavior, failures, boundaries, resource use,
  local efficiency, readability, and tests. Use for every source review.
- **Structure** — responsibilities, interface and data-representation design,
  cohesion, local dependencies, and component-level naming. Use when a
  cohesive module is in scope.
- **Architecture** — module boundaries, dependency direction, cross-module
  protocols, boundary-state ownership, and system constraints. Use when the
  target spans modules.
- **Conditional concerns** — concurrency, performance, and testing when the
  target or its documented context makes them relevant.

A finding in one lens may limit confidence in another. State that condition
and its evidence.

### Inspect interface state and representation

When Structure or Architecture applies, use the interface-state inventory in
[the review record](references/review-record.md#interface-state-and-representation)
to reconstruct important boundaries before judging them.

- Map each boundary's purpose and owner, carried state, permitted mutation,
  lifetime, and required invariants.
- Assess representation through one state-oriented axis: ownership, lifecycle,
  validity, grouping, and redundancy.
- Treat parameter count, field count, and duplicated data only as signals.
  Report a finding only when an interface permits an invalid state, hides
  ownership or a required invariant, leaks an inappropriate representation, or
  leaves a duplicate without a justified source of truth and synchronization
  rule.
- Accept redundancy that deliberately creates a stable snapshot, avoids
  measured hot-path recomputation, supports compatibility, or carries
  independently authoritative data when its ownership and update policy are
  clear.

### Partition large targets

Offer partitioned coverage only when the target spans modules or exceeds a
single coherent inspection pass. Use it only if the user selects it.

- Partition by module, directory, or component so every source file is in
  exactly one partition, and inspect every partition.
- Give each partition its own subagent with a self-contained brief: the
  partition's files, selected coverage, user focus, constraints, and the
  documentation needed to understand it.
- Do not fan out cross-partition lenses; architecture and cross-module
  concerns need the whole target in one pass.
- Merge partition findings into one review record. Deduplicate, keep the
  strongest evidence for each finding, and verify each claim against the
  target before reporting it.

### Inspect

Inspect the selected coverage against the target, direct dependencies, and
documented conventions.

- For each applied lens, read only its matching portion of [the bug-class
  index](references/bug-classes.md). Treat entries as hypotheses to test, not
  findings: report one only with a reachable path, violated contract or
  invariant, and concrete impact.
- Distinguish confirmed findings from questions, assumptions, and strengths.
- Do not invent requirements, recommend unrelated refactoring, or infer a
  defect merely from absent documentation.
- Prefer a clean result over speculative nits. A review with no meaningful
  findings is valid when it says what was checked and what was not covered.

### Report

Present results by affected scope using
[the review record](references/review-record.md): architecture first, then
structure, then implementation quality. Within each scope, order findings by
severity.

- Every finding names its location, impact, evidence, and a concise suggested
  direction.
- Put a conditional concern with the broadest scope it affects—for example, a
  cross-module concurrency protocol under Architecture, or a local allocation
  cost under Implementation quality.
- Use severity for impact, not fix effort: Critical must be fixed; High
  should be fixed; Medium merits tracking or fixing; Low is optional and
  never blocks. Do not raise severity for an imagined future change; state a
  supported reachability condition or record uncertainty as a question.
- Separate confirmed findings from questions, assumptions, strengths, and
  omitted coverage.

## Completion

Finish when the user has the review report and its known limitations.

- Do not change source, create commits, or start another workflow as part of
  the review.

## References

Use [the review record](references/review-record.md) to enforce coverage and
the finding format. Use the relevant portion of [the bug-class
index](references/bug-classes.md) during inspection to prime evidence-backed
defect hypotheses.
