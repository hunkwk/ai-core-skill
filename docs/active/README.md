# Active Tasks Directory

This directory tracks execution progress for ongoing development tasks.

## 📋 Purpose

Real-time progress tracking for:
- TDD development cycles (RED → GREEN → REFACTOR → DONE)
- Bug fixing workflows (REPRODUCING → DIAGNOSING → FIXING → VERIFYING → DONE)
- Refactoring tasks (ANALYSIS → REFACTORING → TESTING → DONE)
- Performance optimization
- Experimental tasks

## 📁 Directory Structure

```
active/
├── README.md                           # This file
├── README_CN.md                        # 中文说明
│
├── {project}/                          # Project-based tracking
│   ├── {version}/                      # Version-based subdirectory
│   │   ├── {type}-{feature}.md
│   │   └── ...
│   └── ...
│
└── archive/                            # Completed tasks
    └── {year}/
        └── {month}/
            └── {type}-{feature}-{timestamp}.completed.md
```

### Organization Structure

#### 1. Project-Based (`{project}/`)

Organize by project or skill name:

```
active/
├── mcda-core/                          # MCDA Core project
│   ├── v0.2/                           # Version 0.2 tasks
│   │   ├── tdd-mcda-core.md
│   │   ├── fix-weight-validation.md
│   │   └── refactor-reporter.md
│   │
│   └── v0.3/                           # Version 0.3 tasks
│       ├── tdd-json-config.md
│       ├── tdd-ahp-algorithm.md
│       └── tdd-html-reports.md
│
├── skill-creator/                      # Skill Creator project
│   └── v0.1/
│       └── tdd-export-import.md
│
└── common/                             # Cross-project tasks
    └── refactor-ci-pipeline.md
```

## 📝 File Naming Convention

```
{type}-{slug}.md

Types:
  tdd-      : TDD development (RED → GREEN → REFACTOR → DONE)
  fix-      : Bug fix (REPRODUCING → DIAGNOSING → FIXING → VERIFYING → DONE)
  refactor- : Code refactoring (ANALYSIS → REFACTORING → TESTING → DONE)
  perf-     : Performance optimization (BENCHMARKING → OPTIMIZING → VERIFYING → DONE)
  exp-      : Experimental tasks (EXPERIMENTING → EVALUATING → DONE)
  review-   : Code review (REVIEWING → DOCUMENTING → DONE)

Slug:
  kebab-case, descriptive

Examples:
  tdd-user-auth.md
  fix-login-crash.md
  refactor-payment-service.md
  perf-database-query.md
  exp-ai-suggestions.md
  review-security-audit.md
```

## 🔄 Status Tracking

### TDD Development Status

```
RED       → Writing failing tests
GREEN     → Making tests pass
REFACTOR  → Improving code quality
DONE      → Complete, tests passing
```

### Bug Fix Status

```
REPRODUCING   → Reproducing the bug
DIAGNOSING    → Finding root cause
FIXING        → Implementing fix
VERIFYING     → Testing fix
DONE          → Complete, bug resolved
```

### Refactoring Status

```
ANALYSIS      → Understanding current code
REFACTORING   → Making changes
TESTING       → Verifying behavior unchanged
DONE          → Complete, code improved
```

## 📄 Progress File Template

```markdown
# {Task Title}

**Type**: {tdd | fix | refactor | perf | exp | review}
**Status**: {current_status}
**Project**: {project-name}
**Version**: v{X.X.X}
**Branch**: {branch-name}
**Created**: {date}
**Updated**: {date}

## Overview
{Brief description}

## Current Status
**{current_status}**

### Progress
- [ ] {step 1}
- [ ] {step 2}
- [x] {completed step}

## Decisions & Notes
{Important decisions, blockers, solutions}

## Test Results
{Test execution results}

## Next Steps
{Immediate next actions}

## Related Docs
- Plan: {link to plan}
- ADR: {link to ADR}
```

## 🔄 Task Lifecycle

```
┌──────────────┐
│   Created    │  Progress file created
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ In Progress  │  Status changes (RED → GREEN → ...)
└──────┬───────┘
       │ completed
       ▼
┌──────────────┐
│    Done      │  Task completed
└──────┬───────┘
       │ archived
       ▼
┌──────────────────────────┐
│   Archived (monthly)     │  Moved to archive/
└──────────────────────────┘
```

## 🔗 Integration with Git Flow

| Branch Type | Progress File Location | Example |
|------------|----------------------|---------|
| `feature/xxx` | `active/{project}/v{version}/tdd-{feature}.md` | `mcda-core/v0.3/tdd-json-config.md` |
| `fix/xxx` | `active/{project}/v{version}/fix-{bug}.md` | `mcda-core/v0.2/fix-weight-validation.md` |
| `refactor/xxx` | `active/{project}/v{version}/refactor-{target}.md` | `common/refactor-ci-pipeline.md` |
| `experiment/xxx` | `active/{project}/exp-{name}.md` | `mcda-core/exp-ai-suggestions.md` |

## 📦 Archive Structure

Completed tasks are archived monthly:

```
active/archive/
├── 2026-01/
│   ├── tdd-mcda-core-20260131.completed.md
│   ├── fix-login-crash-20260115.completed.md
│   └── refactor-payment-service-20260120.completed.md
│
└── 2026-02/
    └── tdd-json-config-20260205.completed.md
```

**Archive naming**: `{type}-{slug}-{YYYYMMDD}.completed.md`

## ✅ Best Practices

1. **Create Early**: Create progress file when starting feature branch
2. **Update Frequently**: Update status after each significant step
3. **Be Specific**: Document decisions, blockers, and solutions
4. **Link Documents**: Reference related plans and ADRs
5. **Archive Promptly**: Move completed tasks to archive monthly

## 🔍 Finding Progress Files

```bash
# List all active tasks
find active/ -name "*.md" -not -path "*/archive/*"

# List tasks by project
ls active/{project}/*/

# List tasks by status
grep -l "Status: RED" active/*/*/*.md

# Find completed tasks
ls active/archive/*/
```

## 📊 Progress Metrics

Track team productivity:

```bash
# Count active tasks
find active/ -name "*.md" -not -path "*/archive/*" | wc -l

# Count completed tasks this month
ls active/archive/$(date +%Y-%m)/ | wc -l

# Find long-running tasks
find active/ -name "*.md" -not -path "*/archive/*" -mtime +7
```

---

**Auto-maintained by**: AI (via `/tdd`, `/code-review`, `/checkpoint`)
**Last Updated**: 2026-02-01
**Next Review**: 2026-03-01
