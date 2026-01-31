# 需求目录

本目录包含需求分析和文档。

## 目录结构

```
requirements/
├── current/      # 正在实现的需求
├── backlog/      # 待办需求池
└── archived/     # 已完成或取消的需求
```

## 生命周期

1. **创建** → `current/`（来自 AI 分析）
2. **批准** → 移动到 `plans/vX.X/`（变为实施计划）
3. **完成** → 移动到 `archived/`

## 文件命名

需求使用数字前缀：
```
001-docs-structure.md
002-user-auth.md
003-performance-optimization.md
```

## 模板

参见 [REQ-XXX 模板](../reference/req-template.md) 查看标准需求格式。

---

**维护者**: AI 协作（通过 `/plan` 输出自动生成）
