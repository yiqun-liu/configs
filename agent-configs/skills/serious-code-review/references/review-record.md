# Serious Review Record

Use this record to make a thorough review inspectable without manufacturing findings.

## Brief

Capture the review target before inspection.

```markdown
Target: [files, directory, or diff]
Goal: [questions the review must answer]
Constraints: [documented decisions that are not review findings]
Documentation read: [files, or none]
```

## Coverage

Record every lens and conditional concern as **Applied** or **N/A**, with a
short reason.

```markdown
| Coverage | Status | Evidence or reason |
| --- | --- | --- |
| Implementation quality | Applied / N/A | |
| Structure | Applied / N/A | |
| Architecture | Applied / N/A | |
| Concurrency | Applied / N/A | |
| Performance | Applied / N/A | |
| Testing | Applied / N/A | |
```

When applied, check the relevant concerns below.

- **Implementation quality** — observable behavior; input and error boundaries;
  cleanup and resource lifetime; local cost and allocation in known hot paths;
  clarity of control flow, names, and tests.
- **Structure** — a single understandable responsibility; ownership and
  interface contracts; cohesion; local dependency direction; testable seams.
- **Architecture** — module boundaries; dependency direction; protocol and
  error contracts; cross-module state, consistency, and failure handling.
- **Concurrency** — shared mutable state; atomicity; lock or transaction
  scope; retries and idempotency; ordering; partial failure; back-pressure.
- **Performance** — measured or structurally evident hot paths; asymptotic
  cost; repeated work or copying; unbounded growth; resource contention. Do
  not report hypothetical micro-optimizations.
- **Testing** — observable behavior rather than implementation detail;
  boundaries and failures; determinism; meaningful integration coverage at
  external contracts.

## Independent checks

Use this section only for user-selected independent review.

```markdown
Core intent: [the problem, independent of the current implementation]

Alternatives considered:
- [At most two materially different, constraint-respecting alternatives]
- [Why each does or does not expose a weakness: complexity, coverage, or
  a likely documented change]

Adversarial conditions:
- [Input, failure, retry, or relevant scheduling interleaving]
- [Observed behavior and supporting code]

Self-containedness:
- [Whether responsibilities, interfaces, and assumptions are understandable
  from code and relevant docs]
```

Do not generate alternatives for fixed requirements or trivial components. If
the current arrangement is already the simplest supported by the evidence,
record that as a strength.

## Findings

Report only confirmed, in-scope findings; a clean result is valid.

```markdown
### [Severity] [short finding title]

Location: [path:line or component]
Impact: [who or what is affected]
Evidence: [specific behavior, path, dependency, or missing invariant]
Suggested direction: [concise, non-prescriptive correction]
```

Then list separately.

```markdown
Questions and assumptions:
- [context required to assess a concern]

Strengths:
- [specific justified design or implementation choice]

Not covered:
- [coverage omitted and why]
```
