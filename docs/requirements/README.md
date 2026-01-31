# Requirements Directory

This directory contains requirements analysis and documentation.

## Structure

```
requirements/
├── current/      # Active requirements being implemented
├── backlog/      # Pending requirements pool
└── archived/     # Completed or cancelled requirements
```

## Lifecycle

1. **Created** → `current/` (from AI analysis)
2. **Approved** → Move to `plans/vX.X/` (becomes implementation plan)
3. **Completed** → Move to `archived/`

## File Naming

Requirements use numbered prefixes:
```
001-docs-structure.md
002-user-auth.md
003-performance-optimization.md
```

## Template

See [REQ-XXX Template](../reference/req-template.md) for the standard requirement format.

---

**Maintained by**: AI collaboration (auto-generated from `/plan` output)
