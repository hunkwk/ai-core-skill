# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records (ADRs) for the project.

## 📋 What is an ADR?

An ADR is a document that describes an important architectural decision in the project:
- **Context**: What is the situation?
- **Decision**: What did we decide?
- **Consequences**: What does this mean?

## 📁 Directory Structure

```
decisions/
├── README.md                           # This file
├── template.md                         # ADR template
├── template_CN.md                      # 中文模板
│
├── {project}/                          # Project-specific ADRs
│   ├── 001-{title}.md
│   ├── 002-{title}.md
│   └── ...
│
├── {feature}/                          # Feature-specific ADRs
│   ├── 001-{title}.md
│   └── ...
│
└── archive/                            # Historical ADRs
    └── {year}/
        └── {month}/
```

### Subdirectory Organization

**By Project** (`{project}/`):
- Organize ADRs by project or skill name
- Examples: `mcda-core/`, `skill-creator/`, `plan/`

**By Feature** (`{feature}/`):
- Cross-cutting features that span multiple projects
- Examples: `authentication/`, `database/`, `api-design/`

**Archive** (`archive/{year}/{month}/`):
- Deprecated or superseded ADRs
- Monthly archival of old decisions

## 📝 ADR Naming Convention

```
{number}-{status}-{short-title}.md

number:    Sequential (001, 002, 003, ...)
status:    (optional) proposed | accepted | deprecated | superseded
title:     kebab-case, descriptive

Examples:
  001-accepted-layered-architecture.md
  002-proposed-json-config-support.md
  003-deprecated-yaml-only-approach.md
```

## 🔄 ADR Lifecycle

```
┌──────────────┐
│   Proposed   │  Draft ADR, under discussion
└──────┬───────┘
       │ approved
       ▼
┌──────────────┐
│   Accepted   │  Current active decision
└──────┬───────┘
       │ replaced/obsolete
       ▼
┌──────────────┐
│  Deprecated  │  No longer recommended
└──────┬───────┘
       │ archived
       ▼
┌──────────────┐
│   Archived   │  Moved to archive/
└──────────────┘
```

## 📄 ADR Template

Use `template.md` or `template_CN.md` to create new ADRs.

**Required Sections**:
1. **Status**: proposed | accepted | deprecated | superseded
2. **Context**: What is the issue?
3. **Decision**: What did we decide?
4. **Consequences**: What does this mean?

**Optional Sections**:
- **Alternatives**: What other options did we consider?
- **Related Decisions**: Links to related ADRs
- **References**: External links or documentation

## 🔢 Number Allocation

Per-project or per-feature numbering:

```
mcda-core/
├── 001-layered-architecture.md
├── 002-normalization-methods.md
├── 003-weighting-roadmap.md
└── 004-aggregation-algorithms.md

authentication/
├── 001-jwt-strategy.md
└── 002-oauth-integration.md
```

## 📚 Integration with Other Docs

- **Plans**: ADRs justify architectural choices in implementation plans
- **Active Progress**: ADRs guide development decisions during implementation
- **Checkpoints**: ADRs are referenced in project milestones

## ✅ Best Practices

1. **Write Early**: Document decisions as they're made
2. **Keep Focused**: One decision per ADR
3. **Be Concise**: ADRs should be 1-2 pages max
4. **Update Status**: Mark deprecated/superseded ADRs
5. **Link Related**: Reference related ADRs and plans

## 🔍 Finding ADRs

```bash
# List all active ADRs
find docs/decisions -name "*accepted*.md" -o -name "*.md" | grep -v deprecated

# Search ADRs by keyword
grep -r "keyword" docs/decisions/

# List ADRs for a specific project
ls docs/decisions/{project}/
```

---

**Maintained by**: AI + Human collaboration
**Last Updated**: 2026-02-01
**Next Review**: 2026-03-01
