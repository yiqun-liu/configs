# Code Review Output Template

Present this format after all requested phases complete (or stop on
blocking findings). Omit any phase section for phases not completed.
Omit "Strengths" or severity subsections when empty — do not leave
placeholder headers.

---

```markdown
## Code Review

**Area inspected**: [file/directory/project name]
**Phases completed**: [Architecture / Structural / Implementation / All]
**Review ID**: [id from .tmp/agent/reviews/{id}]

---

### Architecture

**Strengths**:
- [What's well organized at module level. Be specific with references.]

**Findings**:

#### Critical
[none or list]

#### High
[findings]

#### Medium
[findings]

#### Low
[findings]

---

### Structural

**Strengths**:
- [What's well organized within modules.]

**Findings**:

[Same severity breakdown]

---

### Implementation

**Strengths**:
- [What's well done at function level.]

**Findings**:

[Same severity breakdown]

---

### Open Questions
[Things the reviewer couldn't assess without more context]

### Recommendations
[Improvements spanning multiple levels]
```

---

## Next Steps

After presenting findings, offer structured options:

```
How would you like to proceed?
1. Fix all findings
2. Fix Critical/High only
3. Fix specific items (tell me which)
4. No changes needed
```
