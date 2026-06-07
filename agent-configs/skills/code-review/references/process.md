# Shared Review Process

Severity system, rework impact, communication guidelines, and refactor
heuristics shared across all review phases. Templates for findings
documents and output formats are in `references/template/`.

---

## Severity Classification

| Level | Domain | Action |
|-------|--------|--------|
| Critical | Correctness/safety | Must fix |
| High | Functionality/design | Should fix |
| Medium | Maintainability | Track or fix |
| Low | Style/preference | Optional |

**Rules:**

- Not everything is Critical. Nitpicks should not block.
- Not everything is Low. Real defects should not be dismissed as style.
- If unsure, default to High and let the user decide.
- Severity is about **impact**, not about how easy the fix is.
- Critical and High affect the user's experience (broken vs degraded).
  Medium and Low affect the developer's experience (hard to maintain vs
  slightly messy).
- **Latent correctness bugs** — code that is safe today but would break
  under a plausible change (e.g., adding threading, signal handler
  interaction, reused allocation) — should be rated at least **Medium**,
  not Low. The non-obvious trigger conditions make them more dangerous
  than style issues.

---

## Rework Impact

Each finding carries a rework impact tag — **independent of severity**.
Severity says *how bad it is*. Rework impact says *how much it blocks
downstream work*.

| Rework impact | Meaning | Blocks next phase? |
|---------------|---------|-------------------|
| `local` | Fix doesn't change what next phase inspects (rename, add error check, extract constant) | No |
| `structural` | Fix changes function signatures, data structures, or class interfaces (split a class, redesign a data structure) | Blocks implementation review of affected scope |
| `architectural` | Fix changes module boundaries or inter-module interfaces (split a module, change inter-module protocol) | Blocks both lower phases for affected scope |

**Key principle**: a finding is blocking when its fix would invalidate
the next phase's findings. Examples:

- Medium severity + architectural rework → **blocking** ("this module
  should be split into two")
- High severity + local rework → **not blocking** ("missing null check
  in this function")
- Low severity + local rework → **not blocking** ("rename this variable")

---

## Findings Document Format

Each phase writes a findings document to
`.tmp/agent/reviews/{id}/{phase}-findings.md`.

Load `references/template/findings-document.md` for the findings
document structure, including Scope Model, Checklist Coverage,
Findings, Blocking Assessment, and Not Covered sections.

### Staleness Protocol

When the user fixes a blocking issue:

1. Driver annotates the finding as `[resolved]` in the findings document
2. If the fix has structural or architectural rework impact, driver
   **deletes** downstream findings documents (they are stale)
3. Driver updates `scope.md` with the fix details
4. Re-run from the affected phase

---

## Output Format

After all requested phases complete (or stop on blocking findings),
present the consolidated review. Load the appropriate template:

- Code review: `references/template/code-review-output.md`
- Design review (Design Doc preset):
  `references/template/design-review-output.md`

### Conditional Sections

Omit any phase section for phases not completed. Omit "Strengths" or
severity subsections when empty — do not leave placeholder headers.

### Clean Review Protocol

If no meaningful findings exist for a phase, state explicitly:

> No significant findings at the {phase} level. [What was checked].
> [Any areas not covered].

Never invent nits to fill a review. "No issues found" is a valid and
honest outcome.

---

## Communication Guidelines

- **Confidence-appropriate framing**: Critical and High findings are
  declarative ("This module should be split"). Medium and Low findings
  are observations ("This naming could be more descriptive") rather than
  mandates. Do not append interactive questions.
- **Strengths first**: Acknowledge what's well done before listing
  issues. Be specific with file:line references.
- **Be honest about uncertainty**: If you can't assess something without
  more context, say so rather than guessing.
- **Explain WHY**: every finding should explain why it matters, not just
  what's wrong.
- **Give clear verdict**: do not avoid giving an assessment.

---

## Refactor Heuristics

When recommending fixes:

1. Split by responsibility, not by size
2. Introduce abstraction only when the second use case appears
3. Keep refactors incremental — isolate behavior before moving
4. Preserve behavior first — add tests before restructuring
5. Name things by intent — if naming is hard, the abstraction may be
   wrong
6. Prefer composition over inheritance — inheritance creates tight
   coupling
7. Make illegal states unrepresentable — use types to enforce invariants

---

## Review Anti-Patterns to Avoid

| Anti-pattern | Fix |
|-------------|-----|
| Rubber stamping — approve without checking | Actually read the code before assessing |
| Bike shedding — debate trivial details | Focus on Critical/High, let style go |
| Scope creep — "while you're at it..." | Only flag what's in scope |
| Perfectionism — block for minor preferences | Low should never block |
| Inventing nits — fill silence with noise | "No issues" is valid |

---

## Next Steps Confirmation

After presenting findings, use the next steps from the output template
loaded above. Do NOT implement any changes until the user explicitly
confirms.
