---
name: prompt-retrospective
description: "Session retrospective over the information conveyed in a session, reviewed across two carriers: (1) the agent's standing instructions — skills and standing-instruction files (e.g. AGENTS.md, CLAUDE.md), global/repo/local — and (2) the user's prompts, reviewed for information quality (not language polish). Use when the user asks to review, debrief, or run a retrospective on how skills/instructions/prompts performed, how to improve the agent's prompts, or how to improve the information quality of their own requests in the session. Maps instruction-layer friction to the surface that should change (propose-only, to .tmp/agent/) and surfaces user-prompt information gaps as suggestions. Current session only; never edits durable files. Language polish of user writing belongs to polish-user-writing; capturing knowledge belongs to capture-knowledge."
---

# Prompt Retrospective

Review the **information conveyed** in the current session, then propose changes and
surface observations. "Prompt" spans two carriers this skill reviews on different axes:

- **The agent's standing instructions** — skills and standing-instruction files (e.g.
  AGENTS.md, CLAUDE.md). Reviewed for activation, content, and integrity defects;
  changes are proposed as edits.
- **The user's prompts** — reviewed for *information* quality (completeness, clarity,
  consistency), not language polish. Surfaced as suggestions, not edits.

## Target surfaces (where a proposed fix can land)

A proposal targets one of the agent's **standing-instruction surfaces**. Identify them
by role, then resolve the concrete file path from what the session actually loaded —
never assume a fixed location (skill-dir layouts and config paths differ across agents
and deployments).

| Surface (role) | What it is | How to find the path |
| --- | --- | --- |
| Skill | a skill's SKILL.md + bundled references/scripts | from the triggered skill's own location in the session |
| Global instructions | the always-loaded instruction file (AGENTS.md, CLAUDE.md, …) | from the session's loaded-instructions context |
| Repo instructions | repo-level instruction file(s) at the project root (+ a personal-extended variant) | from the project root / loaded-instructions context |
| Referenced file | any file the above link to | follow the link; verify it exists |

User prompts are **not** a target surface (past prompts can't be edited) — they yield
observations, not file edits. Findings whose fix lives **outside** standing instructions
(hooks, CI, memory entries, tooling) are out of scope — note them briefly for the user;
do not edit them.

## The Process

### Step 1: Collect

Scan the visible current session. If earlier messages are unavailable due to history
compaction, say so briefly and work with what is visible.

Identify, for the session:

- Which skills triggered (the skill-load context).
- Which standing-instruction files were in force (global, repo, personal).
- The user's substantive prompts (skip one-word replies, confirmations, and pasted
  code/logs).
- Where the agent struggled, reworked, over-/under-triggered, or lacked guidance.

If the session was trivial with no meaningful friction, say so and stop — do not invent
findings.

### Step 2: Analyze

Review both carriers in a single pass. For each instruction-layer finding: assign a
**category and signal**, **read the candidate target file** to resolve the exact
section, and form a concrete **before -> after** edit. For each user-prompt finding:
assign a **signal** and form an information-level observation (no edit).

**Instruction layer:**

| Category | Signal | Meaning | Typical surface |
| --- | --- | --- | --- |
| **Activation** | Under-trigger | a skill should have fired but didn't | skill description |
| **Activation** | Over-trigger / wrong skill | a skill fired when it shouldn't, or the wrong one did | skill descriptions (boundary) |
| **Content** | Incorrect | an instruction was followed but caused rework or a poor result | skill body / instruction file |
| **Content** | Missing | the agent had to infer or ask repeatedly; no guidance existed | skill body / instruction file |
| **Content** | Unclear / contradictory | instructions were ambiguous or conflicted | skill body / instruction file |
| **Content** | Bloat / low-salience | too much context loaded, or an instruction was buried | skill body (trim) |
| **Integrity** | Stale/broken reference | an instruction links to a missing or outdated file | instruction file / referenced file |

**User prompts (information quality, not language):**

| Signal | Meaning |
| --- | --- |
| Missing context | necessary info/context omitted; the agent guessed or had to ask |
| Ambiguous intent | the request could be read in more than one way |
| Conflicting | the request contained contradictory requirements |
| Noisy | irrelevant detail obscured the core request |

Always confirm an instruction target surface by reading it — never guess paths or
section names.

**Coverage gaps** (a recurring need no existing skill or instruction covers) sit outside
the axes above — a missing surface, not a defect in an existing one. Surface each as a
suggestion and let the user decide (e.g., create a skill, add an instruction, or ignore).
Never auto-create or auto-invoke another skill.

### Step 3: Propose

Write `proposals.md` to `.tmp/agent/retrospective/YYYY-MM-DDTHHMM/`, ranked by impact
(high -> low), in two sections.

**Instruction-layer proposals** (edits), each:

```markdown
### [impact: high] Activation · Under-trigger — <surface>:<section>
**Evidence (from session):** "<quote or paraphrase>"
**Problem:** <one sentence>
**Proposed change:**
- before: "<current instruction text>"
- after:  "<rewritten instruction text>"
**Rationale:** <one sentence>
```

**User-prompt observations** (information quality; no edits), each:

```markdown
### [impact: high] Prompt · Missing context — <turn or topic>
**Prompt (paraphrased):** "<…>"
**Information gap:** <what was missing/ambiguous/conflicting>
**Suggestion:** <how to convey it better next time>
**Compensable via:** <link to an instruction proposal if one would help, else "—">
```

### Step 4: Present

Show a ranked summary (one line per item). Offer next steps — apply some / refine /
discard — but **edit nothing**. The user applies any changes themselves.

## Guidelines

- **Propose only.** Never edit durable files. Output is a report under `.tmp/agent/`.
- **Evidence-driven.** Every proposal and observation cites what actually happened in
  the session. No generic advice.
- **Read before proposing.** Confirm the exact instruction file and section exist before
  writing a before -> after.
- **Language vs information.** User-prompt findings are about *information conveyed*;
  grammar/phrasing/style belong to `polish-user-writing`. The two skills can review the
  same messages on different axes without conflict.
- **Self-reference is allowed.** This skill may propose edits to its own SKILL.md —
  flag it explicitly when it does.
- **Suggest, don't act.** This skill only proposes. Adjacent concerns — a new-skill
  need, a memory worth keeping (`capture-knowledge`), polishing the user's writing
  (`polish-user-writing`) — are surfaced as suggestions for the user to decide, never
  auto-invoked.
