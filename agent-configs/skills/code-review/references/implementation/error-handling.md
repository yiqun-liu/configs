# Error Handling — Universal Checklist

Identify error handling anti-patterns across all languages. The LLM
understands exception handling concepts — this reference provides
concise identification patterns to clarify what
specifically to flag.

---

## Swallowed Exceptions

Empty catch block or catch with only logging — no recovery, no
propagation, no meaningful action.

```python
# Bad: silent failure
try:
    result = do_something()
except Exception:
    pass  # error disappears

# Bad: log-and-forget
try:
    result = do_something()
except Exception as e:
    logging.error(e)  # logged but nobody handles it
```

```cpp
// Bad: silent failure
try {
    do_something();
} catch (...) {
    // nothing
}
```

---

## Overly Broad Catch

Catching base exception class instead of specific types. Masks
different failure modes under one handler.

```python
# Bad: catches everything including KeyboardInterrupt
except Exception:  # too broad
    handle_error()

# Fix: catch specific types
except (IOError, ValueError) as e:
    handle_error()
```

```cpp
// Bad: catches everything
catch (...) {  // no way to distinguish failure modes
    handle_error();
}

// Fix: catch specific types
catch (const std::runtime_error& e) {
    handle_error();
}
```

---

## Error Information Leakage

Stack traces, internal details, or query strings exposed to end users.

```python
# Bad: exposes internal structure
return Response({"error": str(e), "query": sql}, status=500)

# Fix: generic message to user, detailed log internally
logger.error("Database error", error=e, user_id=user_id)
return Response({"error": "Operation failed"}, status=500)
```

---

## Missing Error Handling

No try-catch/error handling around fallible operations — I/O, network,
parsing, allocation.

```cpp
// Bad: malloc without NULL check
auto* buf = malloc(size);
buf[0] = 0;  // crash if malloc returns NULL

// Fix: check allocation result
auto* buf = malloc(size);
if (!buf) { return ALLOCATION_FAILED; }
buf[0] = 0;
```

```python
# Bad: network call without error handling
response = requests.get(url)  # can raise ConnectionError
data = response.json()  # can raise JSONDecodeError
```

---

## Async Error Propagation

Unhandled promise rejections, missing `.catch()`, async errors not
propagated to caller.

```python
# Bad: async error silently swallowed
async def fetch_data():
    result = await api_call()  # no try-except, error propagates nowhere

# Fix: handle or propagate
async def fetch_data():
    try:
        return await api_call()
    except ApiError as e:
        logger.error("API call failed", error=e)
        raise DataFetchError("Failed to fetch data") from e
```

---

## Fallback Behavior

For recoverable errors: define what should happen instead of crashing.

```python
# Good: defined fallback
try:
    config = load_config()
except FileNotFoundError:
    config = DEFAULT_CONFIG  # explicit fallback
```

```cpp
// Good: defined fallback
auto fd = open(path, O_RDONLY);
if (fd < 0) {
    return default_value();  // explicit fallback
}
```

