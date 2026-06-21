---
name: check-user-prompts
description: "Review and polish the user's writing from a session: grammar, phrasing, and clarity, then run an active-practice phase (Vocabulary, Grammar, Style) with spaced repetition. Triggered explicitly by the user, usually after a technical session. Works for any language."
---

# Check User Prompts

## Overview

Review the user's visible messages (prompts) from the current session for grammar, phrasing, and clarity issues. Provide concise, natural rewrites with highlighted changes. This skill works for any language — detect the language(s) used in the user's messages and provide feedback in the same language.

After findings are presented, an always-on **active-practice** phase (Vocabulary · Grammar · Style) backed by a persistent spaced-repetition bank turns the review into retention.

## The Process

### Step 1: Collect User Messages

Review the visible current session conversation. If earlier messages are unavailable because of history compaction or context limits, say so briefly and review only the user messages you can see.

Identify all messages written by the user (not by the agent). Focus on substantive messages — skip one-word confirmations, simple yes/no responses, and short tool invocations.

Skip pasted or quoted material that is not the user's own prose, unless the user explicitly asks to review it. This includes code, logs, command output, stack traces, copied documentation, transcripts, and prompt examples.

Note the primary language(s) used. If the user mixes languages (e.g., Chinese technical terms with English framing), treat each language portion according to its own norms.

### Step 2: Identify Issues

For each substantive user message, check for:

- **Grammar errors**: incorrect verb forms, tense issues, agreement problems
- **Unnatural phrasing**: awkward word order, overly literal translations from another language, idioms used incorrectly
- **Ambiguity**: sentences that could be interpreted in multiple ways
- **Wordiness**: phrases that could be expressed more concisely without losing meaning
- **Style & precision refinements**: word choices that are grammatically correct but could be more precise, idiomatic, or natural. This includes both one-off word swaps (e.g., "fits" → "aligns with" for abstract concepts) and generalizable patterns (e.g., "which" → "that" for restrictive clauses in AmE, adverb placement like "Probably I" → "I probably", register-appropriate vocabulary). Flag any noticeable improvement — the original is already correct, but a careful writer would appreciate the suggestion.

Do NOT flag:
- Style preferences so minor that they add noise without meaningful value (the line between "useful refinement" and "noise" is judgment-based; when in doubt, include it under Style & Precision rather than omitting)
- Minor typos that don't affect meaning (the agent already understood them)
- Technical shorthand or abbreviations common in the domain (e.g., "TDD", "PR", "refactor")
- Dialectal or regional variations that are grammatically valid (e.g., British vs American English)

### Step 3: Present Findings

Group findings by issue type when there are multiple issues. Use these group names when they fit:

- **Grammar**
- **Phrasing**
- **Ambiguity**
- **Conciseness**
- **Style & Precision**

Within each group, prefer a compact markdown table:

| Original | Rewrite | Changed |
|---|---|---|
| I want it to be something be triggered on demand | I want it to be something **that is** triggered on demand | "be" → "that is" |

Keep rewrites concise. Highlight changed words or phrases in the rewrite with bold text. Do not over-explain or add pedantic grammar notes.

**Separating errors from refinements:** Style & Precision findings must be visually and tonally distinct from Grammar/Phrasing/Ambiguity/Conciseness findings. Errors say "this should be fixed"; refinements say "this could be improved." Place Style & Precision in its own section after the error groups, or add a note like "(enhancement, not an error)" in the Changed column.

When the user asks to elaborate on a refinement, provide a concise explanation of the distinction (e.g., restrictive vs non-restrictive relative clauses, connotative differences between near-synonyms). Keep explanations to 2-3 sentences unless the user asks for more detail.

If the original message is long, do not force it into a table. Use a short quoted excerpt in the table, or use the block format below for readability.

Format:

```
**Original:** "I want it to be something be triggered on demand"
**Rewrite:** "I want it to be something **that is** triggered on demand"
**Changed:** "be" → "that is" (passive verb construction needed)
```

### Step 4: Summarize Patterns

If the same type of issue appears multiple times, summarize the pattern once rather than repeating it for every instance.

Example: "In these messages, 'be' appears where 'that is' or 'which is' would be more natural in English. This often happens when translating from languages that use a different relative clause structure."

When there are no meaningful issues, say that the visible messages were already clear enough and do not invent suggestions.

### Step 5: Active Practice (always-on)

After presenting findings, run an **active-practice** phase that turns review into retention. It runs every check (always-on) and covers **all** candidates that pass the rules below — no artificial cap.

**Three tracks** (the three domains of writing skill). Render all three headers in every session file, even when empty, so gaps are visible at a glance:

- **Vocabulary** — fixed/semi-fixed collocations, idioms, or set phrases the user got wrong or failed to produce (phrase-level naturalness). Drill both formats per item: a **cloze** (fill-in, e.g. "______ variation") and **full recall** (type the whole chunk). Grade by exact/collocation match. *Exclude*: single-word swaps not in a phrase, known domain jargon, typos.
- **Grammar** — sentences with a **clean, generalizable grammatical pattern** (articles, subject–verb agreement, clause structure, sentence completeness, determiner–number). Prompt: "rephrase to fix the error." Accept any valid rewrite that resolves the target pattern. *Exclude*: typos, garbled one-offs, pure naturalness.
- **Style** — sentence-level naturalness: conciseness, clarity (incl. inverted meaning), and one-off awkward/garbled sentences with no clean pattern. Prompt: "express this more simply / naturally." Grade loosely — accept any rewrite that is clearly simpler/more natural and preserves meaning.

**Level split for naturalness:** phrase-level (the right word combination) → Vocabulary; sentence-level (clean, concise flow) → Style. A source may yield items in more than one track — overlap is allowed (they train different skills).

**Persistent bank + spaced repetition.** State persists across sessions in `.tmp/agent/check-user-prompts/`, one timestamped file per session named `YYYY-MM-DDTHHMM.md`. Each item has a stable **id** (Vocabulary = normalized chunk; Grammar = pattern name; Style = sentence slug) so it dedups across sessions. SRS is simple Leitner: intervals 1d → 2d → 4d → 7d → 14d → 30d (doubling, capped at 30d); a correct answer advances one step, an incorrect one resets to 1d; `due = last_reviewed + interval`.

**Flow each session:**

1. Read all prior files in the bank dir; rebuild each item's latest state (most recent entry per id wins).
2. Surface **due** items first and quiz them (review).
3. Collect this session's **new** candidates across all three tracks (every item that passes the rules), skipping ids already quizzed as due.
4. Quiz: Vocabulary (cloze then recall), Grammar (rephrase — reuse the user's own original sentences as exemplars), Style (simplify).
5. Write the new timestamped file; always render all three track headers, even when empty.

**Bank file format:**

````markdown
# Check-User-Prompts Session — 2026-06-21 14:30

## Reviewed
- (which user messages were reviewed)

## Vocabulary
- id: accommodate-variation
  target: "accommodate (this kind of) variation"
  from: "stand this kind of variations"
  cloze: "______ variation"        -> answer: accommodate
  recall:                          -> answer: accommodate
  result: correct | incorrect
  last_reviewed: 2026-06-21   interval: 1d   due: 2026-06-22

## Grammar
- id: article-before-count-noun
  exemplar: "The overview section is not well written"
  user_rephrase: "..."
  result: correct | incorrect
  last_reviewed: 2026-06-21   interval: 2d   due: 2026-06-23

## Style
- id: parse-return-concise
  exemplar: "is being implemented, so that it may return multiple simple types"
  target: "is implemented to return multiple types"
  user_rewrite: "..."
  result: correct | incorrect
  last_reviewed: 2026-06-21   interval: 1d   due: 2026-06-22
````

## Guidelines

- **Lightweight**: This is quick feedback, not a language lesson. Keep it actionable.
- **Selective with errors, generous with refinements**: For Grammar, Phrasing, Ambiguity, and Conciseness, only flag issues that meaningfully affect clarity or naturalness. For Style & Precision, flag any noticeable improvement in precision or idiomaticity — but always frame these as optional, and keep them separate from error corrections.
- **Respectful**: Frame feedback as suggestions, never as corrections. The user's message was already understood — this is about polish, not fixing misunderstandings.
- **Language-aware**: Adapt review criteria to the language being checked. What counts as "unnatural" varies by language.
- **Session-scoped review, cross-session practice**: Only REVIEW messages from the current session; do not reference past sessions when finding issues. The practice bank, however, persists across sessions (Step 5) — surface due items from prior sessions there.
