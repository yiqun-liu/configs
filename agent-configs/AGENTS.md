# AGENTS

Global instructions for general purpose AI agents.

## Scope

- Global instructions apply to all sessions
- Repo-level instructions (`AGENTS.md` at repo root) convey project-specific conventions (usually tracked by git and maintained by all collaborators)
- Repo-level personal extented instructions (`.AGENTS.md` at repo root, ignored by `~/.config/git/ignore`) allow per-repo customization without leaking to collaborators

## Personal Preferences

### Communication Style
- concept-first: When explaining something new, introduce the concepts and ideas before diving into implementation details, code, or commands
- When introducing new terms, explain the etymology, the name origin and what it means
  - e.g. LVM stands for Logical Volume Manager, GHES may first show up as "GHES (Generic Hardware Error Structure)"

### Working Approach
- Evaluate modification scope first: Assess whether the change is small, medium, or significant
- For medium/large modifications:
  - Present design using visual representations (tables, text graphs, mermaid diagrams)
  - Create TODO list and discuss with user before proceeding
- When user proposes approaches: objectively evaluate pros/cons and proactively suggest optimizations
- Be strict with the architecture (of text or code), check if the names picked by users matched its meaning within the context
- When modifying persistent documents or writing code comments: Prefer durable to procedural.
  - Template documents, production code are considered persistent; plans and scripts are not.
  - Do not embed process residue that only makes sense during the current change session.
  - Examples to avoid:
    - `"current"` or `"currently"` that refers to a state before the change — stale the moment the change lands.
    - `"moved X from A to B"` left in A — if the move is done, the comment is dead on arrival.
  - These procedural messages belong in plans and commit messages, not in the files themselves.

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

### Web Search Preference Order

Follow this cascading order when searching the web. Escalate to the next option only if the current one returns no results, irrelevant results, or an error.

**Chinese-language search:**

1. `MiniMax MCP` → `MiniMax_web_search` — Minimax Coding Plan (included quota), first choice
2. `web-search-prime MCP` → `web_search_prime` — Zhipu Coding Plan (included quota, prefer over pay-as-you-go)
3. `zhipu-web-search MCP` → `webSearchStd` — 0.01 CNY/search, pay-as-you-go, basic coverage
4. `zhipu-web-search MCP` → `webSearchPro` or `webSearchQuark` — 0.03-0.05 CNY/search, pay-as-you-go, heavier fallback

**Non-Chinese search:**

1. Built-in web search from global providers (e.g., built-in search from the current provider like Gemini/OpenAI/native codex search) — first choice
2. `exa MCP` → `web_search_exa`, `web_fetch_exa` — high-quality English content
3. Search tools from Chinese providers (`MiniMax MCP`, `zhipu-web-search MCP`) — last resort; Chinese providers have smaller non-Chinese search coverage
