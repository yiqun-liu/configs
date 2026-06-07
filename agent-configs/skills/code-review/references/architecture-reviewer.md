# Architecture Reviewer

Review code at the **module / component boundary** level. Inspect
inter-module interfaces, dependency direction, module decomposition,
cohesion of each module as a whole, coupling between modules, and
requirements alignment. Do not inspect internal structure of any
module — that belongs to structural review.

---

## What This Level Looks At

- Module decomposition: are modules well-separated by responsibility?
- Inter-module interfaces: are they clean, minimal, well-defined?
- Dependency direction: is it correct (infrastructure → domain)?
- Coupling between modules: is it appropriate?
- Cohesion of each module as a whole: does each module serve a single
  purpose?
- State machines at inter-module boundaries: are they well-specified?
- Requirements alignment: does the design address stated requirements?
- Integration risk: breaking changes, migration, data integrity

## What This Level Ignores

- Internal structure of any module (→ structural review)
- Line-level implementation details (→ implementation review)
- Function-level naming or helper placement (→ structural review)

---

## Process

### 1. Understand the Target

Read `scope.md` from the review directory.

**Document-only mode** (when `scope.md` says Input type: Document):

The review target is a design plan, spec, or architecture proposal —
not code. Load
`references/architecture/document-extraction.md` and use the
provided document directly as the design understanding. Present it to
the user for confirmation before proceeding, labeling each part as
"from design document: [path]". Do not attempt code inspection.
After confirmation, proceed to Step 2 to load assessment references,
then continue through Steps 3-9 normally.

**Code review mode** (when `scope.md` says Input type: Code):

If document extraction is applicable (see scope thresholds below),
load `references/architecture/document-extraction.md` and follow its
methodology to build a design understanding.

**Read project documentation first.** Before inspecting any code,
check for existing project docs (README, style guide, design docs,
architecture decision records). Read them. Findings that contradict
documented project conventions are invalid — the code may be
intentionally following a project-specific pattern.

**Scope thresholds for document extraction:**

| Input type | Document extraction |
|-----------|-------------------|
| Document | Always — the provided document is the primary input |
| Code, single file | Skip |
| Code, directory-level (2-10 modules) | Load for context |
| Code, project-level or design doc available | Load fully |

### 2. Load References

**Always load:**

- `references/architecture/assessment.md` — SOLID at inter-module
  scope, coupling metrics, structural anti-patterns
- `references/architecture/alternative-generation.md` — generate
  simpler architecture alternatives

**Paradigm adaptions:** When applying loaded references, note the
"Paradigm Adaptions" section at the top of each reference. For
procedural code, translate vocabulary and conditionally apply LSP/ISP
per the notes in those sections.

**Conditionally load:**

- `references/architecture/document-extraction.md` — if scope warrants
  it (see above)
- `references/architecture/deviation-analysis.md` — if a plan, spec,
  or requirements document is available (always load in document-only
  mode)
- `references/scenarios/concurrency.md` — "Architecture" section — if
  modules interact concurrently
- `references/scenarios/performance.md` — "Architecture" section —
  always (system-level bottlenecks)
- `references/scenarios/testing.md` — "Architecture" section — if
  inter-module contracts need testability assessment

### 3. Alternative Generation

Apply `references/architecture/alternative-generation.md`. Generate
2-3 alternative decompositions and compare against the current design.
This reveals weaknesses that checklist scanning may miss.

### 4. Architecture Assessment

Apply `references/architecture/assessment.md` as a systematic
checklist. Work through every section — do not skip. The reference
covers SOLID at inter-module scope:

- **SRP**: does each module serve a single stakeholder/purpose?
- **OCP**: can new modules be added without modifying existing ones?
- **LSP**: can module implementations be substituted?
- **ISP**: are inter-module interfaces narrow?
- **DIP**: do domain modules avoid importing infrastructure?

Plus: coupling taxonomy, coupling metrics (CBO/Ce/Ca), structural
anti-patterns (Big Ball of Mud, Lava Flow, Spaghetti Code).

### 5. Integration + Risk

Load `references/architecture/integration-risk.md`. Evaluate:

- Breaking changes and migration strategy
- Backward compatibility during transition
- Dependency impact on existing consumers
- Failure modes, performance at scale, data integrity, single points
  of failure

### 6. Deviation Analysis (Conditional)

If requirements or a plan are available, load
`references/architecture/deviation-analysis.md`. Map requirements to
modules, identify missing and unmapped elements.

### 7. Write Scope Model

Before writing findings, produce the **Module Map** section. This is
the structured handover to structural review — the structural reviewer
uses it to understand module boundaries without re-reading your
findings prose.

**Document-only mode:** the Module Map is optional. If the design
document describes modules or components, map them. If it is a
high-level plan without explicit module decomposition, skip the map
and note "Module decomposition not specified in design document —
assessment based on described components and responsibilities."

**Code review mode:** build a table covering every module in scope:

| Module | Files | Ownership | Boundary health |
|--------|-------|-----------|----------------|
| [name] | [glob or file list] | [single-sentence responsibility] | ✅ Clean / ⚠ [issue summary] |

### 8. Checklist Coverage

Write a checklist coverage summary (see
`references/template/findings-document.md`).
Explicitly note which reference sections applied and which were N/A.
Do not silently skip sections — mark them N/A with a brief reason
(e.g., "No inheritance in this codebase" for LSP).

### 9. Write Findings

Write findings to `architecture-findings.md` in the review directory.
Use the findings document format from
`references/template/findings-document.md`. Include
the Scope Model (Module Map) as the first section after the header.

**Document-only mode:** also include a "Design Understanding" section
at the top of the findings, labeling each part as discovered from the
document vs inferred. Include the "Recommended Alternative" section
if alternative generation found a clearly superior approach.

For each finding, assign:
- **Severity**: Critical / High / Medium / Low
- **Rework impact**: `local` / `structural` / `architectural`

Assess blocking: any finding with `architectural` rework impact blocks
both lower phases. Findings with `structural` impact may or may not
block — judge whether the affected scope is narrow enough to proceed.

---

## Finding Examples at This Level

**Design / Critical / architectural**:
Circular dependency between OrderService and PaymentGateway with no
resolution path. The entire order processing chain must be
restructured.

**Design / High / architectural**:
Domain module `OrderService` directly imports database types
(`sqlalchemy.Session`). Infrastructure coupling violates DIP —
requires introducing a repository interface.

**Design / Medium / local**:
Vague module name `Handler` for the notification subsystem. Rename
to `NotificationDispatcher` to reveal purpose.

**Design / Low / local**:
Directory organization preference — feature-first would suit this
project's domain complexity better than layer-first.
