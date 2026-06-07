# Implementation Reviewer

Review code **within a single function or method body**. Inspect
line-by-line correctness, error handling, boundary conditions,
algorithmic choices, and language-specific pitfalls. Do not inspect
module organization or architectural soundness — those belong to
earlier review phases.

---

## What This Level Looks At

- Error handling: swallowed exceptions, missing error handling, error
  leakage
- Boundary conditions: null/None, empty collections, off-by-one,
  division by zero, integer overflow
- Algorithmic correctness: does this function do what it claims?
- Language-specific pitfalls: UB in C++, mutable default arguments in
  Python, etc.
- Comment quality: durable vs procedural, stale comments
- Anti-patterns: stringly-typed code, nested conditionals,
  copy-paste variants, TOCTOU

## What This Level Ignores

- Whether the function belongs in this module (→ structural review)
- Whether the module is the right module (→ architecture review)
- Whether the function signature is well-designed (→ structural review)
- Code organization across functions (→ structural review)

---

## Process

### 1. Understand the Context

Read `scope.md`, `architecture-findings.md`, and
`structural-findings.md` from the review directory.

**Read the Component Map** from structural findings (the Scope Model
section). Use it to determine:
- Which classes/function groups exist in each module and what each owns
- Which components had findings (need line-by-line inspection) vs.
  clean (skip)
- Which components are in scopes marked as needing structural rework —
  skip these, their implementation review would be premature

### 2. Theme Detection

Scan the code for file extensions and keyword patterns to determine
which language and scenario references to load.

**Language detection** (by file extension):

| Extension | Reference to load |
|-----------|-----------------|
| `.c`, `.h` | `references/implementation/lang/c.md` |
| `.cpp`, `.hpp`, `.cc`, `.cxx`, `.hxx` | `references/implementation/lang/cpp.md` |
| `.py`, `.pyi` | `references/implementation/lang/python.md` |

If multiple languages appear, load all matching guides.

**Scenario detection** (by keyword patterns):

| Signal | Scenario section to load |
|--------|------------------------|
| `pthread`, `std::mutex`, `std::thread`, `async`, `.await`, `threading`, `lock`, `mutex`, `std::atomic`, `volatile` | `references/scenarios/concurrency.md` — "Implementation" section |
| `*_test.*`, `test_*.py`, `*_spec.*`, `tests/`, `pytest`, `unittest`, `googletest`, `catch2` | `references/scenarios/testing.md` — "Implementation" section |

`references/scenarios/performance.md` — "Implementation" section — is
**always loaded** because algorithmic complexity is a universal concern.

### 3. Load References

**Always load:**

- `references/implementation/error-handling.md`
- `references/implementation/boundary-conditions.md`
- `references/implementation/anti-patterns.md`
- `references/implementation/comment-quality.md`
- `references/scenarios/performance.md` — "Implementation" section

**Conditionally load:**

- Detected scenario files (concurrency, testing) — "Implementation"
  sections only
- Detected language files (c, cpp, python)

Do NOT load references for scenarios or languages not detected in the
code. This avoids context pollution.

### 4. Inspect Per Theme

Walk through each loaded reference checklist against the code.

For each reference file:
- Apply checklist items to the code
- Record findings with **file:line** references
- Note what's checked and what's not covered

For language-specific guides:
- Apply the pitfall checklist to files of that language
- Focus on the top pitfalls listed in the guide

### 5. Checklist Coverage

Write a checklist coverage summary (see
`references/template/findings-document.md`).
Explicitly note which reference sections applied and which were N/A.
Do not silently skip sections — mark them N/A with a brief reason.

### 6. Write Findings

Write findings to `implementation-findings.md` in the review
directory. Use the findings document format from
`references/template/findings-document.md`.

Implementation findings typically have `local` rework impact — the
fix is within a single function and doesn't change interfaces.
If a finding would require changing a function signature or data
structure, escalate the rework impact to `structural` and note that
structural review should be re-run for the affected scope.

---

## Finding Examples at This Level

**Bug / Critical / local**:
Null pointer dereference in production path — `user->profile->name`
crashes when `profile` is nullptr. Add null guard before access.

**Bug / High / local**:
Missing error handling on network call — `requests.get(url)` can
raise `ConnectionError` with no try/except. Caller receives
unhandled exception.

**Bug / Medium / local**:
Magic string `"active"` used in comparison — use the `Status.ACTIVE`
enum constant that already exists in the codebase.

**Design / Low / local**:
Variable name `tmp` doesn't convey purpose — rename to
`pending_order_count`.
