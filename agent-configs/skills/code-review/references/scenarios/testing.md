# Testing

Testing quality at all three review levels. Load the section relevant
to your current review phase.

---

## Architecture Level

Inter-module testability: are module contracts testable? Is the system
mockable at boundaries?

### Contract Testability

- [ ] Are inter-module interfaces defined narrowly enough that each
  contract can be tested independently?
- [ ] Do interface contracts include error modes, or only happy paths?

### Mockability at Boundaries

- [ ] Can infrastructure modules be replaced with test doubles without
  modifying domain modules?
- [ ] Are inter-module dependencies injectable, or hardcoded?

### Integration Test Coverage

- [ ] Are there integration tests that exercise real module-to-module
  interaction (not just mocked unit tests)?
- [ ] Do integration tests cover the critical paths where modules
  interact?

---

## Structural Level

Within-module testability: are internal seams testable? Is the module's
state machine exercisable?

### Internal Seam Testability

- [ ] Can individual functions/classes within the module be tested in
  isolation?
- [ ] Are internal dependencies injectable, or does everything create
  its own collaborators?

### State Machine Exercisability

- [ ] If the module has a state machine, can every state transition be
  exercised through the public interface?
- [ ] Are invalid state transitions prevented and tested?

### Test Structure Within Module

- [ ] Do tests cover the module's public contract, or do they rely on
  testing private methods?
- [ ] Are test files co-located or discoverable for this module?

---

## Implementation Level

Single-function test quality: behavior vs mocks, edge cases, test
anti-patterns.

### Behavior vs Implementation Details

Tests should verify *observable behavior*, not *internal
implementation*.

```python
# Bad: tests that a mock was called, not that behavior is correct
mock_service.process.assert_called_once_with(data)

# Fix: test the outcome
result = service.process(data)
assert result.status == "completed"
assert result.items == expected_items
```

### Missing Edge Case Tests

```python
# Bad: only tests valid input
def test_process():
    result = process(valid_data)
    assert result is not None

# Fix: also test edge cases
def test_process_empty():
    result = process([])
    assert result == default_result

def test_process_null():
    result = process(None)
    assert result == fallback_result
```

### Missing Negative Tests

```python
# Bad: only tests success case
def test_api_call():
    result = api.fetch()
    assert result.data is not None

# Fix: also test failure
def test_api_call_network_error():
    with mock_network_failure():
        result = api.fetch()
        assert result.error == "network_failure"
```

### Flaky Tests

Common causes:
- Time-dependent assertions (sleep, timeout, wall-clock comparisons)
- Random data generation without fixed seeds
- Race conditions in test setup/teardown
- External service dependencies
- Order-dependent tests that share mutable state

### Overly Complex Test Setup

Test requires extensive mock configuration, making the test harder to
understand than the code it tests.

### Testing Checklist (Implementation)

- [ ] Tests verify behavior/outcomes, not mock interactions?
- [ ] Edge cases covered (empty, null, max-size, boundaries)?
- [ ] Negative tests present (error paths, failures)?
- [ ] No flaky tests (non-deterministic, time-dependent)?
- [ ] Test setup not more complex than the code being tested?
- [ ] Test names describe the scenario, not just the function?
