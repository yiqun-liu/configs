# AGENTS

Global instructions for general purpose AI agents.

## Scope

- Global instructions apply to all sessions
- Repo-level instructions (`AGENTS.md` at repo root) convey project-specific conventions (usually tracked by git and maintained by all collaborators)
- Repo-level personal extented instructions (`.AGENTS.md` at repo root, ignored by `~/.config/git/ignore`) allow per-repo customization without leaking to collaborators

## Personal Preferences

### Communication Style
- concept-first: When introducing new solutions, explain the new terms, concepts and the ideas first
- When introducing new terms, explain the etymology, the name origin and what it means
  - e.g. LVM stands for Logical Volume Manager, GHES may first showed up as "GHES (Generic Hardware Error Structure)"

### Working Approach
- Evaluate modification scope first: Assess whether the change is small, medium, or significant
- For medium/large modifications:
  - Present design using visual representations (tables, text graphs, mermaid diagrams)
  - Create TODO list and discuss with user before proceeding
- When user proposes approaches: objectively evaluate pros/cons and proactively suggest optimizations
- Be strict with the architecture (of text or code), check if the names picked by users matched its meaning within the context

### Temporary Files
- Repositories may use `.tmp/` as a git-ignored, repo-local directory for temporary files
- Agent intermediate files like one-time execution plan or review findings belong under `.tmp/agent/`
- Do not place durable documentation or source changes under `.tmp/`

### Documentation Respect
- Always read and respect top-level `README.md` and other human-facing documentation
- When a development plan would break or contradict documented behavior, explicitly ask the user for confirmation before proceeding

### Research & Information
- Proactively use `webfetch` and web search to improve results and present research as comparisons with trade-offs
- If the agent senses it lacks sufficient information, proactively ask the user for clarification or missing details
