# Code Review Skill — Design Document

Design rationale and key decisions for the unified code-review skill.
This document is **not** loaded by the agent during review — it exists
for the skill author's reference.

---

## Origin

Merged three existing review skills (`design-review`,
`structural-review`, `low-level-review`) that evaluated overlapping
concepts (SOLID, coupling, naming, code smells) at different lifecycle
stages with blurry boundaries.

---

## Core Design: Three-Level Review Hierarchy

```
Code Review (driver)
│
├─ Phase 1: Architecture Review
│   Scope unit: module / component boundary
│   Inspects: inter-module interfaces, dependency direction, module
│             decomposition, coupling between modules, requirements
│             alignment
│   Ignores: internal structure of any module
│
├─ Phase 2: Structural Review
│   Scope unit: single module's interior
│   Inspects: inter-function interaction, data structures, helper
│             placement, naming, duplication within the module
│   Ignores: whether the module itself is the right module
│
└─ Phase 3: Implementation Review
    Scope unit: single function / method body
    Inspects: line-by-line correctness, error handling, boundary
              conditions, language-specific pitfalls
    Ignores: module organization
```

Each level treats the level above as given. Architecture doesn't
question requirements. Structural doesn't question module boundaries.
Implementation doesn't question function signatures.

---

## Key Design Decisions

### Review Model

What the review covers, how findings are classified, and how phases
connect.

#### R1: Three-Level Hierarchy with Presets

Two presets exposed to users — Design (Architecture + Structural) and
All (all three phases). Level names are **internal**, not exposed.
When the user says "implementation review" they expect a complete
review, which is the All preset. Scope size suppresses phases:
single-file scope skips Architecture (no inter-module boundaries).

#### R2: Finding Classification

Three independent axes classify every finding:

- **Category** (Design / Bug / Documentation) — for triage.
- **Severity** (Critical / High / Medium / Low) — impact on user or
  developer experience. Latent correctness bugs (safe today, breaks
  under plausible change) rate at least Medium.
- **Rework impact** (`local` / `structural` / `architectural`) — how
  much the fix blocks downstream work. Independent of severity: a
  Medium API redesign is blocking; a High missing error check is not.

Fix proposals consider both runtime guards and documented preconditions
("settled by spec"), choosing whichever suits the API's trust boundary.

#### R3: Phase Transition Protocol

**Scope Model handover** uses structured tables, not prose. Architecture
produces a Module Map (modules, ownership, boundary health). Structural
produces a Component Map (classes/function groups, responsibility,
health). Maps are purely informational — downstream reviewers inspect
all items in scope.

**Early-stop**: a finding blocks the next phase when its fix would
invalidate downstream findings — architectural blocks both lower phases,
structural blocks implementation, local never blocks.

**Staleness**: on fix, mark resolved, delete stale downstream docs,
re-run from affected phase.

#### R4: Checklist Coverage Audit Trail

Before writing findings, the reviewer writes a table of which reference
sections applied vs N/A. Forces explicit acknowledgment of every
checklist section — prevents silent skipping. Written into the findings
document for transparency.

#### R5: Alternative Generation

Always runs at architecture and structural levels. Reveals weaknesses
that checklist scanning may miss. Architecture: 2-3 alternative
decompositions. Structural: per-component simplification. Skipped when
decomposition is already clean.

### Execution Model

How the skill runs — document management, subagent dispatch.

#### E1: Self-Contained Reviewer Documents

Each level has a `*-reviewer.md` defining what to inspect, references
to load, and how to write findings. The driver SKILL.md contains only
orchestration — no domain knowledge.

#### E2: Subagent Dispatch with Fan-Out

Reviewers can be dispatched as subagents, keeping the driver lean.
Structural fans out by module; implementation by component. Every unit
is inspected — maps provide context, not skip lists. Falls back to
inline sequential execution when subagents are unavailable.

#### E3: Generated Findings Documents

Each phase writes to `.tmp/agent/reviews/{id}/`: scope.md, per-phase
findings (with Scope Model and Checklist Coverage), summary.md. The
driver confirms files are written before proceeding.

#### E4: Document Extraction is Scope-Conditional

Architecture reviewer loads document extraction based on scope size —
skip for single files, load for directory-level and above.

### Adaptive Review Metrics

How the skill adapts to different codebases, languages, and paradigms.

#### A1: Scenario References Span All Levels

Concurrency, performance, and testing manifest at all three levels with
different signals. Scenario files have per-level sections; each reviewer
loads only its level's section.

#### A2: Language-Specific Pitfall Guides

Implementation phase detects language from file extensions and loads
`references/implementation/lang/{c,cpp,python}.md`. Architecture and
structural phases use paradigm adaptions (A3) instead.

#### A3: Paradigm Adaptions (Inline)

Architecture and structural references include inline paradigm
adaptions — vocabulary translation and conditional applicability. No
separate overlay files.

For **procedural code**: "class" → file/module, "interface" → header
API or `struct ops`, "inheritance" → embedded parent struct. LSP and
ISP apply conditionally — only when OOP idioms are detected (struct
embedding, `struct ops` vtables, type enum + void* dispatch). Otherwise
marked N/A in checklist coverage.

Paradigm detected in SKILL.md Step 1, written to scope.md.

#### A4: Project Documentation First

Architecture reviewer reads existing project docs (README, style guide,
design docs) before inspecting code. Findings contradicting documented
conventions are invalid.

---

## Reference Organization

`references/{level}-reviewer.md` — self-contained per-level reviewers.
`references/process.md` — shared severity, rework impact, communication
guidelines. Templates for findings documents and output formats are in
`references/template/`.
`references/{architecture,structural}/` — level-specific checklists
(with inline paradigm adaptions where needed).
`references/implementation/lang/` — per-language pitfall guides.
`references/scenarios/` — cross-level scenario files with per-level
sections. Each reviewer loads only the references it needs; the driver
never loads reference documents.
