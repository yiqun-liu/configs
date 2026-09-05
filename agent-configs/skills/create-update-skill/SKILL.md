---
name: create-update-skill
description: >-
  Use when work creates, updates, renames, removes, or changes a direct
  resource of an agent skill package. Define a distinct trigger and outcome,
  write the smallest durable instruction package that changes agent behavior,
  and verify its metadata, structure, and local references. Do not use for
  general repository instructions, one-off task plans, or ordinary
  documentation.
license: Complete terms in LICENSE.txt
---

# Create or Update Skill

Create, update, rename, or remove a skill whose trigger, outcome, and
non-obvious guidance are worth loading independently of general instructions.

## Scope

Own skill-package changes, including direct scripts, references, and assets.
Put cross-cutting behavior in `AGENTS.md` and one-off task information in the
task or its documentation.

## Trigger

Use this skill whenever a task changes a `SKILL.md` or a direct bundled
resource, including creation, renaming, and removal.

- Do not use it for an ordinary document, repository instruction, or unrelated
  file that merely mentions a skill.

## Inputs and outcome

Use the requested change, target environment, and non-obvious task facts to
deliver a small, valid skill package or a deliberate removal.

- Input: representative requests, expected result, authority boundaries, and
  relevant local conventions or tools.
- Outcome: an accurate `SKILL.md` and only the supporting resources the skill
  repeatedly needs, or a removal with all direct references updated.

## Procedure

Decide the skill boundary, design its lookup structure, then create or revise
only the resources that support that boundary.

### Decide the boundary

- State the skill's distinct trigger and completed outcome in one sentence
  each. Do not create or retain a skill when either cannot be stated clearly.
- Put general safety, planning, testing, or subagent rules in `AGENTS.md`.
- Prefer a task-specific document or direct answer for one-off information.

### Design the instruction package

- Put the triggering condition and exclusions in frontmatter `description`;
  this is what is available before the skill body loads.
- Use one explicit organizing axis for every enumeration, section hierarchy,
  table, taxonomy, and checklist. An ad-hoc division mixes axes, makes missing
  cases hard to see, and silently loses coverage. Common axes include:
  - **Type** — for example, declarative → imperative → behavioral → relational
    claims.
  - **Granularity** — for example, inline → paragraph → section → document.
  - **Linguistic level** — for example, word → sentence → discourse.
- Workflow skills use the shared top-level order: Scope, Trigger, Inputs and
  outcome, Procedure, Completion, then Exceptions or References only when
  needed. Put workflow-specific modes, stages, and checklists under Procedure.
- Use this standard workflow layout when creating or restructuring a workflow
  skill:

  ```markdown
  # <Skill Title>

  <one-line purpose>

  ## Scope
  <what this skill owns and excludes>

  ## Trigger
  <activation condition and exclusions>

  ## Inputs and outcome
  <required context and completed result>

  ## Procedure
  <ordered stages, modes, or criteria>

  ## Completion
  <completion condition and report>

  ## Exceptions
  <only when bounded departures exist>

  ## References
  <only when conditional supporting material exists>
  ```

  Omit empty Exceptions and References sections.
- Start non-trivial sections with a line explaining their contents. Use ordered
  steps, criteria, and short examples instead of explanatory prose.
- Persist only preferences, authority limits, project facts, decision rules,
  and completion criteria that change future behavior.
- Write rules consistently: `Must` and `Never` are unconditional; `Must …
  unless …` names an exception; `Prefer` is a justified default; and `May` is
  optional. Group ad-hoc exceptions under Exceptions and keep them to five or
  fewer.
- Make optional, costly, or opinionated workflows explicit-only. Use automatic
  activation only for a precise condition where omission would be harmful.
- Completing a skill reports its result and waits for user direction. It must
  not automatically invoke another skill or begin follow-on work.

### Add reusable resources

- Add a script only for deterministic, fragile, or repeatedly recreated work;
  test it when it is added or changed.
- Add a reference only for detailed facts needed conditionally. Link it directly
  from `SKILL.md` and say when to read it.
- Add an asset only when the produced result uses it.
- Do not create placeholder directories, sample files, changelogs, or auxiliary
  guides. Do not duplicate information between `SKILL.md` and a reference.

### Create, update, rename, or remove the skill

Create the smallest directory that supports the selected design.

```markdown
---
name: <lowercase-hyphenated-name>
description: <what it does; positive trigger; important exclusions>
---

# <Skill Title>

<one-line purpose>
```

- `name` and `description` are required. Add other frontmatter fields only
  when the target platform permits and needs them.
- Preserve user-authored resources and existing compatible behavior when
  updating a skill.
- When removing or renaming a skill, update its direct index and cross-skill
  references before completion.

### Verify

- Confirm frontmatter is valid, the name matches the directory, and the
  description describes both activation and exclusions.
- Confirm every local reference exists and every bundled resource is used.
- Run relevant focused checks for changed scripts or generated artifacts.
- Review the diff for duplicated, generic, transitional, or unreachable text.

## Completion

Report the skill's trigger, outcome, files changed, and verification result.

- For every added or materially changed section, report its agent-facing value:
  the behavior it adds or changes, why it belongs in this skill, and why it is
  not already supplied by another instruction or resource. Flag a section with
  no distinct value for removal.
- Use this review format when it helps the user inspect a substantive update:

  ```markdown
  | Section | Change | Agent-facing value |
  | --- | --- | --- |
  | Verify | Added focused checks | Prevents invalid metadata from persisting. |
  ```

Do not commit, install, or deploy the skill unless the user explicitly asks.
