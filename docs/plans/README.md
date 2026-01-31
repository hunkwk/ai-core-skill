# Plans Directory

This directory contains versioned implementation plans.

## Structure

```
plans/
├── v0.1/              # Version 0.1 (current)
│   ├── 001-docs-structure.md
│   └── summary.md
├── v0.2/              # Version 0.2 (planned)
└── roadmap.md        # Version roadmap
```

## Version Naming

```
v{major}.{minor}

major: Major architecture changes, breaking changes
minor: New features, backward compatible

Examples:
  v0.1 - Initial version
  v0.2 - Feature additions
  v1.0 - Stable release
```

## Plan Files

Each version contains:
- **Individual plans**: `NNN-{title}.md` (numbered)
- **Summary**: Overall version summary
- **Status**: pending | in-progress | completed

## Lifecycle

1. Requirements approved → Create plan in `plans/vX.X/`
2. Implementation in progress → Update plan status
3. Version completed → Archive and create next version

## Integration

Plans are linked to:
- **Requirements**: `requirements/current/REQ-XXX.md`
- **Active Tasks**: `active/{type}-{feature}.md`
- **Decisions**: `decisions/NNN-{title}.md`

---

**Maintained by**: hunkwk + AI collaboration
