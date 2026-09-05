---
name: polish-user-writing
description: >-
  Use only when the user explicitly asks to review or polish their writing from
  the current session. Rewrite each substantial user message, compare rewrites
  with originals, report language findings, and run this-session Vocabulary,
  Grammar, and Style practice. Works for any language. Do not use for prompt
  information quality, general prose, or cross-session practice tracking.
---

# Polish User Writing

Improve the user's current-session writing and turn its useful corrections into
this-session learning practice.

## Scope

Review the user's own visible, substantive messages in their original language.

- Skip acknowledgements, fragments without sentence structure, and pasted or
  quoted material unless the user asks to review it.
- If earlier messages are unavailable, say so and review the visible subset.
- Preserve technical shorthand and valid regional variation. Do not correct
  intentional casual sentence-start or proper-noun capitalization.

## Trigger

Use this skill only when the user explicitly asks to review or polish their
current-session writing.

- Do not use it for prompt information quality, general prose, or a
  cross-session practice program.

## Inputs and outcome

Use the selected user messages to deliver rewrites, language findings, and
this-session practice.

- Produce a dated, addition-only learning note containing rewrites, findings,
  diversification, and this session's practice. It is not a cross-session
  practice bank or an input to a later run.

## Procedure

Collect messages, rewrite and review them, then turn useful findings into
this-session practice.

### Collect messages

Identify every user-authored message that has enough prose to assess.

1. Identify the language or languages used. Apply the relevant language norms
   to each portion of mixed-language messages.
2. Exclude code, logs, command output, copied documentation, transcripts, and
   prompt examples that are not the user's own writing.
3. Number the selected messages for the rewrite and learning note.

### Rewrite messages

Create a paragraph-level rewrite of every selected message before finding
issues. This is a holistic rewrite, not a sentence-by-sentence substitution.

Record each pair in this format:

```markdown
### Message N
Original: <original paragraph>
Rewrite: <rewritten paragraph>
```

Include messages that need no material change. The rewrite is both useful
feedback and a comparative signal for cross-clause or structural issues a
direct scan might miss.

### Review writing

Inspect each original directly, then use its rewrite as a supplementary check.

- **Grammar** — verb form, tense, agreement, articles, parallelism, and
  complete sentence construction.
- **Phrasing** — natural word order, idioms, collocations, and prepositions.
  Treat language-specific alternatives as refinements, not absolute rules.
- **Ambiguity and conciseness** — meanings that can be read more than one way,
  or wording that can be shortened without losing intent.
- **Style and precision** — an optional improvement to idiomaticity, register,
  or exactness that is not an error.
- **Sentence structure** — cross-clause connections, habitual versus ongoing
  aspect, nominalizations, and run-on constructions.
- **Diversification** — repeated transitions, openings, structures, adjectives,
  or phrases within one message. This is variety feedback, not a correction.

Do not create noise from minor typos that do not affect meaning, common domain
abbreviations, valid dialectal forms, or cosmetic preferences. Keep rewrites,
findings, and exercises ASCII-only by default; preserve non-ASCII user text
only when necessary to discuss that text.

### Present findings

Present material improvements compactly, with errors distinct from optional
refinements and diversification.

Use a table for short excerpts:

```markdown
| Original | Rewrite | Changed |
| --- | --- | --- |
| It needs be on demand | It needs **to be** on demand | "be" -> "to be" |
```

Use a block for a longer passage:

```markdown
Original: "I want it to be something be triggered on demand"
Rewrite: "I want it to be something **that is** triggered on demand"
Changed: "be" -> "that is" (a passive verb construction is needed)
```

- Group multiple findings as Grammar, Phrasing, Ambiguity, Conciseness, Style
  and Precision, Sentence Structure, or Diversification when those headings
  help scanning.
- Label Style and Precision as an enhancement, not an error. Give
  Diversification its own section.
- Explain a refinement in two or three sentences only when the user asks why.
- Summarize a recurring pattern once rather than repeating it for every
  message. A clean result is valid; do not invent suggestions.

### Practice this session

Use the review findings to run active practice after presenting them. Do not
reveal an answer before the user responds.

Create the following tracks whenever the session yields suitable candidates.

- **Vocabulary** — incorrect or missing collocations, idioms, set phrases, and
  diversification alternatives. Use a cloze prompt with a meaning hint or
  synonyms that do not reveal the answer. Grade exact phrase or collocation
  match; exclude known domain jargon.
- **Grammar** — clean, generalizable patterns such as articles, agreement,
  clauses, sentence completeness, parallelism, or habitual present tense. Ask
  the user to rephrase one of their own sentences; accept any valid correction.
- **Style** — one-off naturalness, ambiguity, conciseness, or structural flow.
  Ask for a simpler or more natural rewrite; accept a meaning-preserving answer
  that improves the sentence.

Route phrase-level naturalness to Vocabulary and sentence-level naturalness to
Style. Route generalizable sentence-structure issues to Grammar and one-off
ones to Style. A finding may supply more than one track when they practice
different skills.

For each suitable candidate, progress within this session from recognition to
guided production to an open rewrite when the user wants more practice. Show a
neutral label such as `Vocabulary 1` or `Grammar - article`, not an answer-
revealing diagnostic label. After an answer, give concise feedback and continue
only while the user wants to practice.

### Learning note

Create one dated, addition-only note at
`.tmp/agent/polish-user-writing/YYYY-MM-DDTHHMM.md` for this session.

```markdown
# Polish-User-Writing — <date and time>

## Reviewed messages
- <message numbers or short descriptions>

## Rewrites
### Message 1
Original: <original paragraph>
Rewrite: <rewritten paragraph>

## Findings
### Grammar
- <original -> rewrite, or none>

### Diversification
- <repeated element -> alternatives, or none>

## Practice
### Vocabulary
- Prompt: <exercise>
  Response: <user response, if any>
  Feedback: <concise feedback, if given>

### Grammar
- <exercise and result, or none>

### Style
- <exercise and result, or none>
```

Never overwrite or read prior learning notes as practice input. They are a
record the user may revisit, not a spaced-repetition system.

## Completion

Conclude after findings and the user-selected amount of practice are complete.

- Keep feedback respectful and actionable: corrections improve expression, not
  the user's ability to be understood.
- Do not review past-session messages or start a learning workflow beyond this
  session without an explicit request.
