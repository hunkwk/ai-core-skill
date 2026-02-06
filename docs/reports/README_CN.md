# 报告目录

本目录包含各类开发报告和分析。

## 报告类型

### weekly/ - 周报
- 每周工作总结
- 每周五或周末更新
- 命名: `YYYY-Www.md`（例如：`2025-W04.md`）

### review/ - 代码审查报告
- `/code-review` 命令的结果
- 安全和质量评估
- 命名: `YYYY-MM-DD-{功能}.md`

### metrics/ - 指标统计
- 测试覆盖率趋势
- 性能基线
- 依赖健康度分析

## 报告模板

### 周报模板

```markdown
# 第 YYYY 年第 WW 周

## 本周完成
- [x] 任务 1
- [x] 任务 2

## 进行中
- [ ] 任务 3

## 下周计划
- 计划项 1
- 计划项 2
```

## 自动生成

部分报告由 AI 命令自动生成：
- `/test-coverage` → 更新 `metrics/test-coverage.md`
- `/code-review` → 创建 `review/YYYY-MM-DD-{功能}.md`
- `/learn` → 更新会话摘要

---

**维护者**: hunkwk + AI 协作
