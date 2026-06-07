# C Pitfalls — Language Quick Reference

Loaded when diff contains `.c` or `.h` files. Top pitfalls for C code
review. The LLM understands C concepts — this provides concise
identification patterns.

---

## Pointer / Buffer Overflow

Accessing beyond allocated bounds. Most common C bug category.

```c
// Bad: no bounds check
char buf[10];
strcpy(buf, input);  // input may exceed 9 chars + null

// Fix: bounded copy
strncpy(buf, input, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';
```
---

## Undefined Behavior

Use-after-free, double-free, null dereference, out-of-bounds access.

```c
// Bad: use after free
free(ptr);
process(*ptr);  // UB: accessing freed memory

// Bad: null dereference
struct node *n = get_node(id);
n->value = 0;  // UB if get_node returns NULL

// Fix: check before use
struct node *n = get_node(id);
if (!n) return ERROR;
n->value = 0;
```
---

## Missing malloc NULL Check

malloc/calloc/realloc can return NULL on allocation failure.

```c
// Bad: no NULL check
void *buf = malloc(size);
buf[0] = 0;  // crash if malloc returns NULL

// Fix: always check
void *buf = malloc(size);
if (!buf) return ALLOC_FAILED;
buf[0] = 0;
```
---

## Integer Overflow in Size Calculations

Multiplying dimensions for allocation without overflow check.

```c
// Bad: overflow in size calc
int total = width * height;  // can overflow for large dimensions
void *buf = malloc(total);   // gets wrong size if overflowed

// Fix: use size_t and check
size_t total = (size_t)width * height;
if (total / width != height) return OVERFLOW;
```
---

## Resource Leaks

Missing free, fclose, or other cleanup.

```c
// Bad: leaked file handle
FILE *f = fopen(path, "r");
if (!f) return;
char buf[256];
fgets(buf, sizeof(buf), f);
return buf;  // f never closed

// Fix: always close
FILE *f = fopen(path, "r");
if (!f) return NULL;
char buf[256];
fgets(buf, sizeof(buf), f);
fclose(f);
return buf;
```
---

## Missing static on File-Local Functions

Functions used only within one file should be `static` to avoid
symbol collision and enable compiler optimization.

```c
// Bad: file-local function exposed globally
int helper_function(int x) { return x * 2; }

// Fix: restrict to file scope
static int helper_function(int x) { return x * 2; }
```
---

## volatile Misuse

`volatile` does not make operations atomic. It only prevents compiler
optimization of reads/writes. Not a substitute for proper synchronization.
---

## Signal Handler Safety

Only async-signal-safe functions may be called inside signal handlers.
printf, malloc, most library functions are NOT safe.
---

## C Pitfall Checklist

- [ ] Pointer/buffer access within bounds?
- [ ] No UB (use-after-free, double-free, null deref)?
- [ ] malloc/calloc/realloc return value checked for NULL?
- [ ] Size calculations overflow-safe (use size_t)?
- [ ] All resources properly freed/closed?
- [ ] File-local functions marked static?
- [ ] volatile not misused as atomic?
- [ ] Signal handlers only call async-signal-safe functions?
- [ ] Off-by-one in buffer indexing and loop bounds?