# Ownership Heuristics — Within-Module Scope

Identify responsibility leaks, misplaced helpers, and abstraction
boundary issues within a single module. These heuristics help determine
where logic *should* live vs. where it currently lives.

> **Procedural code:** Replace "class" with file/module, "interface"
> with header API or `struct ops`, throughout this document.

The LLM understands ownership and abstraction concepts. This reference
provides concrete patterns to identify within existing code.

---

## Responsibility Leaks

A function or class is responsible for something it shouldn't own. The
responsibility has leaked from its proper owner.

### Configuration Ownership Leaking into Business Logic

Business logic that parses config files, reads environment variables,
or handles policy strings.

```python
# Leak: business function resolving config details
def process_order(order):
    tax_rate = float(os.environ.get("TAX_RATE", "0.08"))
    return order.total * tax_rate
```

```cpp
// Leak: business function reading env vars
struct PriceCalculator {
    double apply_tax(double amount) {
        return amount * std::stod(getenv("TAX_RATE"));
    }
};
```

**Detection:** Flag when a business function resolves its own
configuration parameters. Business logic should receive pre-resolved
values; configuration resolution belongs in a configuration layer.

### Presentation Ownership Leaking into Business

Business logic that formats output, handles UI concerns, or makes
decisions based on display requirements.

```python
# Leak: business logic deciding how to display
def get_status_text(order):
    if order.status == "pending":
        return "⏳ Awaiting processing..."  # UI concern in business logic
    ...
```

**Detection:** Flag when business logic contains formatting, emoji,
or display-oriented decisions. Presentation decisions belong in the
presentation layer.

### Infrastructure Ownership Leaking into Business

Business logic that directly creates database connections, opens files,
or calls network services.

```cpp
// Leak: business function opening a file
void save_user(const User& u) {
    ofstream file("/data/users.dat");
    file << u.to_string();
}
```

**Detection:** Flag when a business function cannot be tested without
setting up the file system, database, or network.

---

## Helper Placement

### When to Keep Helpers Local

- Helper is only called by one function or class within the module
- Helper's parameters and return type match the local class's
  vocabulary
- Extracting it would require adding knobs/flags that only one caller
  uses
- Helper exists to simplify a local complexity that doesn't generalize

**Detection:** Before moving a helper to shared code, verify that at
least one other module would call it with the same parameters and
expect the same behavior. If no one else would use it — keep it local.

### When to Extract to Shared

- ≥2 classes within the module independently build the same object
  shape or perform the same operation
- Helper uses vocabulary that belongs to a shared domain (not local to
  one class)
- Current duplication is causing inconsistency (one caller has a bug the
  other doesn't)

**Detection:** Flag when multiple callers rebuild the same operation
independently. A shared helper would reduce inconsistency.

### When NOT to Extract

- Only one current caller (YAGNI — wait for the second use case)
- Helper's behavior is test-local — it exists to make tests readable
  but isn't production logic
- Extracting creates an interface with knobs only one caller configures

---

## Abstraction Boundary Issues

### Leaky Abstraction

Return type or interface that exposes internal implementation details —
ORM objects, HTTP response structures, file format specifics.

```python
# Leak: returning ORM object — caller forced to understand SQLAlchemy
def get_users():
    return session.query(User).filter(User.active == True).all()

# Fix: return domain type, hide persistence layer
def get_active_users() -> list[UserDTO]:
    rows = user_repo.find_active()
    return [UserDTO.from_row(r) for r in rows]
```

**Detection:** Flag when a function returns an infrastructure type
(ORM object, HTTP response, raw file handle). If the underlying
storage/format changes, the caller would need to change too — the
abstraction leaks.

### Over-Abstraction

Interface with only one implementer. Abstraction layer that adds
indirection without enabling substitution.

**Detection:** Flag when an interface has only one implementer and
no second implementer is anticipated. If you cannot name a second
implementer that would actually exist, the abstraction is speculative.

### Missing Abstraction

Two callers independently building the same operation — the shared
concept exists in the module but has no named representation.

**Detection:** Flag when the same logic is built independently in
multiple functions. Identify the shared concept and give it a name.

---

## Naming and API Shape

### Vague Names

Names like `Manager`, `Handler`, `Processor`, `Service` that don't
reveal scope or responsibility.

**Detection:** Flag when a class name is so generic that reading the
name alone gives no indication of what the class does.
- `UserCreator` reveals purpose → good
- `UserManager` reveals nothing → likely SRP violation

### Inconsistent Naming

Related operations using different naming conventions or terminology.

```python
# Inconsistent
create_user()     # verb-noun
user_add()        # noun-verb
insert_user()     # different verb for same operation
```

**Detection:** Flag when related operations within the module use
inconsistent naming patterns. A newcomer should be able to guess the
right function name from convention.

### Overly Broad API

Function that accepts a flag/enum to switch between fundamentally
different behaviors.

```python
# Overly broad
def process(data, mode):  # mode switches between entirely different logic
    if mode == "validate": ...
    elif mode == "transform": ...
    elif mode == "export": ...
```

**Detection:** Flag when splitting a function into focused variants
would make each one easier to understand and test.
