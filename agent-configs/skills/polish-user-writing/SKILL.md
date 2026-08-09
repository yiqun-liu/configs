---
name: polish-user-writing
description: "Review and polish the user's writing from a session: use generative and comparative approach to surface grammar, phrasing, structure, and clarity issues, plus a diversification check for repetitive expression. Then run an active-practice phase (Vocabulary, Grammar, Style tracks) with a 3-review practice bank. Triggered explicitly by the user, usually after a technical session. Works for any language."
---

# Polish User Writing

## Overview

Review the user's visible messages (prompts) from the current session. The agent rewrites every non-trivial user message (preserve paragraph-level intent), then derives findings by inspecting the user inputs directly, using the original↔rewrite comparison as a **supplementary** check to catch issues the direct pass might miss — especially cross-clause structural problems.

After findings are presented, an always-on **active-practice** phase (Vocabulary · Grammar · Style) backed by a persistent 3-review practice bank turns the review into retention.

This skill works for any language — detect the language(s) used in the user's messages and provide feedback in the same language.

## The Process

### Step 1: Collect User Messages

Review the visible current session conversation. If earlier messages are unavailable because of history compaction or context limits, say so briefly and review only the user messages you can see.

Identify **every** message authored by the user, not the agent. Skip only fragments with no substantive meaning or sentence structure (e.g., "OK", "yes", "Q1. b", single-word commands). User messages written after the skill trigger point also need inspecting and polish. Point out any issues.

Skip pasted or quoted material that is not the user's own prose, unless the user explicitly asks to review it. This includes code, logs, command output, stack traces, copied documentation, transcripts, and prompt examples.

Note the primary language(s) used. If the user mixes languages (e.g., Chinese technical terms with English framing), treat each language portion according to its own norms.

### Step 2: Rewrite Messages

For each selected user message, write a **paragraph-level rewrite** — an end-to-end optimization of flow, structure, and clarity. This is NOT a sentence-by-sentence table; it's a holistic rewrite of each message.

Write the before/after comparison to the session file under `## Rewrites`, using block format (not a table — cleaner for paragraph-length text):

```
### Message N
**Original:** <original paragraph>
**Rewrite:** <rewritten paragraph>
```

Include correct paragraphs too — the rewrite confirms correctness, and differences between original and rewrite reveal issues the agent might otherwise miss.

After writing all rewrites, the agent **compares originals to rewrites** as one supplementary way to derive findings (Step 3). The comparison itself surfaces issues — the agent notices where its rewrite differs and why.

### Step 3: Identify Issues

For each user message, inspect directly for the following issue types. The rewrite comparison from Step 2 serves as a supplementary check to catch issues the direct pass might miss.

- **Grammar errors**: incorrect verb forms, tense issues, agreement problems
- **Unnatural phrasing**: awkward word order, overly literal translations from another language, idioms used incorrectly
- **Ambiguity**: sentences that could be interpreted in multiple ways
- **Wordiness**: phrases that could be expressed more concisely without losing meaning
- **Style & precision refinements**: word choices that are grammatically correct but could be more precise, idiomatic, or natural. This includes both one-off word swaps (e.g., "fits" → "aligns with" for abstract concepts) and generalizable patterns (e.g., "which" → "that" for restrictive clauses in AmE, adverb placement like "Probably I" → "I probably", register-appropriate vocabulary). Flag any noticeable improvement — the original is already correct, but a careful writer would appreciate the suggestion.
- **Collocation and preposition choice**: catch meaningful, non-idiomatic combinations even when they are understandable, especially with abstract nouns. For example, use “the intuition behind X” when asking for the rationale or underlying idea of X; “the intuition of X” can be valid when referring to someone’s intuition about or perception of X. Treat this as a phrasing/style refinement, not an absolute replacement rule.
- **Sentence Structure** (cross-clause issues): broken clause connections (dangling connectors like "just one refers"), missing verbs in parallel predicates joined by conjunctions ("has X and not Y" → "has X and is not Y"), aspect/tense inconsistency across clauses ("while we are calling" for habitual → "while we call"), clunky nominalizations spanning clause boundaries ("convention of X being Y" → "uses X like Y"), run-on constructions.
- **Diversification**: scan for repeated transitions, connectors, sentence openers, sentence structures, adjectives, and phrases within a single message. Offer alternatives with similar meaning. This is about variety, not correctness — place in its own section, visually distinct from errors.

Do NOT flag:
- Style preferences so minor that they add noise without meaningful value (the line between "useful refinement" and "noise" is judgment-based; when in doubt, include it under Style & Precision rather than omit it)
- Minor typos that don't affect meaning (the agent already understood them)
- Technical shorthand or abbreviations common in the domain (e.g., "TDD", "PR", "FFN", "Q/K/V", "dim", "params", "refactor"). Preserve such shorthand in rewrites and suggestions unless it makes the meaning genuinely ambiguous; do not expand it merely for formality.
- Non-ASCII notation introduced by the agent in a suggestion. Keep rewrites, findings, and practice prompts ASCII-only by default; use forms such as "sqrt(d_k)", "x", "->", and straight quotes instead of Unicode mathematical symbols or typographic punctuation. Preserve non-ASCII text from the user's original only when it is necessary to discuss that exact text.
- Dialectal or regional variations that are grammatically valid (e.g., British vs American English)
- **Sentence-start capitalization and casual proper-noun capitalization** — the user knows the rule and skips it intentionally in casual input. (Technical term/acronym capitalization like SHA-1 vs sha1 is still flagged — that's correct terminology, not casual laziness.)

### Step 4: Present Findings

Group findings by issue type when there are multiple issues. Use these group names when they fit:

- **Grammar**
- **Phrasing**
- **Ambiguity**
- **Conciseness**
- **Style & Precision**
- **Sentence Structure**
- **Diversification**

Within each group, prefer a compact markdown table:

| Original | Rewrite | Changed |
|---|---|---|
| I want it to be something be triggered on demand | I want it to be something **that is** triggered on demand | "be" → "that is" |

Keep rewrites concise. Highlight changed words or phrases in the rewrite with bold text. Do not over-explain or add pedantic grammar notes.

**Separating errors from refinements:** Style & Precision findings must be visually and tonally distinct from Grammar/Phrasing/Ambiguity/Conciseness/Sentence Structure findings. Errors say "this should be fixed"; refinements say "this could be improved." Place Style & Precision in its own section after the error groups, or add a note like "(enhancement, not an error)" in the Changed column.

**Diversification** gets its own top-level section, visually distinct from both errors and refinements — it's about expression variety, not correctness or precision.

When the user asks to elaborate on a refinement, provide a concise explanation of the distinction (e.g., restrictive vs non-restrictive relative clauses, connotative differences between near-synonyms). Keep explanations to 2-3 sentences unless the user asks for more detail.

If the original message is long, do not force it into a table. Use a short quoted excerpt in the table, or use the block format below for readability.

Format:

```
**Original:** "I want it to be something be triggered on demand"
**Rewrite:** "I want it to be something **that is** triggered on demand"
**Changed:** "be" → "that is" (passive verb construction needed)
```

### Step 5: Summarize Patterns

If the same type of issue appears multiple times, summarize the pattern once rather than repeating it for every instance.

Example: "In these messages, 'be' appears where 'that is' or 'which is' would be more natural in English. This often happens when translating from languages that use a different relative clause structure."

When there are no meaningful issues, say that the visible messages were already clear enough and do not invent suggestions.

### Step 6: Active Practice (always-on)

After presenting findings, run an **active-practice** phase that turns review into retention.

**Quiz rules:**

- **Never reveal the answer.**
  - Exercise prompt must describe the meaning or grammar point, not the target itself. For non-choice exercise, do not include the answer itself in the prompt.
  - Do not print detailed descriptive information like `discuss-no-preposition` or `bug-in-collocation` which gives away the answer.
  - Show only the exercise prompt (cloze blank / sentence to rephrase / sentence to simplify) and a neutral label like "Vocabulary 1" or "Grammar — article". 

- **Format escalates by review stage:** #1 → single-choice (recognition), #2 → scaffolded (cloze / rephrase / simplify), #3 → open production (full recall / open rephrase). Single-choice distractors come from the item's meaning/synonym field and other bank items. Deviate only when an item doesn't suit a tier.

**Three tracks** (the three domains of writing skill). Render all three headers in every session file, even when empty, so gaps are visible at a glance:

- **Vocabulary** — fixed/semi-fixed collocations, idioms, or set phrases the user got wrong or failed to produce (phrase-level naturalness).
  - **Cloze prompts must include a meaning hint or synonyms** (e.g. "______ variation (verb: to allow for, make room for)" → "accommodate") so the blank is not ambiguous. The hint should never include the word or phrase itself.
  - Grade by exact/collocation match.
  - *Exclude*: known domain jargon.
- **Grammar** — sentences with a **clean, generalizable grammatical pattern** (articles, subject–verb agreement, clause structure, sentence completeness, article-noun agreement, faulty parallelism, simple present for habits).
  - Prompt: "rephrase to fix the error." Reuse the user's own original sentences as exemplars. Accept any valid rewrite that resolves the target pattern.
- **Style** — sentence-level naturalness
  - conciseness, clarity (incl. inverted meaning), and one-off awkward/garbled sentences with no clean pattern (including one-off structural garbles like broken clause connections or clunky nominalizations).
  - Prompt: "express this more simply / naturally."
  - Grade loosely — accept any rewrite that is clearly simpler/more natural and preserves meaning.

**Routing review findings → practice tracks.** The three tracks absorb all review dimensions via two axes — level (phrase vs sentence) and generality (generalizable vs one-off):

| Review dimension | Level | → Track |
|---|---|---|
| Grammar errors | — | Grammar |
| Phrasing (unnatural) | phrase / sentence | Vocabulary (phrase) / Style (sentence) |
| Ambiguity | sentence | Style |
| Conciseness | sentence | Style |
| Style & Precision | phrase / sentence | Vocabulary (collocation) / excluded if bare word-swap / Style (sentence) |
| Sentence Structure | clause | Grammar (generalizable) / Style (one-off) |
| Diversification | phrase | Vocabulary (synonym-variety) |

**Level split for naturalness:** phrase-level (the right word combination) → Vocabulary; sentence-level (clean, concise flow) → Style. A source may yield items in more than one track — overlap is allowed (they train different skills). One-off non-collocation word swaps (e.g. "fits" → "aligns with") are surfaced as findings but not banked, since they won't recur.

**Persistent bank + 3-review mastery.** State persists across sessions in `.tmp/agent/polish-user-writing/`, one timestamped file per session named `YYYY-MM-DDTHHMM.md`. Each item has a stable **id** (Vocabulary = normalized chunk; Grammar = pattern name; Style = sentence slug) so it dedups across sessions. A simple mastery model replaces spaced repetition: each item needs **3 correct reviews** (across however many sessions) to be mastered; an incorrect answer does **not** advance the count (and does not reset it). Each session, surface non-mastered items, oldest-reviewed first. Mastered items stay on record but are no longer surfaced.

**Flow each session:**

1. Read all prior files in the bank dir; rebuild each item's latest state (most recent entry per id wins).
2. Surface **non-mastered** items first (oldest-reviewed first) as the review queue.
3. Collect this session's **new** candidates across all three tracks (every item that passes the routing rules), skipping ids already in the review queue.
4. Quiz the review queue first, then new candidates, following the per-track quiz rules and the quiz-rules block above.
5. Write the new timestamped file (combined: rewrites + diversification + 3-review practice bank); always render all three track headers, even when empty.

**Bank file format:**

````markdown
# Polish-User-Writing Session — 2026-06-21 14:30

## Reviewed
- (which user messages were reviewed)

## Rewrites
### Message 1
**Original:** <original paragraph>
**Rewrite:** <rewritten paragraph>

### Message 2
**Original:** <original paragraph>
**Rewrite:** <rewritten paragraph>

## Diversification
| Repeated element | Count | Alternatives offered |
|---|---|---|
| "In addition" (transition) | 2 | moreover, furthermore, additionally |

## Vocabulary
- id: verb-allow-for-variation
  target: "accommodate (this kind of) variation"
  from: "stand this kind of variations"
  meaning: "to allow for, make room for, adapt to"
  cloze: "______ variation (verb: to allow for, make room for)" -> answer: accommodate
  recall: "What verb means 'to allow for' and collocates with 'variation'?" -> answer: accommodate
  result: correct | incorrect
  correct_count: 0   last_reviewed: 2026-06-21   mastered: no

- id: synonym-transition-in-addition
  target: alternatives to "In addition" — moreover, furthermore, additionally
  from: Diversification finding ("In addition" used 2x)
  meaning: "transitions that add a further point"
  recall: "Give 3 alternatives to 'In addition'." -> answer: moreover, furthermore, additionally
  result: correct | incorrect
  correct_count: 0   last_reviewed: 2026-06-21   mastered: no

## Grammar
- id: article-before-count-noun
  exemplar: "The overview section is not well written"
  user_rephrase: "..."
  result: correct | incorrect
  correct_count: 1   last_reviewed: 2026-06-21   mastered: no

## Style
- id: parse-return-concise
  exemplar: "is being implemented, so that it may return multiple simple types"
  target: "is implemented to return multiple types"
  user_rewrite: "..."
  result: correct | incorrect
  correct_count: 3   last_reviewed: 2026-06-21   mastered: yes
````

## Guidelines

- **Lightweight**: This is quick feedback, not a language lesson. Keep it actionable.
- **Selective with errors, generous with refinements**: For Grammar, Phrasing, Ambiguity, Conciseness, and Sentence Structure, only flag issues that meaningfully affect clarity or naturalness. For Style & Precision, flag any noticeable improvement in precision or idiomaticity — but always frame these as optional, and keep them separate from error corrections.
- **Respectful**: Frame feedback as suggestions, never as corrections. The user's message was already understood — this is about polish, not fixing misunderstandings.
- **Language-aware**: Adapt review criteria to the language being checked. What counts as "unnatural" varies by language.
- **Session-scoped review, cross-session practice**: Only REVIEW messages from the current session; do not reference past sessions when finding issues. The practice bank, however, persists across sessions (Step 6) — surface non-mastered items from prior sessions there.
- **Generation-supplemented**: The rewrite-all step (Step 2) is a supplementary evaluation mechanism. Findings come primarily from direct analysis (Step 3's checklist), with the rewrite comparison surfacing additional issues the direct pass might miss — especially cross-clause structural problems. The user is encouraged to review the rewrites if they have time.
