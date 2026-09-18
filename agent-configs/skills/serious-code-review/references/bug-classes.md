# Bug-Class Index

Concrete inspection prompts for applied review lenses. The [review
record](review-record.md) says what to assess; this index helps the reviewer
actively check defect patterns it might otherwise overlook.

Read only the portions matching the applied lenses and target language. Each
entry is a hypothesis, not a finding: report it only with a reachable path, a
violated contract or invariant, and concrete impact. Do not report a pattern
because it resembles a known smell or could fail after an imagined future
change.

## Implementation quality

Boundaries and values:

- Null or absent value dereferenced without a check (None, nullptr,
  undefined, an error return used as a value).
- Truthiness mistakes — `0`, `""`, and `false` are valid values but
  read as absent.
- Empty or single-element collections: first or last access without a
  size check.
- Division or modulo without a zero guard.
- Integer overflow in size arithmetic; float equality without an
  epsilon.
- Off-by-one in loop bounds, slicing, and pagination.
- Whitespace-only strings passing a presence check.
- Failure chains that hide the first real error — optional chaining,
  error codes tunneled through return values.

Error handling:

- Swallowed exceptions — empty or log-only catch, no recovery or
  propagation.
- Overly broad catch masking distinct failure modes.
- Fallible operations — allocation, I/O, network, parse — with no
  check and no defined fallback.
- Async errors that never reach the caller: missing await, missing
  `.catch`, fire-and-forget.
- Resources not released on early-return or exception paths.
- Internal details (stack traces, SQL, paths) leaked to end users.

## Design signals

These patterns warrant structural judgment, but are not defects by themselves.

- New code duplicating an existing project utility.
- Parameter sprawl — four or more positional parameters where an
  options object fits.
- Leaky abstraction — a return type exposing ORM, HTTP, or file-format
  internals.
- Stringly-typed values where an enum or constant belongs.
- Deeply nested conditionals where early returns or a lookup table fit.
- Copy-paste variants differing only in a constant.
- Redundant state — a stored field derivable from other fields.
- No-op updates — a handler writing even when nothing changed.

## Structure signals

These coupling and cohesion patterns are concerns only when they violate a
documented boundary, make a supported behavior unsafe, or create concrete
maintenance cost.

- Stamp coupling — a whole object passed where the receiver uses a
  subset.
- Control coupling — a flag selecting between unrelated paths in one
  function.
- Common coupling — unrelated functions sharing mutable module or
  class state.
- Content coupling — reaching into another unit's private internals.
- Coincidental, logical, or temporal cohesion — members grouped by
  nothing, by category, or by call timing.
- Business logic importing infrastructure directly, untestable without
  a database, file system, or network.

## Architecture signals

These patterns are concerns only when they conflict with documented system
constraints or leave a current cross-module contract unsafe or ambiguous.

- A module acting as a shared cache or global registry that other
  modules mutate without coordination.
- Business modules depending on infrastructure instead of an
  abstraction they own.
- Cross-module protocols whose error and ordering rules exist only by
  convention, not in code.

## Concurrency

- Shared mutable state without a lock or atomic; non-atomic
  read-modify-write such as a bare counter increment.
- Lazy initialization without synchronization.
- Check-then-act on external state (TOCTOU); prefer try-act-handle.
- Locks held across I/O; inconsistent multi-lock acquisition order.
- Thread-unsafe collections used in shared contexts.
- Lost updates — read-modify-write without a version check or
  transaction.
- Retried operations that are not idempotent.
- Unbounded queues with no back-pressure — a latent OOM.
- Multi-step operations with no compensation for partial failure.

## Performance

- Accidental quadratic behavior — nested scans or per-item lookups
  inside a loop over the same data.
- Loop-invariant work inside the loop; repeated parse or fetch per
  iteration.
- Independent async operations awaited sequentially.
- Unbounded caches or collections with no eviction.
- Large objects retained by closures or long-lived references after
  their last use.
- Whole-collection loads where a filtered query or early exit fits.

## Testing

- Tests asserting mock interactions instead of observable behavior.
- Missing boundary and failure-path tests — empty, zero, error,
  retry.
- Flaky tests — wall-clock, ordering, unseeded randomness, or shared
  mutable state.
- Test setup more complex than the code under test.
- No integration coverage at external contracts.

## Language prompts

Language-specific entries still require code- and contract-level evidence.

- C — buffer bounds; use-after-free and double-free; unchecked allocation;
  overflow-safe size math (`size_t`); leaked handles; `volatile` is not atomic;
  only async-signal-safe calls in signal handlers.
- C++ — resource ownership and RAII; rule of 0/3/5; exception safety
  (commit or roll back); dangling references and iterators; unnecessary copies;
  `std::move` on a return value defeating copy elision.
- Python — mutable default arguments; bare `except`; shared mutable
  class attributes; `is` for value comparison; mutating a list during
  iteration; string `+=` in loops; resources not opened with `with`.
