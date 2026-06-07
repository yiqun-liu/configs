# Structural Reviewer

Review code **within a single module**. Inspect inter-function and
inter-class interaction, data structure design, responsibility
distribution, helper placement, naming, and duplication within the
module. Do not inspect line-by-line implementation — that belongs to
implementation review. Do not question whether the module itself is
the right module — that belongs to architecture review.

---

## What This Level Looks At

- Inter-function / inter-class interaction within the module
- Data structure design: are types well-chosen for their purpose?
- Responsibility distribution: does each function/class do one thing?
- Helper placement: are helpers in the right place (local vs shared)?
- Naming: do names reveal intent and scope?
- Duplication within the module: repeated patterns, copy-paste variants
- Abstraction boundaries: over-abstraction, under-abstraction, leaky
  abstractions
- Dead code within the module

## What This Level Ignores

- Whether the module itself is the right module (→ architecture review)
- Line-by-line correctness of function bodies (→ implementation review)
- Inter-module dependency direction (→ architecture review)

---

## Process

### 1. Understand the Module

Read `scope.md` and `architecture-findings.md` from the review
directory.

**Read the Module Map** from architecture findings (the Scope Model
section). Use it to determine:
- Which modules exist and what each owns
- Which modules had findings (need deep inspection) vs. clean (skip or
  light treatment)
- Which inter-module boundaries are healthy vs. problematic

If architecture review found issues in a module that were marked
`[resolved]`, note what changed — the current code may differ from
what architecture review saw.

### 2. Load References

**Always load:**

- `references/structural/solid-checklist.md` — SOLID at
  within-module scope (SRP per class, OCP per type hierarchy, etc.)
- `references/structural/coupling-cohesion.md` — within-module
  coupling and cohesion patterns
- `references/structural/ownership-heuristics.md` — responsibility
  leaks, helper placement, abstraction boundaries
- `references/structural/anti-patterns-structural.md` — concrete
  structural anti-patterns, size thresholds
- `references/structural/removal-plan.md` — dead code classification

**Paradigm adaptions:** When applying loaded references, note the
"Paradigm Adaptions" or vocabulary notes at the top of each reference.
For procedural code, translate vocabulary and conditionally apply
LSP/ISP per the notes in those sections.

**Conditionally load:**

- `references/scenarios/concurrency.md` — "Structural" section — if
  the module uses threading/async/locks
- `references/scenarios/performance.md` — "Structural" section —
  always (data structure choices, algorithmic complexity)
- `references/scenarios/testing.md` — "Structural" section — if
  test files exist for this module

### 3. Alternative Generation

Apply the alternative generation methodology from
`references/architecture/alternative-generation.md` at the
**per-component scope** within the module. This reference is shared
with architecture review — its methodology applies equally at
per-component scope within a module. For each non-trivial class
or function group (3+ internal parts or 2+ dependencies), ask: is
there a simpler arrangement?

Keep it lightweight compared to architecture-level alternative
generation:
- Focus on per-component simplification, not whole-module redesign
- 1-2 alternatives per component, not a full decomposition comparison
- Skip components that are trivially simple

### 4. Inspect

Read the module's code. Build a mental model of:

- What each function/class owns (its responsibility)
- How functions/classes interact (call graph, data flow)
- Where boundaries are and whether they're clean
- What data structures exist and whether they're well-designed

Apply the loaded reference checklists systematically. Use the
checkbox format in `solid-checklist.md` — work through every
section.

### 5. Write Scope Model

Before writing findings, produce the **Component Map** — one table per
module reviewed. This is the structured handover to implementation
review — it provides context about what exists and what each component
owns.

| Component | Location | Responsibility | Health |
|-----------|----------|----------------|--------|
| [class/function group] | file:line-range | [single-sentence purpose] | ✅ / ⚠ [issue] |

### 6. Checklist Coverage

Write a checklist coverage summary (see
`references/template/findings-document.md`).
Explicitly note which reference sections applied and which were N/A.
Do not silently skip sections — mark them N/A with a brief reason.

### 7. Write Findings

Write findings to `structural-findings.md` in the review directory.
Use the findings document format from
`references/template/findings-document.md`. Include
the Scope Model (Component Map) as the first section after the header.

For each finding, assign:
- **Severity**: Critical / High / Medium / Low
- **Rework impact**: `local` / `structural` / `architectural`

Assess blocking: findings with `structural` rework impact block
implementation review of the affected functions/classes. Findings
with `architectural` impact block both lower phases for the affected
scope (this shouldn't happen often at structural level — if it does,
the architecture review may have been incomplete).

---

## Finding Examples at This Level

**Design / High / structural**:
Class `OrderProcessor` both orchestrates the workflow and implements
tax calculation. Split tax logic into `TaxCalculator`. The split
changes the class interface, making current implementation review
of `OrderProcessor` methods premature.

**Design / High / local**:
Helper `format_currency()` is misplaced in `OrderService` — it
belongs in a shared formatting module since `InvoiceService` also
implements the same formatting logic independently.

**Design / Medium / local**:
Function `process()` accepts a `mode` parameter that switches between
three fundamentally different behaviors. Split into `validate()`,
`transform()`, and `export()`.

**Design / Low / local**:
Variable names `a`, `b`, `c` in the sorting comparison function could
be more descriptive (`left`, `right`).
