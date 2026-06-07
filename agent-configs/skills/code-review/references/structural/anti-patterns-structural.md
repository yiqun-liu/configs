# Structural Anti-Patterns — Within-Module Scope

Identify maintainability anti-patterns within a single module. These
degrade maintainability without necessarily causing bugs today.

> **Procedural code:** Replace "class" with file/module throughout this
> document. "Copy-paste variants" applies to macros and repeated struct
> initialization patterns.

---

## Nested Conditionals

Ternary chains ≥2 deep or if/else nesting ≥3 levels.

```python
# Bad: nested ternary chain
label = (
    "Admin" if role == "admin" else
    "Manager" if role == "manager" else
    "Viewer" if role == "viewer" else
    "Unknown"
)

# Fix: lookup table
ROLE_LABELS = {"admin": "Admin", "manager": "Manager", "viewer": "Viewer"}
label = ROLE_LABELS.get(role, "Unknown")
```

- [ ] Ternary chains ≥2 deep?
- [ ] If/else nesting ≥3 levels?

---

## Copy-Paste Variants

≥2 code blocks that differ only in variable name, URL, or string
constant.

```python
# Bad: two handlers differing only in URL
async def delete_post(id):
    await fetch(f"/api/posts/{id}", method="DELETE")
    router.push("/posts")

async def delete_comment(id):
    await fetch(f"/api/comments/{id}", method="DELETE")
    router.push("/comments")

# Fix: parameterized
async def delete_resource(resource, id):
    await fetch(f"/api/{resource}/{id}", method="DELETE")
    router.push(f"/{resource}")
```

- [ ] ≥2 code blocks differing only in variable/URL/string constant?

---

## No-Op Updates

Polling, interval, or event handler that triggers state updates even
when data hasn't changed.

```python
# Bad: poll always triggers update
for item in items:
    new_status = compute_status(item)
    db.update(item.id, status=new_status)  # writes even if unchanged

# Fix: check before write
for item in items:
    new_status = compute_status(item)
    if item.status != new_status:
        db.update(item.id, status=new_status)
```

- [ ] Update path checks whether value changed before writing?

---

## Overly Broad Operations

Reading entire collection/file then using only a subset.

```python
# Bad: load all, filter in code
all_items = db.query("SELECT * FROM orders")
pending = [i for i in all_items if i.status == "pending"]

# Fix: filter at source
pending = db.query("SELECT * FROM orders WHERE status = ?", ["pending"])
```

- [ ] Loading everything and discarding most?

---

## Redundant State

Stored field that can be derived from other fields in the same object.

```python
# Bad: fullName is redundant
class User:
    first_name: str
    last_name: str
    full_name: str  # derivable from first + last

# Fix: compute property
class User:
    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

- [ ] Stored field derivable from other fields?

---

## TOCTOU in Structural Context

Check-then-act patterns that can be replaced with atomic operations.

```python
# Bad: file might disappear between check and open
if os.path.exists(path):
    with open(path) as f:
        data = f.read()

# Fix: try-act-catch
try:
    with open(path) as f:
        data = f.read()
except FileNotFoundError:
    data = None
```

- [ ] Check-then-act where check and act are not atomic?

---

## Over-Engineering vs Speculative Generality

These are distinct concerns with different severities and scopes.

### Speculative Generality — Medium

Complexity added for hypothetical future needs with no current
requirement driving it. **Scoped to within-module**: unused abstract
classes, single-implementation interfaces, hooks within a class that
no caller exercises.

- [ ] Interface with only one implementer (exception: testability
  interfaces where production + mock count as two implementations)
- [ ] Abstraction layer within the module that no current caller uses
- [ ] "We might need this later" with no concrete use case within
  the module

### Over-Engineering — High

Gratuitous complexity in the current design — elements that solve real
problems but could be achieved more simply. Includes patternitis:
applying design patterns where straightforward code would suffice.

- [ ] Simple conditional replaced by strategy + factory + registry
- [ ] Understanding a single operation requires tracing through
  multiple abstraction layers
- [ ] Code significantly longer because of pattern application
- [ ] Element that could be removed without losing capability
- [ ] Interface with only one implementation (see exception under
  Speculative Generality)

**Distinction:** Speculative generality targets complexity for
hypothetical futures (Medium — wait and see). Over-engineering targets
gratuitous complexity in the current code (High — simplify now).

---

## Size Thresholds

Rough guidance — cohesion matters more than line count. For
one-class-per-file languages, use the stricter threshold.

| Artifact | Threshold | Flag as |
|----------|-----------|---------|
| File | > 500 lines | Medium if low cohesion |
| Function | > 80 lines | Medium — likely mixes concerns |
| Class/module | > 300 lines | Medium if LCOM4 > 2 |
| Parameters | ≥ 4 | Medium — prefer options object |
| Nesting | ≥ 4 levels | Medium — simplify control flow |

- [ ] File exceeds 500 lines with low cohesion?
- [ ] Function exceeds 80 lines?
- [ ] Class exceeds 300 lines with multiple responsibility groups?
- [ ] Function has ≥4 positional parameters?
- [ ] Nesting depth ≥4 levels?
