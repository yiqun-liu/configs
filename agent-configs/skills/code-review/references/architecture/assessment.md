# Architecture Assessment — Inter-Module Scope

Work through each section in order. Evaluate every signal against the
module decomposition and inter-module interfaces. A design that
*invites* violations is a finding even if no code exists yet.

---

## Paradigm Adaptions

This reference uses OOP vocabulary. For procedural code (C, procedural
C++), translate vocabulary and conditionally apply LSP/ISP.

**Vocabulary:** "class" → file/module, "method" → exported function,
"interface" → header file API or `struct ops` function pointer table,
"inheritance" → embedded parent struct as first field of child struct.

SRP, OCP, and DIP apply directly with this vocabulary translation. LSP
and ISP apply conditionally — see the "Procedural Code" notes in those
sections. When the code contains no OOP idioms, mark LSP and ISP as
N/A in checklist coverage.

---

## SRP — Responsibility & Cohesion (Module Level)

Check: does each module have a single reason to change?

- [ ] Module described as doing multiple unrelated things
- [ ] Different stakeholders would request different changes to the
  same module
- [ ] Data model mixes domain concerns with infrastructure concerns
- [ ] High public interface count (**corroborating only** — cohesive
  modules may legitimately have many methods)
- [ ] Vague or generic module name (`Manager`, `Handler`, `Processor`,
  `Service`, `System`) — **weak signal**; investigate only when paired
  with other signals

### Related: God Object

- [ ] Single module central to everything — removal would break
  features across unrelated domains

### Related: Module Cohesion

Check the cohesion level of each module (Functional → Sequential →
Communicational → Temporal → Logical → Coincidental). Qualifications:

- **Communicational** (CRUD on one entity) is acceptable for
  data-oriented modules (repository pattern).
- **Logical** (`Utilities`, `Helpers`) is borderline — `UserValidator`
  for all user rules may be functionally cohesive; `Validators`
  spanning multiple entities is genuinely logical.

---

## OCP — Extensibility & Evolution (Module Level)

Check: can new modules be added without touching existing code?

- [ ] Adding a new module requires modifying a central switch or
  dispatcher
- [ ] No plugin, strategy, or hook points for variation in the design
- [ ] Configuration hardcoded where **variation is expected** (distinguish
  from true constants — business rules that genuinely don't change)

### Related: Extension Points

- [ ] Check whether hooks/events or hardcoded behaviors are used, and
  whether the choice matches expected variation

**Trade-off:** Hooks have invisible side effects, ordering ambiguity,
and debugging difficulty. Over-hooking produces its own Big Ball of Mud.
Use hooks when behaviors will grow; hardcoded when the behavior set is
small and stable.

### Related: Speculative Generality

Adding complexity for hypothetical future needs with no current
requirement driving it. **Scoped to inter-module**: unnecessary module
abstractions, unused layers between modules, module interfaces with
no second implementer. **File as a single finding.** For within-module
speculative generality (unused abstract classes, single-implementation
interfaces), see `references/structural/anti-patterns-structural.md`.

- [ ] "We might need this later" or "For future extensibility" with
  no concrete use case at the module level
- [ ] Abstractions, layers, or modules added without solving a current
  problem

---

## LSP — Type Substitutability (Module Level)

Check: can any module implementation be substituted without the caller
knowing?

- [ ] Calling code contains module type checks or casts
- [ ] Module described as "a special case" that behaves differently
  from the interface contract
- [ ] Interface contract vague enough that implementers must interpret it
- [ ] Module throws for interface-defined operations, or returns no-op
  results

Key nuance: prefer composition over inheritance as a preventive
principle. Inheritance creates tight coupling and makes LSP violations
likely.

### Procedural Code

This section applies only when the code uses inheritance-like patterns
across module boundaries. If no such patterns exist, mark this section
N/A in checklist coverage.

- [ ] Embedded parent struct in child struct across modules — callers
  treat the child as the parent. Check that parent-level operations
  don't break for child instances.
- [ ] `struct xxx_ops` function pointer table shared across modules —
  different modules provide different ops implementations. Check that
  all implementations fulfill the same contract.

---

## ISP — Interface Design (Inter-Module)

Check: do all consumers use all methods of each inter-module interface?

- [ ] Some consumers need stub/empty implementations for certain methods
- [ ] Different consumers use only distinct subsets of the same
  interface
- [ ] High method count (**corroborating only** — a well-scoped interface
  may have many methods)
- [ ] Broad interface name (`IManager`, `IService`)

### Procedural Code

This section applies only when the code uses interface-like patterns
across module boundaries. If no such patterns exist, mark this section
N/A in checklist coverage.

- [ ] `struct xxx_ops` shared across modules with many function pointers
  where different modules only use a subset — split into narrower ops
  tables.
- [ ] Inter-module header declaring functions unused by some consumer
  modules — consider splitting into focused headers.

### Related: Stamp Coupling

- [ ] Interface passes a complex data structure where the receiver only
  uses part (e.g., full `User` object where only `user.name` is read)

Cross-reference: Stamp coupling also appears under §DIP. **File once,
not twice.**

---

## DIP — Dependency Structure (Inter-Module)

Check: can implementations be swapped without changing business logic?

- [ ] Domain/business module imports concrete infrastructure types
- [ ] Hardcoded configuration or connection strings in domain modules
- [ ] Business logic that is difficult to test without setting up
  infrastructure

### Related: Clean Architecture Dependency Direction

- [ ] Domain layer references database types, HTTP clients, file system
  paths, or any infrastructure detail — **High finding**

The domain layer may define interfaces that infrastructure implements.

### Related: Coupling Taxonomy

Classify each inter-module dependency. Qualifications:

- **Stamp** coupling also relates to ISP (see §ISP) — file once.
- **Control** coupling also relates to OCP — suggest strategy pattern.
- **Common** coupling with *immutable* global state is much less
  dangerous than mutable shared state.

### Related: Coupling Metrics

- [ ] Estimate coupling metrics where the design provides enough detail

| Metric | Good | Warning | Concern |
|--------|------|---------|---------|
| CBO | < 5 | 5-10 | > 10 |
| Ce (efferent) | < 7 | — | > 7 |
| Ca (afferent) | — | — | High = widely used, needs stability; not inherently bad |

---

## Structural Anti-Patterns

Flag as Critical or High.

- [ ] **Big Ball of Mud:** No interface contracts, no layering, no
  ownership
- [ ] **Lava Flow:** "We can't change this because it's legacy" /
  "This has always been this way"
- [ ] **Spaghetti Code:** Circular imports, mixed layers, no clear
  pipeline
