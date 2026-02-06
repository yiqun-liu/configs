---
name: brainstorm
description: "Explores user intent, requirements and design, inspire user before implementation or execution."
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.
Also look up the internet for related projects and ideas. Search early (after understanding core intent) and present findings as comparisons, not just links. Frame research as "Here's what others have done" with clear trade-offs against your user's direction.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover architecture, components, data flow, error handling, testing if it is a programming project
- Be ready to go back and clarify if something doesn't make sense

**Research and inspiration:**
- Search the web early—once you understand the core intent and constraints
- Look for: similar projects, patterns, anti-patterns, well-designed examples
- Present findings as comparison: "X did A which is similar, but they chose B because..."
- Quote specific techniques but always link back to user's goals
- If nothing relevant exists, say so—this is valuable signal too

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`

**Implementation (if it is a programming project):**
- Ask: "Ready to set up for implementation?"
- Use write-coding-plans to create detailed implementation plan

## Recording Ruled-Out Options

During exploration, note rejected approaches with brief rationale. Include in the final design doc under "Alternatives Considered":

```markdown
## Alternatives Considered

- **Approach A**: [description] — Ruled out because [reason]
- **Approach B**: [description] — Chosen because [why it wins over alternatives]
```

Keep explanations short (1-2 sentences). This prevents re-hashing decisions later and captures institutional knowledge.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense
