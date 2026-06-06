# Design Architecture Evaluation Reference

Work through each section in order. For each section, check every signal
against the proposed design. A design that *invites* violations is a
finding even if no code exists yet.

---

## SOLID Principles and Extensions

### SRP — Responsibility & Cohesion

Check: does each module have a single reason to change?

- [ ] Module described as doing multiple unrelated things
- [ ] Different stakeholders would request different changes to the same module
- [ ] Data model mixes domain concerns with infrastructure concerns
- [ ] High public interface count (**corroborating only** — cohesive modules
  may legitimately have many methods; not a finding on its own)
- [ ] Vague or generic module name (`Manager`, `Handler`, `Processor`,
  `Service`, `System`) — **weak signal**; investigate only when paired
  with other signals

#### Related: God Object

- [ ] Single module central to everything — removal would break features
  across unrelated domains

#### Related: Cohesion

Check the cohesion level of each module (Functional → Sequential →
Communicational → Temporal → Logical → Coincidental). Qualifications:

- **Communicational** (CRUD on one entity) is acceptable for data-oriented
  modules (repository pattern).
- **Logical** (`Utilities`, `Helpers`) is borderline — `UserValidator`
  for all user rules may be functionally cohesive; `Validators` spanning
  multiple entities is genuinely logical.

#### Related: LCOM4

- [ ] Can the module's operations be partitioned into independent groups
  that share no data? (LCOM4 is measured on code; at design time use as
  a conceptual lens)

| LCOM4 | Assessment |
|-------|------------|
| 1 | Ideal |
| 2-3 | Warning |
| > 3 | Concern |

---

### OCP — Extensibility & Evolution

Check: can new variants be added without touching existing code?

- [ ] Adding a new type or behavior requires modifying a central
  switch/if-chain
- [ ] No plugin, strategy, or hook points for variation in the design
- [ ] Configuration hardcoded where **variation is expected** (distinguish
  from true constants — business rules that genuinely don't change)

#### Related: Extension Points

- [ ] Check whether hooks/events or hardcoded behaviors are used, and
  whether the choice matches expected variation

**Trade-off:** Hooks have invisible side effects, ordering ambiguity, and
debugging difficulty. Over-hooking produces its own Big Ball of Mud. Use
hooks when behaviors will grow; hardcoded when the behavior set is small
and stable.

#### Related: Extensibility Assessment

- [ ] **Functional:** Can new features be added without modifying core logic?
- [ ] **Data:** Can the data model accommodate new fields without breaking
  existing consumers?

#### Related: Speculative Generality / Boat Anchor

Adding complexity for hypothetical future needs with no current requirement
driving it. **File as a single finding.**

- [ ] "We might need this later" or "For future extensibility" with no
  concrete use case
- [ ] Abstractions, layers, or patterns added without solving a current
  problem

#### Related: Patternitis

- [ ] Simple conditional replaced by strategy + factory + registry
- [ ] Interface with only one implementation (**exception:** testability
  interfaces where production + mock count as two implementations)
- [ ] Code significantly longer because of pattern application
- [ ] Understanding a single operation requires tracing through multiple
  abstraction layers

---

### LSP — Type Substitutability

Check: can any subtype be substituted without the caller knowing?

- [ ] Calling code contains subtype checks or casts
- [ ] Subtype described as "a special case" that behaves differently
  from the parent
- [ ] Interface contract vague enough that implementers must interpret it
- [ ] Subtype throws for parent-defined operations, or returns no-op results

Key nuance: prefer composition over inheritance as a preventive principle.
Inheritance creates tight coupling and makes LSP violations likely.

---

### ISP — Interface Design

Check: do all implementers use all methods of each interface?

- [ ] Some implementers need stub/empty implementations for certain methods
- [ ] Different clients use only distinct subsets of the same interface
- [ ] High method count (**corroborating only** — a well-scoped interface
  may have many methods, e.g., a repository with query variations)
- [ ] Broad interface name (`IManager`, `IService`)

#### Related: Stamp Coupling

- [ ] Interface passes a complex data structure where the receiver only
  uses part (e.g., full `User` object where only `user.name` is read)

Cross-reference: Stamp coupling also appears under §DIP. **File once, not
twice.**

#### Related: Options Object Pattern

- [ ] Functions with ≥4 parameters — prefer options object/struct

---

### DIP — Dependency Structure

Check: can implementations be swapped without changing business logic?

- [ ] Domain/business logic imports concrete infrastructure types
- [ ] Hardcoded configuration or connection strings in domain modules
- [ ] Test plan mentions difficulty testing business logic without
  infrastructure

#### Related: Clean Architecture Dependency Direction

- [ ] Domain layer references database types, HTTP clients, file system
  paths, or any infrastructure detail — **High finding**

The domain layer may define interfaces that infrastructure implements.

#### Related: Coupling Taxonomy

Classify each inter-module dependency. Qualifications:

- **Stamp** coupling also relates to ISP (see §ISP) — file once.
- **Control** coupling also relates to OCP — suggest strategy pattern.
- **Common** coupling with *immutable* global state is much less dangerous
  than mutable shared state.

#### Related: Coupling Metrics

- [ ] Estimate coupling metrics where the design provides enough detail

| Metric | Good | Warning | Concern |
|--------|------|---------|---------|
| CBO | < 5 | 5-10 | > 10 |
| Ce (efferent) | < 7 | — | > 7 |
| Ca (afferent) | — | — | High = widely used, needs stability; not inherently bad |

---

## Beyond SOLID

### Structural Anti-Patterns

Flag as Critical or High.

- [ ] **Big Ball of Mud:** No interface contracts, no layering, no ownership
- [ ] **Lava Flow:** "We can't change this because it's legacy" / "This has
  always been this way"
- [ ] **Spaghetti Code:** Circular imports, mixed layers, no clear pipeline

### Over-engineering

For each new layer, data structure, lock, counter, or abstraction
introduced by the design:

- [ ] Can this element be eliminated without losing capability?
- [ ] Can this element be merged with an existing one without increasing
  coupling or reducing clarity?
- [ ] Does this element pay for its complexity? If removing it costs
  nothing, it's unnecessary complexity.

Distinct from Speculative Generality (§OCP): that targets complexity
for hypothetical future needs. This targets gratuitous complexity in
the current design — elements that solve real problems but could be
achieved more simply.

### Pattern Appropriateness

For each design pattern used in the proposed design:

- [ ] **What breaks if we remove this pattern?** If nothing, it's patternitis.
- [ ] **Golden Hammer:** Same solution applied to unrelated problems

### Organization & Conventions

Medium-Low concerns. Flag only when actively hindering maintainability.

- [ ] **Directory structure:** Feature-first or layer-first — does the
  choice suit the project's size and domain complexity?
- [ ] **Naming:** Can module/class/method names be understood without
  context? Vague names are weak SRP signals (see §SRP).
- [ ] **Size thresholds exceeded:** (rough guidance — cohesion matters
  more than line count; for one-class-per-file languages, use the stricter
  threshold)

| Artifact | Threshold |
|----------|-----------|
| File | > 500 lines |
| Function | > 80 lines |
| Class/module | > 300 lines |
| Parameters | ≥ 4 |
| Nesting | ≥ 4 levels |

### Operational Extensibility

- [ ] At 10x current volume, does the design still work? (Scope: evaluate
  only when the design directly creates scaling limitations — shared
  mutable state, single-host architecture, unbounded queues)

### Concurrency & Distribution

Evaluate only when the design involves concurrent access, multiple
processes, or distributed components. Skip for single-threaded,
single-host designs.

- [ ] **Race conditions**: are there shared mutable resources accessed
  from multiple execution contexts without explicit coordination?
- [ ] **Deadlock potential**: do coordinating components acquire multiple
  locks or hold resources while waiting on others? Is the acquisition
  order consistent?
- [ ] **Consistency model**: if data is replicated or distributed, is the
  consistency model (strong, eventual, causal) stated and appropriate
  for the use case? Strong consistency where eventual suffices adds
  unnecessary coordination cost; eventual where strong is required
  causes user-visible anomalies.
- [ ] **Idempotency**: for operations that may be retried (message
  consumers, API endpoints), does the design ensure duplicate
  processing produces the same result?
- [ ] **Message ordering**: if the design relies on event or message
  ordering, is the ordering guarantee documented and realistic?
  (FIFO queues at scale have throughput trade-offs.)
- [ ] **Partial failure**: in multi-step distributed operations, can one
  step fail while others succeed? Is there a compensation or saga
  pattern, or is the design assuming atomic execution across
  boundaries it doesn't control?
- [ ] **Back-pressure**: if a producer can outpace a consumer, does the
  design include flow control? (Unbounded queues are a latent OOM.)

### Design-Level Code Smells

Check each against the proposed design. (Divergent Change → §SRP,
Speculative Generality → §OCP — do not double-file.)

- [ ] Long method — single function orchestrating many unrelated steps
- [ ] Feature envy — module references another module's data more than its own
- [ ] Data clumps — same fields passed together across multiple signatures
- [ ] Primitive obsession — raw strings/numbers where a domain type would
  add clarity
- [ ] Shotgun surgery — one change requires touching many modules
- [ ] Dead code — unused features, placeholders, or "future" sections
- [ ] Magic numbers/strings — hardcoded values without named constants

### General Refactor Heuristics

When recommending fixes for findings:

1. Split by responsibility, not by size
2. Introduce abstraction only when the second use case appears
3. Keep refactors incremental — one concern per change
4. Prefer composition over inheritance
5. Make illegal states unrepresentable