# Comment Quality — Universal Checklist

Review comments in persistent files (production code, templates, headers)
and commit messages (if applicable) for durability and correctness.
Also detect stale comments near modified code.

The LLM understands documentation concepts — this reference clarifies
the specific standard: durable vs procedural, and the stale-comment
detection protocol.

---

## Durable vs Procedural Comments

**Durable comments** describe *why* and *what* — they remain meaningful
regardless of when the change was made. They explain design intent,
invariants, contracts, and non-obvious constraints.

**Procedural comments** describe *when* and *how* a change happened —
they become stale the moment the change lands. They belong in commit
messages, not in persistent files.

### Procedural residue to flag

```python
# Bad: stale temporal reference
# Currently, we process orders in batch mode.
# → "currently" refers to pre-change state; stale after change lands

# Bad: change-history residue
# Moved order processing from OrderHandler to OrderService.
# → if the move is done, this comment is dead on arrival

# Bad: migration note in production code
# TODO: migrate to new API after v2 release
# → migration status belongs in commit messages or issue tracker,
#   not in code that persists indefinitely
```

### Durable comment examples

```python
# Good: explains invariant
# Order total must equal sum of item prices minus discounts.
# This invariant is enforced by recalculate() after any mutation.

# Good: explains non-obvious constraint
# Rate limiter uses a sliding window of 60s because the upstream
# API enforces per-minute quotas. Fixed-window would cause burst
# spikes at window boundaries.
```

```cpp
// Good: explains contract
// Returns nullptr if key not found. Caller must check before use.
// Does NOT throw — designed for lookup-optional patterns.

// Good: explains why, not how
// Uses exponential backoff because the downstream service has
// documented rate limits that penalize immediate retries.
```

---

## Commit Message Quality (If Applicable)

When reviewing a git range, check commit messages for:

### Good commit messages

- Conventional commit format: `<type>: <short description>`
- Types: feat, fix, refactor, docs, test, chore
- Body explains *why* the change was made, not *what* was changed
  (the diff shows what)
- No procedural residue that belongs in code comments

### Bad commit messages

- "wip" or "fix stuff" — no context
- "moved X from A to B" — procedural, belongs as code comment
  (durable version) or not at all
- Multiple unrelated changes in one commit — should be split
- Vague descriptions that don't help future readers understand intent

---

## Stale Comment Detection

Bottom-up search protocol for stale comments near modified code.

### How to detect

For each modified line in the diff:

1. Read surrounding context (±10 lines)
2. Look for comments that reference code that no longer exists or
   describe state that has changed
3. Check for TODO/FIXME/HACK markers — are they still relevant?
4. Check for docstrings/function headers that describe pre-change
   behavior

### Common stale patterns

```python
# Comment references deleted parameter
def process(data):  # 'data' was renamed, but comment says 'input'
    """Process the input parameter and return results."""
    # → "input" no longer matches the parameter name

# Comment describes old behavior
# This function sorts results by date.
# → function now sorts by priority (behavior changed, comment unchanged)

# TODO that's already resolved
# TODO: add error handling for network failures
# → error handling was added 3 commits ago, TODO still present
```

```cpp
// Stale: references removed field
// Computes total from items and discount
// → discount field was removed last week

// Stale: describes old algorithm
// Uses bubble sort for ordering
// → was replaced with quicksort, comment unchanged
```

### Search strategy

- Start from diff hunks (modified lines)
- Expand outward ±10 lines
- Stop expanding when surrounding context is clearly unrelated
- Focus on comments that directly reference modified code or its
  pre-change behavior