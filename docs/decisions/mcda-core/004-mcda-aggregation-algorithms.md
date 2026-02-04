# ADR-004: MCDA 汇总算法架构设计

## 状态
**已接受 (Accepted)**

## 日期
2026-01-31

## 上下文 (Context)

MCDA Core 框架需要支持多种汇总算法（Aggregation Algorithms），将标准化数据和权重聚合为最终排名。现有文献中存在 12+ 种常用汇总算法，需要确定实现优先级和分阶段计划。

**候选算法列表**:

### 线性聚合算法
1. **WSM** (Weighted Sum Model) - 加权算术平均
2. **WPM** (Weighted Product Model) - 加权几何平均
3. **SAW** (Simple Additive Weighting) - 简单加权法

### 距离类算法
4. **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution) - 逼近理想解排序法
5. **VIKOR** (VIseKriterijumska Optimizacija I Kompromisno Resenje) - 折衷排序法

### 偏好类算法
6. **PROMETHEE-II** (Preference Ranking Organization METHod for Enrichment Evaluations) - 优先排序法
7. **ELECTRE-I** (Elimination Et Choix Traduisant la REalité) - 消除与选择转换法

### 效用类算法
8. **COPRAS** (COmplex PRoportional ASsessment) - 复杂比例评估
9. **MOORA** (Multi-Objective Optimization on the basis of Ratio Analysis) - 比率分析多目标优化

### 特殊场景算法
10. **TODIM** (Tomada de Decisao Interativa e Multicriterio) - 交互式多准则决策（前景理论）
11. **MACBETH** (Measuring Attractiveness by a Categorical Based Evaluation Technique) - 定性偏好量化
12. **ORESTE** (Organisation, Rangement et Synthese de Donnes Relationale) - 关系数据排序

**挑战**:
- 如何平衡应用热度、实现难度、用户价值？
- 如何分阶段实施，确保每个版本都有可用功能？
- 如何设计统一的算法接口？

---

## 决策 (Decision)

### 1. 优先级评分体系

采用**四维评分法**确定优先级：

| 维度 | 权重 | 评分标准 (1-5 分) |
|------|------|------------------|
| **应用热度** | 40% | 文献引用量、实际使用频率、社区活跃度 |
| **实现难度** | 30% | 算法复杂度 (5=最简单)、依赖库需求 (5=最少)、开发工作量 (5=最小) |
| **用户价值** | 20% | 解决实际问题的能力、适用场景广度 |
| **架构兼容性** | 10% | 与现有框架的适配度、接口设计难度 |

### 2. 综合评分结果（architect agent 审查后调整）

| 排名 | 算法 | 中文名 | 热度 | 难度 | 价值 | 兼容 | **总分** | 类型 | **新阶段** | 变化 |
|------|------|--------|------|------|------|------|----------|------|-----------|------|
| **1** | **WSM** | 加权算术平均 | 5.0 | 5.0 | 5.0 | 5.0 | **5.00** | 线性 | **v0.1** | - |
| **2** | **TOPSIS** | 逼近理想解 | 5.0 | 4.5 | 5.0 | 5.0 | **4.90** | 距离 | **v0.2** | **↑ 评分升级** |
| **3** | **WPM** | 加权几何平均 | 4.5 | 5.0 | 4.5 | 5.0 | **4.70** | 非线性 | **v0.1** | - |
| **🎯4** | **VIKOR** | 折衷排序 | 5.0 | 3.5 | 5.0 | 5.0 | **4.70** | 折衷 | **v0.2** | **↑ 升级 P0** |
| 5 | **PROMETHEE-II** | 优先排序 | 4.0 | 3.0 | 4.5 | 4.5 | **3.85** | 偏好 | **v0.3** | - |
| 6 | **COPRAS** | 复杂比例 | 3.5 | 4.0 | 4.0 | 5.0 | **3.85** | 效用 | **v0.3** | **↓ 降级** |
| 7 | **MOORA** | 比率分析 | 3.5 | 4.5 | 3.5 | 5.0 | **3.80** | 效用 | **v0.4+** | **↓ 降级** |
| 8 | **ELECTRE-I** | 消除选择 | 3.5 | 2.5 | 4.0 | 3.0 | **3.25** | 级别 | **v0.4+** | - |
| 9 | **TODIM** | 交互决策 | 3.0 | 2.5 | 4.5 | 4.0 | **3.20** | 前景 | **v0.4+** | - |
| 10 | **SAW** | 简单加权 | 4.5 | 5.0 | 4.5 | 2.0 | **4.20** | 线性 | **v0.4** | **↓↓ 降级** |
| 11 | **MACBETH** | 分类评估 | 2.5 | 3.0 | 4.0 | 3.5 | **3.00** | 定量 | **v0.4+** | - |
| 12 | **ORESTE** | 关系排序 | 2.0 | 3.5 | 3.5 | 3.0 | **2.65** | 距离 | **v0.4+** | - |

**关键变化说明**:
- **VIKOR 升级到 v0.2 (P0)**: 唯一提供折衷解的算法，符合"权衡取舍"核心需求，用户价值从 4.5 → 5.0
- **TOPSIS 评分升级**: 架构依赖从 4.5 → 5.0（Vector 标准化必需）
- **SAW 大幅降级**: 与 WSM 几乎无差异，仅标准化方式不同，兼容性从 5.0 → 2.0
- **COPRAS 降级**: 与 WSM 价值重叠

### 3. 分阶段实施计划（architect agent 审查后调整）

#### v0.1: MVP 必备（2 人日，1-2 天）

**目标**: 验证架构可行性，交付基础决策能力

| 算法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **WSM** | P0 | 1 人日 | 最简单、验证可插拔架构 |
| **WPM** | P0 | 1 人日 | 非线性聚合示例，与 WSM 互补 |

**总工作量**: **2 人日**

**里程碑**:
- [ ] 基础算法可插拔验证
- [ ] 算法注册机制工作
- [ ] 测试覆盖率 >= 80%

---

#### v0.2: 基础扩展（5 人日，1 周）⭐ MVP 核心

**目标**: 引入距离概念和折衷解，提升决策质量

| 算法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **TOPSIS** | P0 | 2 人日 | 最热门距离算法 |
| **VIKOR** | P0 | 3 人日 | 唯一提供折衷解的算法 ⭐ |

**总工作量**: **5 人日**

**里程碑**:
- [ ] 支持距离类算法
- [ ] 支持折衷解决策
- [ ] Vector 标准化集成（ADR-002）
- [ ] 完整测试覆盖

---

#### v0.3: 高级算法（6 人日，1.5 周）

**目标**: 支持偏好关系决策场景

| 算法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **PROMETHEE-II** | P1 | 4 人日 | 基于偏好函数 |
| **COPRAS** | P2 | 2 人日 | 效用型，区分效益/成本 |

**总工作量**: **6 人日**

**里程碑**:
- [ ] 支持偏好关系决策
- [ ] 算法对比文档
- [ ] 用户使用指南

---

#### v0.4: 特殊场景（8 人日，2 周）

**目标**: 覆盖特殊决策需求

| 算法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **SAW** | P3 | 0.5 人日 | WSM 变体，Minmax 标准化 |
| **TODIM** | P1 | 4 人日 | 考虑损失厌恶（前景理论） |
| **ELECTRE-I** | P2 | 4 人日 | 支配关系筛选 |
| **MACBETH** | P2 | 5 人日 | 定性偏好量化 |
| **MOORA** | P3 | 2 人日 | 参考点法 |
| **ORESTE** | P3 | 3 人日 | 数据不完整场景 |

**总工作量**: **8 人日**

**汇总算法总计**: **21 人日** (原 29.5 人日，节省 **8.5 人日**)

---

### 4. 核心接口设计

#### 4.1 算法抽象基类

```python
# lib/algorithms/base.py
from abc import ABC, abstractmethod
from ..models import DecisionProblem, DecisionResult

class MCDAAlgorithm(ABC):
    """MCDA 算法基类"""

    @abstractmethod
    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        """执行计算，返回决策结果"""
        pass

    def validate(self, problem: DecisionProblem) -> ValidationResult:
        """验证输入数据（可覆盖）"""
        return ValidationResult(is_valid=True)

    @property
    @abstractmethod
    def name(self) -> str:
        """算法名称"""
        pass

    @property
    def metadata(self) -> AlgorithmMetadata:
        """算法元数据（默认实现）"""
        return AlgorithmMetadata(
            name=self.name,
            version="1.0.0",
            requires_normalized_weights=True,
            score_range=(0, 100),
        )
```

#### 4.2 算法注册机制

```python
# lib/algorithms/__init__.py
from typing import Dict, Type, Callable

_algorithms: Dict[str, Type[MCDAAlgorithm]] = {}

def register_algorithm(name: str) -> Callable:
    """算法注册装饰器"""
    def decorator(cls: Type[MCDAAlgorithm]) -> Type[MCDAAlgorithm]:
        _algorithms[name] = cls
        return cls
    return decorator

def get_algorithm(name: str) -> MCDAAlgorithm:
    """获取算法实例"""
    if name not in _algorithms:
        available = ", ".join(_algorithms.keys())
        raise ValueError(f"未知的算法: '{name}'. 可用: {available}")
    return _algorithms[name]()

# 使用示例
@register_algorithm("wsm")
class WSMAlgorithm(MCDAAlgorithm):
    ...
```

#### 4.3 统一结果接口

```python
# lib/models.py
@dataclass
class AggregationResult:
    """汇总算法结果"""
    algorithm_name: str
    rankings: list[RankingItem]
    raw_scores: dict[str, float]

    # 算法特定指标
    metrics: dict[str, Any] = field(default_factory=dict)
    # 示例:
    # - WSM: {"weighted_sums": {...}}
    # - TOPSIS: {"closeness": {...}, "d_plus": {...}, "d_minus": {...}}
    # - VIKOR: {"S": {...}, "R": {...}, "Q": {...}, "compromise_set": [...]}
    # - PROMETHEE: {"phi_plus": {...}, "phi_minus": {...}, "phi": {...}}
```

---

### 5. 核心算法实现

#### 5.1 WSM (Weighted Sum Model)

**公式**: `S_i = Σ w_j · r_ij`

**适用场景**: 最通用、最直观的决策场景

```python
@register_algorithm("wsm")
class WSMAlgorithm(MCDAAlgorithm):
    """加权算术平均模型

    公式: S_i = Σ w_j · r_ij
    适用: 通用场景，准则间独立
    """

    @property
    def name(self) -> str:
        return "wsm"

    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        scores = {}
        for alt in problem.alternatives:
            weighted_sum = 0.0
            for crit in problem.criteria:
                value = problem.scores[alt][crit.name]
                # 处理 lower_better（方向反转）
                if crit.direction == "lower_better":
                    value = self._invert(value, problem, crit.name)
                weighted_sum += crit.weight * value
            scores[alt] = weighted_sum

        # 排序
        sorted_alts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rankings = [
            RankingItem(rank=i, alternative=alt, score=round(score, 4))
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        return DecisionResult(
            rankings=rankings,
            raw_scores=scores,
            metadata=ResultMetadata(
                algorithm_name=self.name,
                problem_size=(len(problem.alternatives), len(problem.criteria)),
            ),
            metrics={"weighted_sums": scores},
        )
```

**工作量**: 1 人日

---

#### 5.2 WPM (Weighted Product Model)

**公式**: `P_i = Π r_ij^w_j`

**适用场景**: 准则间有乘积效应、"短板效应"

```python
@register_algorithm("wpm")
class WPMAlgorithm(MCDAAlgorithm):
    """加权几何平均模型

    公式: P_i = Π r_ij^w_j
    适用: 准则间有相互作用，强调短板
    """

    @property
    def name(self) -> str:
        return "wpm"

    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        scores = {}
        for alt in problem.alternatives:
            product = 1.0
            for crit in problem.criteria:
                value = problem.scores[alt][crit.name]
                if crit.direction == "lower_better":
                    value = self._invert(value, problem, crit.name)
                # 避免 0 值，加一个小常数
                value = max(value, 1e-10)
                product *= value ** crit.weight
            scores[alt] = product

        # 排序
        sorted_alts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rankings = [
            RankingItem(rank=i, alternative=alt, score=round(score, 4))
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        return DecisionResult(
            rankings=rankings,
            raw_scores=scores,
            metadata=ResultMetadata(
                algorithm_name=self.name,
                problem_size=(len(problem.alternatives), len(problem.criteria)),
            ),
            metrics={"products": scores},
        )
```

**工作量**: 1 人日

---

#### 5.3 TOPSIS

**公式**:
1. 标准化: `r_ij = x_ij / sqrt(Σ x_ij²)` ← 需要 Vector 标准化
2. 加权标准化: `v_ij = w_j · r_ij`
3. 距离: `D_i⁺ = sqrt(Σ (v_ij - v_j⁺)²)`, `D_i⁻ = sqrt(Σ (v_ij - v_j⁻)²)`
4. 相对接近度: `C_i = D_i⁻ / (D_i⁺ + D_i⁻)`

**适用场景**: 需要距离概念的决策，TOPSIS 是最热门距离算法

```python
@register_algorithm("topsis")
class TOPSISAlgorithm(MCDAAlgorithm):
    """逼近理想解排序法

    核心思想: 距离正理想解最近，同时距离负理想解最远
    公式: C_i = D_i⁻ / (D_i⁺ + D_i⁻)
    适用: 需要距离概念的决策场景
    """

    @property
    def name(self) -> str:
        return "topsis"

    @property
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name=self.name,
            version="1.0.0",
            requires_normalized_weights=True,
            requires_normalization="vector",  # 必须使用 Vector 标准化
            score_range=(0, 1),
        )

    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        import numpy as np

        # 1. 构建决策矩阵
        m = len(problem.alternatives)
        n = len(problem.criteria)
        X = np.zeros((m, n))

        for i, alt in enumerate(problem.alternatives):
            for j, crit in enumerate(problem.criteria):
                X[i, j] = problem.scores[alt][crit.name]

        # 2. Vector 标准化
        norms = np.sqrt(np.sum(X ** 2, axis=0))
        R = X / norms

        # 3. 加权标准化
        weights = np.array([c.weight for c in problem.criteria])
        V = R * weights

        # 4. 确定理想解（正负理想解）
        v_plus = np.max(V, axis=0)  # 正理想解
        v_minus = np.min(V, axis=0)  # 负理想解

        # 5. 计算距离
        D_plus = np.sqrt(np.sum((V - v_plus) ** 2, axis=1))
        D_minus = np.sqrt(np.sum((V - v_minus) ** 2, axis=1))

        # 6. 计算相对接近度
        C = D_minus / (D_plus + D_minus)

        scores = {alt: C[i] for i, alt in enumerate(problem.alternatives)}

        # 排序
        sorted_alts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rankings = [
            RankingItem(rank=i, alternative=alt, score=round(score, 4))
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        return DecisionResult(
            rankings=rankings,
            raw_scores=scores,
            metadata=ResultMetadata(
                algorithm_name=self.name,
                problem_size=(len(problem.alternatives), len(problem.criteria)),
            ),
            metrics={
                "closeness": scores,
                "d_plus": {alt: D_plus[i] for i, alt in enumerate(problem.alternatives)},
                "d_minus": {alt: D_minus[i] for i, alt in enumerate(problem.alternatives)},
            },
        )
```

**工作量**: 2 人日

---

#### 5.4 VIKOR

**公式**:
- 群体效用: `S_i = Σ w_j · (x_j^max - x_ij) / (x_j^max - x_j^min)`
- 个别遗憾: `R_i = max_j [w_j · (x_j^max - x_ij) / (x_j^max - x_j^min)]`
- 折衷值: `Q_i = v · (S_i - S_min) / (S_max - S_min) + (1-v) · (R_i - R_min) / (R_max - R_min)`

**适用场景**: 需要折衷解的决策，同时优化群体效用和个别遗憾

```python
@register_algorithm("vikor")
class VIKORAlgorithm(MCDAAlgorithm):
    """折衷排序法

    核心思想: 同时最大化群体效用和最小化个别遗憾
    参数 v: 决策策略系数（0-1），v=0.5 为折衷
    适用: 需要折衷解的决策场景
    """

    def __init__(self, v: float = 0.5):
        self.v = v  # 决策策略系数

    @property
    def name(self) -> str:
        return "vikor"

    def calculate(self, problem: DecisionProblem, v: float = 0.5) -> DecisionResult:
        import numpy as np

        # 1. 标准化到 [0, 1]
        normalized = self._normalize(problem)

        # 2. 计算群体效用 S_i 和个别遗憾 R_i
        S = {}
        R = {}
        for alt in problem.alternatives:
            s_i = 0.0
            r_max = 0.0
            for crit in problem.criteria:
                f = normalized[alt][crit.name]
                s_i += crit.weight * f
                r_max = max(r_max, crit.weight * f)
            S[alt] = s_i
            R[alt] = r_max

        # 3. 计算 Q_i
        S_min, S_max = min(S.values()), max(S.values())
        R_min, R_max = min(R.values()), max(R.values())

        Q = {}
        for alt in problem.alternatives:
            q = v * (S[alt] - S_min) / (S_max - S_min) + \
                (1 - v) * (R[alt] - R_min) / (R_max - R_min)
            Q[alt] = q

        # 4. 确定折衷解（同时优化 S, R, Q）
        # ... 折衷解判定逻辑

        # 排序（按 Q 值）
        sorted_alts = sorted(Q.items(), key=lambda x: x[1])
        rankings = [
            RankingItem(rank=i, alternative=alt, score=round(score, 4))
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        return DecisionResult(
            rankings=rankings,
            raw_scores=Q,
            metadata=ResultMetadata(
                algorithm_name=self.name,
                problem_size=(len(problem.alternatives), len(problem.criteria)),
            ),
            metrics={
                "Q": Q,
                "S": S,  # 群体效用
                "R": R,  # 个别遗憾
                "v": v,
            },
        )
```

**工作量**: 3 人日

---

#### 5.5 PROMETHEE-II

**核心**: 基于偏好函数的流出/流入量

**适用场景**: 需要定义偏好关系的决策

```python
@register_algorithm("promethee2")
class PROMETHEE2Algorithm(MCDAAlgorithm):
    """优先排序法 II

    核心思想: 基于偏好函数计算流出量和流入量
    公式: Φ = Φ⁺ - Φ⁻
    适用: 需要明确偏好关系的决策场景
    """

    @property
    def name(self) -> str:
        return "promethee2"

    def calculate(
        self,
        problem: DecisionProblem,
        pref_type: str = "usual",
        p: float = 0.5,  # 线性偏好函数阈值
        q: float = 0.2,  # 准偏好函数阈值
    ) -> DecisionResult:
        import numpy as np

        # 1. 定义偏好函数
        def preference_function(d, p_type="usual", p=0.5, q=0.2):
            """d = a - b (方案a对b的优势)"""
            if p_type == "usual":
                return 1 if d > 0 else 0
            elif p_type == "linear":
                return max(0, min(1, d / p))
            elif p_type == "quasi":
                return 1 if d > q else 0
            # ... 其他偏好函数

        # 2. 计算成对偏好
        m = len(problem.alternatives)
        pi = np.zeros((m, m))

        for i, a in enumerate(problem.alternatives):
            for j, b in enumerate(problem.alternatives):
                for crit in problem.criteria:
                    d = problem.scores[a][crit.name] - \
                        problem.scores[b][crit.name]
                    pi[i, j] += crit.weight * preference_function(d, pref_type, p, q)

        # 3. 计算流出量和流入量
        phi_plus = np.sum(pi, axis=1)  # 流出量
        phi_minus = np.sum(pi, axis=0)  # 流入量

        # 4. 计算净流量
        phi = phi_plus - phi_minus

        scores = {alt: phi[i] for i, alt in enumerate(problem.alternatives)}

        # 排序
        sorted_alts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rankings = [
            RankingItem(rank=i, alternative=alt, score=round(score, 4))
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        return DecisionResult(
            rankings=rankings,
            raw_scores=scores,
            metadata=ResultMetadata(
                algorithm_name=self.name,
                problem_size=(len(problem.alternatives), len(problem.criteria)),
            ),
            metrics={
                "phi": scores,
                "phi_plus": {alt: phi_plus[i] for i, alt in enumerate(problem.alternatives)},
                "phi_minus": {alt: phi_minus[i] for i, alt in enumerate(problem.alternatives)},
            },
        )
```

**工作量**: 4 人日

---

### 6. 算法分类与对比

#### 6.1 算法分类体系

```
MCDAAlgorithm (抽象基类)
    │
    ├── LinearAggregation (线性聚合)
    │   ├── WSM (加权算术平均)
    │   ├── WPM (加权几何平均)
    │   └── SAW (简单加权)
    │
    ├── DistanceBased (距离类)
    │   ├── TOPSIS (逼近理想解)
    │   └── VIKOR (折衷排序)
    │
    ├── PreferenceBased (偏好类)
    │   ├── PROMETHEE-II (优先排序)
    │   └── ELECTRE-I (消除选择)
    │
    └── UtilityBased (效用类)
        ├── COPRAS (复杂比例)
        ├── MOORA (比率分析)
        └── TODIM (前景理论)
```

#### 6.2 算法对比矩阵

| 算法 | 适用场景 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| **WSM** | 通用决策 | 最简单、直观 | 准则间独立 | ⭐⭐⭐⭐⭐ |
| **WPM** | 短板效应 | 考虑准则间相互作用 | 对零值敏感 | ⭐⭐⭐⭐ |
| **TOPSIS** | 距离相关 | 考虑理想解距离 | 不保序 | ⭐⭐⭐⭐⭐ |
| **VIKOR** | 折衷决策 | 提供折衷解 | 参数调优复杂 | ⭐⭐⭐⭐ |
| **SAW** | 快速决策 | WSM 变体 | 与 WSM 类似 | ⭐⭐⭐ |
| **PROMETHEE-II** | 偏好关系 | 偏好函数灵活 | 需要定义偏好 | ⭐⭐⭐⭐ |
| **COPRAS** | 效用明确 | 区分效益/成本 | 场景受限 | ⭐⭐⭐ |
| **MOORA** | 参考点法 | 双重评分 | 理解复杂 | ⭐⭐⭐ |
| **ELECTRE-I** | 支配筛选 | 处理不完整信息 | 阈值敏感 | ⭐⭐⭐ |
| **TODIM** | 风险敏感 | 前景理论 | 参数复杂 | ⭐⭐⭐ |
| **MACBETH** | 定性量化 | 转换定性偏好 | 实施复杂 | ⭐⭐ |
| **ORESTE** | 数据缺失 | 不完整数据 | 应用面窄 | ⭐⭐ |

---

### 7. 依赖决策

| 算法 | 核心依赖 | 可选依赖 | 说明 |
|------|---------|----------|------|
| WSM, WPM, SAW | Python 标准库 | - | 零外部依赖 |
| TOPSIS, VIKOR, COPRAS | numpy | - | 矩阵运算 |
| PROMETHEE-II, MOORA | numpy | - | 矩阵运算 |
| ELECTRE-I, TODIM, MACBETH | numpy | - | 矩阵运算 |

**策略**: 全部算法仅需 numpy，符合"最小依赖原则"

---

## 权衡分析 (Trade-offs)

### 决策 1: v0.1 MVP 算法选择

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **仅 WSM** | 最简单，快速验证 | 算法单一 | ❌ |
| **WSM + WPM** | 线性+非线性，验证架构 | 工作量略增 | ✅ 采用 |
| **WSM + TOPSIS** | 线性+距离，覆盖广 | 工作量大 | ❌ |

**决策**: WSM + WPM，理由：
- WSM 验证可插拔架构
- WPM 提供非线性视角，与 WSM 互补
- 工作量小（2人日），快速交付

### 决策 2: TOPSIS 实施时机

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **v0.1 包含 TOPSIS** | 一步到位 | MVP 太重 | ❌ |
| **v0.2 包含 TOPSIS** | 平衡复杂度 | 延迟热门算法 | ✅ 采用 |
| **v0.3 包含 TOPSIS** | 风险最低 | 影响用户价值 | ❌ |

**决策**: v0.2 实施 TOPSIS，理由：
- v0.1 专注架构验证
- v0.2 引入距离类算法，提升决策精度
- TOPSIS 是最热门距离算法（5.0 热度）

### 决策 3: VIKOR 实施优先级

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **v0.2 包含 VIKOR** | 快速提供折衷解 | 实施压力大 | ❌ |
| **v0.3 包含 VIKOR** | 作为高级算法 | 延迟折衷能力 | ✅ 采用 |
| **v0.4 包含 VIKOR** | 风险最低 | 用户需求延迟 | ❌ |

**决策**: v0.3 实施 VIKOR，理由：
- VIKOR 是唯一提供折衷解的算法
- v0.3 作为高级算法，专注复杂决策场景
- 避免过早优化

### 正面影响 ✅
1. **清晰路线图**: 分 4 个阶段，每个阶段都有明确交付目标
2. **优先级合理**: 平衡热度、难度、价值
3. **架构可扩展**: 统一接口，易于添加新算法
4. **向后兼容**: 不破坏已实现的算法
5. **最小依赖**: 仅需 numpy，符合轻量原则

### 负面影响 ⚠️
1. **开发周期长**: 完整实施需要 7-8 周
2. **学习曲线**: 用户需要理解不同算法的适用场景
3. **算法选择困难**: 多种算法可能让用户困惑

### 缓解措施 🛡️
1. **MVP 优先**: v0.1 先交付 WSM + WPM，验证架构
2. **算法推荐**: 根据决策场景自动推荐算法
3. **完善文档**: 每种算法的使用场景和示例
4. **渐进式披露**: v0.1-v0.2 覆盖 80% 用户需求

---

## 后果 (Consequences)

### 对开发的影响
- **v0.1** (2人日): MVP 验证，WSM + WPM
- **v0.2** (2.5人日): 基础扩展，+ TOPSIS + SAW
- **v0.3** (9人日): 高级算法，+ VIKOR + PROMETHEE-II + COPRAS
- **v0.4** (16人日): 特殊场景，+ TODIM + ELECTRE-I + MACBETH + MOORA + ORESTE

### 对用户的影响
- **早期用户** (v0.1-v0.2): 可用线性+距离算法，覆盖 80% 场景
- **中期用户** (v0.3): 支持折衷解和偏好关系
- **成熟用户** (v0.4): 覆盖特殊决策需求

### 对架构的影响
- **新增模块**: `lib/algorithms/` （算法实现）
- **模块依赖**: 算法层依赖标准化层（ADR-002）和赋权层（ADR-003）
- **接口扩展**: `DecisionProblem` 增加 `algorithm` 字段

---

## 未来演进

### 短期 (v0.1 - 2周)
- WSM, WPM（线性+非线性）
- 算法注册机制

### 中期 (v0.2 - v0.3, 4-6周)
- TOPSIS, SAW（距离类）
- VIKOR, PROMETHEE-II, COPRAS（高级）

### 长期 (v0.4, 7-8周)
- TODIM, ELECTRE-I, MACBETH, MOORA, ORESTE（特殊场景）

### 可选扩展 (v1.0+)
- 算法组合（如 WSM + TOPSIS 混合）
- 自定义算法插件
- Web UI 算法选择器

---

## 算法选择指南

### 场景映射表

| 决策场景 | 推荐算法 | 理由 |
|----------|----------|------|
| 快速决策，准则独立 | **WSM** | 最简单、最直观 |
| 强调短板效应 | **WPM** | 几何平均，低分拖累 |
| 需要距离概念 | **TOPSIS** | 最热门距离算法 |
| 需要折衷解 | **VIKOR** | 唯一提供折衷解 |
| 明确偏好关系 | **PROMETHEE-II** | 偏好函数灵活 |
| 风险敏感 | **TODIM** | 前景理论，损失厌恶 |

### 算法组合建议

| 组合 | 适用场景 |
|------|----------|
| WSM + TOPSIS | 通用决策（线性+距离验证） |
| WSM + WPM | 准则独立 vs 相互作用对比 |
| WSM + VIKOR | 常规排名 + 折衷解验证 |
| TOPSIS + VIKOR | 距离类双验证 |

---

## 参考资料

### 学术文献
- [Comparison of Aggregation Methods in MCDA](https://www.sciencedirect.com/science/article/pii/S136481521500001X)
- [TOPSIS Method: A Comprehensive Review](https://www.sciencedirect.com/science/article/pii/S0957417416306298)
- [VIKOR Method with Applications](https://www.sciencedirect.com/science/article/pii/S036083521100218X)

### 相关文档
- [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-002: 标准化方法](./002-mcda-normalization-methods.md)
- [ADR-003: 赋权方法路线图](./003-mcda-weighting-roadmap.md)
- [需求文档: MCDA Core v2.0](../requirements/mcda-core.md)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-01-31
**最后更新**: 2026-01-31（architect agent 审查后调整）
**状态**: ✅ 已批准（优先级已调整，VIKOR 升级到 v0.2）
**总工作量**: 21 人日 (原 29.5 人日，优化节省 8.5 人日)
