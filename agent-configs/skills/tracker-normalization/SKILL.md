---
name: tracker-normalization
description: Normalize TODO / Goal tracker sections into trawl-compatible format. Trigger when TODO or Goal sections have been reviewed and the user explicitly wants them to be trawl-compatible.
---

# Tracker Normalization

Ensure an existing repository has trawl-compatible work-tracker sections
at minimum maintenance cost. Related project: [trawl](https://github.com/yiqun-liu/trawl).

## References

Fetch the trawl goal tracker compatibility reference before normalizing:

https://raw.githubusercontent.com/yiqun-liu/trawl/main/docs/goal-tracker-compatibility.md

**The fetched reference doc defines the facts (what trawl requires);
this skill defines the procedure (what the normalizer should do).**

## Procedure

### 1. Scope

Ask the user three questions:

1. **"Normalize existing trackers, or also extract new trackers from
   non-tracker content?"** — "Normalize only" uses the discovery
   procedure below. "Extract" requires the user to point to source
   documents (see Step 2).

2. **"Inspect only uncommitted changes, or the entire repo?"** —
   determines the file set for normalization. Extraction always
   uses only the user-specified files.

3. **"Also attempt multi-file correlation?"** — after normalization,
   optionally link trackers across the directory hierarchy via
   cross-document references (Step 6). Off by default; say yes only if
   parent/child trackers should form a hierarchy.

### 2. Discover candidate sections

**Normalization** — follow the small/large scope procedure below.

**Extraction** — the user must point to the source document(s).
Read only those files — do not search subdirectories or discover
additional candidates beyond what the user specified. Identify the
content to extract into a tracker section.

**Small scope** (≤ ~30 markdown or text files named `TODO`): read every
file. Find sections that contain a set of trackable goals or tasks.

**Large scope**: first-pass grep all markdown section headers
(`^#{2,6}\s+\S`). Keep headings whose text contains (case-insensitive,
substring) any of: `TODO`, `Goal`, `Task`, `Work`, `Plan`, `Sprint`,
`Milestone`, `Checklist`.

Second-pass: process each candidate as a tree. For a candidate heading,
classify its *direct* content (the items before any deeper heading):

- **Structured** (bullet lists, checkbox lists, or tables) → keep.
- **Prose, but predominantly enumerating goals or tasks** → keep as
  *transformable* (see Step 3). "Predominantly" means the prose is mostly
  imperatives, deliverables, milestones, or sequenced action items — e.g.
  "First implement X, then write tests for Y, and ship Z by Friday" —
  rather than explanation, history, or discussion.
- **Narrative/context prose, inline TODOs only, or code blocks only** →
  skip and report why.

Then recurse: every deeper heading inside the candidate is a subsection
(a group node within the same tracker), so classify its direct content
the same way and continue down the tree. Subsections are part of the
candidate, not separate ones — they are normalized with it, never
re-listed.

A second keyword-matching heading at the same or higher level
is a different tracker that trawl will silently ignore (first-match-wins;
see the reference doc → Detection) — flag it to the user rather than
processing it.

If many candidates remain, use subagents in parallel.

### 3. Classify and pick format

Use the reference doc's "Choosing a format" table (→ Syntax → Choosing a
format) as the authoritative format menu — do not re-derive it here. Pick
by two dimensions: **how many fields per entry** and **is there
hierarchy?** As a heuristic:

- **One field per entry** → checkboxes.
- **Multiple fields, flat** → table.
- **Multiple fields, hierarchical** → mixed (checkbox tree for structure,
  per-group tables for metadata).
- **Large tracker needing named phases, or an objective spanning multiple
  files** → subsection headings or cross-document references (see the
  reference doc's corresponding rows).

If the section is already trawl-compatible (`- [ ]`/`- [x]` or valid
tables with recognized headers), no format change is needed — just
run the column header audit below. Skip sections with only narrative
or context prose, inline TODOs, or code blocks and report why.
Transformable-prose candidates (flagged in Step 2) follow the
prose→structure procedure below.

Prose alongside structured items becomes a `Notes`/`Description`
column in a table. Nested items map to checkboxes with indentation
preserving the hierarchy naturally.

#### Plain bullets: group container or task?

A plain bullet (`- Foo`) is ambiguous — decide per bullet (see the
reference doc's group-node rules → Syntax):

- It is a **group container** if it names a phase/category whose children
  are the real work items (e.g. `- Sprint 1` with `- [ ] task` children).
  Keep it as `- ` — converting it to `- [ ]` would give a structural
  container a spurious checkbox state.
- It is an **incomplete task** if it represents a single trackable work
  item. Convert to `- [ ]`.

#### Cross-document references

If the objective spans multiple files, consider a `[[target]]` (or
`[display](target)`) reference line that pulls in another doc's tracker
as a subtree. Syntax and target preconditions are in the reference doc
(→ Syntax → Cross-document references) — do not restate them here. When
in doubt whether a multi-file objective should be one tracker or several
linked by references, ask the user.

#### Column header compatibility audit

**Before** picking a format, audit every table's column headers against
the keyword lists from the fetched reference doc (→ Syntax → Tables →
Column detection). This is a **mandatory** check — a single unrecognized
header can make an entire table invisible to trawl.

For each table column, determine whether it is *intended* as a standard
field (task, state, owner, priority, tag, due). If a column serves as
one of these fields but its header text does not contain any keyword
from the corresponding list in the reference doc, **flag it** for
`.trawl.toml` registration. Example: a `| Chapter |` column that serves
as the task description does not contain any task keyword — it must be
registered.

See the reference doc's substring matching caution (→ Syntax → Tables →
Column detection) for false-positive risks when registering keywords.

#### Transformable prose → structure

For each transformable-prose candidate (flagged in Step 2), rewrite the
prose into checkbox items: one `- [ ]` per goal or task the prose
actually enumerates, preserving order and wording. **Do not invent tasks
the prose does not contain** — this is faithful extraction, not
generation. Because rewriting prose can drop qualifiers, prerequisites,
or context, route every transformable-prose candidate through the
information-loss check immediately below and confirm with the user
before converting.

#### Information loss check

After picking a format, list any fields, attributes, or prose that
would be dropped by the transformation (e.g. prerequisites, practice
exercises, learning objectives). Warn the user explicitly and ask
whether to preserve them in a `Notes`/`Description` column or accept
the loss.

### 4. Pick heading name and configure `.trawl.toml`

1. Read any existing `.trawl.toml` for the `goal_section_names` list.
2. If the original heading matches a name from the reference doc's
   section detection rules (→ Detection → Section detection) — **keep
   it**.
3. If the heading is non-standard (`## Tasks`, `## Learning Plan`, …) —
   pick a name that traces back to the original while matching the
   **convention of the document**:
   - If the doc's other headings use sentence case (`## Getting started`) →
     use sentence case (`## Goal tracker`).
   - If they use title case → title case (`## Goal Tracker`).
   - If they use ALL CAPS → all caps (`## GOAL TRACKER`).
   Record the new name in `.trawl.toml`'s `goal_section_names`.
4. If multiple names are needed across files, register all of them.
5. When creating a **new** tracker section (extraction), ask the user
   for the heading name. Apply the same convention-matching rules.
   If the chosen name is not a trawl default, register it in
   `.trawl.toml`'s `goal_section_names`.
6. Do **not** rename across the entire repo if the original name is
   already trawl-recognisable under the same naming convention.
7. **Prefer `Goal Tracker` over `TODO`** for a section that is purely a
   tracker. `TODO` is also a default inline keyword, so a `## TODO`
   heading is additionally captured as an inline task (by design — a
   heading may double as a reminder). `Goal Tracker` avoids that overlap
   (see the reference doc → Detection → Section detection).

**Inbound-reference safety**: before moving/renaming a file, or removing
its only tracker section, check whether other docs reference it via
`[[…]]`. References resolve by **file path**, not section name (see the
reference doc → Syntax → Cross-document references) — so renaming a
section is always safe, but moving a file or stripping its last tracker
breaks every inbound reference. Flag affected inbound links to the user
before proceeding.

Generate or update `.trawl.toml` when any of these conditions apply:

- **Header keyword registration** (routine): flagged during the column
  header compatibility audit. Domain-specific vocabulary like "Chapter",
  "Paper", or "Recipe" is legitimate — trawl should adapt via config,
  not require the user to rename their columns.
- **Section name registration** (last resort): a non-standard heading
  name was picked in steps 3–5 above. Prefer renaming the heading to
  match a trawl default unless the name carries domain meaning.
- **Exclude paths**: noise directories (`.agents/`, `vendor/`, …)
  should be excluded from scanning.

Always merge with an existing `.trawl.toml` if one is present. Omit the
file entirely if none of the three conditions above apply.

### 5. Convert

- **Never add or remove items.** Convert list markers to trawl form, but
  selectively: incomplete-task bullets (`* `/`- `) → `- [ ]`; **group
  containers stay as `- `** (see Step 3's plain-bullet decision). Apply
  table formatting where chosen.

  > Converting an approved transformable-prose candidate (Step 3) to
  > checkbox items is restructuring, not addition: each enumerated goal or
  > task becomes one `- [ ]` item; nothing the source does not contain may
  > be introduced.
- **Never change the section's scope.** Same heading level, same items.
- **Do not re-level internal subsection headings** — a heading's level
  relative to the section defines group-node nesting; changing it
  restructures the tree.
- **Preserve reference lines as-is** — a `[[target]]` or
  `[display](target)` that is the entire line content is structurally
  meaningful; do not embed it in prose, strip it, or rewrap it in a
  bullet it did not have.
- Preserve nesting: indentation maps to milestones (items with children)
  and leaf tasks (items without children).
- Do not alter metadata tokens (`@owner`, `#tag`, `!priority`, `~due`)
  already present in the text.
- Map existing status indicators to trawl representations:

| Existing indicator | Table cell | Checkbox |
|---|---|---|
| `COMPLETED`, `DONE`, `done`, `✓`, `~~strikethrough~~` | `done` | `- [x]` |
| `PENDING`, `TODO`, bare text, empty | (empty) | `- [ ]` |
| `IN PROGRESS`, `ON-GOING` | (empty) | `- [ ]` |

> Per the reference doc's Done detection section (→ Interpretation),
> trawl has a binary model: any non-empty state cell without "TODO"
> counts as done. "IN PROGRESS", "wontfix", and "skipped" all count as
> done — which may surprise the user. To keep an item as not-done in a
> table, the state cell must be empty or contain "TODO". To preserve
> intermediate status text, put it in a custom "Notes" column rather
> than the state column.

- **When creating or editing a table**, keep it well-formed so trawl does
  not replace it with a `⚠` warning marker: a separator row (`|---|`)
  directly under the header, at least one header containing a task
  keyword, and **bare values in cells** (`high`, not `!high`; `alice`,
  not `@alice`). The column header already identifies the field — token
  prefixes are inline-only (see the reference doc → Metadata → Column
  override rule). trawl flags a malformed or task-less table in the
  `--no-tui` `warnings:` section, so a silent skip is now catchable there.

### 6. Correlate multi-file trackers

Skip this step entirely unless the user opted in at Step 1.

After every tracker is individually trawl-compatible, look for hierarchy
that spans files: a tracker in a parent directory may have sub-trackers
in child directories (e.g. `foo/README.md` and `foo/bar/README.md`).
Directory nesting *suggests* but does not *imply* goal hierarchy — most
such pairs are independent — so this step only proposes links; the user
confirms every one.

**Discover pairs**: for each tracker, find trackers in its
subdirectories (potential children). For each potential child, look for
a parent item whose text, topic, or directory name corresponds to the
child's title or location (e.g. a parent item `- [ ] Machine Learning`
matches a child titled "Machine Learning" in `ml/`).

**No match → skip**: if no parent item plausibly corresponds to the
child, there is nowhere sensible to attach a reference, so skip the
pair silently. Co-location alone is not a relationship.

**Propose, never auto-link**: for each matching pair, present the
reasoning (parent item ↔ child tracker) and ask the user to confirm.
False hierarchies are worse than flat trackers.

**Link parent → child only**: add a `[[<child>]]` reference line under
the corresponding parent item, making the child a subtree of the parent.
Never add a back-reference — that inverts the hierarchy and risks
cycles. Reference syntax and relative-path resolution are in the
reference doc (→ Syntax → Cross-document references); the child already
satisfies the target preconditions after Step 5.

> This is the only step in the whole procedure that adds content —
> reference lines, each by explicit user confirmation. Step 5's "never
> add items" rule governs normalization; this step has its own charter.

If no plausible pairs are found (or the user declines all), report "no
correlations made."

### 7. Verify

After every conversion, run `trawl --path <dir> --no-tui` and confirm:

- Every expected goal appears with correct progress/status.
- No unexpected goals appear (e.g., from substring false matches in
  header keyword registration).
- No goals that should be visible are missing.
- The `warnings:` section is empty. A non-empty list flags malformed or
  skipped tables (e.g. a missing separator row, or a table with no task
  column), broken references, or cycles — all of which would otherwise be
  silent. This is the single place to catch a table trawl dropped.
- Each converted file's `# H1` heading is correct and meaningful — trawl
  uses it as the goal title and as the display text for inbound
  `[[wikilink]]` references (see the reference doc → Detection →
  File-level derived fields). Typos here become goal titles.

If a goal is missing, follow the diagnosis decision tree from the
fetched reference doc (→ Verification → Diagnosing missing goals).
Fix any issues, re-run verification, then proceed.

### 8. Report

After verification passes, report a summary:

```
Tracker normalisation complete.

Converted:
  <file>: "## TODO" (12 checkbox items)
  <file>: "## Goal tracker" (table, 6 rows)
  <file>: "## GOAL TRACKER" (2 group nodes, 1 [[...]] reference)

Config-only (no structural change):
  <file>: "## Goal Tracker" — added "chapter" to headers.task

Skipped:
  <file>: "## TODO" — prose only, no structured items
  <file>: "## Plan" — code blocks only

Inbound references checked:
  <file> is referenced by N docs via [[<ref>]] — not moved

Correlations (multi-file):
  <parent-file> → [[<child-ref>]] under "<item>"
  <parent-file> → [[<child-ref>]] under "<item>"

.trawl.toml: updated (added section name "Goal tracker"; excluded ".agents/"; added "chapter" to headers.task)

Verification: trawl --path <dir> --no-tui — N goals, all visible, no false positives, no ⚠/↻ markers.
```
