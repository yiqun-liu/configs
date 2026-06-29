---
name: prompt-retrospective
description: "Session retrospective over the agent's persistent-prompt layer — skills, AGENTS.md files (global, repo, .AGENTS.md), and files they reference. Use when the user asks to review, debrief, or run a retrospective on how the agent's skills/instructions/prompts performed in the current session, or how to improve them after a session (e.g. 'how did the skills work this session', 'retrospective on the prompts/instructions', 'debrief the agent'). Maps session friction to the instruction surface that should change and writes ranked, propose-only proposals to .tmp/agent/. Current session only; proposes, never edits durable files. Do not use for polishing the user's own writing (see polish-user-writing) or capturing domain knowledge (see capture-knowledge)."
---

# Prompt Retrospective

Review how the agent's **instruction layer** performed in the current session, then propose targeted edits to the persistent prompt surfaces that shape behavior.

"Prompt" here means the agent's **standing instructions** — skills and AGENTS.md files — not the user's inputs.

## Target surfaces (where a proposed fix can land)

| Surface | Path |
|---|---|
| Skill | `agent-configs/skills/<name>/SKILL.md` (+ bundled references/scripts) |
| Global AGENTS.md | `~/.config/opencode/AGENTS.md` (source: `agent-configs/AGENTS.md`) |
| Repo AGENTS.md | repo `AGENTS.md`, `.AGENTS.md` |
| Referenced file | any file an AGENTS.md links to |

Findings whose fix lives **outside** the prompt layer (hooks, CI, memory entries) are out of scope. A **new-skill gap** is the one exception — hand it off to `skill-creator`.

## The Process

### Step 1: Collect

Scan the visible current session. If earlier messages are unavailable due to history compaction, say so briefly and work with what is visible.

Identify, for the session:
- Which skills triggered (the `<skill_content>` blocks loaded).
- Which AGENTS.md instructions were in force (global, repo, personal).
- Where the agent struggled, reworked, over-/under-triggered, or lacked guidance.

If the session was trivial with no meaningful friction, say so and stop — do not invent findings.

### Step 2: Analyze

In a single pass over the friction, for each candidate finding: assign a **signal type**, **read the candidate target file** to resolve the exact section, and form a concrete **before -> after** proposal.

| Signal | Meaning | Typical surface |
|---|---|---|
| Wrong/weak instruction | An instruction was followed but caused rework or a poor result | skill / AGENTS.md |
| Under-trigger | A skill should have fired but didn't | skill description |
| Over-trigger / wrong skill | A skill fired when it shouldn't, or the wrong one did | skill descriptions (boundary) |
| Missing instruction | The agent had to infer or ask repeatedly; no guidance existed | skill / AGENTS.md (or new-skill gap) |
| Ambiguous / contradictory | Instructions were unclear or conflicted | skill / AGENTS.md |
| Bloat / ignored | Too much context loaded, or an instruction was disregarded | skill (trim) |
| Stale/broken reference | AGENTS.md references a missing or outdated file | AGENTS.md / referenced file |

Always confirm the target surface by reading it — never guess paths or section names.

### Step 3: Propose

Write `proposals.md` to `.tmp/agent/retrospective/YYYY-MM-DDTHHMM/`, grouped by target surface, ranked by impact (high -> low). Each proposal:

```
### [impact: high] <signal type> — <target file>:<section>
**Evidence (from session):** "<quote or paraphrase>"
**Problem:** <one sentence>
**Proposed change:**
- before: "<current instruction text>"
- after:  "<rewritten instruction text>"
**Rationale:** <one sentence>
```

### Step 4: Present

Show a ranked summary (one line per proposal). Offer next steps — apply some / refine / discard — but **edit nothing**. The user applies changes themselves, respecting the repo's deploy-safety rules.

## Guidelines

- **Propose only.** Never edit durable files. Output is a report under `.tmp/agent/`.
- **Evidence-driven.** Every proposal cites what actually happened in the session. No generic advice.
- **Read before proposing.** Confirm the exact file and section exist before writing a before -> after.
- **Self-reference is allowed.** This skill may propose edits to its own SKILL.md — flag it explicitly when it does.
- **Respect boundaries.** Domain knowledge worth remembering -> `capture-knowledge`; polishing the user's writing -> `polish-user-writing`; building a brand-new skill -> `skill-creator`.
