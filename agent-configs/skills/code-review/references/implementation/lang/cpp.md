# C++ Pitfalls — Language Quick Reference

Loaded when diff contains `.cpp`, `.hpp`, `.cc`, `.cxx`, `.hxx` files.
Top pitfalls for C++ code review. The LLM understands C++ concepts —
this provides concise identification patterns.

---

## RAII Compliance

Every resource (memory, file handle, lock, socket) should be managed
by an RAII wrapper. Raw `new`/`delete` or manual resource management
is a finding.

```cpp
// Bad: manual resource management
FILE* f = fopen(path, "r");
// ... use f ...
fclose(f);  // what if an exception is thrown before this?

// Fix: RAII wrapper
auto f = std::unique_ptr<FILE, decltype(&fclose)>(
    fopen(path, "r"), &fclose);
```
---

## Rule of 0/3/5

If a class manages a resource, it must define *all* of:
destructor, copy constructor, copy assignment, move constructor,
move assignment. If it manages no resource, it should define *none*.

```cpp
// Bad: destructor defined but copy/move missing
class Buffer {
    int* data;
    size_t size;
public:
    ~Buffer() { delete[] data; }  // destructor
    // missing: copy ctor, copy assign, move ctor, move assign
    // → double-delete if copied, leaked if moved-from
};

// Fix: Rule of 5 — define all or use smart pointers for Rule of 0
class Buffer {
    std::unique_ptr<int[]> data;
    size_t size;
public:
    // Rule of 0: unique_ptr handles everything, no custom dtor needed
};
```
---

## Exception Safety

Operations that may throw should leave the object in a valid state.
Use `noexcept` where throwing is impossible.

```cpp
// Bad: partial state on exception
void update(Config& c) {
    c.set_a(new_a);  // succeeds
    c.set_b(new_b);  // throws → c has inconsistent a/b
}

// Fix: commit-or-rollback
void update(Config& c) {
    auto old_a = c.a();
    auto old_b = c.b();
    c.set_a(new_a);
    try { c.set_b(new_b); }
    catch (...) { c.set_a(old_a); throw; }
}
```
---

## Dangling References

Returning references/iterators to containers that may be modified or
destroyed.

```cpp
// Bad: reference to local
const std::string& get_name() {
    std::string name = compute_name();
    return name;  // dangling: name destroyed after return
}

// Fix: return by value
std::string get_name() {
    return compute_name();
}
```
---

## Unnecessary Copies

Missing `std::move` or pass-by-reference where copy is wasteful.

```cpp
// Bad: unnecessary copy
void process(std::vector<int> data) {  // copies entire vector
    ...
}

// Fix: pass by reference or move
void process(const std::vector<int>& data) {  // no copy
    ...
}
void process(std::vector<int> data) {  // caller can move into this
    ...
}
```
---

## std::move in Return

Never `std::move` a return value — it prevents copy elision (RVO/NRVO).

```cpp
// Bad: prevents RVO
std::string make_name() {
    std::string name = compute();
    return std::move(name);  // actually WORSE than returning by value
}

// Fix: just return
std::string make_name() {
    std::string name = compute();
    return name;  // compiler applies RVO or NRVO
}
```
---

## Smart Pointer Misuse

`shared_ptr` overused where `unique_ptr` suffices. Raw `new` instead
of `make_unique`/`make_shared`.

```cpp
// Bad: shared_ptr where unique ownership is fine
auto p = std::make_shared<Data>();  // unnecessary atomic overhead

// Fix: unique_ptr for single ownership
auto p = std::make_unique<Data>();

// Bad: raw new
Data* p = new Data();  // no automatic cleanup
// Fix: make_unique
auto p = std::make_unique<Data>();
```
---

## C++ Pitfall Checklist

- [ ] All resources managed by RAII wrappers?
- [ ] Rule of 0/3/5 satisfied?
- [ ] Exception safety: partial state avoided on throw?
- [ ] No dangling references/iterators?
- [ ] Unnecessary copies eliminated (pass by ref or move)?
- [ ] No std::move on return values?
- [ ] Smart pointers: unique_ptr preferred over shared_ptr?
- [ ] make_unique/make_shared used instead of raw new?