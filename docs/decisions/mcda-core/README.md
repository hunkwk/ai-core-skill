# MCDA Core 架构决策记录 (ADR)

**目录**: MCDA Core 项目的架构决策记录

---

## 📋 ADR 索引

| 编号 | 标题 | 状态 | 日期 | 主题 |
|------|------|------|------|------|
| [ADR-001](./001-mcda-layered-architecture.md) | 分层架构设计 | ✅ 已接受 | 2026-01-31 | 架构 |
| [ADR-002](./002-mcda-normalization-methods.md) | 标准化方法 | ✅ 已接受 | 2026-01-31 | 标准化 |
| [ADR-003](./003-mcda-weighting-roadmap.md) | 赋权方法路线图 | ✅ 已接受 | 2026-01-31 | 赋权 |
| [ADR-004](./004-mcda-aggregation-algorithms.md) | 汇总算法架构设计 | ✅ 已接受 | 2026-01-31 | 算法 |
| [ADR-005](./005-loader-abstract-layer.md) | 加载器抽象层 | ✅ 已接受 | 2026-01-31 | 数据加载 |
| [ADR-006](./006-sensitivity-service-refactoring.md) | 敏感性分析服务重构 | ✅ 已接受 | 2026-01-31 | 服务 |
| [ADR-007](./007-interval-fuzzy-mcda-architecture.md) | 区间数/模糊数 MCDA 架构设计 | 📋 提议 | 2026-02-03 | 不确定性 |
| [ADR-008](./008-group-decision-aggregation-strategy.md) | 群决策聚合策略选择 | 📋 提议 | 2026-02-03 | 群决策 |
| [ADR-014](./014-veto-mechanism.md) | 一票否决机制架构设计 | 📋 提议 | 2026-02-05 | 约束系统 |

---

## 📊 ADR 分类

### 按状态分类

**已接受 (Accepted)**: 6 个
- ADR-001: 分层架构设计
- ADR-002: 标准化方法
- ADR-003: 赋权方法路线图
- ADR-004: 汇总算法架构设计
- ADR-005: 加载器抽象层
- ADR-006: 敏感性分析服务重构

**提议 (Proposed)**: 3 个
- ADR-007: 区间数/模糊数 MCDA 架构设计
- ADR-008: 群决策聚合策略选择
- ADR-014: 一票否决机制架构设计

**已归档 (Archived)**: 5 个
- ADR-009-013: 版本规划调整（已归档到 [version-planning-history.md](../../active/mcda-core/version-planning-history.md)）

### 按主题分类

**架构设计** (2 个)
- ADR-001: 分层架构设计
- ADR-005: 加载器抽象层

**算法** (1 个)
- ADR-004: 汇总算法架构设计

**数据处理** (2 个)
- ADR-002: 标准化方法
- ADR-003: 赋权方法路线图

**服务** (1 个)
- ADR-006: 敏感性分析服务重构

**高级功能** (3 个)
- ADR-007: 区间数/模糊数 MCDA 架构设计
- ADR-008: 群决策聚合策略选择
- ADR-014: 一票否决机制架构设计

**版本规划** (归档)
- ADR-009-013: 版本规划调整（5个，已归档）

---

## 🔍 快速导航

### 核心架构

**新手入门**:
1. 📖 [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md) - **必读**
2. 📖 [ADR-004: 汇总算法架构设计](./004-mcda-aggregation-algorithms.md) - **必读**

**数据流**:
1. [ADR-002: 标准化方法](./002-mcda-normalization-methods.md)
2. [ADR-003: 赋权方法路线图](./003-mcda-weighting-roadmap.md)
3. [ADR-005: 加载器抽象层](./005-loader-abstract-layer.md)

**服务**:
1. [ADR-006: 敏感性分析服务重构](./006-sensitivity-service-refactoring.md)

### 高级功能

**不确定性决策**:
1. 📋 [ADR-007: 区间数/模糊数 MCDA](./007-interval-fuzzy-mcda-architecture.md) - v0.5-v0.7

**群决策**:
1. 📋 [ADR-008: 群决策聚合策略](./008-group-decision-aggregation-strategy.md) - v0.5-v0.6

**约束系统**:
1. 📋 [ADR-014: 一票否决机制](./014-veto-mechanism.md) - v0.10

### 版本规划

**版本规划历史**:
1. 📜 [版本规划历史](../active/mcda-core/version-planning-history.md) - 统一的历史记录（包含 ADR-009 ~ 013）

**路线图**:
1. 📋 [完整路线图](../plans/mcda-core/roadmap-complete.md) - v0.1 → v1.0

---

## 📝 ADR 模板

新 ADR 请使用以下模板:

```markdown
# ADR-XXX: [标题]

## 状态
**提议 (Proposed)** / **已接受 (Accepted)** / **已弃用 (Deprecated)** / **已替代 (Superseded)**

## 日期
YYYY-MM-DD

## 上下文 (Context)
[描述当前情况,面临的问题或挑战]

## 决策 (Decision)
[详细说明决策内容,包括技术方案、实现方式等]

## 权衡分析 (Trade-offs)
[分析不同方案的优缺点,解释为什么做出这个决策]

## 后果 (Consequences)
[说明决策带来的正面和负面影响,以及缓解措施]

## 参考资料
[相关文档链接]
```

---

## 🔄 ADR 生命周期

1. **提议 (Proposed)**: 初始提案,待审查
2. **已接受 (Accepted)**: 已批准并实施
3. **已弃用 (Deprecated)**: 不再推荐,但仍在使用
4. **已替代 (Superseded)**: 已被新 ADR 替代

---

## 📈 统计信息

**总 ADR 数**: 14 个（9 个活跃 + 5 个归档）

**活跃 ADR 按状态**:
- ✅ 已接受: 6 个 (67%)
- 📋 提议: 3 个 (33%)

**归档 ADR**:
- 版本规划调整: 5 个 (ADR-009 ~ 013)

**按主题分类**:
- 架构设计: 2 个
- 算法: 1 个
- 数据处理: 2 个
- 服务: 1 个
- 高级功能: 3 个（含一票否决）

---

## 🔗 相关文档

### 规划文档
- [v0.5-v1.0 版本路线图](../plans/mcda-core/roadmap-v0.5-to-v1.0.md)

### 进度文档
- [v0.4 进度总结](../active/mcda-core/v0.4/progress-summary.md)

### 决策文档
- [ADR 索引 (本文件)](./README.md)

---

**维护者**: hunkwk + AI
**最后更新**: 2026-02-05
**下次审查**: v0.10 完成后
