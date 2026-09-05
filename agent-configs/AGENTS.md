# AGENTS

Cross-project working defaults for general-purpose agents.

## Instruction resolution

Use these defaults unless higher-priority instructions, an explicit task
requirement, or repository guidance refines them.

- A repository-root `AGENTS.md` holds shared project conventions.
- A repository-root `.AGENTS.md` holds git-untracked personal extensions.
- If applicable instructions conflict and precedence does not resolve them, ask
  before proceeding.

## Understand

Establish the relevant constraints and evidence before changing a repository.

- Read the repository's top-level guidance and documentation for the affected
  area.
- Research externally when fresh, precise, or outside evidence would materially
  improve the result. Present meaningful alternatives with their trade-offs.
- Choose research sources in this order: the platform's built-in search by
  default; a regional or specialized provider when it covers the needed sources
  better; then a metered option only when the earlier results are inadequate.
- Ask for missing information only when it would materially change the outcome;
  otherwise state a reasonable assumption and continue.

## Decide and plan

Choose a proportionate approach before modifying files or external state.

- Assess scope, ambiguity, risk, and reversibility.
- For substantial work, maintain a compact task list or table.
- Pause for discussion when a consequential choice remains unresolved or a
  proposed change would contradict documented behavior.
- Evaluate user-proposed approaches objectively; explain material trade-offs
  and suggest improvements when warranted.
- Keep architecture and naming aligned: a name describes the role of the thing
  it identifies in its context.

### Large work and checkpoints

Keep substantial work reviewable by choosing stage boundaries deliberately.

- Split work into coherent stages with a clear result and verification boundary.
- Estimate each stage's scope, risk, and reversibility.
- Ask the user whether they want a review at each checkpoint or want the
  stages shortened or lengthened before proceeding.

### Testing behavior changes

Choose a test strategy before changing observable behavior.

- Prefer a focused behavior or regression test when practical, following
  repository conventions.
- Do not change production structure solely for test access without explaining
  the trade-off and obtaining approval.

## Act

Create durable artifacts that describe the resulting system and follow the
repository's local conventions.

- In durable documents and code comments, describe the resulting system rather
  than the history of the change. For example, write “B owns request parsing,”
  not “request parsing moved from A to B.” Put transition notes in plans and
  commits.
- Treat `.tmp/` as gitignored by default. Store non-durable artifacts and
  temporary documents under `.tmp/agent/`; never put durable source or
  documentation there. A skill uses `.tmp/agent/<skill-name>/` and prefixes
  temporary-document names with `YYYY-MM-DD-`.
- Use the project's managed Python environment when present. For standalone
  Python execution, prefer `uv`, then `python3` when `uv` is unavailable.

### Subagent coordination

Coordinate editing subagents through explicit ownership and isolation.

- Assign each editing subagent a task boundary, isolation method, and commit
  authority.
- For a multi-commit or concurrent subtask, use a dedicated worktree and
  branch. Reuse the repository's configured worktree root; otherwise prefer an
  existing `.worktrees/` or `worktrees/` directory, then `.worktrees/`.
- Before creating a project-local worktree, confirm that its root is ignored
  and that the target branch and path are unused. If this needs a tracked
  `.gitignore` change, ask the user rather than modifying it implicitly.
- In a new worktree, follow repository setup guidance and establish a relevant
  clean baseline before making changes when practical.
- Estimate the work for each task and divide it as evenly as dependencies and
  ownership boundaries allow.
- Run subagents concurrently only when their worktrees, files, and dependencies
  are isolated; otherwise sequence them.
- When validation is needed, subagents work independently to validate each
  other's work.

## Verify

Confirm the change with proportionate checks: use repository validation first,
Report important checks that failed not run.

## Communicate

Make unfamiliar material understandable before presenting its details.

- Establish concepts and their relationships before implementation details,
  code, or commands.
- Clarify the interface or behavior changes before elborating on the design.
- Explain unfamiliar terms on first use. Expand unfamiliar acronyms; discuss a
  term's origin only when it materially aids understanding.
- In terminal or TUI chat, write simple mathematics with Unicode, such as
  `x² ≤ ∑ᵢ yᵢ`, rather than LaTeX. Use LaTeX only in artifacts whose target
  renderer supports it.
