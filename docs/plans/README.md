# Plans Directory

This directory contains versioned implementation plans and feature planning documents.

## 📁 Directory Structure

```
plans/
├── README.md                           # This file
├── README_CN.md                        # 中文说明
├── roadmap.md                          # Overall project roadmap
├── roadmap_CN.md                       # 项目路线图（中文）
│
├── {version}/                          # Version-based planning
│   ├── summary.md                      # Version summary
│   ├── 001-{feature-plan}.md
│   ├── 002-{feature-plan}.md
│   └── ...
│
└── {feature}/                          # Feature-based planning (cross-version)
    ├── README.md
    ├── requirements.md
    ├── design.md
    └── implementation.md
```

### Organization Strategies

#### 1. Version-Based (`{version}/`)

Organize by release version for version-specific planning:

```
plans/
├── v0.1/                               # Version 0.1 (completed)
│   ├── summary.md
│   └── 001-docs-structure.md
│
├── v0.2/                               # Version 0.2 (completed)
│   ├── summary.md
│   ├── 001-mcda-core-phase1.md
│   └── 002-mcda-core-phase2.md
│
└── v0.3/                               # Version 0.3 (planned)
    ├── summary.md
    ├── 001-json-config-support.md
    ├── 002-ahp-algorithm.md
    └── 003-html-reports.md
```

#### 2. Feature-Based (`{feature}/`)

Organize by feature for cross-version feature planning:

```
plans/
├── mcda-core/                          # MCDA Core feature
│   ├── README.md
│   ├── roadmap.md
│   ├── requirements.md
│   └── iterations/
│       ├── v0.2-mvp.md
│       ├── v0.3-enhancement.md
│       └── v0.4-advanced.md
│
├── authentication/                     # Authentication feature
│   ├── README.md
│   ├── design.md
│   └── implementation.md
│
└── database-migration/                 # Database migration feature
    ├── README.md
    ├── strategy.md
    └── rollback-plan.md
```

## 📝 Plan File Types

### Version Plans (`v{X.X}/`)

**Summary** (`summary.md`):
- Version overview
- Feature list
- Timeline
- Dependencies

**Individual Plans** (`NNN-{title}.md`):
- Feature requirements
- Implementation approach
- Testing strategy
- Acceptance criteria

### Feature Plans (`{feature}/`)

**README.md**: Feature overview
**requirements.md**: Detailed requirements
**design.md**: Technical design
**implementation.md**: Implementation steps
**roadmap.md**: Feature evolution roadmap

## 🎯 Version Naming Convention

```
v{major}.{minor}.{patch}

major: Major architecture changes, breaking changes
minor: New features, backward compatible
patch: Bug fixes, small improvements

Examples:
  v0.1 - Initial MVP
  v0.2 - Feature additions
  v0.2.1 - Patch release
  v1.0 - Stable release
```

## 📋 Plan File Template

### Individual Plan Template

```markdown
# {Feature Title}

**Status**: pending | in-progress | completed
**Priority**: high | medium | low
**Estimated**: {time estimate}
**Version**: v{X.X.X}

## Overview
{Brief description}

## Requirements
- {req 1}
- {req 2}

## Implementation Approach
{Implementation strategy}

## Testing Strategy
{Testing approach}

## Acceptance Criteria
- [ ] {criteria 1}
- [ ] {criteria 2}

## Related Docs
- Requirements: {link}
- ADR: {link}
```

## 🔄 Plan Lifecycle

```
┌──────────────┐
│    Pending   │  Planned, not started
└──────┬───────┘
       │ approved
       ▼
┌──────────────┐
│ In Progress  │  Currently being implemented
└──────┬───────┘
       │ completed
       ▼
┌──────────────┐
│  Completed   │  Feature delivered
└──────┬───────┘
       │ released
       ▼
┌──────────────┐
│   Archived   │  Version released
└──────────────┘
```

## 🔢 Number Allocation

Per-version numbering:

```
v0.3/
├── 001-json-config-support.md
├── 002-ahp-algorithm.md
├── 003-entropy-weighting.md
└── 004-html-reports.md
```

## 📚 Integration with Other Docs

- **Requirements**: `requirements/` directory contains detailed requirements analysis
- **Decisions**: ADRs in `decisions/` justify architectural choices
- **Active Progress**: `active/` tracks implementation progress
- **Checkpoints**: `checkpoints/` records completed milestones

## ✅ Best Practices

1. **Plan Before Implement**: Always create plan before coding
2. **Update Status**: Keep plan status synchronized with progress
3. **Link Documents**: Reference related ADRs, requirements, and active files
4. **Version Control**: One version per directory for clear history
5. **Summarize**: Always include `summary.md` in version directories

## 🔍 Finding Plans

```bash
# List all version plans
ls plans/v*/

# List all feature plans
ls plans/*/README.md

# Search plans by keyword
grep -r "keyword" plans/

# Find current version plans
ls plans/v0.3/
```

---

**Maintained by**: hunkwk + AI collaboration
**Last Updated**: 2026-02-01
**Next Review**: 2026-03-01
