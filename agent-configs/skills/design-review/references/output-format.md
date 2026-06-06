# Output Format — Design Review

Output template, clean review protocol, and next steps for design review
findings.

---

## Output Template

```markdown
## Design Review

**Artifact reviewed**: [plan name / spec / implementation only]
**Scope**: [modules / features covered]
**Design understanding sources**:
- Design doc: [found: path] / [not found — inferred from implementation]
- Interface doc: [found: path] / [not found] / [not applicable — internal change]
- Change description: [commit message] / [PR description] / [user prompt]

**Document availability issue**: [flag if design doc was missing — Medium finding]

---

### Design Understanding

[Summary of the design being reviewed. Clearly label each part as
"from design doc" or "inferred from implementation".]

[For multi-module changes: include logical view as text diagram or
mermaid. For simple changes: prose is sufficient.]

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

**For each finding:**
- What the issue is
- Why it matters in this context
- Suggested resolution (if not obvious)

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

## Clean Review Protocol

If no meaningful findings exist, state explicitly:

```markdown
## Design Review

**Artifact reviewed**: [name]
**Scope**: [what was assessed]
**Design understanding sources**:
- Design doc: [found: path] / [not found — inferred from implementation]
- Change description: [source]

No significant findings. The design addresses all stated requirements,
follows sound architectural principles, and integrates cleanly with the
existing system.

**Not covered**: [anything the reviewer couldn't assess]
**Residual risks**: [any low-probability concerns worth noting]
```

Never invent findings to fill a review. "No issues found" is a valid
and honest outcome.

---

## Next Steps Confirmation

After presenting findings, offer structured options:

```
How would you like to proceed?
1. Revise design based on all findings
2. Revise based on Critical/High only
3. Revise specific items (tell me which)
4. Proceed as-is
```

Do not implement any design revisions until the user explicitly chooses.