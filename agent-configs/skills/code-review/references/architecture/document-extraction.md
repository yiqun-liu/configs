# Document Discovery + Extraction

Progressive document discovery and fallback extraction methodology for
design review. The agent first searches for existing documentation, then
extracts missing understanding from implementation where needed.

---

## Discovery Process

### 1. Search for Documents

**Design doc** — scan first-level subdirectories for `doc/`, `docs/`,
`documentation/`. Search for `.md`, `.rst`, `.txt` files whose name
or content relates to the change topic (module name, feature name).

**Interface doc** — same directories; look for files with "interface",
"api", "contract", "spec" in the name or content. Not always present
(refactors may not change interfaces).

**Change description** — check:
- Git commit messages in the review range (`git log --oneline`)
- `.tmp/agent/plans/` for recently created implementation plans
- User-provided description from the prompt

If nothing found → ask user: "I couldn't find design documentation
for this change. Can you point me to relevant docs, or describe what
this change is intended to accomplish?"

### 2. Assess Completeness

Determine what's available, what's missing, and what each document
feeds into later review steps:

| Document | Feeds into | If missing |
|----------|-----------|------------|
| Design doc | Steps 2-5 (SOLID, coupling, patterns, risk, deviation) | Extract from implementation |
| Interface doc | Step 3 (integration, contracts, migration) | Extract only if change crosses module boundaries; skip for internal fixes |
| Change description | Step 5 (intention, deviation analysis) | Infer from commit messages, diff, function names |

Use what's available. Extract only the missing parts. Don't re-derive
what documents already cover.

### 3. Fill Gaps (Fallback)

When parts are missing, extract from implementation using the
methodology below. Extraction is scoped to the change being reviewed,
not the entire project.

### 4. Present for Confirmation

Always present the design understanding to the user before proceeding
to architectural assessment:

- Label each part: "from design doc: [path]" vs "inferred from
  implementation"
- Explicitly flag missing documentation: "Design document not found
  — the following understanding was inferred from implementation.
  Please confirm this is correct."
- Flag absent docs as a Medium finding (process issue)
- Wait for user confirmation or correction

If the user corrects: update inferred parts and proceed.
If the user confirms: proceed to Step 2.

---

## Edge Cases

| Situation | How to handle |
|-----------|-------------|
| No docs, no user description | Ask user directly. If user can't provide context, proceed with full extraction and flag missing documentation as a Medium finding |
| Partial documentation | Use what's available, extract only the missing parts, don't re-derive what docs already cover |
| Mixed doc + code review | Separate design concerns (from docs) from implementation details (from code); focus review on the design layer |
| User provides description in prompt | Treat as change description; still search for formal docs for deeper reference |
| Intention unclear from implementation | Flag as a finding: "The purpose of this change is unclear — user confirmation needed" |

---

## Document Types

### Design Document

Covers major design choices: why decisions were made, what alternatives
were considered, what trade-offs exist, and what constraints apply.
Typically includes: problem statement, proposed solution, rationale,
risk assessment.

### Interface Document

Defines contracts between modules or subsystems: entry points (function
signatures, API endpoints), data types (input/output shapes),
preconditions, postconditions, error modes. Not always present —
refactors that don't change boundaries may have no interface changes.

### Change Description

Explains what the change does and why. May be informal: a commit
message, a sentence in the user's prompt, or a PR description.
Sufficient for simple changes but not for architectural assessment
on its own.

---

## Scanning Strategy

### First-Level Directory Scan

Look at the project's first-level subdirectories. Common doc locations:

| Pattern | Typical location |
|---------|-----------------|
| `doc/`, `docs/`, `documentation/` | Dedicated doc directory |
| `.tmp/agent/plans/` | Agent-generated implementation plans |
| Files in project root | `README.md`, `DESIGN.md`, `ARCHITECTURE.md` |

### File Extension Search

Search for `.md`, `.rst`, `.txt` files whose name or content relates
to the change topic. Use the module or feature name as search keywords.

### Change Description Sources

| Source | How to access |
|--------|-------------|
| Commit messages | `git log --oneline {BASE}..{HEAD}` |
| PR description | `gh pr view {PR_NUMBER}` if available |
| User prompt | Provided directly in the review request |
| Implementation plan | `.tmp/agent/plans/` — look for recent files |

---

## Extraction Methodology

When documents are missing, extract from implementation. Extraction is
always **scoped to the change being reviewed**, not the entire project.

### 1. Intention Inference

Determine what problem this change solves and what it aims to accomplish.

**Sources of intention signals:**

- Diff content: what was added, removed, or modified
- Commit messages: summary line and body
- Function/class names: `add_rate_limiting`, `fix_null_deref`,
  `refactor_order_processing`
- Call graph changes: new callers, removed callers, changed
  interaction patterns
- Configuration changes: new settings, changed defaults

**Output format:** 1-3 sentence intention statement.

```
Intention (inferred from implementation):
This change adds rate limiting to the order processing pipeline to
prevent overwhelming the downstream service under high load. It
introduces a sliding window limiter and a retry-with-backoff
strategy for rejected requests.
```

**If intention is unclear:** that's itself a finding. Flag as:
"The purpose of this change is unclear from the implementation.
Multiple possible interpretations exist — user confirmation needed."

### 2. Logical View Extraction

Map data structures, key procedures, and module interactions within
the change scope.

**What to extract:**

- Data structures involved: structs, classes, schemas, config objects
  that the change creates or modifies
- Key procedure flow: the main execution path through the changed code
- Module interactions: which modules call into the changed area, and
  which modules the changed area calls into

**Scope rule:** read only the modules directly involved in the change
and their immediate callers/dependents. Do not read the entire project
architecture.

**How to extract:**

1. From the diff, identify which modules/files were changed
2. Read those files to understand their structure
3. Read calling modules (importers/callers) to understand how the
   changed code is used
4. Read called modules (imports/dependencies) to understand what the
   changed code depends on
5. Stop at one level of indirection — don't recursively read the
   entire dependency tree

**Output format:**

For simple changes (1-2 modules, clear purpose):

```
Logical view (inferred from implementation):
- OrderService.create_order() now checks RateLimiter before
  submitting to DownstreamClient
- RateLimiter tracks request count per time window (sliding)
- On rejection: RetryHandler applies exponential backoff
- Data: RateLimitConfig (max_requests, window_seconds), RetryPolicy
  (max_retries, base_delay_ms)
```

For multi-module changes (3+ modules, complex interaction):

```
Logical view (inferred from implementation):

┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│ OrderService │───→ │ RateLimiter  │───→ │ DownstreamClient │
└─────────────┘     └─────────────┘     └──────────────────┘
      │                    │
      │              ┌─────────────┐
      └────────────→ │ RetryHandler │
                     └─────────────┘

Data structures:
- RateLimitConfig: {max_requests, window_seconds}
- RetryPolicy: {max_retries, base_delay_ms, max_delay_ms}

Key procedure:
1. OrderService.create_order(order)
2. → RateLimiter.check(order.customer_id)
3.   → if allowed: DownstreamClient.submit(order)
4.   → if rejected: RetryHandler.retry_with_backoff(order)
```

### 3. Interface Contract Extraction (Scope-Dependent)

Extract interface contracts **only** when the change involves module or
subsystem boundaries. Skip for internal-only changes.

**When to extract:**

- Change adds or modifies a public/subsystem API
- Change introduces a new module that others will call
- Change modifies the contract between existing modules

**When to skip:**

- Bug fix within a single module (no boundary changes)
- Internal refactor that doesn't change external behavior
- Performance optimization within existing boundaries

**What to extract (when applicable):**

- Entry points: function signatures, API endpoints, event handlers
- Data types: input parameters, return values, error types
- Contracts: preconditions, postconditions, error modes, guarantees

**Output format:**

```
Interface contracts (inferred from implementation):

RateLimiter interface:
- check(client_id: str) → Result {allowed: bool, retry_after: int | None}
- Preconditions: client_id is a valid identifier
- Postconditions: if allowed, request may proceed; if not, retry_after
  indicates seconds until next check may pass
- Error mode: returns RateLimitError if internal state corrupt

RetryHandler interface:
- retry_with_backoff(order: Order, policy: RetryPolicy) → Result
- Preconditions: policy.max_retries > 0
- Postconditions: either succeeds within max_retries, or returns
  MaxRetriesExceededError
```

---

## Scope Adaptation

| Change type | Extraction depth | What to extract |
|-------------|----------------|-----------------|
| Small single-module fix | Minimal | Intention only |
| Feature addition (1-2 modules) | Moderate | Intention + logical view |
| Feature crossing module boundaries | Full | Intention + logical view + interface contracts |
| Refactor touching shared interfaces | Full | Intention + logical view + interface contracts |
| Architecture change (3+ modules) | Full | All three, with text diagram for logical view |

**Rule of thumb:** if the change affects how other modules interact with
the changed area, extract interface contracts. If it only affects
internal logic, skip them.

---

## Confirmation Protocol

Always present the extracted understanding to the user for confirmation
before proceeding to Step 2. The presentation must:

1. **Label sources clearly**: "from design doc: [path]" vs "inferred
   from implementation"
2. **Flag missing documentation explicitly**: "Design document not
   found — the following understanding was inferred from implementation.
   Please confirm this is correct."
3. **Flag Medium finding for absent docs**: missing design documentation
   is a process issue worth tracking, not just an inconvenience
4. **Wait for confirmation**: the user must confirm or correct before
   the agent proceeds to architectural assessment

**If the user corrects the understanding:** update the inferred parts
with the user's input and proceed.

**If the user confirms:** proceed to Step 2.

---

## Example Outputs

### All Documents Found

```
Design Understanding

Design doc (from docs/order-rate-limiting-design.md):
- Problem: downstream service rejects >100 req/s per client
- Solution: sliding window rate limiter + exponential backoff retry
- Rationale: fixed-window causes burst spikes at boundaries

Interface doc (from docs/api-contracts.md, §OrderService):
- create_order() contract unchanged; RateLimiter inserted internally

Change description (from commit messages):
- feat: add rate limiting for order processing pipeline

[No extraction needed — all documentation available.]
```

### Partial Documents — Change Description Only

```
Design Understanding

Design doc: **Not found** — inferred from implementation
- Intention: prevent overwhelming downstream service under high load
- Logical view (inferred):

  OrderService → RateLimiter → DownstreamClient
                     ↓
               RetryHandler

  RateLimitConfig: {max_requests, window_seconds}
  RetryPolicy: {max_retries, base_delay_ms}

Interface doc: **Not applicable** — internal change, no boundary changes
- RateLimiter is internal to OrderService; no new subsystem interface

Change description (from git log):
- feat: add rate limiting for order processing pipeline

**⚠️ Design document not found.** The understanding above was inferred
from implementation. Please confirm this is correct, or provide the
design document path.
```

### No Documents at All — Full Extraction

```
Design Understanding

Design doc: **Not found** — inferred from implementation
- Intention: fix race condition in concurrent order processing where
  two processes can simultaneously modify the same order state
- Logical view (inferred):

  OrderService.process(order)
    → acquires OrderLock(order.id)
    → reads current state
    → modifies state
    → releases OrderLock

  Data: OrderLock wraps pthread_mutex, scoped by order ID

Interface doc: **Not found** — inferred from implementation
- OrderLock interface:
  - acquire(order_id: str) → LockResult
  - release(order_id: str) → void
  - Preconditions: order_id is valid
  - Error mode: DeadlockError if lock held >30s

Change description: **Not found** — inferred from commit messages
  ("fix: concurrent order processing race condition")

**⚠️ No design documentation found.** All understanding above was
inferred from implementation. This is a Medium finding — design changes
should be documented. Please confirm the inferred understanding is
correct.
```