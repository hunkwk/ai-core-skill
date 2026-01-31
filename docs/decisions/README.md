# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for significant technical decisions.

## What is an ADR?

An ADR documents:
- **Context**: What is the problem?
- **Decision**: What did we decide?
- **Consequences**: What does this mean?

## File Naming

```
{number}-{short-title}.md

Examples:
  001-use-redis-vectors.md
  002-flat-skill-structure.md
  003-git-flow-simplified.md
```

## Template

```markdown
# ADR-XXX: [Decision Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
[Describe the problem and current state]

## Decision
[Describe the decision made]

## Consequences
- **Positive**: [Benefits]
- **Negative**: [Drawbacks]

## Related
- Link: [Related issue/commit]
- Author: hunkwk
- Date: YYYY-MM-DD
```

## Usage

When making significant technical decisions:
1. Copy `template.md`
2. Fill in ADR content
3. Number sequentially
4. Commit with decision

---

**See**: [ADR Template](template.md)
