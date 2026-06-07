# Python Pitfalls — Language Quick Reference

Loaded when diff contains `.py` or `.pyi` files. Top pitfalls for
Python code review. The LLM understands Python concepts — this
provides concise identification patterns.

---

## Mutable Default Arguments

Default mutable objects (list, dict, set) are shared across all calls.

```python
# Bad: shared default list
def append_item(item, items=[]):
    items.append(item)
    return items

# Fix: None default + create inside
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```
---

## Bare except

Catches everything including KeyboardInterrupt and SystemExit — makes
it impossible to interrupt the program.

```python
# Bad: catches everything
try:
    do_work()
except:  # catches KeyboardInterrupt, SystemExit
    handle_error()

# Fix: catch specific exceptions
try:
    do_work()
except (IOError, ValueError) as e:
    handle_error()
```
---

## Shared Mutable Class Attributes

Class-level mutable objects shared across all instances.

```python
# Bad: shared list across instances
class Config:
    defaults = []  # all instances share this same list

c1 = Config()
c1.defaults.append("a")
c2 = Config()
print(c2.defaults)  # ['a'] — shared, not instance-local

# Fix: instance attribute in __init__
class Config:
    def __init__(self):
        self.defaults = []  # each instance gets its own
```
---

## is vs == for Value Comparison

`is` checks identity, `==` checks equality. Using `is` for value
comparison works for small ints and some strings (interning) but
fails for larger values.

```python
# Bad: is for value comparison
if status is "active":  # unreliable — depends on string interning

# Fix: == for value comparison
if status == "active":  # always correct
```
---

## Modifying List During Iteration

Removing/adding elements while iterating over the same list.

```python
# Bad: remove during iteration
for item in items:
    if item.invalid:
        items.remove(item)  # skips adjacent items

# Fix: filter or copy
items = [item for item in items if not item.invalid]
# or: iterate over copy
for item in items[:]:  # copy
    if item.invalid:
        items.remove(item)
```
---

## String Concatenation in Loops

Repeated `+=` creates a new string each iteration — O(n²) total.

```python
# Bad: repeated concatenation
result = ""
for s in strings:
    result += s  # new string each time

# Fix: join
result = "".join(strings)
```
---

## Missing with Statement for Resources

File handles, network connections, locks opened without `with` —
may not be closed on exception.

```python
# Bad: file not closed on exception
f = open("data.txt")
content = f.read()  # if exception here, f stays open

# Fix: with statement auto-closes
with open("data.txt") as f:
    content = f.read()
```
---

## Missing Type Annotations

Public functions without type annotations make it harder for tools
and readers to understand signatures.

```python
# Bad: no annotations on public function
def process(data, options):
    ...

# Fix: annotate public functions
def process(data: list[Item], options: ProcessOptions) -> Result:
    ...
```
---

## Python Pitfall Checklist

- [ ] No mutable default arguments (use None + create inside)?
- [ ] No bare except (catch specific types)?
- [ ] No shared mutable class attributes?
- [ ] is used only for None, == for values?
- [ ] No list modification during iteration?
- [ ] No string += in loops (use join)?
- [ ] Resources opened with with statement?
- [ ] Public functions have type annotations?