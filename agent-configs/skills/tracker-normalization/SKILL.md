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

Ask the user two questions:

1. **"Normalize existing trackers, or also extract new trackers from
   non-tracker content?"** — "Normalize only" uses the discovery
   procedure below. "Extract" requires the user to point to source
   documents (see Step 2).

2. **"Inspect only uncommitted changes, or the entire repo?"** —
   determines the file set for normalization. Extraction always
   uses only the user-specified files.

### 2. Discover candidate sections

**Normalization** — follow the small/large scope procedure below.

**Extraction** — the user must point to the source document(s).
Read only those files — do not search subdirectories or discover
additional candidates beyond what the user specified. Identify the
content to extract into a tracker section.

**Small scope** (≤ ~30 markdown or text files named `TODO`): read every
file. Find sections which are a set of goals of targets.

**Large scope**: first-pass grep all markdown section headers
(`^#{2,6}\s+\S`). Keep headings whose text contains (case-insensitive,
substring) any of: `TODO`, `Goal`, `Task`, `Work`, `Plan`, `Sprint`,
`Milestone`, `Checklist`.

Second-pass: for each candidate heading, read the section body and
**confirm** it has structured items (bullet lists, checkbox lists, tables)
— not just prose or code blocks. If many candidates, use subagents in
parallel.

### 3. Classify and pick format

Use the reference doc's "Choosing a format" section (→ Syntax →
Choosing a format) for trade-offs. The format depends on two
dimensions: **how many fields per entry** and **is there hierarchy?**

| Items per entry | Hierarchy? | Convert to |
|---|---|---|
| One field | Any | **Checkboxes** |
| Multiple fields | No | **Table** |
| Multiple fields | Yes | **Mixed** (checkboxes for structure, per-group tables for metadata) |

If the section is already trawl-compatible (`- [ ]`/`- [x]` or valid
tables with recognized headers), no format change is needed — just
run the column header audit below. Skip sections with only prose,
inline TODOs, or code blocks and report why.

Prose alongside structured items becomes a `Notes`/`Description`
column in a table. Nested items map to checkboxes with indentation
preserving the hierarchy naturally.

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

- **Never add or remove items.** Only change list markers (`* `/`- ` →
  `- [ ]`) and apply table formatting where chosen.
- **Never change the section's scope.** Same heading level, same items.
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

### 6. Verify

After every conversion, run `trawl --path <dir> --no-tui` and confirm:

- Every expected goal appears with correct progress/status.
- No unexpected goals appear (e.g., from substring false matches in
  header keyword registration).
- No goals that should be visible are missing.

If a goal is missing, follow the diagnosis decision tree from the
fetched reference doc (→ Verification → Diagnosing missing goals).
Fix any issues, re-run verification, then proceed.

### 7. Report

After verification passes, report a summary:

```
Tracker normalisation complete.

Converted:
  path/to/book-tracker/README.md: "## TODO" (12 checkbox items)
  path/to/other.md: "## Goal tracker" (table, 6 rows)

Config-only (no structural change):
  path/to/book-tracker/README.md: "## Goal Tracker" — added "chapter" to headers.task

Skipped:
  path/to/notes.md: "## TODO" — prose only, no structured items
  path/to/scratch.md: "## Plan" — code blocks only

.trawl.toml: updated (added section name "Goal tracker"; excluded ".agents/"; added "chapter" to headers.task)

Verification: trawl --path <dir> --no-tui — 14 goals, all visible, no false positives.
```
