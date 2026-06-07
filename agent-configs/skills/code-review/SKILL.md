---
name: code-review
description: "Unified code review across three levels — architecture (inter-module boundaries), structural (within-module organization), and implementation (line-by-line correctness). Use when the user asks to review, inspect, or assess any code for quality. Handles scope from a single function to an entire project. Also use for opinions on API shape, naming, helper placement, or design quality. Also reviews design plans, specs, and architecture proposals — document-only mode runs architecture-level assessment without requiring code. Do not use for commit history quality (→ pr-review)."
---

# Code Review

Review code at three levels, from architecture down to implementation.
Stop early when blocking findings require fixes before deeper review
is meaningful.

## The Three Levels

| Level | Scope unit | Looks at | Ignores |
|-------|-----------|----------|---------|
| Architecture | Module/component boundary | Inter-module interfaces, dependency direction, module decomposition | Internal structure of any module |
| Structural | Single module interior | Inter-function interaction, data structures, helper placement, naming | Whether the module itself is correct |
| Implementation | Single function body | Line-by-line correctness, error handling, boundary conditions | Module organization |

**Each level treats the level above as given.** Architecture doesn't
question requirements. Structural doesn't question module boundaries.
Implementation doesn't question function signatures.

### Document-Only Mode

When the user provides a design plan, spec, or architecture proposal
(instead of code files), the review runs in document-only mode. This
mode runs architecture-level assessment only — alternative generation,
SOLID evaluation, integration/risk assessment, and deviation analysis
against the document. Structural and implementation phases are skipped
since there is no code to inspect at those levels.

---

## Subagent Model

Each level has a self-contained reviewer document
(`references/{level}-reviewer.md`) that defines what to inspect, what
references to load, and how to write findings. Each reviewer reads
upstream findings and writes its own findings document.

When subagents are available, **dispatch phases as subagents** rather
than loading reviewer documents into the driver's context. The driver
only reads findings documents — never reviewer instructions or
reference checklists.

### Fan-out patterns

Architecture review runs as a single subagent (it needs the full scope
to assess inter-module boundaries).

**Structural review** fans out by module: dispatch one subagent per
module listed in the architecture findings' Module Map. Every module
in scope must be inspected — the Module Map provides context, not
a skip list. Each subagent writes its own findings document
(e.g. `structural-findings-{module}.md`).

**Implementation review** fans out further: dispatch one subagent per
component group from the structural findings' Component Map. Every
component in scope must be inspected. Each subagent writes
`implementation-findings-{component}.md`.

The driver merges findings from parallel subagents into a consolidated
view before presenting to the user.

When subagents are not available, load the reviewer document inline
and execute its process directly (sequential, no fan-out).

---

## The Process

### Step 1: Scope + Phase Selection

Determine what to review and which preset to use.

**Gather scope:**

- User-named file, directory, or project
- Git range if reviewing changes: `git diff --stat {BASE}..{HEAD}`

**Input type detection:**

Determine whether the review target is code or a design document.

| Signal | Input type |
|--------|-----------|
| File path ends in `.md`, `.rst`, `.txt` and user calls it a "plan", "spec", "design", "proposal", or "architecture document" | Document |
| User asks to "review this design/plan/spec/proposal" and provides a prose document | Document |
| User provides a file path or directory containing source code | Code |
| Git range or diff-based review | Code |

When ambiguous, ask the user. Input type determines the preset and
whether document extraction is the primary input source.

**Paradigm detection:**

Detect the programming paradigm from file extensions and code patterns.
Check for OOP idioms in procedural languages — embedded parent structs,
`struct ops` function pointer tables, type enum + void* dispatch.

| Signals | Paradigm |
|---------|----------|
| `.c`/`.h` files, no OOP idioms | Procedural |
| `.c`/`.h` files, with struct embedding or `struct ops` | Procedural with OOP idioms |
| `.cpp`/`.hpp` with `class`, inheritance, `virtual` | OOP |
| `.py` with `class`, inheritance | OOP |
| Mixed | Note primary paradigm, flag OOP idioms where found |

**Phase selection:**

Three presets exist. All user requests map to one of these.

| User request | Preset | Phases run |
|-------------|--------|-----------|
| "design review", "architecture review" (of code) | Design | Architecture + Structural |
| "review this plan/spec/design/proposal" (document input) | Design Doc | Architecture only (document-only mode) |
| Everything else — "review this", "any bugs?", "implementation review", unspecified | All | Architecture + Structural + Implementation |

Level names are internal — not exposed to users. When the user says
"implementation review" they expect a complete review, which is the All
preset.

**Scope size adaptation:**

The preset determines which phases *attempt* to run. Scope size and
input type determine which phases actually make sense:

- **Single file**: skip Architecture (no inter-module boundaries to
  inspect). Structural and Implementation still apply.
- **Directory or project**: all phases in the preset run.
- **Document input** (Design Doc preset): Structural and Implementation
  are always skipped regardless of scope size — there is no code to
  inspect at those levels. Architecture runs in document-only mode.

**Create review directory:**

```
mkdir -p .tmp/agent/reviews/{timestamp-or-id}/
```

Write `scope.md`:

```markdown
# Review Scope

**Target**: [file/directory/project/document]
**Input type**: [Code / Document]
**Git range**: [BASE..HEAD or N/A]
**Phase**: [Design / Design Doc / All]
**Paradigm**: [OOP / Procedural / Procedural with OOP idioms / N/A (document)]
**User intent**: [what the user wants from the review]
**Scope size**: [single file / directory / project / document]
```

Load `references/process.md` for severity system and rework impact.
Load output templates from `references/template/` as needed.

### Step 2: Architecture Review (if applicable)

Dispatch or execute `references/architecture-reviewer.md`.

The reviewer reads `scope.md`, performs its inspection, and writes
`architecture-findings.md` to the review directory. When dispatching
as a subagent, confirm the file was written before proceeding.

**Skip if:** scope is a single file (code input), or preset is Design
and scope has no inter-module boundaries to assess.

**After completion**, read the "Blocking Assessment" section of
`architecture-findings.md`:

- Findings with `architectural` rework impact → **stop and present**
- No blocking findings → proceed to Step 3

If stopping:
1. Present findings to user
2. Offer next-step options from the output template
3. Wait for user to fix blocking issues
4. Mark resolved findings `[resolved]`, update `scope.md`, re-run
   Step 2

### Step 3: Structural Review (if applicable)

Dispatch or execute `references/structural-reviewer.md`.

When using subagents, fan out by module — one subagent per module from
the architecture findings' Module Map. Every module in scope must be
inspected.

The reviewer reads `scope.md` and `architecture-findings.md`, performs
its inspection, and writes `structural-findings.md` (or per-module
findings files). Confirm files were written before proceeding.

**Skip if:** preset does not include Structural — Design Doc preset
skips this phase.

**After completion**, read the "Blocking Assessment" section:

- Findings with `architectural` rework impact → **stop** (escalate)
- Findings with `structural` rework impact → **stop and present**
- No blocking findings → proceed to Step 4

If stopping: same protocol as Step 2.

### Step 4: Implementation Review (if applicable)

Dispatch or execute `references/implementation-reviewer.md`.

When using subagents, fan out by component group — one subagent per
component from the structural findings' Component Map. Every component
in scope must be inspected.

The reviewer reads `scope.md`, `architecture-findings.md`, and
`structural-findings.md`, performs its inspection, and writes
`implementation-findings.md` (or per-component findings files). Confirm
files were written before proceeding.

No lower phase exists — report all findings.

**Skip if:** preset is Design or Design Doc (Architecture phase only, or
Architecture + Structural only).

### Step 5: Output

Present consolidated findings across all completed phases. When
subagents produced per-module or per-component files, merge them into
a unified view ordered by severity.

Use the output format from `references/template/code-review-output.md`.
For Design Doc preset, use
`references/template/design-review-output.md`.

Write `summary.md` to the review directory with the full output.

Offer structured next steps:

```
How would you like to proceed?
1. Fix all findings
2. Fix Critical/High only
3. Fix specific items (tell me which)
4. No changes needed
```

**Do not implement any fixes until the user explicitly confirms.**

---

## Early-Stop Rules

A finding **blocks the next phase** when its fix would invalidate the
next phase's findings:

| Current phase | Finding rework impact | Action |
|--------------|----------------------|--------|
| Architecture | `architectural` | Stop. Fix. Re-run architecture. |
| Architecture | `structural` or `local` | Continue to structural. |
| Structural | `architectural` | Stop. Fix. Re-run from architecture. |
| Structural | `structural` | Stop. Fix. Re-run structural. |
| Structural | `local` | Continue to implementation. |
| Implementation | any | Report all. No lower phase to block. |

### Staleness Prevention

When the user fixes a blocking issue:

1. Mark the finding as `[resolved]` in the findings document
2. If the fix has `structural` or `architectural` rework impact:
   **delete** downstream findings documents (they are stale)
3. Update `scope.md` with the fix details
4. Re-run from the affected phase

---

## Boundaries

- Do not force a commit-message or diff-summary workflow into code
  review
- Do not require tests to pass before presenting findings
- Do not implement fixes until the user confirms
- Do not question requirements — that is the user's domain
(exception: deviation analysis in document-only mode maps requirements
to design elements as an assessment lens, not to question the
requirements themselves)
- PR review (commit history, stale comments) is a separate skill
