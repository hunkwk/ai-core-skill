# AI Core Skill 文档中心

> AI 友好的文档索引，便于快速定位

## 快速导航

### 规划与需求
- [需求分析](requirements/) - 需求文档（AI 输出）
  - [当前需求](requirements/current/) - 正在开发的需求
  - [待办需求](requirements/backlog/) - 需求池
- [实施计划](plans/) - 实施计划（按版本）
  - [v0.1](plans/v0.1/) - 当前版本计划
  - [路线图](plans/roadmap.md) - 版本路线图

### 执行与进度
- [活跃任务](active/) - **执行进度跟踪**
  - TDD 任务：`tdd-{feature}.md`
  - Bug 修复：`fix-{bug}.md`
  - 重构：`refactor-{target}.md`

### 报告与分析
- [周报](reports/weekly/) - 开发总结
- [代码审查](reports/review/) - 审查报告
- [指标统计](reports/metrics/) - 覆盖率与性能

### 决策记录
- [ADR 索引](decisions/) - 架构决策记录

## 文档维护

- 使用 `/update-docs` 命令自动更新
- 遵循 [CLAUDE.md](../CLAUDE.md) 规范
- AI 维护 `active/` 目录中的进度文件

## 文件命名规范

**进度文件**（`active/`）：
```
tdd-{feature}.md      # TDD 开发
fix-{bug-name}.md     # Bug 修复
refactor-{target}.md   # 重构
```

**状态跟踪**：
- TDD：`RED | GREEN | REFACTOR | DONE`
- Fix：`REPRODUCING | DIAGNOSING | FIXING | VERIFYING | DONE`

---

**最后更新**: 2025-01-31
**维护者**: hunkwk + AI 协作
