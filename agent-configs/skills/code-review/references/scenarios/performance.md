# Performance

Performance concerns at all three review levels. Load the section
relevant to your current review phase.

---

## Architecture Level

System-level performance: bottlenecks at module boundaries, scaling
limits of the module decomposition.

### System Bottleneck

- [ ] Is there a module that all requests must pass through? If it
  becomes slow, does the entire system degrade?
- [ ] Is there a synchronous chain of module calls where latency
  accumulates?

### Scaling Limit

- [ ] Does the architecture handle 10x growth without architectural
  changes?
- [ ] Scope: evaluate only when the architecture directly creates
  scaling limitations — shared mutable state, single-host architecture,
  unbounded queues.
- [ ] Is there shared mutable state that prevents horizontal scaling?

### Resource Contention

- [ ] Do multiple modules contend for the same resource (database
  connection pool, file system, network bandwidth)?
- [ ] Is there isolation between modules that need different resource
  profiles?

### Data Flow Efficiency

- [ ] Do modules exchange data through expensive serialization when
  in-process communication would suffice?
- [ ] Is there unnecessary data copying or transformation between
  module boundaries?

---

## Structural Level

Within-module performance: data structure choices, algorithmic
complexity, unnecessary copies across function calls.

### Data Structure Choice

- [ ] Does the module use a data structure with O(n) lookup where O(1)
  or O(log n) is available?
- [ ] Does the module copy large objects when references would suffice?

### Inter-Function Data Flow

- [ ] Do functions pass large objects by value instead of by reference?
- [ ] Is there repeated serialization/deserialization within the module?

### O(n²) and Worse

Nested loops where the inner loop iterates over the same data as the
outer loop, or per-item operations that are O(n) inside an O(n) loop.

```python
# Bad: O(n²) — find duplicates via nested loops
def find_duplicates(arr):
    dupes = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                dupes.append(arr[i])
    return dupes

# Fix: O(n) — use set
def find_duplicates(arr):
    seen = set()
    dupes = set()
    for item in arr:
        if item in seen:
            dupes.add(item)
        seen.add(item)
    return list(dupes)
```

---

## Implementation Level

Single-function performance: algorithmic complexity, memory management,
resource handling.

### Loop-Invariant Work

```python
# Bad: config parsed every iteration
for path in paths:
    config = json.loads(read_file("config.json"))
    process_file(path, config)

# Fix: compute once outside loop
config = json.loads(read_file("config.json"))
for path in paths:
    process_file(path, config)
```

### Missed Concurrency Opportunities

```python
# Bad: sequential await
a = await fetch_a()
b = await fetch_b()

# Fix: concurrent
a, b = await asyncio.gather(fetch_a(), fetch_b())
```

### Unbounded Collections

```python
# Bad: unbounded global cache
_cache: dict[str, Any] = {}

# Fix: bounded LRU
from functools import lru_cache

@lru_cache(maxsize=256)
def get_cached(key: str) -> Any:
    return expensive_computation(key)
```

### Large Object Retention

```python
# Bad: closure holds reference to large data
def create_handler():
    large_data = load_huge_file()  # 1GB
    return lambda: large_data[0]  # entire 1GB retained

# Fix: extract only needed value
def create_handler():
    large_data = load_huge_file()
    first = large_data[0]
    return lambda: first
```

### String Concatenation in Loops

```python
# Bad: creates new string each iteration
result = ""
for item in items:
    result += str(item)  # O(n²) total

# Fix: join
result = "".join(str(item) for item in items)
```

### Resource Leaks

```python
# Bad: file handle not closed
f = open("data.txt")
content = f.read()

# Fix: with statement
with open("data.txt") as f:
    content = f.read()
```

### Performance Checklist (Implementation)

- [ ] Time complexity: no O(n²) or worse in hot paths?
- [ ] Loop-invariant work hoisted outside loops?
- [ ] Independent async ops run concurrently where possible?
- [ ] Collections bounded (max-size, TTL, eviction)?
- [ ] Large objects released when no longer needed?
- [ ] String building uses join/reserve, not repeated concat?
- [ ] All resources properly released?
- [ ] Hot paths avoid unnecessary allocation/computation?
