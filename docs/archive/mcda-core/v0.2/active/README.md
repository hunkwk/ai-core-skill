# Active Tasks Directory

This directory tracks execution progress for ongoing development tasks.

## Purpose

Real-time progress tracking for:
- TDD development cycles
- Bug fixing workflows
- Refactoring tasks
- Performance optimization

## File Naming

```
{type}-{slug}.md

Types:
  tdd-      : TDD development (RED → GREEN → REFACTOR)
  fix-      : Bug fix (REPRODUCING → DIAGNOSING → FIXING → VERIFYING)
  refactor- : Code refactoring (ANALYSIS → REFACTORING → TESTING)
  perf-     : Performance optimization
  exp-      : Experimental tasks

Examples:
  tdd-user-auth.md
  fix-login-crash.md
  refactor-payment-service.md
```

## Workflow

```bash
# Start new task
git feature user-auth
# Creates: docs/active/tdd-user-auth.md

# Update progress
# AI updates status in progress file

# Complete task
git finish
# Archives: docs/active/archive/2025-01/tdd-user-auth.completed.md
```

## Integration with Git Flow

| Branch | Progress File |
|--------|--------------|
| `feature/user-auth` | `active/tdd-user-auth.md` |
| `fix/login-crash` | `active/fix-login-crash.md` |
| `refactor/payment` | `active/refactor-payment.md` |

## Archive Structure

Completed tasks are archived monthly:
```
archive/
└── 2025-01/
    ├── tdd-user-auth.completed.md
    └── fix-login-crash.completed.md
```

---

**Auto-maintained by**: AI (via `/tdd`, `/code-review`, `/checkpoint`)
