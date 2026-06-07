# Universal Anti-Patterns — Low-Level Review Lens

Identify code quality anti-patterns across all languages. The LLM
understands these concepts — this reference provides concise before/after
examples in Python and C/C++ to clarify what specifically to flag,
and identification patterns for each pattern.

---

## Q1: Reuse Audit

New code duplicates an existing utility in the project.

```python
# Bad: hand-written path joining — project already has PathBuilder
def get_config_path(name):
    base = os.environ.get("APP_ROOT", ".")
    return os.path.join(base, "config", name + ".json")

# Fix: use existing utility
def get_config_path(name):
    return PathBuilder.config(f"{name}.json")
```

```cpp
// Bad: hand-written string hash — project already has hash_util
uint32_t my_hash(const std::string& s) {
    uint32_t h = 0;
    for (char c : s) h = h * 31 + c;
    return h;
}

// Fix: use existing
uint32_t h = hash_util::compute(s);
```

---

## Q2: Parameter Sprawl

Function with ≥4 positional parameters.

```python
# Bad: positional parameters hard to read and maintain
def create_user(name, email, role, team, active, timezone):
    ...

# Fix: options object / dataclass
@dataclass
class CreateUserOptions:
    name: str
    email: str
    role: Role = Role.MEMBER
    team: str | None = None
    timezone: str = "UTC"

def create_user(opts: CreateUserOptions) -> User:
    ...
```

```cpp
// Bad: positional parameters
User create_user(std::string name, std::string email, Role role, bool active);

// Fix: options struct
struct CreateUserOptions {
    std::string name;
    std::string email;
    Role role = Role::Member;
    bool active = true;
};
User create_user(const CreateUserOptions& opts);
```

---

## Q3: Leaky Abstraction

Return type exposes internal implementation (ORM object, HTTP response
structure, file format specifics).

```python
# Bad: returns ORM object — caller forced to understand SQLAlchemy
def get_users():
    return session.query(User).all()

# Fix: return domain type
def get_users() -> list[UserDTO]:
    rows = repo.find_all()
    return [UserDTO.from_row(r) for r in rows]
```

---

## Q4: Stringly-Typed Code

Magic strings instead of enum/constant/union type.

```python
# Bad: magic strings — typo risk, no IDE support
if status == "active": ...

# Fix: enum
class Status(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

if user.status == Status.ACTIVE: ...
```

```cpp
// Bad: magic string — typo silent
if (status == "active") { ... }

// Fix: constant or enum
enum class Status { Active, Suspended };
if (status == Status::Active) { ... }
```

---

## Q5: Nested Conditionals

Ternary ≥2 deep, if/else ≥3 deep.

```python
# Bad: nested ternary
label = "Admin" if role == "admin" else "Manager" if role == "manager" else "Unknown"

# Fix: lookup table
ROLE_LABELS = {"admin": "Admin", "manager": "Manager"}
label = ROLE_LABELS.get(role, "Unknown")
```

```cpp
// Bad: nested if 3+ levels
if (order) {
    if (order->items.size() > 0) {
        for (auto& item : order->items) {
            if (item.price > 0) { process(item); }
        }
    }
}

// Fix: early return + guard
if (!order || order->items.empty()) return;
for (auto& item : order->items) {
    if (item.price <= 0) continue;
    process(item);
}
```

---

## Q6: Copy-Paste Variants

≥2 code blocks differing only in variable/URL/string constant.

```python
# Bad: two handlers differing only in URL
async def delete_post(id):
    await fetch(f"/api/posts/{id}", method="DELETE")
async def delete_comment(id):
    await fetch(f"/api/comments/{id}", method="DELETE")

# Fix: parameterized
async def delete_resource(resource: str, id: str):
    await fetch(f"/api/{resource}/{id}", method="DELETE")
```

---

## Q7: No-Op Updates

Polling / event handler / interval triggers updates without checking
whether data actually changed.

```python
# Bad: always writes to DB even if unchanged
for item in items:
    new_status = compute_status(item)
    session.commit()  # writes regardless

# Fix: write only when changed
for item in items:
    new_status = compute_status(item)
    if item.status != new_status:
        item.status = new_status
        session.commit()
```

---

## Q8: Overly Broad Operations

Read entire collection/file then use only a subset.

```python
# Bad: load all users to find one
users = list(User.objects.all())
user = next(u for u in users if u.id == user_id)

# Fix: query at source
user = User.objects.get(id=user_id)
```

---

## Q9: Redundant State

Stored field derivable from other fields.

```python
# Bad: full_name stored separately
class User:
    first_name: str
    last_name: str
    full_name: str  # redundant

# Fix: computed property
class User:
    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

```cpp
// Bad: item_count stored separately
struct Order {
    std::vector<Item> items;
    int item_count;  // redundant with items.size()
};

// Fix: derive
struct Order {
    std::vector<Item> items;
    size_t count() const { return items.size(); }
};
```

---

## Q10: TOCTOU

Check-then-act pattern where the check and the act are not atomic.

```python
# Bad: file might disappear between check and open
if os.path.exists(path):
    with open(path) as f: data = f.read()

# Fix: try-act-catch
try:
    with open(path) as f: data = f.read()
except FileNotFoundError:
    data = None
```

```cpp
// Bad: memory might be exhausted between check and allocation
if (available > size) {
    auto* buf = malloc(size);  // available is stale
}

// Fix: attempt and handle failure
auto* buf = malloc(size);
if (!buf) { handle_error(); }
```
