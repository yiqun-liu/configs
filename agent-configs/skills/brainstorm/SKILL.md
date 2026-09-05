---
name: brainstorm
description: "Use only when the user explicitly asks to brainstorm, explore a design, or develop a specification before execution. Turn the request into a reviewed design or decision record; do not use for an already specified implementation request."
---

# Brainstorm

Turn an ambiguous idea into a reviewed design or decision record.

## Scope

Own pre-execution design exploration; leave planning and implementation to a
later, user-selected workflow.

## Trigger

Use this skill only for an explicit request to explore or shape a design before
execution.

- Apply it to an idea, feature, module, process, or other decision whose design
  is not yet settled.
- Do not apply it to an implementation request whose design and acceptance
  criteria are already specified.

## Inputs and outcome

Use the user's idea, relevant repository context, and desired control level to
agree on the target outcome before choosing the depth or order of design work.

- **Incremental outcome:** resolve decisions in the user's chosen order, such
  as usage → design → components.
- **End-to-end outcome:** produce an implementation-ready design that covers
  the decisions needed for the eventual system to work as a whole.

End with a validated interface, design document, decision memo, or other record
that matches the agreed outcome. Omit sections that do not affect that decision.

## Procedure

Move from the intended outcome to a validated decision in the following order.

### Orient

Ground the discussion in the current situation and confirm the outcome before
proposing a solution.

- Inspect relevant files, documentation, and recent changes.
- Confirm whether the user wants incremental control or an end-to-end design.
- Identify the purpose, boundaries, and success criteria. Ask before continuing
  when the outcome remains ambiguous.

### Map decision space

Identify the decisions needed to reach the agreed outcome before selecting a
solution.

- Start with the decision layers relevant to the outcome: user-facing usage,
  system design, components and interfaces, data or control flow, and
  acceptance or validation constraints. Include validation only when it affects
  the design; omit layers that do not affect the work.
- Order dependent decisions before the decisions they constrain; for example,
  settle usage before component boundaries when usage determines those
  boundaries.
- For each material decision, mark it as known, evidence-needed, user-owned,
  or a non-blocking assumption to make visible for review.
- Search comparable systems when they can reveal decision dimensions, patterns,
  or failure modes missing from the initial framing. Use them to expand the
  decision space, not to select or copy a solution prematurely.

### Work through decisions

Resolve each material decision in dependency order without overwhelming the
user.

- Start with the next decision whose dependencies are known or deliberately
  recorded as assumptions.
- Inspect the repository or research external evidence when facts can resolve
  the decision.
- When material alternatives remain, present two or three with their trade-offs,
  lead with the recommendation, and explain why it best meets the criteria.
- Ask one question per message; split a topic into several questions when
  needed. Ask the user only about user-owned choices or genuinely ambiguous
  outcomes.
- Prefer multiple-choice questions when they make the decision easier; use an
  open question when its answer must be discovered.
- State when relevant research found no useful precedent or could not be
  completed, and record the resulting assumption for review.

### Present and confirm

Present the resulting decisions in a form suited to the agreed outcome, then
return to clarification when a piece exposes an unresolved assumption.

- Make each material decision, its rationale, and any unresolved assumption
  easy to find.
- Keep obvious facts or trivial choices out of the deliverables.
- When the user chose incremental control, confirm each material decision
  before moving to the next. For an end-to-end design, confirm each material
  section before treating it as accepted.

## Completion

Finish when the agreed outcome is accepted by the user.

- Report the completed design or decision record.
- Do not start planning, implementation, or another specialized workflow until
  the user explicitly requests it.
