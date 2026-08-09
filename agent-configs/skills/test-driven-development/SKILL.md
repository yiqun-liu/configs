---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

**Always:** new features, bug fixes, refactoring, behavior changes.

**Exceptions (ask your human partner):** throwaway prototypes, generated code, configuration files.

Thinking "skip TDD just this once"? Stop. That's rationalization.

## Preflight — Understand the Test Surface

Before writing a test:

- Check the current status of relevant tests when practical.
- Look for existing examples that show where tests belong, naming patterns, fixtures, helpers, and commands.
- Prefer the project's explicit test rules and nearby conventions over inventing new structure.

If there are no existing test examples, or no explicit project rule for where this test should go, stop and propose the test location, style/framework, verification command, and why this fits the codebase. Ask your human partner for confirmation before creating the test.

## The Iron Law

```text
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**

- Don't keep it as "reference".
- Don't "adapt" it while writing tests.
- Don't look at it.
- Delete means delete.

Implement fresh from tests. Period.

## Red-Green-Refactor

**RED — Write one failing test.** One behavior, clear name, real code (no mocks unless unavoidable).

**Good:**

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

Clear name, tests real behavior, one thing.

**Bad:**

```typescript
test('retry works', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```

Vague name, tests mock not code.

**Verify RED — MANDATORY. Never skip.** Run the test, confirm: it fails (not errors), the failure message is expected, it fails because the feature is missing (not typos). Test passes? You're testing existing behavior — fix the test. Test errors? Fix the error, re-run until it fails correctly.

**GREEN — Write the simplest code to pass the test.** Don't add features, refactor other code, or "improve" beyond the test.

**Good:**

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```

Just enough to pass.

**Bad:**

```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```

Over-engineered.

**Verify GREEN — MANDATORY.** Run the test, confirm: it passes, other tests still pass, output is pristine (no errors, warnings). Test fails? Fix code, not test. Other tests fail? Fix now.

**REFACTOR — Clean up after green only.** Remove duplication, improve names, extract helpers. Keep tests green. Don't add behavior.

**Repeat** — next failing test for next feature.

## Good Tests

| Quality | Good | Bad |
| --- | --- | --- |
| **Minimal** | One thing. "and" in name? Split it. | `test('validates email and domain and whitespace')` |
| **Clear** | Name describes behavior | `test('test1')` |
| **Shows intent** | Demonstrates desired API | Obscures what code should do |

## Why Order Matters

Tests written after code pass immediately, proving nothing — they may test the wrong thing, test the implementation rather than the behavior, or miss edge cases you forgot. Test-first forces you to see the test fail, proving it actually tests something. Tests-after answer "what does this do?"; tests-first answer "what should this do?" — tests-after are biased by your implementation.

## Testability and Architecture Changes

Hard-to-test code is useful design feedback, but do not silently change production architecture only to make a test possible.

When meaningful testing requires changing visibility, extracting internals, adding dependency injection, introducing interfaces, or otherwise altering production structure:

- Judge whether the change improves long-term design, not just test access.
- Prefer testing public behavior when it gives decent confidence.
- Avoid adding test-only production APIs.
- Be conservative about production changes whose only purpose is testing.
- If the architecture change seems worthwhile, explain the tradeoff and ask your human partner for confirmation before making it.
- If the change is not clearly worthwhile, propose the best lower-impact test strategy instead.

## When Stuck

| Problem | Solution |
| --- | --- |
| Don't know how to test | Write wished-for API. Write assertion first. Ask your human partner. |
| Test too complicated | Design too complicated. Simplify interface. |
| Must mock everything | Code too coupled. Consider dependency injection, but ask your human partner before changing production architecture. |
| Test setup huge | Extract test helpers. If production structure must change, ask your human partner first. |

## Debugging Integration

Bug found? Write a failing test reproducing it. Follow the TDD cycle. The test proves the fix and prevents regression. Never fix bugs without a test.

## Testing Anti-Patterns

When adding mocks or test utilities, read `@testing-anti-patterns.md` to avoid common pitfalls: testing mock behavior instead of real behavior, adding test-only methods to production classes, mocking without understanding dependencies.

## Red Flags — Stop and Start Over

- Code written before test.
- Test passes immediately.
- Rationalizing "just this once".

All of these mean: delete the code, start over with TDD.

## Completion

Before completing, confirm every new or changed required behavior—including relevant boundaries and error cases—has a test that was observed failing for the expected reason before its production implementation, and all relevant tests pass without unexpected warnings or errors.

## Final Rule

```text
Production code → test exists and failed first
Otherwise → not TDD
```

No exceptions without your human partner's permission.
