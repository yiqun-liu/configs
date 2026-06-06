---
name: design-review
description: "Review a design plan, architecture proposal, or early-stage implementation for soundness. Use when the user asks to review a plan, spec, or architecture before or during early implementation — checking SOLID, coupling, dependency direction, design patterns, extensibility, and plan-requirement alignment. Do not use for line-by-line correctness (use low-level-review), code organization inspection (use structural-review), or commit history (use pr-review)."
---

# Design Review

Review a design plan, architecture proposal, or early-stage implementation
for architectural soundness before significant code is written.

## When to Use

- User asks to review a plan, spec, or architecture document
- Before or during early implementation, before major code exists
- After writing a plan skill output, before proceeding to implementation
- When evaluating whether a proposed design is fit for purpose

**Do not use** for line-by-line correctness review (→ `low-level-review`),
code organization inspection (→ `structural-review`),
or commit history quality (→ `pr-review`).

## The Process

### Step 1: Context + Document Discovery

Understand what is being designed and why, by progressively discovering
available documentation and filling gaps from implementation where needed.

Load `references/document-extraction.md` for the full process: document
search strategy, completeness assessment, extraction methodology, and
confirmation protocol.

In summary:

1. Search for design doc, interface doc, and change description
2. Assess what's available and what's missing
3. Fill gaps by extracting from implementation (intention, logical view,
   interface contracts — scoped to the change, not the entire project)
4. Present understanding to user for confirmation, labeling each part
   as "discovered from documents" vs "inferred from implementation"
5. Explicitly flag missing documentation as a Medium finding

### Step 2: Alternative Generation

Before the systematic checklist, attempt to **generate simpler or better
alternative approaches** to the proposed design. Comparison reveals
weaknesses that principle-by-principle scanning may miss.

Load `references/alternative-generation.md` and apply its methodology.
Dispatch a subagent if available; otherwise apply inline. The methodology
distills the core intent, generates alternatives at both whole-design
and per-component scope, and compares them against the proposed design
to produce:
- Weaknesses (to merge into severity-sorted findings)
- A recommended alternative (if one is truly better)
- Strengths (components where no simpler alternative exists)

### Step 3: Architecture Assessment

Load `references/architecture-assessment.md` and work through it as a
**checklist** — evaluate every section in order. Do not skip sections or
selectively read. Each section (SRP, OCP, LSP, ISP, DIP, then Beyond SOLID)
must be explicitly checked against the proposed design, even if earlier
sections found no issues. Missing a real defect is worse than confirming
a section is clean.

The reference organizes evaluation points under their relevant SOLID
principle with descriptive scope names: SRP — Responsibility & Cohesion,
OCP — Extensibility & Evolution, LSP — Type Substitutability,
ISP — Interface Design, DIP — Dependency Structure.

For each violation found, explain *why* it matters in this specific context
and suggest a minimal fix.

### Step 4: Integration Assessment

Evaluate how the proposed design fits with the existing system.

- **Breaking changes**: does this design break existing interfaces? If so,
  is there a migration strategy?
- **Backward compatibility**: can existing consumers continue working during
  the transition?
- **Interface contracts**: are new interfaces well-defined with clear input/
  output contracts?
- **Dependency impact**: what existing modules depend on the changed area,
  and are they affected?
- **Data migration** (for persistent storage only): if schema changes are involved, is there a migration
  plan with rollback?

### Step 5: Risk Identification

Identify what could go wrong at the design level.

- **Failure modes**: what are the most likely ways this design could fail
  in production?
- **Performance at scale**: does the design handle 10x/100x growth without
  architectural changes?
- **Data integrity**: are there operations where partial failure could leave
  the data / system in inconsistent state?
- **Single points of failure**: are there components whose failure would
  break the entire system?

### Step 6: Deviation Analysis

Load `references/deviation-analysis.md` and compare the design against
requirements.

- Are all stated requirements addressed by the design?
- If requirements are partially addressed, which are missing and why?
- Are there design elements not traceable to any requirement? (scope creep)
- If the design deviates from an original plan, is the deviation a justified
  improvement or a problematic departure?

### Step 7: Output

Present structured findings using the severity system.

Load `references/output-format.md` for the full output template, clean
review protocol, and next steps confirmation format.

In summary: output includes a Design Understanding section (labeling
discovered vs inferred parts), strengths, findings by severity
(Critical/High/Medium/Low) — with alternative generation weaknesses
merged in, a Recommended Alternative section (if a truly better
approach was found), open questions, recommendations, and a clear
assessment verdict. After presenting findings, offer structured
next-step options and wait for user confirmation before implementing
any revisions.

---

## Severity System

Severity distinguishes **correctness and safety** (Critical, High) from
**maintainability** (Medium, Low):

| Level | Domain | Action | Examples |
|-------|--------|--------|----------|
| Critical | Correctness/safety | Must address before proceeding | Design that guarantees data loss, circular dependencies with no resolution path, shared mutable state with no coordination |
| High | Performance/usability | Should address before implementation | Design bottleneck under load, missing fallback causing poor UX, domain layer importing infrastructure types, missing stated requirement |
| Medium | Maintainability | Address or track as follow-up | Moderate coupling, missing extension point, missing design documentation, scope creep element, unnecessary abstraction layer |
| Low | Maintainability | Optional improvement | Naming suggestion, directory organization preference, minor over-engineering of a single component |

---

## Communication Guidelines

- **Confidence-appropriate framing**: Critical and High findings are
  declarative ("Concurrent access causes data loss"). Medium and Low
  findings are observations ("Extracting this logic would reduce
  duplication") rather than mandates. Do not append interactive questions.
- **Strengths first**: Always acknowledge what's well done before listing
  issues. Be specific.
- **Be honest about uncertainty**: If you can't assess something, say so
  rather than guessing.
