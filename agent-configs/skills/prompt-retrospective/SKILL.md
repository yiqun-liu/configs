---
name: prompt-retrospective
description: >-
  Use only when the user explicitly asks to review, debrief, or improve how
  instructions and prompts performed in the current session. Diagnose
  instruction-layer friction and prompt-information gaps from session evidence;
  propose changes but never edit durable files. Do not use for language polish
  or general-purpose knowledge capture.
---

# Prompt Retrospective

Diagnose information and instruction friction from the current session, then
propose evidence-backed improvements.

## Scope

Own a proposal-only retrospective of the visible current session; do not edit
durable files, review unrelated history, or capture general knowledge.

## Trigger

Use this skill only for an explicit retrospective of this session's prompts,
skills, or standing instructions.

- Do not use it for language or writing polish; use `polish-user-writing` when
  the user explicitly requests that outcome.
- Do not use it to capture durable knowledge, inspect unrelated history, or
  make the proposed edits.

## Inputs and outcome

Use visible session context and deliver a ranked list of evidence-backed
instruction proposals and user-prompt observations.

- Inputs include the substantive user prompts, skills triggered, and standing
  instructions loaded in the visible session.
- State when unavailable history, instructions, or target files limit the
  result.

## Procedure

Turn session evidence into proposals with an explicit remedy target.

### Observations and targets

An observation is a session-evidenced mismatch between what the user needed and
what the agent, its instructions, or the prompt supplied. It may be a wrong
action, a missing action, repeated rework, unnecessary work, unclear guidance,
or information the agent had to guess.

Classify each observation by the surface where its remedy belongs.

- **Standing instructions** — the observation concerns a skill or instruction
  that over- or under-triggered, prescribed the wrong action, omitted needed
  guidance, conflicted with another rule, or referenced a stale file. Read the
  actual target before proposing an edit.
- **User prompts** — the observation concerns a substantive request that was
  missing context, ambiguous, conflicting, or noisy. Describe how to improve a
  future request; do not propose an edit to the historical prompt.
- **Outside scope** — hooks, CI, tools, memory, and other systems. Mention a
  recurring observation briefly, but do not create or invoke another workflow.

### Evidence review

Turn observed session friction into a specific, verifiable proposal.

1. Scan visible session context: triggered skills, loaded instructions,
   substantive prompts, and places the agent reworked, guessed, over-triggered,
   or lacked guidance. If history is incomplete, say so.
2. Stop with a clean result if the session contains no meaningful friction; do
   not invent findings.
3. Classify instruction findings as activation, incorrect or missing content,
   ambiguity, bloat, or reference integrity. Classify prompt observations as
   missing context, ambiguous intent, conflicting requirements, or noise.
4. For an instruction finding, read the candidate file and identify its exact
   section. For a prompt observation, identify the request and the missing or
   conflicting information.

### Proposals

Use the relevant format below. Rank results by impact and present only claims
supported by the session.

**Instruction-layer proposal:**

```markdown
### [impact: high] Activation · Under-trigger — <surface>:<section>
Evidence: [session event, quoted or paraphrased]
Problem: [one sentence]
Proposed change:
- before: "<current instruction text>"
- after: "<rewritten instruction text>"
Rationale: [one sentence]
```

**User-prompt observation:**

```markdown
### [impact: high] Prompt · Missing context — <turn or topic>
Prompt: [paraphrase]
Information gap: [what was missing, ambiguous, conflicting, or noisy]
Suggestion: [how to convey it better next time]
Compensable via: [instruction proposal, or "—"]
```

## Completion

Present a ranked summary and wait for the user's direction.

- State any session material, instructions, or target files that could not be
  inspected.
- Propose only: do not edit durable files, create another skill, or invoke a
  follow-on workflow.
