# Tracker Normalization

Ensure an existing repository has trawl-compatible work-tracker sections
at minimum maintenance cost. Related project: [trawl](https://github.com/yiqun-liu/trawl).

Trigger this skill when the user asks to "normalize tracker sections" or
"make this repo trawl-compatible."

## Procedure

### 1. Scope

Ask the user: **"Inspect only uncommitted changes, or the entire repo?"**
The answer determines the file set.

### 2. Discover candidate sections

**Small scope** (≤ ~30 markdown or text files named `TODO`): read every
file. Find sections whose body contains bullets or checkboxes.

**Large scope**: first-pass grep all markdown section headers
(`^#{2,6}\s+\S`). Keep headings whose text contains (case-insensitive,
substring) any of: `TODO`, `Goal`, `Task`, `Work`, `Plan`, `Sprint`,
`Milestone`, `Checklist`.

Second-pass: for each candidate heading, read the section body and
**confirm** it has structured items (bullet lists, checkbox lists, tables)
— not just prose or code blocks. If many candidates, use subagents in
parallel.

### 3. Classify and pick format

For each confirmed section, make a single pass and decide:

| Shape of the section body | Convert to |
|---|---|
| Each entry has **multiple fields** (task + status + owner + priority + …) | **Table** — one column per field |
| Flat list of single-field entries | **Checkboxes** (`- [ ]`) |
| Nested entries (items with sub-items) | **Checkboxes**, indentation preserved |
| Already trawl-compatible (`- [ ]`/`- [x]`) | **No change** |
| Only prose, inline TODOs, or code blocks | **Skip** — report to user why |

The table-vs-checkbox rule: a table earns its width when every entry
carries *more than one* piece of tracked information (e.g. a paper name
AND a venue AND a status). A flat topic list does not.

### 4. Pick the heading name

1. Read any existing `.trawl.toml` for the `goal_section_names` list.
2. If the original heading is an exact match for a trawl-recognised name
   (`GOAL TRACKER`, `TODO`) — **keep it**.
3. If the heading is non-standard (`## Tasks`, `## Learning Plan`, …) —
   pick a name that traces back to the original while matching the
   **convention of the document**:
   - If the doc's other headings use sentence case (`## Getting started`) →
     use sentence case (`## Goal tracker`).
   - If they use title case → title case (`## Goal Tracker`).
   - If they use ALL CAPS → all caps (`## GOAL TRACKER`).
   Record the new name in `.trawl.toml`'s `goal_section_names`.
4. If multiple names are needed across files, register all of them.

Do **not** rename across the entire repo if the original name is already
trawl-recognisable under the same naming convention.

### 5. `.trawl.toml` (only when needed)

Generate or update a `.trawl.toml` **only** when:

- Non-standard section names were picked and need registering, or
- Noise directories (`.agents/`, `vendor/`, …) should be excluded.

Always merge with an existing `.trawl.toml` if one is present.  Omit the
file entirely if trawl's built-in defaults suffice.

### 6. Convert

- **Never add or remove items.** Only change list markers (`* `/`- ` →
  `- [ ]`) and apply table formatting where chosen.
- **Never change the section's scope.** Same heading level, same items.
- Preserve nesting: indentation maps to milestones (items with children)
  and leaf tasks (items without children).
- Do not alter metadata tokens (`@owner`, `#tag`, `!priority`, `~due`)
  already present in the text.

### 7. Report

After every conversion, report a summary:

```
Tracker normalisation complete.

Converted:
  path/to/file.md: "## TODO" (12 checkbox items)
  path/to/other.md: "## Goal tracker" (table, 6 rows)

Skipped:
  path/to/notes.md: "## TODO" — prose only, no structured items
  path/to/scratch.md: "## Plan" — code blocks only

.trawl.toml: updated (added section name "Goal tracker"; excluded ".agents/")
```

## Constraints

- Match heading style to the surrounding document (see Step 4).  Do not
  introduce a style that clashes with the file's existing heading
  convention.
- Read `.trawl.toml` before deciding on section names — never duplicate a
  name that is already configured.
- A `.trawl.toml` is a *last resort* — omit it when the defaults are
  sufficient.
