# Testing Anti-Patterns

**Load this reference when:** writing or changing tests, adding mocks, or tempted to add test-only methods to production code.

## Overview

Tests must verify real behavior, not mock behavior. Mocks are a means to isolate, not the thing being tested.

**Core principle:** Test what the code does, not what the mocks do.

**Following strict TDD prevents these anti-patterns.**

## The Iron Laws

```text
1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies
```

## Anti-Pattern 1: Testing Mock Behavior

**Violation:** asserting that a mock exists or was called, instead of asserting real behavior.

```typescript
// ❌ BAD: testing that the mock exists
expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();

// ✅ GOOD: test real component behavior
expect(screen.getByRole('navigation')).toBeInTheDocument();
```

**Gate function:** before asserting on any mock element, ask "Am I testing real component behavior or just mock existence?" If testing mock existence → stop, delete the assertion or unmock the component.

## Anti-Pattern 2: Test-Only Methods in Production

**Violation:** adding a method to a production class only used by tests (e.g. a `destroy()` for `afterEach` cleanup).

**Fix:** move test-only methods to test utilities. The production class shouldn't carry code only tests call; that pollutes the API and risks accidental production use.

**Gate function:** before adding any method to a production class, ask "Is this only used by tests?" If yes → stop, put it in test utilities. Then ask "Does this class own this resource's lifecycle?" If no → wrong class for this method.

## Anti-Pattern 3: Mocking Without Understanding

**Violation:** mocking a method whose side effects the test depends on, breaking the test logic invisibly.

```typescript
// ❌ BAD: mock prevents the config write the test depends on
vi.mock('ToolCatalog', () => ({
  discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
}));
await addServer(config);  // Should detect duplicate, but won't

// ✅ GOOD: mock the slow part, preserve behavior the test needs
vi.mock('MCPServerManager');
await addServer(config);  // Config written, duplicate detected
```

**Gate function:** before mocking any method, ask what side effects the real method has, whether the test depends on any of them, and whether you fully understand what the test needs. If unsure, run the test with the real implementation first, observe what actually needs to happen, then add minimal mocking at the right level.

## Anti-Pattern 4: Incomplete Mocks

**Violation:** mocking only the fields your immediate test uses, hiding structural assumptions. Downstream code may depend on fields you didn't include.

**Fix:** mock the COMPLETE data structure as it exists in reality, not just the fields your immediate test uses. If uncertain, include all documented fields.

## Anti-Pattern 5: Integration Tests as Afterthought

**Violation:** "Implementation complete. No tests written. Ready for testing."

Testing is part of implementation, not optional follow-up. TDD would have caught this.

## Quick Reference

| Anti-Pattern | Fix |
| --- | --- |
| Assert on mock elements | Test real component or unmock it |
| Test-only methods in production | Move to test utilities |
| Mock without understanding | Understand dependencies first, mock minimally |
| Incomplete mocks | Mirror real API completely |
| Tests as afterthought | TDD — tests first |
| Over-complex mocks | Reconsider the unit boundary; prefer real-component integration tests when simpler |

## Red Flags

- Assertion checks for `*-mock` test IDs.
- Methods only called in test files.
- Mock setup is >50% of the test.
- Test fails when you remove the mock.
- Can't explain why the mock is needed.
- Mocking "just to be safe".

## TDD Prevents These Anti-Patterns

1. **Write test first** → forces you to think about what you're actually testing.
2. **Watch it fail** → confirms the test tests real behavior, not mocks.
3. **Minimal implementation** → no test-only methods creep in.
4. **Real dependencies** → you see what the test actually needs before mocking.

If you're testing mock behavior, you violated TDD — you added mocks without watching the test fail against real code first.
