# ADR-008: 群决策聚合策略选择

## 状态
**已接受**

## 日期
2026-02-03
**实施完成**: 2026-02-04 (v0.6)
**架构审查**: 2026-02-06

## 上下文 (Context)

群决策(Group Decision Making, GDM)是多准则决策分析的重要扩展。在实际决策中,往往需要**多个决策者**共同参与,每个决策者可能有不同的:
- **专业知识背景**
- **价值偏好**
- **风险态度**
- **信息来源**

### 群决策场景

**典型应用**:
1. **企业战略决策**: 董事会成员投票
2. **项目评审**: 专家委员会评分
3. **公共政策制定**: 多方利益相关者协商
4. **医疗诊断**: 多位医生会诊

### 核心挑战

**技术挑战**:
1. **决策者权重**: 如何根据专家可信度赋权?
2. **偏好聚合**: 如何整合多个决策者的评分?
3. **共识达成**: 如何处理意见分歧?
4. **公平性**: 如何避免少数人被忽视?

**架构挑战**:
1. 如何扩展现有数据模型支持多决策者?
2. 如何设计灵活的聚合策略?
3. 如何保证聚合结果的合理性?

---

## 决策 (Decision)

### 1. 群决策数据模型

#### 1.1 决策者定义

```python
@dataclass(frozen=True)
class DecisionMaker:
    """决策者"""
    id: str
    name: str
    weight: float = 1.0  # 决策者权重(默认平等)
    expertise: dict[str, float] | None = None  # 领域专长 {criterion: score}

    def __post_init__(self):
        if self.weight <= 0:
            raise ValueError(f"DecisionMaker weight must be positive: {self.weight}")

        # 验证专长分数
        if self.expertise:
            for crit, score in self.expertise.items():
                if not 0 <= score <= 1:
                    raise ValueError(f"Expertise score must be in [0,1]: {crit}={score}")
```

#### 1.2 群决策问题

```python
@dataclass(frozen=True)
class GroupDecisionProblem:
    """群决策问题"""
    # 基础决策信息
    base_problem: DecisionProblem

    # 决策者信息
    decision_makers: list[DecisionMaker]

    # 决策者评分: {decision_maker_id: {alternative: {criterion: score}}}
    individual_scores: dict[str, dict[str, dict[str, float]]]

    # 聚合配置
    aggregation_config: AggregationConfig | None = None

    def validate(self) -> ValidationResult:
        """验证群决策数据"""
        # 1. 检查决策者权重归一化
        total_weight = sum(dm.weight for dm in self.decision_makers)
        if not abs(total_weight - 1.0) < 1e-6:
            return ValidationResult(
                is_valid=False,
                errors=[f"DecisionMaker weights must sum to 1.0, got {total_weight}"]
            )

        # 2. 检查评分完整性
        for dm_id, scores in self.individual_scores.items():
            for alt in self.base_problem.alternatives:
                if alt not in scores:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Missing scores for decision maker {dm_id}, alternative {alt}"]
                    )

        return ValidationResult(is_valid=True)
```

#### 1.3 聚合配置

```python
@dataclass(frozen=True)
class AggregationConfig:
    """聚合配置"""
    # 评分聚合方法
    score_aggregation: Literal[
        "weighted_average",  # 加权平均
        "weighted_geometric",  # 加权几何平均
        " borda_count",  # Borda 计数
        "copeland",  # Copeland 方法
        "majority",  # 多数原则
    ] = "weighted_average"

    # 共识达成策略
    consensus_strategy: Literal[
        "none",  # 不检查共识
        "threshold",  # 阈值检查
        "feedback",  # 反馈调整
    ] = "none"

    # 共识阈值(0-1, 越高要求共识度越高)
    consensus_threshold: float = 0.7

    # 冲突解决策略
    conflict_resolution: Literal[
        "ignore",  # 忽略冲突
        "delphi",  # 德尔菲法多轮调整
        "moderator",  # 协调人裁决
    ] = "ignore"
```

---

### 2. 评分聚合方法

#### 2.1 加权平均法 (Weighted Average)

**适用场景**: 决策者平等或权重明确

**公式**:
```
x_ij^agg = Σ (w_k × x_ijk) / Σ w_k
```

其中:
- x_ij^agg = 方案 i 在准则 j 的聚合评分
- w_k = 决策者 k 的权重
- x_ijk = 决策者 k 对方案 i 在准则 j 的评分

**实现**:
```python
def weighted_average_aggregation(
    problem: GroupDecisionProblem
) -> DecisionProblem:
    """加权平均聚合"""

    aggregated_scores = {}

    for alt in problem.base_problem.alternatives:
        aggregated_scores[alt] = {}

        for crit in problem.base_problem.criteria:
            # 收集所有决策者对该方案在该准则的评分
            scores = []
            weights = []

            for dm in problem.decision_makers:
                score = problem.individual_scores[dm.id][alt][crit.name]
                weight = dm.weight

                scores.append(score)
                weights.append(weight)

            # 加权平均
            avg_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
            aggregated_scores[alt][crit.name] = avg_score

    return DecisionProblem(
        alternatives=problem.base_problem.alternatives,
        criteria=problem.base_problem.criteria,
        weights=problem.base_problem.weights,
        scores=aggregated_scores,
    )
```

**优点**:
- 简单直观
- 计算高效
- 公平(考虑权重)

**缺点**:
- 容易受极端值影响
- 不考虑共识度

#### 2.2 加权几何平均法 (Weighted Geometric)

**适用场景**: 强调共识,惩罚低分

**公式**:
```
x_ij^agg = Π (x_ijk ^ w_k) ^ (1 / Σ w_k)
```

**实现**:
```python
def weighted_geometric_aggregation(
    problem: GroupDecisionProblem
) -> DecisionProblem:
    """加权几何平均聚合"""

    aggregated_scores = {}

    for alt in problem.base_problem.alternatives:
        aggregated_scores[alt] = {}

        for crit in problem.base_problem.criteria:
            product = 1.0
            total_weight = 0.0

            for dm in problem.decision_makers:
                score = problem.individual_scores[dm.id][alt][crit.name]
                weight = dm.weight

                # 避免 0 值
                score = max(score, 1e-10)

                product *= score ** weight
                total_weight += weight

            geo_score = product ** (1 / total_weight)
            aggregated_scores[alt][crit.name] = geo_score

    return DecisionProblem(
        alternatives=problem.base_problem.alternatives,
        criteria=problem.base_problem.criteria,
        weights=problem.base_problem.weights,
        scores=aggregated_scores,
    )
```

**优点**:
- 强调共识
- 惩罚极端低分("短板效应")

**缺点**:
- 对 0 值敏感
- 计算复杂度略高

#### 2.3 Borda 计数法 (Borda Count)

**适用场景**: 排序型决策,强调相对排名

**公式**:
```
Borda_ijk = n - rank_ijk  # n = 方案数量
x_ij^agg = Σ (w_k × Borda_ijk) / Σ w_k
```

**实现**:
```python
def borda_count_aggregation(
    problem: GroupDecisionProblem
) -> DecisionProblem:
    """Borda 计数聚合"""

    aggregated_scores = {}

    for alt in problem.base_problem.alternatives:
        aggregated_scores[alt] = {}

        for crit in problem.base_problem.criteria:
            borda_scores = []
            weights = []

            # 对每个决策者,计算 Borda 分数
            for dm in problem.decision_makers:
                # 收集该决策者对所有方案在该准则的评分
                all_scores = {
                    a: problem.individual_scores[dm.id][a][crit.name]
                    for a in problem.base_problem.alternatives
                }

                # 排序(从高到低)
                sorted_alts = sorted(
                    all_scores.keys(),
                    key=lambda a: all_scores[a],
                    reverse=True
                )

                # 计算 Borda 分数
                rank = sorted_alts.index(alt)
                borda = len(problem.base_problem.alternatives) - rank

                borda_scores.append(borda)
                weights.append(dm.weight)

            # 加权平均 Borda 分数
            avg_borda = sum(b * w for b, w in zip(borda_scores, weights)) / sum(weights)
            aggregated_scores[alt][crit.name] = avg_borda

    return DecisionProblem(
        alternatives=problem.base_problem.alternatives,
        criteria=problem.base_problem.criteria,
        weights=problem.base_problem.weights,
        scores=aggregated_scores,
    )
```

**优点**:
- 基于排序,不受评分尺度影响
- 减少策略性投票

**缺点**:
- 丢失评分绝对信息
- 计算复杂

#### 2.4 Copeland 方法

**适用场景**: 需要考虑方案间的支配关系

**逻辑**:
- 对每对方案 (A, B),统计多数决策者偏好
- Copeland 分数 = 净胜场数

**实现**:
```python
def copeland_aggregation(
    problem: GroupDecisionProblem
) -> DecisionProblem:
    """Copeland 方法聚合"""

    # 计算每对方案的 Copeland 分数
    copeland_scores = {alt: 0 for alt in problem.base_problem.alternatives}

    for alt_a in problem.base_problem.alternatives:
        for alt_b in problem.base_problem.alternatives:
            if alt_a == alt_b:
                continue

            wins = 0
            for dm in problem.decision_makers:
                score_a = problem.individual_scores[dm.id][alt_a][crit.name]
                score_b = problem.individual_scores[dm.id][alt_b][crit.name]

                if score_a > score_b:
                    wins += dm.weight
                elif score_a < score_b:
                    wins -= dm.weight

            if wins > 0:
                copeland_scores[alt_a] += 1
            elif wins < 0:
                copeland_scores[alt_a] -= 1

    # 转换为评分(归一化到 [0, 1])
    min_score = min(copeland_scores.values())
    max_score = max(copeland_scores.values())

    normalized_scores = {}
    for alt, score in copeland_scores.items():
        if max_score == min_score:
            normalized_scores[alt] = 0.5
        else:
            normalized_scores[alt] = (score - min_score) / (max_score - min_score)

    return DecisionProblem(
        alternatives=problem.base_problem.alternatives,
        criteria=problem.base_problem.criteria,
        weights=problem.base_problem.weights,
        scores={alt: {crit: normalized_scores[alt] for crit in problem.base_problem.criteria}},
    )
```

---

### 3. 共识达成策略

#### 3.1 共识度测量

**定义**:
```
Consensus = 1 - (1 / (n × m)) Σ Σ |x_ijk - x_ij^agg|
```

其中:
- n = 方案数量
- m = 决策者数量
- x_ij^agg = 聚合评分

**实现**:
```python
def measure_consensus(
    problem: GroupDecisionProblem,
    aggregated: DecisionProblem
) -> float:
    """测量共识度(0-1)"""

    total_deviation = 0.0
    count = 0

    for alt in problem.base_problem.alternatives:
        for crit in problem.base_problem.criteria:
            agg_score = aggregated.scores[alt][crit.name]

            for dm in problem.decision_makers:
                dm_score = problem.individual_scores[dm.id][alt][crit.name]
                deviation = abs(dm_score - agg_score)

                # 归一化偏差(假设评分范围 [0, 100])
                normalized_dev = deviation / 100.0
                total_deviation += normalized_dev
                count += 1

    consensus = 1 - (total_deviation / count)
    return max(0, min(1, consensus))  # 限制在 [0, 1]
```

#### 3.2 阈值检查策略

**逻辑**:
1. 计算共识度
2. 如果共识度 < 阈值,发出警告
3. 决策者选择:
   - 接受低共识结果
   - 重新讨论评分
   - 使用德尔菲法多轮调整

**实现**:
```python
def threshold_consensus_check(
    problem: GroupDecisionProblem,
    aggregated: DecisionProblem,
    threshold: float = 0.7
) -> ValidationResult:
    """阈值共识检查"""

    consensus = measure_consensus(problem, aggregated)

    if consensus < threshold:
        return ValidationResult(
            is_valid=False,
            errors=[
                f"Low consensus: {consensus:.2f} < {threshold}",
                "Consider:",
                "1. Re-evaluating controversial scores",
                "2. Using Delphi method for multiple rounds",
                "3. Accepting the result despite disagreement"
            ]
        )

    return ValidationResult(is_valid=True)
```

#### 3.3 德尔菲法多轮调整

**流程**:
1. **第一轮**: 收集初始评分
2. **反馈**: 提供匿名统计摘要(均值,中位数,四分位数)
3. **第二轮**: 决策者根据反馈调整评分
4. **收敛检查**: 重复步骤 2-3 直到共识达成

**数据模型**:
```python
@dataclass(frozen=True)
class DelphiRound:
    """德尔菲法轮次"""
    round_number: int
    scores: dict[str, dict[str, dict[str, float]]]  # {dm_id: {alt: {crit: score}}}
    statistics: dict[str, dict[str, dict[str, dict]]]  # 统计摘要

@dataclass(frozen=True)
class DelphiProcess:
    """德尔菲法过程"""
    initial_problem: GroupDecisionProblem
    rounds: list[DelphiRound]
    max_rounds: int = 3
    convergence_threshold: float = 0.05  # 评分变化 < 5% 视为收敛
```

---

### 4. 群决策服务

```python
class GroupDecisionService:
    """群决策服务"""

    def __init__(self, algorithm: MCDAAlgorithm):
        self.algorithm = algorithm

    def solve(
        self,
        problem: GroupDecisionProblem,
        aggregation_method: str = "weighted_average"
    ) -> GroupDecisionResult:
        """求解群决策问题"""

        # 1. 验证输入
        validation = problem.validate()
        if not validation.is_valid:
            raise ValueError(f"Invalid GroupDecisionProblem: {validation.errors}")

        # 2. 聚合评分
        aggregator = self._get_aggregator(aggregation_method)
        aggregated_problem = aggregator(problem)

        # 3. 共识检查(可选)
        if problem.aggregation_config:
            if problem.aggregation_config.consensus_strategy == "threshold":
                consensus_check = threshold_consensus_check(
                    problem,
                    aggregated_problem,
                    problem.aggregation_config.consensus_threshold
                )
                if not consensus_check.is_valid:
                    # 返回警告,但不阻止计算
                    pass

        # 4. 调用算法
        result = self.algorithm.calculate(aggregated_problem)

        # 5. 构建群决策结果
        return GroupDecisionResult(
            base_result=result,
            individual_results=self._calculate_individual_results(problem),
            consensus_score=measure_consensus(problem, aggregated_problem),
            aggregation_method=aggregation_method,
        )

    def _get_aggregator(self, method: str):
        """获取聚合方法"""
        aggregators = {
            "weighted_average": weighted_average_aggregation,
            "weighted_geometric": weighted_geometric_aggregation,
            "borda_count": borda_count_aggregation,
            "copeland": copeland_aggregation,
        }

        if method not in aggregators:
            raise ValueError(f"Unknown aggregation method: {method}")

        return aggregators[method]

    def _calculate_individual_results(
        self,
        problem: GroupDecisionProblem
    ) -> dict[str, DecisionResult]:
        """计算每个决策者的个人结果"""

        individual_results = {}

        for dm in problem.decision_makers:
            # 构建个人决策问题
            individual_problem = DecisionProblem(
                alternatives=problem.base_problem.alternatives,
                criteria=problem.base_problem.criteria,
                weights=problem.base_problem.weights,
                scores=problem.individual_scores[dm.id],
            )

            # 求解
            result = self.algorithm.calculate(individual_problem)
            individual_results[dm.id] = result

        return individual_results
```

---

### 5. 实施优先级

#### v0.5: 基础群决策 (3 人日)

**交付物**:
- DecisionMaker 数据模型
- GroupDecisionProblem 数据模型
- 加权平均聚合
- 简单共识度测量
- GroupDecisionService 基础实现

#### v0.6: 高级聚合方法 (4 人日)

**交付物**:
- 加权几何平均聚合
- Borda 计数法
- Copeland 方法
- 阈值共识检查

#### v0.7: 德尔菲法支持 (5 人日)

**交付物**:
- DelphiProcess 数据模型
- 多轮评分管理
- 收敛检查
- 统计摘要生成

---

## 权衡分析 (Trade-offs)

### 决策1: 默认聚合方法

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **加权平均** | 简单,易理解 | 容易受极端值影响 | ✅ 采用 |
| **加权几何** | 强调共识 | 对 0 值敏感 | ❌ |
| **Borda 计数** | 避免策略性投票 | 丢失绝对信息 | ⚠️ 可选 |

**决策**: 默认使用加权平均,其他方法可选

### 决策2: 共识检查策略

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **强制共识** | 保证决策质量 | 可能无法达成共识 | ❌ |
| **阈值警告** | 平衡质量和效率 | 可能接受低共识 | ✅ 采用 |
| **忽略共识** | 高效 | 可能不合理 | ❌ |

**决策**: 使用阈值警告,不阻止计算

### 决策3: 决策者权重确定

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **等权重** | 简单,公平 | 忽略专长差异 | ⚠️ 默认 |
| **基于专长** | 考虑能力差异 | 主观,难量化 | ✅ 支持 |
| **动态权重** | 自适应 | 复杂 | ❌ 推迟到 v1.0 |

**决策**: 默认等权重,支持基于专长的权重配置

---

## 后果 (Consequences)

### 正面影响 ✅

1. **扩展应用场景**: 支持多人决策
2. **灵活聚合**: 多种聚合方法可选
3. **共识机制**: 促进意见统一
4. **向后兼容**: 不影响单决策者功能

### 负面影响 ⚠️

1. **复杂度增加**: 数据模型和业务逻辑复杂化
2. **性能下降**: 计算量增加 O(m) 倍(m=决策者数量)
3. **学习曲线**: 用户需要理解聚合方法

### 缓解措施 🛡️

1. **可选功能**: 群决策显式启用
2. **合理默认**: 加权平均 + 等权重
3. **完善文档**: 提供教程和最佳实践
4. **性能优化**: 并行计算个人结果

---

## 参考资料

### 学术文献
- [Group Decision Making: A Survey](https://www.sciencedirect.com/science/article/pii/S136481521500001X)
- [Consensus Reaching Processes](https://www.sciencedirect.com/science/article/pii/S036083521100218X)
- [Delphi Method](https://en.wikipedia.org/wiki/Delphi_method)

### 相关文档
- [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-007: 区间数/模糊数 MCDA](./007-interval-fuzzy-mcda-architecture.md)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-02-03
**状态**: ✅ 已接受并实施
**实施完成**: v0.6 (2026-02-04)
**实施工期**: 12 人日

**实施功能**:
- ✅ DecisionMaker 数据模型
- ✅ GroupDecisionProblem 数据模型
- ✅ 加权平均聚合
- ✅ 加权几何平均聚合
- ✅ Borda 计数法
- ✅ Copeland 方法
- ✅ 德尔菲法（Delphi Method）
- ✅ 共识度测量（标准差、变异系数、距离方法）
- ✅ GroupDecisionService
- ✅ 单元测试覆盖率 92% (153个测试)
