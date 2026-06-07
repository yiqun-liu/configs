# Boundary Conditions — Universal Checklist

Identify boundary condition bugs across all languages. The LLM understands
edge cases — this reference provides concise identification patterns
to clarify what to flag specifically.

---

## Null / Undefined / None

Accessing properties on potentially null objects without checks.

```python
# Bad: no null check
name = user.profile.name  # crash if profile is None

# Fix: guard
if user.profile is None:
    return "unknown"
name = user.profile.name
```

```cpp
// Bad: no null check
auto name = user->profile->name;  // crash if profile is nullptr

// Fix: guard
if (!user || !user->profile) return "unknown";
auto name = user->profile->name;
```

---

## Truthy / Falsy Confusion

Using `if (value)` when 0, "", or False are valid values.

```python
# Bad: 0 is a valid count but treated as falsy
if item_count:  # skips when item_count == 0
    process(items)

# Fix: explicit comparison
if item_count > 0:
    process(items)
if item_count is not None:
    process(items)
```

```cpp
// Bad: 0 is valid but used as failure indicator
if (count) {  // skip when count == 0
    process(items);
}
// Fix: explicit check
if (count > 0) { process(items); }
```

---

## Optional Chaining Overuse

`a?.b?.c?.d` in JavaScript/TypeScript hides structural issues — the
chain silently returns undefined instead of surfacing the problem.

---

## Empty Collections

Code assumes array/list/vector has items.

```python
# Bad: assumes items exist
first = items[0]  # IndexError if empty

# Fix: check length
if items:
    first = items[0]
```

```cpp
// Bad: assumes vector has items
auto first = items[0];  // undefined behavior if empty

// Fix: check size
if (!items.empty()) {
    auto first = items[0];
}
```

---

## First / Last Element Access

`arr[0]` or `arr[arr.length-1]` without length check.

Same pattern as empty collections — flag both.

---

## Division by Zero

Missing check before division operations.

```python
# Bad: can divide by zero
average = total / count  # crash if count == 0

# Fix: guard
if count > 0:
    average = total / count
else:
    average = 0
```

```cpp
// Bad: no check
double avg = total / count;  // UB if count == 0 (integer division)

// Fix: guard
double avg = (count > 0) ? total / count : 0.0;
```

---

## Integer Overflow / Float Comparison

Large numbers exceeding safe range; floating point equality checks.

```python
# Bad: float equality
if x == 0.1:  # 0.1 is not exactly representable in IEEE 754

# Fix: epsilon comparison
if abs(x - 0.1) < 1e-9:
```

```cpp
// Bad: integer overflow in size calculation
int total = width * height;  // overflow for large images

// Fix: use wider type or check
size_t total = static_cast<size_t>(width) * height;
```

---

## Off-by-One

Loop bounds, array slicing, pagination calculations.

```python
# Bad: off-by-one in range
for i in range(len(items)):  # correct
    process(items[i])
# vs.
for i in range(1, len(items)):  # skips first element

# Pagination off-by-one
page_start = (page - 1) * limit  # correct
page_start = page * limit  # skips first page's items
```

---

## String Boundaries

Empty string, whitespace-only string, Unicode edge cases.

```python
# Bad: whitespace-only passes truthy check
if name:  # "   " passes this check
    greet(name)

# Fix: strip and check
if name.strip():
    greet(name.strip())
```

---

## Universal Boundary Checklist

- [ ] Null/None/nullptr handled?
- [ ] Truthy/falsy check excludes valid 0/""/False values?
- [ ] Empty collection handled before access?
- [ ] Division by zero guarded?
- [ ] Integer overflow possible in size calculations?
- [ ] Float comparison uses epsilon, not exact equality?
- [ ] Off-by-one in loop bounds, slicing, pagination?
- [ ] String checks handle whitespace-only and empty?