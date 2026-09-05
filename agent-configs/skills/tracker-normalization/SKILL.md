---
name: tracker-normalization
description: >-
  Use only when the user explicitly wants TODO or Goal tracker sections made
  trawl-compatible, including faithful extraction of tracker items from
  user-specified documents. Preserve task meaning and hierarchy; add multi-file
  links only when the user explicitly requests correlation.
---

# Tracker Normalization

Make existing or user-specified task material trawl-compatible with the minimum
semantic change required.

## Scope

Own tracker normalization and faithful tracker extraction; do not invent tasks,
silently discard information, or create a hierarchy from directory layout alone.

- **Normalization** converts existing tracker sections.
- **Extraction** turns task-enumerating content in user-specified documents into
  a tracker section. It is faithful restructuring, not task generation.
- **Correlation** adds parent-to-child tracker references only as an explicitly
  requested, separately confirmed extension.

## Trigger

Use this skill only when the user explicitly asks for trawl compatibility,
tracker normalization, or tracker extraction.

## Inputs and outcome

Use the user's target, requested mode, and the current trawl compatibility
reference to produce verified, compatible trackers.

- Input: the target directory, changed files, or source documents. For
  extraction, the user must name the source documents; do not discover more.
- Input: whether the work is normalization, extraction, or both. Ask only when
  the request does not make that choice clear.
- Input: whether to correlate trackers across files. Default to no correlation.
- Outcome: converted or extracted sections, a merged `.trawl.toml` only when
  required, verification results, and a report of changes and skips.

## Procedure

Read the authoritative trawl reference, then discover, transform, and verify
only the selected material.

### Read the compatibility reference

Fetch and read the current
[trawl goal-tracker compatibility reference](https://raw.githubusercontent.com/yiqun-liu/trawl/main/docs/goal-tracker-compatibility.md).

The reference defines trawl syntax and behavior. This skill defines how to
preserve meaning while applying it.

### Discover candidate material

Inspect only the user-selected scope.

- **Normalization** — find candidate goal/task sections. Keep direct content
  that is structured or predominantly enumerates goals; skip narrative context,
  inline TODOs, and code-only sections, and report the reason.
- **Extraction** — inspect only the user-specified documents. Identify the
  material that explicitly enumerates goals or tasks; do not search adjacent
  files or infer additional work.
- Treat deeper headings as groups within the same candidate. A second matching
  tracker heading at the same or higher level may be ignored by trawl; flag it
  rather than normalizing it as the same tracker.

### Choose a compatible representation

Select the smallest representation that preserves the tracker structure.

- Use checkboxes for one field per item, tables for flat items with multiple
  fields, and a mixed form for hierarchical items with metadata.
- Treat a plain bullet as a group only when its children are the actual tasks;
  otherwise convert it to an incomplete task.
- Audit every table header against the reference's recognized fields. Register
  domain-specific task, state, owner, priority, tag, or due-date headers in
  `.trawl.toml` rather than renaming meaningful vocabulary.
- Keep a recognized section heading. If a non-standard heading must remain,
  register it in `.trawl.toml`; otherwise prefer a recognized name that follows
  the document's heading convention.
- List information that conversion could lose. Before converting prose or
  dropping qualifiers, ask the user whether to preserve it in a description or
  notes field.

### Apply the minimal transformation

Convert the selected material without changing its task meaning.

- Never add or remove task items. Extraction may create one task per goal the
  selected prose explicitly enumerates, but may not invent tasks.
- Preserve heading levels, nesting, reference-only lines, and existing metadata
  tokens such as owners, tags, priorities, and dates.
- Map existing status only according to the reference. In particular, trawl's
  table state is binary: a non-empty state that is not `TODO` counts as done.
  Preserve intermediate status in a notes field when it must remain not-done.
- Keep edited tables structurally valid and use the reference's column-value
  conventions so trawl does not skip them.
- Merge `.trawl.toml` with existing configuration. Create it only for required
  header or section-name registration, or selected scan exclusions.
- Before moving a file or removing its only tracker section, check inbound
  tracker references and ask the user before breaking them.

### Correlate trackers

Run this step only when the user explicitly requested multi-file correlation.

- Normalize each tracker before considering links.
- Propose a parent-to-child reference only when a parent task clearly matches a
  child tracker by topic or stated relationship. Directory nesting alone is not
  enough.
- Explain each proposed link and obtain confirmation before adding it. Never
  add a reverse link.

### Verify

Run `trawl --path <dir> --no-tui` after conversion and resolve relevant
warnings.

- Confirm every expected goal appears with its intended status.
- Confirm no unexpected goals appear and no expected goals are missing.
- Confirm `warnings:` is empty, including warnings for malformed tables,
  skipped trackers, broken references, or cycles.
- Confirm each converted file has a meaningful H1 because trawl uses it for the
  goal title and inbound-reference display text.

## Completion

Finish when verification passes or remaining limits are clearly reported.

```text
Converted: <file and tracker format>
Extracted: <file and source material, if any>
Config-only: <.trawl.toml change, if any>
Skipped: <file and reason>
Correlations: <confirmed links, or none>
Verification: <trawl command and result>
```

Do not create follow-on trackers or change unrelated content after reporting.

## References

Use the current
[trawl goal-tracker compatibility reference](https://raw.githubusercontent.com/yiqun-liu/trawl/main/docs/goal-tracker-compatibility.md)
for syntax, recognition, and diagnostic facts.
