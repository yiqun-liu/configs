# Concurrency

Concurrency concerns at all three review levels. Load the section
relevant to your current review phase.

---

## Architecture Level

Inter-module concurrency: shared state across module boundaries, lock
ordering between modules, message ordering between services.

### Race Conditions at Module Boundaries

- [ ] Shared mutable state accessed by multiple modules without
  coordination?
- [ ] Module acts as a shared cache or global registry that multiple
  other modules read/write?

### Deadlock Potential

- [ ] Coordinating modules acquire multiple locks or hold resources
  while waiting on others?
- [ ] Is the acquisition order consistent across all modules?

### Consistency Model

- [ ] If data is replicated or distributed across modules, is the
  consistency model (strong, eventual, causal) stated and appropriate?
- [ ] Strong consistency where eventual suffices adds unnecessary
  coordination cost; eventual where strong is required causes
  user-visible anomalies.

### Idempotency

- [ ] For operations that may be retried (message consumers, API
  endpoints), does the inter-module protocol ensure duplicate
  processing produces the same result?

### Message Ordering

- [ ] If modules communicate via events or messages, is the ordering
  guarantee documented and realistic?

### Partial Failure

- [ ] In multi-step operations across module boundaries, can one step
  fail while others succeed? Is there a compensation or saga pattern?

### Back-Pressure

- [ ] If a producing module can outpace a consuming module, is there
  flow control? (Unbounded queues are a latent OOM.)

---

## Structural Level

Within-module concurrency: lock granularity, thread-safe data structure
design, synchronization patterns within a single module.

### Lock Granularity

- [ ] Does the module use coarse-grained locks that protect unrelated
  data? Consider finer-grained locking or lock striping.
- [ ] Does the module hold locks during I/O or slow operations?
  Consider releasing before I/O and re-acquiring after.

### Thread-Safe Data Structures

- [ ] Does the module use collections that are not thread-safe
  (`std::vector`, `list`, `dict`) in concurrent contexts?
- [ ] Consider concurrent alternatives (`ConcurrentHashMap`,
  `std::shared_mutex`, lock-free structures).

### Internal State Machine Concurrency

- [ ] Does the module have a state machine that transitions in response
  to concurrent events?
- [ ] Are state transitions atomic? Can the state machine reach an
  invalid state under concurrent access?

---

## Implementation Level

Single-function concurrency: race conditions, TOCTOU, atomic
correctness.

### Shared State Without Synchronization

Multiple threads/processes accessing shared mutable state without
locking or atomic operations.

```cpp
// Bad: shared counter without synchronization
int counter = 0;  // global, accessed by multiple threads

void increment() {
    counter++;  // non-atomic read-modify-write
}

// Fix: atomic operation
std::atomic<int> counter{0};

void increment() {
    counter.fetch_add(1, std::memory_order_relaxed);
}
```

```python
# Bad: shared dict accessed by multiple processes
shared_state = {}  # no locking

def update(key, value):
    shared_state[key] = value  # race with concurrent reads

# Fix: lock
from threading import Lock
lock = Lock()

def update(key, value):
    with lock:
        shared_state[key] = value
```

### Lazy Initialization Without Locking

```cpp
// Bad: double-checked locking without proper synchronization
static Data* instance = nullptr;

Data* get_instance() {
    if (!instance) {          // check (not atomic)
        instance = new Data(); // act (may happen twice)
    }
    return instance;
}

// Fix: use std::call_once or static initialization
static Data* get_instance() {
    static Data instance;  // guaranteed single initialization in C++11+
    return &instance;
}
```

### TOCTOU — Time-of-Check-to-Time-of-Use

```python
# Bad: check exists, then open — file might disappear
if os.path.exists(path):
    with open(path) as f:
        data = f.read()

# Fix: attempt operation, handle failure
try:
    with open(path) as f:
        data = f.read()
except FileNotFoundError:
    data = None
```

### Database Concurrency

```python
# Bad: read, modify, write — no version check
order = db.get_order(id)
order.status = "processed"
db.save(order)  # another process may have modified order

# Fix: optimistic locking with version column
order = db.get_order(id)
order.status = "processed"
db.save(order, expected_version=order.version)
```

### Concurrency Checklist (Implementation)

- [ ] Shared mutable state: protected by lock, mutex, or atomic?
- [ ] Lazy initialization: atomic or properly synchronized?
- [ ] TOCTOU: check-then-act replaced with try-act-catch?
- [ ] Multi-step state changes: inside lock or transaction?
- [ ] Database operations: optimistic/pessimistic locking where needed?
- [ ] Counter increments: atomic, not read-modify-write?
- [ ] Process communication: race-free?
