# Deviation Analysis — Design Evaluation Lens

Compare a proposed design against stated requirements and identify
deviations — both missing requirements and additions not traceable to
any requirement.

The LLM understands the concept of scope creep and requirements alignment.
This reference provides a structured protocol for the comparison, with
analysis prompts and a framework for evaluating whether deviations are
justified.

---

## Comparison Protocol

### 1. Enumerate Requirements

List every stated requirement from the plan, spec, or issue description.
If requirements are implicit (assumed by the user), ask for clarification
before proceeding.

**Ask:** "Can I see the complete list of requirements this design should
address?"

### 2. Map Requirements to Design Elements

For each requirement, identify which design element addresses it.

| Requirement | Design element | Status |
|-------------|---------------|--------|
| Req 1: ... | Module A, operation X | Addressed |
| Req 2: ... | Not found in design | **Missing** |
| Req 3: ... | Module B + Module C | Addressed (split across modules) |

### 3. Identify Unmapped Design Elements

Design elements not traceable to any requirement. These are potential
scope creep.

| Design element | Traceable requirement? | Assessment |
|----------------|----------------------|------------|
| Feature X | No requirement found | **Unmapped** — scope creep candidate |
| Cache layer | Performance requirement implied | Justified extension |
| Admin panel | Not requested | **Unmapped** — ask user if needed |

---

## Deviation Evaluation

Not all deviations are bad. A design that improves on the requirements
is a justified deviation. A design that omits critical requirements or
adds unnecessary complexity is problematic.

### Justified Deviations (Positive)

- Design addresses a requirement *better* than the spec envisioned
  (e.g., cleaner abstraction, simpler implementation)
- Design adds a safety measure not explicitly required but clearly
  beneficial (e.g., fallback behavior, error boundary)
- Design generalizes a narrow requirement in a way that reduces future
  maintenance cost without adding current complexity

**Ask:** "Does this deviation improve the outcome without adding
unnecessary complexity?"

### Problematic Deviations (Negative)

- Design omits a stated requirement entirely (High finding)
- Design addresses a requirement differently than specified, and the
  difference weakens the outcome (e.g., missing edge case handling
  that the spec called for)
- Design adds features not requested and not justified by implied
  requirements — classic scope creep (Medium finding)
- Design over-generalizes a specific requirement, adding abstractions
  that serve no current caller (patternitis)

**Ask:** "Is this deviation solving a real problem or adding complexity
for hypothetical future needs?"

---

## Scope Creep Detection

Red flags for scope creep in a design:

- Features described as "nice to have" or "we might need this"
  with no current requirement
- Design significantly larger than what the requirements describe
- Design includes configuration options no current caller uses
- "While we're at it" additions that aren't part of the original scope
- Abstractions that have only one current implementation

**Ask:** "Which current requirement is the smallest set this design
must address? Does the design go beyond that set?"

---

## Output Template for Deviation Findings

```markdown
### Requirements Mapping
| Req | Design element | Status |
|-----|---------------|--------|
| R1  | Module A      | ✅ Addressed |
| R2  | —             | ❌ Missing |
| R3  | Module B      | ✅ Addressed |

### Deviations
- **Missing**: R2 has no corresponding design element. [Impact and suggestion]
- **Unmapped**: Feature X is not traceable to any requirement. [Ask: needed?]
- **Justified**: Cache layer added beyond spec — addresses implied
  performance concern. [Acceptable]

```

---

## Deviation Analysis Without a Formal Plan

When the design understanding was inferred from implementation (no formal
design doc exists), deviation analysis still applies — but the reference
point changes from a written plan to the **inferred intention**.

### How It Works

Instead of comparing against a written plan, compare the implementation
against the inferred intention produced in Step 1c:

1. **Does the implementation fully address the inferred intention?**
   - If the intention says "add rate limiting" but the implementation
     only adds a counter without actual limiting → incomplete (High)
   - If the intention says "fix race condition" and the implementation
     adds proper locking → fully addressed

2. **Are there implementation elements not traceable to any inferred
   purpose?** (scope creep — even without a formal plan, code can
   exceed what was needed)
   - Implementation adds an admin dashboard, but the inferred intention
     only mentions rate limiting → unmapped element, ask user

3. **Are there aspects of the inferred intention that the implementation
   doesn't cover?** (incomplete implementation)
   - Intention mentions "retry with backoff" but implementation only
     has rate limiting without retry → missing (High)

### Key Difference From Plan-Based Analysis

The assessment is **less precise** because the "requirements" are
inferred, not formally stated. The inferred intention may be wrong —
the agent might have misunderstood the code's purpose.

Flag this uncertainty explicitly:

> "Deviation analysis is based on inferred intention, not a formal
> plan. Findings about scope and completeness should be verified
> with the user."

### Output Template for Inferred Deviation Findings

```markdown
### Requirements Mapping (inferred intention)
| Inferred requirement | Design element | Status |
|----------------------|---------------|--------|
| Rate limit requests  | RateLimiter   | ✅ Addressed |
| Retry on rejection   | —             | ❌ Missing |
| Configurable limits  | RateLimitConfig | ✅ Addressed |

**Note**: Requirements are inferred from implementation, not from a
formal design document. User verification recommended.

### Deviations
- **Missing**: "retry on rejection" — inferred intention mentions it
  but no RetryHandler found in implementation. [High — confirm with
  user whether retry was intended]
- **Unmapped**: AdminStatsDashboard added but no inferred requirement
  mentions it. [Medium — ask user if this was part of the intended scope]
- **Justified**: RateLimitConfig includes `window_seconds` with
  sensible defaults — not explicitly mentioned in intention but
  clearly necessary for rate limiting to work. [Acceptable]
```