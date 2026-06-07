# SOLID Checklist — Within-Module Scope

Evaluate code organization within a single module against SOLID
principles. Each principle includes a declarative principle statement,
identification signals, and refactor heuristics.

For general refactor heuristics, see `references/process.md`.

---

## Paradigm Adaptions

This checklist uses OOP vocabulary. For procedural code (C, procedural
C++), translate vocabulary and conditionally apply LSP/ISP.

**Vocabulary:**

| OOP term | Procedural equivalent |
|----------|----------------------|
| Class | File, module, or compilation unit |
| Method | Non-static function exported via header |
| Interface | Header file API, or `struct ops` function pointer table |
| Inheritance | Embedded parent struct as first field of child struct |
| Polymorphism | Function pointer table (`struct xxx_ops`), or type enum + void* |
| Attribute | Struct field |

SRP, OCP, and DIP apply directly with this vocabulary translation. LSP
and ISP apply conditionally — see the "Procedural Code" subsections
within those sections. When the procedural code contains no OOP idioms,
mark LSP and ISP as N/A in checklist coverage.

---

## SRP — Single Responsibility Principle

**Principle:** A class or function should have a single reason to
change.

### Identification Signals

- [ ] Class with >5-7 public methods operating on different data
- [ ] Class name contains "And", "Manager", "Handler", "Processor"
- [ ] File >300 lines with low cohesion between sections
- [ ] Class that both orchestrates workflow and implements domain rules
- [ ] Function imported by many callers for different purposes
- [ ] Config parsing mixed with business logic in the same function

### Related: LCOM4 (Conceptual Lens)

- [ ] Can the class's operations be partitioned into independent groups
  that share no data?

| LCOM4 | Assessment |
|-------|------------|
| 1 | Ideal |
| 2-3 | Warning — consider splitting |
| > 3 | Concern — class likely serves multiple purposes |

### Refactor Heuristics

- Split by responsibility, not by size — a small class can still
  violate SRP if it serves two stakeholder groups
- Extract orchestration into a coordinator; keep domain rules in a
  focused class
- If the class serves two purposes, propose two classes with a narrow
  coordination interface

---

## OCP — Open/Closed Principle

**Principle:** New variants should be addable without modifying existing
code.

### Identification Signals

- [ ] Switch/if-else chains that grow with each new type added
- [ ] Central function modified every time a new behavior is introduced
- [ ] `instanceof` or type-checking scattered across callers
- [ ] Feature flags or config keys that trigger branching in core logic
- [ ] No plugin, strategy, or hook architecture — all behavior
  hardcoded

### Refactor Heuristics

- Introduce abstraction only when the second use case exists (YAGNI
  first)
- Replace switch chains with strategy pattern + registry
- Make variation injectable: accept a function/interface rather than
  branching on a flag

---

## LSP — Liskov Substitution Principle

**Principle:** Any subclass should be freely substitutable without the
caller needing to know the concrete type.

### Identification Signals

- [ ] `dynamic_cast`, `instanceof`, `type()` checks in calling code
- [ ] Subclass method that throws for an operation the parent defines
- [ ] Override that no-ops or returns a sentinel value
- [ ] Subclass with weaker preconditions or stronger postconditions
- [ ] Caller that must know the concrete type to use correctly

### Refactor Heuristics

- If subtypes can't be freely substituted, the interface abstraction is
  wrong — redesign the interface around what callers actually need
- Prefer composition: instead of inheriting and overriding, compose
  with strategies or delegates
- Make the interface contract explicit and narrow — every implementer
  should be able to fulfill all operations meaningfully

### Procedural Code

This section applies only when the code uses inheritance-like patterns.
If none of these patterns exist, mark this section N/A in checklist
coverage.

- [ ] Embedded parent struct as first field of child struct (inheritance
  via struct embedding). Check that code operating on parent pointers
  doesn't break when given a child.
- [ ] `struct xxx_ops` or similar function pointer table (vtable
  pattern). Check that all ops implementations fulfill the same
  contract — same preconditions, same postconditions.
- [ ] Type enum + void* dispatch (ad-hoc polymorphism). Check that all
  type cases handle the full contract.

---

## ISP — Interface Segregation Principle

**Principle:** All implementers should meaningfully use all methods of
an interface.

### Identification Signals

- [ ] Interface with >5-7 methods
- [ ] Implementer with empty/stub method bodies
- [ ] Interface name too broad (`IManager`, `IService`)
- [ ] Different clients using only disjoint subsets of the same
  interface
- [ ] Fat base class that subclasses inherit methods they don't need

### Refactor Heuristics

- Split broad interface into narrow, role-specific interfaces
- Each client should depend only on the interface matching its actual
  usage pattern
- Don't let one powerful implementer dictate a broad interface —
  design around the callers' needs

### Procedural Code

This section applies only when the code uses interface-like patterns.
If no interface-like patterns exist, mark this section N/A in checklist
coverage.

- [ ] `struct xxx_ops` with many function pointers where different
  callers only use a subset — the ops table is too broad. Split into
  narrower tables.
- [ ] Header file declaring functions unused by some consumers —
  consider splitting into focused headers.

---

## DIP — Dependency Inversion Principle

**Principle:** High-level logic should depend on abstractions, not on
concrete infrastructure implementations.

### Identification Signals

- [ ] Domain/business function importing database types, HTTP client, or
  file format specifics
- [ ] Hardcoded `new` or direct construction of infrastructure objects
  in business logic
- [ ] Business logic that knows about specific config file paths,
  connection strings, or environment variable names
- [ ] Function that is difficult to unit test without setting up
  infrastructure
- [ ] Import chain: business → ORM → database driver

### Refactor Heuristics

- Define the interface (abstraction) in the high-level module
- Infrastructure module implements that interface
- Business logic references the interface, never the concrete type
- Dependency direction: infrastructure → domain, never reversed
- Use constructor injection or factory injection — not service locator

---

## Code Smells (Within Module)

- [ ] Long method — function >50 lines with multiple levels of nesting
- [ ] Feature envy — function accessing another module's data more than
  its own
- [ ] Data clumps — same parameter group passed together in multiple
  calls
- [ ] Primitive obsession — raw strings/ints used where a domain type
  adds clarity
- [ ] Shotgun surgery — one change requires editing many functions
  across the module
- [ ] Divergent change — one module changes for many unrelated reasons
- [ ] Dead code — unreachable code, never-called functions, unused
  imports
- [ ] Magic numbers/strings — hardcoded values without named constants
