# AGENTS

Cross-project working preferences for general-purpose agents.

## Applying these instructions

- Treat these as defaults. More specific repository guidance and explicit task
  requirements refine them unless higher-priority instructions say otherwise.
- A repository-root `AGENTS.md` contains shared project conventions. A repository-root
  `.AGENTS.md` contains personal extensions that must remain untracked.
- If applicable instructions conflict and their precedence does not resolve the
  conflict, ask before proceeding.

## Understand the context

- Before changing a repository, read its top-level guidance and the documentation
  relevant to the affected area.
- Use external research when freshness, precision, or outside evidence would
  materially improve the result. Present meaningful alternatives as comparisons with
  trade-offs.
- Use the platform's built-in search by default. Choose a regional or specialized
  provider when it better covers the sources needed for the task.
- Among similarly suitable providers, prefer included-quota tools over metered tools.
  Escalate only when earlier results are inadequate.
- Ask for missing information only when it would materially change the outcome;
  otherwise state a reasonable assumption and continue.

## Decide and plan proportionally

- Assess the task's scope, ambiguity, risk, and reversibility before modifying files
  or external state.
- For substantial work, maintain a compact task list. Use a table, diagram, or other
  visual only when it makes important relationships easier to inspect.
- Pause for discussion when a consequential choice remains unresolved or a proposed
  change would contradict documented behavior.
- Evaluate user-proposed approaches objectively. Explain material trade-offs and
  suggest improvements when warranted.
- Keep architecture and naming aligned: a name should accurately describe the role of
  the thing it identifies within its context.

## Act and create artifacts

- In durable documents and code comments, describe the resulting system rather than
  the history of the change. For example, prefer "B owns request parsing" over
  "request parsing was moved from A to B." Put transition notes in plans and commits.
- When a repository provides a git-ignored `.tmp/` directory, place agent-generated
  plans, reviews, and other intermediate files under `.tmp/agent/`. Never place
  durable source or documentation there.
- Use a project's managed Python environment when present. For standalone Python
  execution, prefer `uv`; fall back to `python3` when `uv` is unavailable.

## Verify the result

- After changing files, run checks in proportion to the change and its risk. Start
  with focused validation and expand only when broader verification is necessary.
- Prefer the repository's own validation commands and configuration. When none exist,
  use appropriate ecosystem tools already available in the environment.
- Report important checks that failed or could not be run.

## Communicate clearly

- When explaining an unfamiliar subject, establish its concepts and relationships
  before presenting implementation details, code, or commands.
- Explain unfamiliar terms on first use. Expand unfamiliar acronyms; discuss a term's
  origin only when it materially aids understanding.
- In terminal or TUI chat, write simple mathematics with Unicode, such as
  `x² ≤ ∑ᵢ yᵢ`, rather than LaTeX. Use LaTeX only in artifacts whose target
  renderer is known to support it.
