# MCDA Core v0.6 执行计划

**创建日期**: 2026-02-03
**最后更新**: 2026-02-03 (架构审查后调整)
**状态**: ✅ 已批准
**预计工期**: 17 人日 (3.5 周)
**Git 分支**: feature/mcda-core

---

## 📋 变更历史

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-02-03 | v1.0 | 初始版本 |
| 2026-02-03 | v1.1 | 架构审查后调整：工期17人日，65个测试，数据模型优化 |

---

## 1. 需求重述

### 1.1 核心需求

根据 roadmap-complete.md、ADR-008 和架构审查建议，v0.6 包含以下功能：

| 优先级 | 功能 | 工期 | 说明 |
|--------|------|------|------|
| **P1** | **群决策基础** | 6人日 | 多决策者支持（ADR-008） |
| **P2** | **PCA 主成分分析** | 4人日 | 客观赋权方法 |
| **P3** | **高级聚合方法** | 2人日 | Borda、Copeland 等 |
| **P3** | **德尔菲法（简化）** | 2人日 | 基础多轮专家咨询 |

**总工期**: 14 人日(核心) + 3 人日(测试文档) = **17 人日**

### 1.2 架构改进（基于架构审查）

#### 新增模块

```
lib/
├── aggregation/              # 新增：聚合服务模块
│   ├── __init__.py
│   ├── base.py              # AggregationMethod 抽象基类
│   ├── weighted_average.py  # 加权平均聚合
│   ├── weighted_geometric.py # 加权几何平均
│   ├── borda_count.py       # Borda 计数法
│   └── copeland.py          # Copeland 方法
│
├── group/                    # 新增：群决策模块
│   ├── __init__.py
│   ├── models.py            # DecisionMaker, GroupDecisionProblem
│   ├── service.py           # GroupDecisionService
│   └── consensus.py         # 共识度测量
│
└── weighting/
    └── pca_weighting.py     # 新增：PCA 赋权
```

#### 数据模型优化

**改进 1**: `GroupDecisionProblem` 不再组合 `DecisionProblem`
```python
@dataclass(frozen=True)
class GroupDecisionProblem:
    """群决策问题（独立于 DecisionProblem）"""
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    decision_makers: tuple[DecisionMaker, ...]
    individual_scores: dict[str, dict[str, dict[str, float]]]
    aggregation_config: AggregationConfig | None = None

    def to_decision_problem(self, aggregation_method) -> DecisionProblem:
        """转换为单决策者问题"""
        ...
```

**改进 2**: `DelphiProcess` 改为非冻结类
```python
class DelphiProcess:
    """德尔菲法过程管理器（可变状态）"""
    def __init__(self, ...):
        self._rounds: list[DelphiRound] = []

    def add_round(self, scores: dict) -> DelphiRound:
        """添加新轮次，返回不可变记录"""
        ...
```

### 1.3 验收标准

**功能完整性**:
- [ ] 群决策数据模型实现（独立设计）
- [ ] 聚合服务模块实现（4种方法）
- [ ] 共识度测量机制实现
- [ ] PCA 赋权算法实现（含准则限制）
- [ ] 德尔菲法基础流程实现

**质量指标**:
- [ ] 测试覆盖率 >= 80%
- [ ] 所有测试通过
- [ ] 代码质量 >= 4 星
- [ ] 文档完整

**性能指标**:
- [ ] 群决策执行时间 < 2 秒
- [ ] PCA 执行时间 < 1 秒
- [ ] 德尔菲法单轮执行时间 < 0.5 秒

---

## 2. 分阶段计划

### Phase 1: 群决策基础 (6 人日, 1.5 周)

**复杂度**: High
**依赖**: ADR-008
**工期调整理由**: 数据模型优化，新增聚合服务模块

#### 数据模型

```python
@dataclass(frozen=True)
class DecisionMaker:
    """决策者"""
    id: str
    name: str
    weight: float = 1.0
    expertise: dict[str, float] | None = None

@dataclass(frozen=True)
class GroupDecisionProblem:
    """群决策问题（独立于 DecisionProblem）"""
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    decision_makers: tuple[DecisionMaker, ...]
    individual_scores: dict[str, dict[str, dict[str, float]]]
    aggregation_config: AggregationConfig | None = None

    def to_decision_problem(self, aggregation_method) -> DecisionProblem:
        """转换为单决策者问题"""
        aggregated_scores = aggregation_method.aggregate(
            self.individual_scores,
            self.decision_makers
        )
        return DecisionProblem(
            alternatives=self.alternatives,
            criteria=self.criteria,
            scores=aggregated_scores
        )

@dataclass(frozen=True)
class AggregationConfig:
    """聚合配置"""
    score_aggregation: Literal[
        "weighted_average",
        "weighted_geometric",
        "borda_count",
        "copeland",
    ] = "weighted_average"
    consensus_strategy: Literal[
        "none", "threshold", "feedback"
    ] = "none"
    consensus_threshold: float = 0.7
```

#### 实施步骤

**Day 1-2: RED - 编写测试**
- DecisionMaker 数据模型测试 (4 个)
- GroupDecisionProblem 数据模型测试 (6 个)
- 验证逻辑测试 (4 个)
- AggregationConfig 测试 (2 个)

**Day 3: GREEN - 实现数据模型**
- 创建 `lib/group/` 目录
- 实现 DecisionMaker 类
- 实现 GroupDecisionProblem 类（独立设计）
- 实现 AggregationConfig 类
- 实现验证逻辑

**Day 4: GREEN - 创建聚合服务模块**
- 创建 `lib/aggregation/` 目录
- 实现 AggregationMethod 抽象基类
- 实现注册机制
- 实现加权平均聚合
- 实现共识度测量

**Day 5: GREEN - 实现群决策服务**
- 实现 GroupDecisionService
- 实现 to_decision_problem 转换
- 实现共识度测量

**Day 6: REFACTOR - 优化**
- 代码结构优化
- 添加文档
- 测试覆盖率 >= 85%

**验收标准**:
- [ ] 18 个测试全部通过
- [ ] 测试覆盖率 >= 85%
- [ ] 执行时间 < 0.5 秒

---

### Phase 2: PCA 主成分分析 (4 人日, 1 周)

**复杂度**: High

#### 数学模型

```
1. 标准化决策矩阵
   z_ij = (x_ij - μ_j) / σ_j

2. 计算协方差矩阵
   C = X^T · X / (n-1)

3. 特征值分解
   C · v_k = λ_k · v_k

4. 提取主成分权重
   w_j = Σ λ_k · v_kj² / Σ λ_k
```

#### 数值稳定性措施

```python
# 使用 np.linalg.eigh（对称矩阵专用，更稳定）
eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

# 添加正则化避免数值不稳定
covariance_matrix += np.eye(n_criteria) * epsilon

# 准则数量限制
MAX_CRITERIA = 50
if n_criteria > MAX_CRITERIA:
    raise ValueError(f"PCA 不支持超过 {MAX_CRITERIA} 个准则")
```

#### 实施步骤

**Day 1: RED - 编写测试**
- 基础功能测试 (6 个)
- 数学正确性测试 (4 个)
- 边界条件测试 (3 个)
- 错误处理测试 (2 个)

**Day 2: GREEN - 实现核心算法**
- 实现 PCAWeighting 类
- 实现标准化逻辑
- 实现协方差矩阵计算（含正则化）
- 实现特征值分解（使用 eigh）

**Day 3: GREEN - 实现权重提取**
- 实现主成分权重提取
- 实现主成分选择策略（累积方差 >= 85%）
- 添加准则数量限制（MAX_CRITERIA = 50）
- 添加输入验证

**Day 4: REFACTOR - 优化**
- 数值稳定性优化
- 性能优化（numpy 向量化）
- 添加文档和示例

**验收标准**:
- [ ] 15 个测试全部通过
- [ ] 测试覆盖率 >= 80%
- [ ] 执行时间 < 1 秒
- [ ] 准则数 > 50 时发出警告

---

### Phase 3: 高级聚合方法 (2 人日, 0.5 周)

**复杂度**: Medium
**依赖**: Phase 1 (聚合服务模块)

#### 实施步骤

**Day 1: RED + GREEN - 实现高级聚合**
- 加权几何平均聚合（3个测试 + 实现）
  - 使用对数域计算避免溢出
- Borda 计数法（3个测试 + 实现）
- Copeland 方法（3个测试 + 实现）
- 阈值共识检查（3个测试 + 实现）

**Day 2: REFACTOR - 优化**
- 性能优化（numpy 向量化）
- 添加文档
- 边界条件测试

**验收标准**:
- [ ] 12 个测试全部通过
- [ ] 测试覆盖率 >= 80%

---

### Phase 4: 德尔菲法（简化） (2 人日, 0.5 周)

**复杂度**: Medium
**依赖**: Phase 1 (GroupDecisionProblem)
**工期调整理由**: 简化实现，降低优先级到 P3

#### 数据模型

```python
@dataclass(frozen=True)
class DelphiRound:
    """德尔菲法轮次（不可变记录）"""
    round_number: int
    scores: dict[str, dict[str, dict[str, float]]]
    statistics: dict[str, dict[str, dict[str, float]]]
    convergence_score: float

class DelphiProcess:
    """德尔菲法过程管理器（可变状态）"""

    def __init__(
        self,
        initial_problem: GroupDecisionProblem,
        max_rounds: int = 3,
        convergence_threshold: float = 0.05
    ):
        self.initial_problem = initial_problem
        self.max_rounds = max_rounds
        self.convergence_threshold = convergence_threshold
        self._rounds: list[DelphiRound] = []

    def add_round(self, scores: dict) -> DelphiRound:
        """添加新轮次，返回不可变记录"""
        round_num = len(self._rounds) + 1
        statistics = self._calculate_statistics(scores)
        convergence = self._check_convergence(scores)

        new_round = DelphiRound(
            round_number=round_num,
            scores=scores,
            statistics=statistics,
            convergence_score=convergence
        )
        self._rounds.append(new_round)
        return new_round

    @property
    def rounds(self) -> tuple[DelphiRound, ...]:
        """获取所有轮次（返回不可变副本）"""
        return tuple(self._rounds)
```

#### 实施步骤

**Day 1: RED + GREEN - 实现基础功能**
- DelphiRound 数据模型测试 (2 个) + 实现
- DelphiProcess 管理器测试 (3 个) + 实现
- 统计摘要测试 (2 个) + 实现
- 收敛检查测试 (1 个) + 实现

**Day 2: REFACTOR - 集成**
- 与群决策集成
- 添加文档和示例
- 简化工作流

**验收标准**:
- [ ] 8 个测试全部通过
- [ ] 测试覆盖率 >= 85%
- [ ] 执行时间 < 0.5 秒/轮

---

### Phase 5: 集成测试与文档 (3 人日, 0.5 周)

**复杂度**: Low
**工期调整理由**: 增加集成测试覆盖

#### 实施步骤

**Day 1-2: 集成测试**
- 群决策 + PCA 赋权集成测试 (3 个)
- 群决策 + 所有聚合方法集成测试 (3 个)
- 群决策 + 德尔菲法集成测试 (2 个)
- 端到端 YAML 配置测试 (2 个)
- 多算法对比测试 (2 个)

**Day 3: 文档编写**
- API 文档更新
- 用户指南
- 示例代码
- CHANGELOG
- 架构说明（新增模块）

**验收标准**:
- [ ] 12 个集成测试全部通过
- [ ] 文档完整
- [ ] 所有性能指标达标

---

## 3. 依赖关系

```
Phase 1: 群决策基础 (无依赖)
    ├─ 创建 lib/aggregation/ 模块
    └─ 创建 lib/group/ 模块
        ↓
Phase 2: PCA 赋权 (无依赖，可与 Phase 1 并行)
    └─ 扩展 lib/weighting/
        ↓
Phase 3: 高级聚合方法 (依赖 Phase 1 - 聚合服务模块)
    └─ 扩展 lib/aggregation/
        ↓
Phase 4: 德尔菲法（依赖 Phase 1 - GroupDecisionProblem）
    └─ 扩展 lib/group/
        ↓
Phase 5: 集成测试与文档 (依赖所有前置)
```

**关键路径**: Phase 1 → Phase 3 → Phase 4 → Phase 5 (11 人日)

**并行机会**:
- Phase 2 (PCA) 可以与 Phase 1 并行开发
- 总工期可压缩到 15 人日（如果并行开发）

---

## 4. 测试计划

### 测试数量

| Phase | 功能 | 测试数 | 调整 |
|-------|------|--------|------|
| Phase 1 | 群决策基础 | 18 | +4 (增加聚合方法测试) |
| Phase 2 | PCA 赋权 | 15 | 保持 |
| Phase 3 | 高级聚合方法 | 12 | +4 (增加边界条件测试) |
| Phase 4 | 德尔菲法（简化） | 8 | -4 (简化实现) |
| Phase 5 | 集成测试 | 12 | +2 (增加集成测试) |
| **总计** | | **65** | +6 |

**v0.6 总测试数**: 295 (v0.5: 230 + v0.6: 65)

### 测试分类

| 类别 | 比例 | 数量 |
|------|------|------|
| 基础功能 | 35% | 23 |
| 详细功能 | 30% | 20 |
| 边界条件 | 20% | 13 |
| 错误处理 | 10% | 7 |
| 集成测试 | 5% | 2 |

---

## 5. 风险与缓解

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| PCA 特征值分解数值不稳定 | 中 | 高 | ✅ 使用 numpy.linalg.eigh，添加正则化 |
| 群决策数据模型复杂度高 | 低 | 中 | ✅ 独立设计 GroupDecisionProblem |
| 加权几何平均溢出 | 低 | 中 | ✅ 使用对数域计算 |
| 协方差矩阵奇异 | 中 | 高 | ✅ 添加 epsilon 正则化项 |
| 高级聚合方法性能问题 | 低 | 低 | ✅ 优化算法，numpy 向量化 |
| 德尔菲法状态管理混乱 | 中 | 中 | ✅ 使用不可变记录，分离状态 |

### 进度风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Phase 1 工作量低估 | 低 | 高 | ✅ 已增加 1 人日（5→6） |
| Phase 2 PCA 复杂度超预期 | 中 | 中 | ✅ 添加准则数量限制，参考 sklearn |
| 集成测试时间不足 | 低 | 中 | ✅ 已增加 1 人日（2→3） |
| 聚合方法边界条件遗漏 | 中 | 低 | ✅ Phase 3 增加边界条件测试 |

---

## 6. 工具链

### 测试工具

```bash
# 运行测试
pytest tests/mcda-core/ -v

# 测试覆盖率
pytest tests/mcda-core/ --cov=mcda_core --cov-report=html

# 类型检查
mypy skills/mcda-core/lib/

# 代码格式化
ruff check skills/mcda-core/lib/
```

### 进度追踪

使用 `docs/active/mcda-core/v0.6/` 下的进度文件：
- `tdd-group-decision.md` - Phase 1 进度
- `tdd-pca-weighting.md` - Phase 2 进度
- `tdd-advanced-aggregation.md` - Phase 3 进度
- `tdd-delphi-method.md` - Phase 4 进度
- `progress-summary.md` - 总体进度

---

## 7. 成功标准

### 代码质量
- 测试覆盖率 >= 80%
- 所有测试通过 (pytest)
- 代码通过 linting (ruff)
- 类型检查通过 (mypy)

### 功能完整性
- 群决策基础功能正常工作（独立数据模型）
- 聚合服务模块正常工作（4种方法）
- PCA 赋权算法正常工作（含准则限制）
- 德尔菲法基础流程正常工作（简化版）
- 高级聚合方法正常工作

### 性能指标
- 群决策执行时间 < 2 秒
- PCA 执行时间 < 1 秒
- 德尔菲法单轮执行时间 < 0.5 秒
- 总测试执行时间 < 10 秒

### 架构改进
- ✅ 创建 `lib/aggregation/` 模块
- ✅ 创建 `lib/group/` 模块
- ✅ 优化 GroupDecisionProblem 数据模型
- ✅ 修改 DelphiProcess 为非冻结类
- ✅ 添加 PCA 准则数量限制

---

## 8. 下一步

**立即行动**:
1. 创建进度追踪文件 `docs/active/mcda-core/v0.6/`
2. 开始 Phase 1: 群决策基础 TDD 开发
3. 创建 `lib/aggregation/` 和 `lib/group/` 目录

**命令**:
```bash
# 开始 TDD 开发
/tdd

# 或创建进度文件
# docs/active/mcda-core/v0.6/tdd-group-decision.md
```

---

## 9. 版本对比

### v0.5 → v0.6

| 指标 | v0.5 | v0.6 (调整后) | 增长 |
|------|------|-------------|------|
| 算法数量 | 5 | 5 | - |
| 赋权方法 | 4 | 5 | +25% |
| 聚合方法 | 0 | 4 | 新增 |
| 特殊场景 | 基础 | 群决策+德尔菲（简化） | - |
| 测试数量 | 230 | 295 | +28% |
| 代码行数 | ~3500 | ~4500 | +29% |
| 模块数量 | 6 | 8 | +33% |

### 新增功能

| 功能 | v0.5 | v0.6 | 说明 |
|------|------|------|------|
| 群决策支持 | ❌ | ✅ | 独立数据模型 |
| 聚合服务模块 | ❌ | ✅ | 4种方法 |
| 共识度测量 | ❌ | ✅ | 基础实现 |
| PCA 赋权 | ❌ | ✅ | 含准则限制 |
| 德尔菲法 | ❌ | 🟡 | 简化版 |
| 高级聚合方法 | ❌ | ✅ | Borda、Copeland |

### 新增模块

| 模块 | 说明 |
|------|------|
| `lib/aggregation/` | 聚合服务模块（4种方法） |
| `lib/group/` | 群决策模块（数据模型+服务） |
| `lib/weighting/pca_weighting.py` | PCA 赋权 |

---

## 10. 架构改进摘要

基于架构审查（2026-02-03），v0.6 计划采纳以下改进：

### 立即实施
- ✅ 创建聚合服务模块 `lib/aggregation/`
- ✅ 创建群决策模块 `lib/group/`
- ✅ 优化 GroupDecisionProblem（独立设计）
- ✅ 修改 DelphiProcess（非冻结类）
- ✅ 添加 PCA 准则数量限制

### 性能优化
- ✅ 使用 np.linalg.eigh（特征值分解）
- ✅ 加权几何平均使用对数域计算
- ✅ 协方差矩阵添加正则化

### 测试增强
- ✅ 增加聚合方法边界条件测试
- ✅ 增加集成测试覆盖
- ✅ 总测试数 59 → 65

---

**文档版本**: v1.1
**创建日期**: 2026-02-03
**最后更新**: 2026-02-03
**状态**: ✅ 已批准（架构审查后调整）
**预计完成**: 2026-02-26 (3.5 周)

---

**相关文档**:
- [ADR-008: 群决策聚合策略](../../../decisions/mcda-core/008-group-decision-aggregation-strategy.md)
- [ADR-001: 分层架构设计](../../../decisions/mcda-core/001-mcda-layered-architecture.md)
- [完整路线图](../roadmap-complete.md)
- [v0.5 执行计划](../v0.5/execution-plan.md)
- [v0.6 架构分析报告](../../../checkpoints/mcda-core/checkpoint-v0.6-architecture-analysis.md)
