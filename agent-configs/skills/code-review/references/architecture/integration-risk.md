# Integration + Risk — Architecture Level

Evaluate how the code integrates with the existing system and identify
risks at the architecture level. This reference covers two concerns:
integration assessment and risk identification.

---

## Integration Assessment

Evaluate how the code fits with the existing system.

### Breaking Changes

- [ ] Does this code break existing interfaces?
- [ ] If interfaces break, is there a migration strategy?
- [ ] Can existing consumers continue working during the transition?
- [ ] Is there a deprecation timeline for old interfaces?

### Interface Contracts

- [ ] Are new interfaces well-defined with clear input/output
  contracts?
- [ ] Are error modes documented for each interface?
- [ ] Are preconditions and postconditions explicit?

### Dependency Impact

- [ ] What existing modules depend on the changed area?
- [ ] Are those dependents affected by the change?
- [ ] If affected, what is the blast radius?

### Data Migration (Persistent Storage Only)

Only applicable when schema changes are involved.

- [ ] Is there a migration plan?
- [ ] Is there a rollback plan?
- [ ] Can the migration be done incrementally or does it require
  downtime?

---

## Risk Identification

Identify what could go wrong at the architecture level.

### Failure Modes

- [ ] What are the most likely ways this architecture could fail in
  production?
- [ ] Are there single points of failure — components whose failure
  breaks the entire system?

### Performance at Scale

- [ ] Does the architecture handle 10x growth without architectural
  changes?
- [ ] Scope: evaluate only when the architecture directly creates
  scaling limitations — shared mutable state, single-host
  architecture, unbounded queues.

### Data Integrity

- [ ] Are there operations where partial failure could leave the data
  in an inconsistent state?
- [ ] Are multi-step operations atomic, compensatable, or vulnerable
  to partial failure?

For concurrency signals at architecture scope (shared mutable state,
race conditions at module boundaries, consistency model), see
`references/scenarios/concurrency.md` — "Architecture" section.
