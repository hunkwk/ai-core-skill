# 活跃任务目录

本目录跟踪正在进行的开发任务的执行进度。

## 用途

实时跟踪以下任务进度：
- TDD 开发循环
- Bug 修复工作流
- 重构任务
- 性能优化

## 文件命名

```
{类型}-{简述}.md

类型:
  tdd-      : TDD 开发（RED → GREEN → REFACTOR）
  fix-      : Bug 修复（REPRODUCING → DIAGNOSING → FIXING → VERIFYING）
  refactor- : 代码重构（ANALYSIS → REFACTORING → TESTING）
  perf-     : 性能优化
  exp-      : 实验性任务

示例:
  tdd-user-auth.md
  fix-login-crash.md
  refactor-payment-service.md
```

## 工作流程

```bash
# 开始新任务
git feature user-auth
# 创建: docs/active/tdd-user-auth.md

# 更新进度
# AI 更新进度文件中的状态

# 完成任务
git finish
# 归档: docs/active/archive/2025-01/tdd-user-auth.completed.md
```

## 与 Git Flow 的集成

| 分支 | 进度文件 |
|------|---------|
| `feature/user-auth` | `active/tdd-user-auth.md` |
| `fix/login-crash` | `active/fix-login-crash.md` |
| `refactor/payment` | `active/refactor-payment.md` |

## 归档结构

已完成的任务按月归档：
```
archive/
└── 2025-01/
    ├── tdd-user-auth.completed.md
    └── fix-login-crash.completed.md
```

---

**自动维护**: AI（通过 `/tdd`、`/code-review`、`/checkpoint`）
