---
name: check-user-prompts
description: "Review and polish the user's writing from a session: grammar, phrasing, and clarity. Triggered explicitly by the user, usually after a technical session. Works for any language."
---

# Check User Prompts

## Overview

Review the user's visible messages (prompts) from the current session for grammar, phrasing, and clarity issues. Provide concise, natural rewrites with highlighted changes. This skill works for any language — detect the language(s) used in the user's messages and provide feedback in the same language.

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

## Guidelines

- **Lightweight**: This is quick feedback, not a language lesson. Keep it actionable.
- **Selective with errors, generous with refinements**: For Grammar, Phrasing, Ambiguity, and Conciseness, only flag issues that meaningfully affect clarity or naturalness. For Style & Precision, flag any noticeable improvement in precision or idiomaticity — but always frame these as optional, and keep them separate from error corrections.
- **Respectful**: Frame feedback as suggestions, never as corrections. The user's message was already understood — this is about polish, not fixing misunderstandings.
- **Language-aware**: Adapt review criteria to the language being checked. What counts as "unnatural" varies by language.
- **Session-scoped**: Only review messages from the current session. Do not reference past sessions or make assumptions about the user's general writing patterns beyond what's visible here.
