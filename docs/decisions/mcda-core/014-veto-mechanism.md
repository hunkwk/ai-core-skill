# ADR-014: MCDA 一票否决机制（Veto Mechanism）架构设计

## 状态
**提议 (Proposed)**

## 日期
2026-02-05

## 上下文 (Context)

### 业务需求

在实际的多准则决策分析场景中，某些关键指标具有"一票否决"的权力：

1. **供应商准入资质评估**
   - 无营业执照 → 直接排除
   - 资质等级不足 → 直接排除
   - 在黑名单中 → 直接排除
   - 财务风险过高 → 扣分惩罚

2. **项目风险评估**
   - 政策不合规 → 直接排除
   - 技术风险过高 → 分级处理（低风险接受/中风险警示/高风险拒绝）
   - 资金风险过高 → 分级处理

3. **合同风险评估**
   - 法律合规问题 → 直接排除
   - 付款条款风险 → 组合判断（周期过长 OR 预付款比例过低 → 扣分）
   - 违约责任风险 → 组合判断（高风险 AND 无保险 → 拒绝）

### 技术挑战

现有 mcda-core 架构（ADR-001）支持多种决策算法，但**不支持约束和否决机制**：

- ✅ 支持综合评分计算（WSM、TOPSIS、VIKOR 等）
- ✅ 支持权重分配和标准化
- ❌ 不支持硬约束（不满足直接排除）
- ❌ 不支持软约束（不满足扣分）
- ❌ 不支持分级约束（多档位管理）
- ❌ 不支持组合约束（AND/OR 逻辑）

**核心问题**：
1. 如何在现有架构中集成约束/否决机制？
2. 如何支持多种否决类型（硬、软、分级、组合）？
3. 如何与现有算法无缝集成？
4. 如何设计灵活的配置方式？

### 文献背景

在 MCDA 理论中，一票否决对应以下概念：

| 理论概念 | 描述 | 相关算法 |
|----------|------|----------|
| **不和谐性（Discordance）** | 当方案在某准则上表现太差时，其他准则的优异表现无法补偿 | ELECTRE 系列 |
| **否决阈值（Veto Threshold）** | 定义准则的最低可接受水平 | ELECTRE-III/IV |
| **筛选条件（Screening）** | 预先设置的条件，不满足则排除 | 筛选-排序法 |
| **硬约束（Hard Constraint）** | 必须满足的约束条件 | 线性规划 |

**现状**：
- ELECTRE-I（已实现）有相对不和谐性，但不是绝对一票否决
- ELECTRE-III/IV（未实现）有否决阈值，最接近一票否决

## 决策 (Decision)

### 核心决策

采用**独立约束服务（ConstraintService）** + **多种否决类型**的架构设计，在不修改现有算法的前提下，实现灵活的一票否决机制。

### 架构设计

#### 1. 分层集成（基于 ADR-001）

```
┌─────────────────────────────────────────────────────────────────┐
│                       核心服务层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   验证服务   │  │  报告服务   │  │   敏感性分析服务        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         ConstraintService (约束服务) ← 新增              │   │
│  │  - filter_problem(): 过滤被否决的方案                    │   │
│  │  - apply_penalties(): 应用软否决惩罚                     │   │
│  │  - get_constraint_metadata(): 获取约束元数据            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      算法抽象层                                  │
│                   ┌─────────────┐                               │
│                   │ MCDAAlgorithm│ (无需修改)                    │
│                   └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      约束模块层 (新增)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ VetoConfig  │  │VetoEvaluator│  │   VetoResult            │ │
│  │ (否决配置)   │  │ (否决评估器) │  │   (否决结果)            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**关键设计决策**：
- ✅ 不修改现有算法（算法层保持不变）
- ✅ 通过服务层集成（ConstraintService）
- ✅ 支持前置过滤（算法执行前过滤被否决的方案）
- ✅ 支持后处理（应用软否决惩罚分数）

#### 2. 支持的否决类型

| 否决类型 | 描述 | 配置复杂度 | 应用场景 |
|----------|------|------------|----------|
| **hard** 硬否决 | 不满足条件直接排除 | ⭐ 简单 | 合规性指标（法律法规） |
| **soft** 软否决 | 不满足条件扣分惩罚 | ⭐ 简单 | 风险指标（风险警示） |
| **tiered** 分级否决 | 多档位管理（低/中/高风险） | ⭐⭐ 中等 | 风险等级评估 |
| **composite** 组合否决 | 多条件组合（AND/OR 逻辑） | ⭐⭐⭐ 复杂 | 复杂业务规则 |

#### 3. 数据模型设计

```python
# 核心数据模型
@dataclass(frozen=True)
class VetoCondition:
    """否决条件"""
    operator: Literal["==", "!=", ">", ">=", "<", "<=", "in", "not_in"]
    value: Any
    action: Literal["accept", "warning", "reject"] = "warning"
    penalty_score: float = 0.0
    label: str = ""

@dataclass(frozen=True)
class VetoConfig:
    """否决配置"""
    type: Literal["hard", "soft", "tiered", "composite"]
    condition: VetoCondition | None = None           # 用于 hard/soft
    tiers: tuple[VetoTier, ...] = ()                # 用于 tiered
    conditions: tuple[VetoCondition, ...] = ()      # 用于 composite
    logic: Literal["and", "or"] = "or"              # 用于 composite
    penalty_score: float = -20.0
    reject_reason: str = "未满足否决条件"

@dataclass(frozen=True)
class VetoResult:
    """否决评估结果"""
    is_rejected: bool                    # 是否被拒绝
    is_warning: bool                     # 是否有警告
    penalty_applied: float               # 应用的惩罚分数
    reject_reasons: tuple[str, ...]      # 拒绝原因列表
    warning_labels: tuple[str, ...]      # 警告标签列表
    details: dict[str, dict[str, Any]]   # 详细结果
```

#### 4. 扩展现有模型

```python
# 扩展 Criterion 数据模型
@dataclass(frozen=True)
class Criterion:
    """评价准则（扩展版）"""
    name: str
    weight: float
    direction: Direction
    description: str = ""
    scoring_rule: ScoringRule | None = None
    column: str | None = None
    # 新增：否决配置
    veto: VetoConfig | None = None

# 扩展 DecisionResult 数据模型
@dataclass
class DecisionResult:
    """决策结果（扩展版）"""
    rankings: list[RankingItem]
    raw_scores: dict[str, float]
    metadata: ResultMetadata
    sensitivity: SensitivityResult | None = None
    # 新增：否决评估结果
    veto_results: dict[str, VetoResult] = field(default_factory=dict)
```

#### 5. 配置方式（YAML）

**硬否决示例**：
```yaml
criteria:
  - name: "营业执照"
    weight: 0.0  # 硬否决不参与加权
    direction: "higher_better"
    veto:
      type: "hard"
      condition:
        operator: "=="
        value: 1
      reject_reason: "无有效营业执照"
```

**软否决示例**：
```yaml
criteria:
  - name: "财务风险评分"
    weight: 0.25
    direction: "lower_better"
    veto:
      type: "soft"
      condition:
        operator: ">"
        value: 60
        penalty_score: -30
```

**分级否决示例**：
```yaml
criteria:
  - name: "技术风险"
    weight: 0.25
    direction: "lower_better"
    veto:
      type: "tiered"
      tiers:
        - threshold: {operator: "<=", value: 30}
          action: "accept"
          label: "低风险"
        - threshold: {operator: "<=", value: 60}
          action: "warning"
          label: "中风险"
          penalty_score: -15
        - threshold: {operator: ">", value: 60}
          action: "reject"
          label: "高风险"
          reject_reason: "技术风险过高"
```

**组合否决示例**：
```yaml
criteria:
  - name: "付款条款风险"
    weight: 0.20
    direction: "lower_better"
    veto:
      type: "composite"
      logic: "or"
      conditions:
        - operator: ">"
          value: 70
          action: "warning"
          penalty_score: -20
          label: "付款周期过长"
        - operator: "<"
          value: 30
          action: "warning"
          penalty_score: -10
          label: "预付款比例过低"
```

### 实现方案

#### 文件结构

```
skills/mcda-core/lib/
├── constraints/
│   ├── __init__.py               # 约束模块导出
│   ├── models.py                 # VetoConfig, VetoResult 等数据模型
│   ├── evaluator.py              # VetoEvaluator 评估器核心逻辑
│   └── filters.py                # 方案过滤功能
├── services/
│   └── constraint_service.py     # ConstraintService 约束服务
└── models.py                     # 扩展 Criterion 和 DecisionResult
```

#### 核心类设计

**VetoEvaluator**（否决评估器）：
```python
class VetoEvaluator:
    """否决评估器

    评估方案是否满足否决条件。
    """

    def evaluate(
        self,
        alternative: str,
        scores: dict[str, dict[str, float]],
        criteria_with_veto: dict[str, tuple]
    ) -> VetoResult:
        """评估单个方案的否决情况"""
        pass

    def _evaluate_hard(self, veto_config, score, crit_name) -> dict:
        """评估硬否决"""
        pass

    def _evaluate_soft(self, veto_config, score, crit_name) -> dict:
        """评估软否决"""
        pass

    def _evaluate_tiered(self, veto_config, score, crit_name) -> dict:
        """评估分级否决"""
        pass

    def _evaluate_composite(self, veto_config, score, crit_name) -> dict:
        """评估组合否决"""
        pass
```

**ConstraintService**（约束服务）：
```python
class ConstraintService:
    """约束服务

    处理决策问题中的约束和否决规则。
    """

    def filter_problem(
        self,
        problem: DecisionProblem
    ) -> tuple[DecisionProblem, dict[str, VetoResult]]:
        """过滤决策问题，移除被否决的方案

        Returns:
            (过滤后的决策问题, 否决结果字典)
        """
        pass

    def apply_penalties(
        self,
        problem: DecisionProblem,
        veto_results: dict[str, VetoResult]
    ) -> DecisionProblem:
        """应用软否决惩罚分数"""
        pass

    def get_constraint_metadata(
        self,
        veto_results: dict[str, VetoResult]
    ) -> ConstraintMetadata:
        """获取约束元数据"""
        pass
```

#### 集成流程

```python
# 典型使用流程
from mcda_core.services import ConstraintService
from mcda_core.algorithms import TOPSIS

# 1. 创建约束服务
constraint_service = ConstraintService()

# 2. 过滤被否决的方案（前置过滤）
filtered_problem, veto_results = constraint_service.filter_problem(problem)

# 3. 执行决策算法
algorithm = TOPSIS()
result = algorithm.calculate(filtered_problem)

# 4. 合并否决结果到决策结果
result.veto_results = veto_results

# 5. 应用软否决惩罚（可选）
result_with_penalties = constraint_service.apply_penalties(
    filtered_problem, veto_results
)
```

### 版本规划

#### 推荐版本：v0.10

**理由**：
- 一票否决是决策分析的核心功能，应在 v1.0 前完成
- Web UI 需要展示约束配置和结果
- 供应商准入、风险评估是典型企业场景

#### 工期评估

| 阶段 | 功能 | 工期 | 优先级 |
|------|------|------|--------|
| **Phase 1** | 硬否决 | 1.5人日 | P0 |
| **Phase 2** | 软否决 | 1人日 | P0 |
| **Phase 3** | 分级否决 | 1.5人日 | P1 |
| **Phase 4** | 组合否决 | 1.5人日 | P2 |
| **Phase 5** | 集成与测试 | 0.5人日 | P0 |
| **总计** | - | **6人日** | - |

**建议**：先实现 Phase 1-2（硬否决 + 软否决），满足 80% 的需求。

## 权衡分析 (Trade-offs)

### 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **方案1: 独立约束服务** | 不修改现有算法，易于扩展，职责清晰 | 增加一层抽象，轻微性能开销 | ⭐⭐⭐⭐⭐ |
| 方案2: 修改每个算法 | 深度集成，性能最优 | 修改量大，风险高，难以维护 | ⭐⭐ |
| 方案3: 算法包装器 | 比方案2简单 | 仍然需要修改每个算法的调用点 | ⭐⭐⭐ |
| 方案4: 后处理过滤器 | 实现简单 | 浪费计算（被否决的方案仍参与算法） | ⭐⭐⭐ |

**选择方案1的理由**：
1. **不修改现有算法**：降低风险，保持算法层稳定性
2. **职责分离**：约束逻辑独立，易于测试和维护
3. **可扩展性**：未来新增否决类型无需修改算法
4. **性能可接受**：评估逻辑简单，O(n) 复杂度

### 技术权衡

#### 权重处理

**问题**：一票否决的准则是否需要权重？

| 选项 | 描述 | 推荐处理 |
|------|------|----------|
| **权重为 0** | 硬否决准则不参与加权计算 | ✅ 推荐（合规性指标） |
| **保留权重** | 准则仍参与非否决方案的计算 | ✅ 可选（风险指标） |

**决策**：允许配置权重，但硬否决准则通常权重为 0。

#### 执行时机

**问题**：否决检查在算法执行前还是后？

| 选项 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **前置过滤** | 避免无效计算，性能好 | 可能所有方案都被否决 | ✅ 推荐 |
| **后处理** | 保留所有方案信息 | 浪费计算 | ⚠️ 可选 |

**决策**：默认前置过滤，提供后处理选项。

#### 组合逻辑

**问题**：多个否决条件的逻辑关系？

| 选项 | 描述 | 应用场景 |
|------|------|----------|
| **OR 逻辑** | 任一条件满足即触发 | 大多数场景 |
| **AND 逻辑** | 所有条件都满足才触发 | 严格场景 |
| **自定义** | 复杂表达式（A OR B）AND C | 高级场景 |

**决策**：支持 OR/AND，未来可扩展自定义逻辑。

## 后果 (Consequences)

### 正面影响

1. **功能完整性**
   - 支持企业级决策场景（供应商准入、风险评估）
   - 满足合规性和风险控制需求
   - 提升mcda-core 的实用性

2. **架构优势**
   - 不修改现有算法，保持稳定性
   - 职责分离，易于测试和维护
   - 可扩展性好，支持未来需求

3. **用户体验**
   - YAML 配置灵活，适应多种场景
   - 支持渐进式采用（先用硬否决，再用软否决）
   - 结果展示清晰（被否决的方案及原因）

4. **理论对齐**
   - 对齐 MCDA 理论（ELECTRE 不和谐性）
   - 支持学术研究和教学

### 负面影响

1. **性能开销**
   - 否决评估增加计算时间
   - **缓解**：评估逻辑简单，O(n) 复杂度，影响可忽略

2. **配置复杂度**
   - 多种否决类型增加学习成本
   - **缓解**：提供配置模板和向导，充分文档化

3. **维护成本**
   - 新增代码需要维护
   - **缓解**：职责清晰，单元测试覆盖，易于维护

4. **向后兼容性**
   - 旧配置文件可能需要升级
   - **缓解**：veto 字段可选，默认为 None，完全兼容

### 风险和缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 配置错误导致意外否决 | 高 | 中 | 提供配置验证，充分测试 |
| 性能问题 | 中 | 低 | 性能测试，优化评估逻辑 |
| 与现有算法不兼容 | 中 | 低 | 通过服务层隔离，充分集成测试 |
| 用户理解困难 | 中 | 中 | 提供示例和文档，配置向导 |

## 实施计划

### Phase 1: 基础架构（0.5人日）
- [ ] 创建 constraints/ 目录
- [ ] 实现 VetoConfig, VetoCondition, VetoResult 数据模型
- [ ] 编写单元测试

### Phase 2: 硬否决（1.5人日）
- [ ] 实现 VetoEvaluator._evaluate_hard()
- [ ] 实现 ConstraintService.filter_problem()
- [ ] 扩展 Criterion 模型（添加 veto 字段）
- [ ] CLI 集成和测试
- [ ] 编写文档和示例

### Phase 3: 软否决（1人日）
- [ ] 实现 VetoEvaluator._evaluate_soft()
- [ ] 实现 ConstraintService.apply_penalties()
- [ ] 集成测试和文档

### Phase 4: 分级否决（1.5人日）
- [ ] 实现 VetoTier 数据模型
- [ ] 实现 VetoEvaluator._evaluate_tiered()
- [ ] 测试和文档

### Phase 5: 组合否决（1.5人日）
- [ ] 实现 VetoEvaluator._evaluate_composite()
- [ ] 支持 AND/OR 逻辑
- [ ] 测试和文档

### 总计：6人日

## 参考资料

### 相关 ADR
- [ADR-001: MCDA Core 分层架构设计](./001-mcda-layered-architecture.md) - 架构基础
- [ADR-004: MCDA 汇总算法架构设计](./004-mcda-aggregation-algorithms.md) - 算法层
- [ADR-007: 区间数/模糊数 MCDA 架构设计](./007-interval-fuzzy-mcda-architecture.md) - 不确定性决策

### MCDA 理论
- ELECTRE 方法系列（ELECTRE-I, II, III, IV）
- Roy, B. (1968). "Classement et choix en présence de points de vue multiples"
- Figueira, J. et al. (2005). "Multiple Criteria Decision Analysis: State of the Art Surveys"

### 应用场景
- 供应商评估：政府采购、企业采购
- 项目评估：立项评审、投资决策
- 风险评估：贷款审批、合同评审

---

**起草人**: Claude Sonnet 4.5 (Architect Agent)
**状态**: 📋 提议 (Proposed)
**审查**: 待用户确认
**计划版本**: v0.10
