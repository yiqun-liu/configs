# Coupling and Cohesion — Within-Module Scope

Assess coupling and cohesion **within a single module**. For inter-module
coupling, see `references/architecture/assessment.md` (§DIP — Coupling
Taxonomy).

> **Procedural code:** Replace "class" with file/module, "interface"
> with header API or `struct ops`, throughout this document.

This is the *code assessment lens* — you're observing actual
dependencies and data flow, not evaluating a proposed design.

The LLM understands coupling/cohesion concepts. This reference provides
identification signals specific to existing code within a module.

---

## Coupling — What to Look For

### Stamp Coupling

A function passes a complex object but the receiver only uses part of
it.

```cpp
// Stamp coupling: passing full User but only reading name
void print_label(const User& u) {
    std::cout << u.name;  // needs only .name, receives entire User
}
```

**Detection:** Flag when a function receives a complex object but only
reads a subset of its fields — the interface is wider than necessary.
Suggest narrowing the interface.

### Control Coupling

A caller passes a flag that switches the callee's behavior.

```python
# Control coupling
def process(data, is_admin):
    if is_admin:
        return admin_process(data)
    else:
        return user_process(data)
```

**Detection:** Flag when a boolean or enum parameter selects between
fundamentally different code paths within the same function. Suggest
separate operations or strategy injection.

### Common Coupling

Two functions/classes read/write the same mutable state at class or
module scope.

```python
# Common coupling
_config = {}  # class-level or module-level mutable

def function_a():
    _config["key"] = "value_a"

def function_b():
    print(_config["key"])  # reads what function_a wrote
```

**Detection:** Flag when two unrelated functions or classes within the
module share mutable state. The coupling is implicit — changes in one
silently affect the other.

### Content Coupling

A function directly accesses another class's private or internal data.

```cpp
// Content coupling: reaching into internals
void hack(User& u) {
    u._internal_cache.clear();  // accessing private implementation
}
```

**Detection:** Flag when code reaches into another class's internals
(bypassing its public interface). This is the worst coupling type —
fix by exposing a proper method.

---

## Cohesion — What to Look For

### Temporal Cohesion

A class groups methods that run at the same time but share no data
or logic.

```python
# Temporal cohesion: init methods unrelated but called together
class Initializer:
    def init_database(self): ...
    def init_logger(self): ...
    def init_cache(self): ...
```

**Detection:** Flag when a class's methods are only grouped because
they run at the same lifecycle point (init, shutdown, setup). Each
should be called independently at the point of need.

### Logical Cohesion

A class groups methods by category, not by purpose.

```cpp
// Logical cohesion: "all utils" but unrelated
namespace utils {
    std::string format_date(Date d);  // formatting
    int compute_hash(std::string s);  // hashing
    void log_error(std::string msg);  // logging
}
```

**Detection:** Flag when removing one method from a class leaves the
others with no meaningful relationship. Split by purpose.

### Coincidental Cohesion

No meaningful relationship between a class's methods.

**Detection:** Flag when it is impossible to state a single reason the
class would change. Every method changes for different reasons — split
into focused classes.

---

## Clean Architecture — Dependency Check

Within a module, look for business logic that imports infrastructure:

```python
# Violation: business function uses database directly
from sqlalchemy import Session

class OrderService:
    def get_orders(self):
        return Session().query(Order).all()
```

```cpp
// Violation: business function opens file
#include <fstream>

class OrderService {
    void save(const Order& o) {
        std::ofstream f("/data/orders.dat");
    }
};
```

**Detection:** Flag when a business function cannot be tested without
a database, file system, or network running. The dependency direction
is wrong — business logic should receive pre-resolved data, not fetch
it from infrastructure.

**Fix:** Business logic defines an interface. Infrastructure implements
it. Business logic depends on the abstraction, never the concrete type.
