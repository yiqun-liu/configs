# Design Review Output Template

Present this format when the preset is Design Doc (document-only mode).
Omit "Strengths", severity subsections, "Recommended Alternative",
or "Open Questions" sections when empty — do not leave placeholder
headers.

---

```markdown
## Design Review

**Artifact reviewed**: [plan name / spec / document path]
**Scope**: [modules / features covered]
**Design understanding sources**:
- Design doc: [found: path] / [not found — inferred from implementation]
- Interface doc: [found: path] / [not found] / [not applicable]
- Change description: [source]

**Document availability issue**: [flag if design doc was missing — Medium finding]

---

### Design Understanding

[Summary of the design being reviewed. Clearly label each part as
"from design document" or "inferred from implementation".]

[For multi-module designs: include logical view as text diagram or
mermaid. For simple designs: prose is sufficient.]

---

### Strengths
- [What's well done. Be specific — reference design elements, not vague praise.]

### Findings

#### Critical
[Breaks correctness or corrupts the system — must address before proceeding]

#### High
[Works but user can sense degradation — should address before implementation]

#### Medium
[Maintainability concerns — can be deferred or tracked]

#### Low
[Minor cleanup opportunities — optional]

### Open Questions
[Things the reviewer couldn't assess without more context]

### Recommended Alternative
[Only present if alternative generation found a clearly superior approach.
Describe at a high level: architecture shape, key modules, how requirements
are met, why it's better than the proposed design.
Omit this section entirely if no alternative is clearly better.]

### Recommendations
[Architectural improvements, risk mitigations]

### Assessment

**Proceed?** [Yes / With revisions / Major redesign needed]

**Reasoning:** [1-2 sentence technical assessment]
```

---

## Next Steps

After presenting findings, offer structured options:

```
How would you like to proceed?
1. Revise design based on all findings
2. Revise based on Critical/High only
3. Revise specific items (tell me which)
4. Proceed as-is
```
