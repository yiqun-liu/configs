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
- Respect the structure described below.
- Keep number of words of each sections within 300 words
- Do not include obvious fact or trivial design choice
- Ask after each section whether it looks right so far
- Output format may be: design doc, decision memo, or action plan
- Be ready to go back and clarify if something doesn't make sense

**Research and inspiration:**
- Search the web early—once you understand the core intent and constraints
- Look for: similar projects, patterns, anti-patterns, well-designed examples
- Present findings as comparison: "X did A which is similar, but they chose B because..."
- Quote specific techniques but always link back to user's goals
- If nothing relevant exists or the search fails, say so

## Document Structure

```markdown
# [Project / Module Name] Design Doc

## Goals

[bullet points about the goals or motivations]

## Architecture

[The key design ideas or paradigms applied in the design]

### [Components (for multi-component project) or Functions (for simple project)]

[bullet points for each components or functions]
[if there are 5+ components or functions, create a text graphics or mermaid graph to describe their relationship]

### Work Flow

[mermaid sequence graph which summarizes the interactions between components]

## Methods

### Data Structure Design Considerations
[This secton only applies for proramming projects]

### [Key Process N]

[2-3 sentences to describe the sub proecsses]

[Key ideas, algorithms (for programming projects)]

## Validation

[key test cases for programming projects, validation-follow-ups for non-programming projects]

## References

**Related Works**
[bullet points about popular related projects or practices]
[key third-party dependencies for programming projects]

```

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`

**Implementation (only for programming projects):**
- First evaluate the modification scope (small/medium/significant)
- For small modifications: skip detailed implementation planning, ask user if ready to implement directly
- For medium/large modifications: use write-coding-plans skill to create detailed implementation plan

**What next (for non-programming work):**
- Ask user what they want to do next: deeper analysis, writing, research, or move to execution

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
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense
