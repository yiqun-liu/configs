# Alternative Generation — Design Review Step

Generate alternative approaches to a proposed design and compare them to
reveal weaknesses the checklist might miss. This is a generative,
comparative methodology — not a systematic scan.

---

## Input

You receive the design context gathered during document discovery:

- The proposed design (from design doc, spec, or inferred from
  implementation)
- The core requirements the design must satisfy
- The existing system it integrates with (if applicable)

---

## Methodology

### 1. Distill Core Intent

State the problem the design solves in one or two sentences, stripped of
implementation details. This anchors the comparison — alternatives must
solve the same core problem.

Example: "A design for processing incoming orders, validating them,
updating inventory, and notifying the warehouse" distills to "Reliably
transform validated orders into fulfilled shipments."

### 2. Generate Alternatives

Consider alternatives at two scopes:

**Whole-design scope** — a fundamentally different architecture for the
entire problem. Look for:
- Different architectural styles (event-driven vs request-response,
  pipeline vs orchestration, push vs pull)
- Different decomposition strategies (by feature vs by layer vs by
  workflow)
- Eliminated indirection (does a coordinating layer need to exist, or
  can participants interact directly?)

**Per-component scope** — simpler arrangements of specific modules:
- Merged modules that don't justify separate existence
- Removed layers that add indirection without clear benefit
- Replaced patterns with simpler alternatives (e.g., direct call vs
  observer, function vs factory)

**Dimensions to explore** (pick the ones that are meaningfully different,
not all four every time):

| Dimension | Question |
|-----------|----------|
| Simpler | Fewer moving parts — can we remove modules or layers? |
| Faster | Less indirection — can we reduce the call depth? |
| More conventional | Well-known approach — is the design reinventing something? |
| Minimal viable | Simplest thing that works — what's the 20% that handles 80%? |

### 3. Compare

For each viable alternative, compare against the proposed design on three
criteria:

**Complexity** — fewer moving parts, fewer modules, fewer indirection
layers. Count matters: if the alternative achieves the same result with
half the components, the proposed design carries unjustified complexity.

**Coverage** — does the alternative handle all stated requirements? If an
alternative covers 90% of requirements with 50% of the complexity, the
remaining 10% should justify the other 50% — otherwise the design is
over-built.

**Evolvability** — can the alternative adapt to likely changes? A simpler
design that can't evolve is worse than a slightly more complex one that
can. But don't speculate — only consider evolvability for changes the
requirements or context explicitly suggest.

If **no simpler alternative** exists for a component, that component is
well-justified. Note it as a strength.

### 4. Derive Findings

Weaknesses surface from the comparison, not from principle violations:

- "A simpler approach exists that handles the same requirements" →
  the extra complexity is unjustified. Severity depends on how much
  complexity is removed: entire layer → High, minor simplification →
  Medium.
- "The proposed design adds indirection for a problem that doesn't
  require it" → unnecessary abstraction. Medium finding.
- "No simpler alternative exists" → strength. The design's complexity
  is justified by the problem it solves.

---

## Stop Conditions

- **2-3 alternative directions** maximum. Don't enumerate minor
  variations of the same approach.
- **If the proposed design is already the simplest obvious approach**,
  state that explicitly and move on. Not every design has a simpler
  alternative.
- **Skip per-component alternatives** for components that are trivially
  simple (a single function, a thin wrapper). Focus on components with
  3+ internal parts or 2+ dependencies.
- **Don't generate alternatives for requirements that are fixed.** If
  the requirement says "use REST", don't propose gRPC. Work within the
  stated constraints.

---

## Output Format

Return findings in this structure for the parent skill to incorporate:

```
### Alternative Generation Findings

#### Weaknesses

1. [Severity] [Component/aspect]: [what the weakness is]
   - Proposed: [current design approach]
   - Simpler alternative: [what could be done instead]
   - Why it's better: [complexity/coverage/evolvability comparison]

2. ...

#### Recommended Alternative (if one is truly better)

[Describe the alternative design at a high level — enough to understand
its shape, not full detail. Include: architecture, key modules, how
requirements are met, why it's better.]

[Only present if an alternative is clearly superior — not just
slightly different. If alternatives trade off equally, present them
as findings, not as a recommended replacement.]

#### Strengths Identified

- [Component]: no simpler alternative exists for [reason]. The current
  design's complexity is justified.
```
