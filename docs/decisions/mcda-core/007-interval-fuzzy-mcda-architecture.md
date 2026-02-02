# ADR-007: 区间数/模糊数 MCDA 架构设计

## 状态
**提议 (Proposed)**

## 日期
2026-02-03

## 上下文 (Context)

MCDA Core v0.4 已实现 4 个经典算法(TOPSIS, TODIM, ELECTRE-I, PROMETHEE),均基于**精确数(crisp numbers)**输入。然而,实际决策场景中常面临**不确定性**和**模糊性**:

### 不确定性场景

**1. 区间数 (Interval Numbers)**
- **场景**: 决策者只能给出一个范围,而非精确值
- **示例**:
  - "成本在 80-120 万之间"
  - "质量评分 8-9 分"
- **数学表示**: x = [x^L, x^U], 其中 x^L ≤ x^U

**2. 模糊数 (Fuzzy Numbers)**
- **场景**: 评价语言模糊,难以精确量化
- **示例**:
  - "这个方案'比较好'"
  - "成本'中等偏上'"
- **数学表示**: 使用隶属度函数 μ(x) 描述
  - **三角模糊数**: Ã = (a, b, c)
  - **梯形模糊数**: Ã = (a, b, c, d)

### 挑战

**技术挑战**:
1. 如何扩展现有算法支持区间/模糊输入?
2. 如何定义区间/模糊数的排序和比较?
3. 如何保证与现有架构兼容?
4. 如何控制复杂度,避免代码爆炸?

**业务挑战**:
1. 用户是否真的需要这些高级功能?
2. 学习成本是否会显著增加?
3. 是否有足够的应用场景?

---

## 决策 (Decision)

### 1. 分阶段实施策略

采用**3 阶段渐进式实施**,降低风险和复杂度:

#### Phase 1: 区间数基础 (v0.5, 4 人日)

**目标**: 建立区间数数据模型和基础运算

**交付物**:
1. **区间数数据类型**
   ```python
   @dataclass(frozen=True)
   class Interval:
       """区间数 [lower, upper]"""
       lower: float
       upper: float

       def __post_init__(self):
           if self.lower > self.upper:
               raise ValueError(f"Invalid interval: [{self.lower}, {self.upper}]")

       @property
       def midpoint(self) -> float:
           """中点值"""
           return (self.lower + self.upper) / 2

       @property
       def width(self) -> float:
           """区间宽度"""
           return self.upper - self.lower
   ```

2. **区间算术运算**
   - 加法: [a, b] + [c, d] = [a+c, b+d]
   - 减法: [a, b] - [c, d] = [a-d, b-c]
   - 乘法: [a, b] × [c, d] = [min(ac,ad,bc,bd), max(ac,ad,bc,bd)]
   - 数乘: k × [a, b] = [ka, kb] (k ≥ 0)

3. **区间排序方法**
   - **中点法**: 按 (a+b)/2 排序(最简单)
   - **可能度法**: P(A ≥ B) (更精确)

4. **TOPSIS 区间版本**
   - 只实现 TOPSIS 区间版本(最常用)
   - 其他算法延迟到 v0.6

#### Phase 2: 模糊数基础 (v0.6, 5 人日)

**目标**: 扩展支持三角模糊数

**交付物**:
1. **三角模糊数数据类型**
   ```python
   @dataclass(frozen=True)
   class TriangularFuzzy:
       """三角模糊数 (a, b, c)"""
       a: float  # 最小值
       b: float  # 中值
       c: float  # 最大值

       @property
       def defuzzified(self) -> float:
           """去模糊化: 重心法"""
           return (self.a + self.b + self.c) / 3
   ```

2. **模糊算术运算**
   - 加法: (a1, b1, c1) + (a2, b2, c2) = (a1+a2, b1+b2, c1+c2)
   - 数乘: k × (a, b, c) = (ka, kb, kc)
   - 距离测度(用于 TOPSIS)

3. **TOPSIS 模糊版本**
   - 基于距离测度的模糊 TOPSIS

#### Phase 3: 全面扩展 (v0.7, 8 人日)

**目标**: 所有算法支持区间/模糊输入

**交付物**:
- TODIM 区间版本
- ELECTRE-I 区间版本
- PROMETHEE 区间版本
- VIKOR 区间版本(如果已实现)

---

### 2. 数据模型扩展

#### 2.1 保持向后兼容

```python
# 现有接口保持不变
class MCDAAlgorithm(ABC):
    @abstractmethod
    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        pass

# 扩展:支持区间/模糊输入
class IntervalMCDAAlgorithm(MCDAAlgorithm):
    """支持区间数的算法"""

    def calculate(
        self,
        problem: DecisionProblem | IntervalDecisionProblem
    ) -> DecisionResult:
        # 自动检测输入类型
        if isinstance(problem, IntervalDecisionProblem):
            return self._calculate_interval(problem)
        return self._calculate_crisp(problem)
```

#### 2.2 区间决策问题

```python
@dataclass(frozen=True)
class IntervalDecisionProblem:
    """区间数决策问题"""
    alternatives: list[str]
    criteria: list[Criterion]
    weights: dict[str, float]  # 准则权重(精确数)
    scores: dict[str, dict[str, Interval]]  # 区间评分

    def validate(self) -> ValidationResult:
        """验证区间数据"""
        # 检查区间有效性
        for alt, crit_scores in self.scores.items():
            for crit, interval in crit_scores.items():
                if interval.lower < 0 or interval.upper < 0:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Negative interval: {alt}.{crit} = {interval}"]
                    )
        return ValidationResult(is_valid=True)
```

#### 2.3 模糊决策问题

```python
@dataclass(frozen=True)
class FuzzyDecisionProblem:
    """模糊数决策问题"""
    alternatives: list[str]
    criteria: list[Criterion]
    weights: dict[str, float]  # 准则权重(精确数)
    scores: dict[str, dict[str, TriangularFuzzy]]  # 模糊评分
```

---

### 3. 算法适配器模式

使用**适配器模式**统一接口,避免代码重复:

```python
class IntervalAlgorithmAdapter:
    """区间算法适配器"""

    def __init__(self, crisp_algorithm: MCDAAlgorithm):
        self.crisp = crisp_algorithm

    def calculate(self, problem: IntervalDecisionProblem) -> DecisionResult:
        """将区间问题转换为精确问题,然后调用 crisp 算法"""

        # 策略1: 中点法(最简单)
        crisp_problem = self._to_midpoint_problem(problem)
        return self.crisp.calculate(crisp_problem)

        # 策略2: 可能度法(更精确,待实现)
        # crisp_problem = self._to_possibility_problem(problem)

    def _to_midpoint_problem(self, problem: IntervalDecisionProblem) -> DecisionProblem:
        """转换为中点问题"""
        scores = {}
        for alt, crit_scores in problem.scores.items():
            scores[alt] = {
                crit: interval.midpoint
                for crit, interval in crit_scores.items()
            }

        return DecisionProblem(
            alternatives=problem.alternatives,
            criteria=problem.criteria,
            weights=problem.weights,
            scores=scores,
        )
```

---

### 4. TOPSIS 区间版本实现

#### 4.1 数学模型

**步骤1**: 标准化(保持区间)
```
r_ij = x_ij / sqrt(Σ x_ij²)
```

**步骤2**: 加权标准化
```
v_ij = w_j × r_ij
```

**步骤3**: 确定区间理想解
```
V⁺ = { [max v_ij^L, max v_ij^U] | j ∈ J_benefit }
V⁻ = { [min v_ij^L, min v_ij^U] | j ∈ J_benefit }
```

**步骤4**: 计算区间距离
```
D_i⁺ = sqrt(Σ (v_ij - V_j⁺)²)
D_i⁻ = sqrt(Σ (v_ij - V_j⁻)²)
```

**步骤5**: 计算相对贴近度(区间)
```
C_i = D_i⁻ / (D_i⁺ + D_i⁻) = [C_i^L, C_i^U]
```

**步骤6**: 排序
```
按 C_i 的中点排序,或使用可能度比较
```

#### 4.2 代码框架

```python
@register_algorithm("topsis_interval")
class TOPSISIntervalAlgorithm(MCDAAlgorithm):
    """TOPSIS 区间版本"""

    @property
    def name(self) -> str:
        return "topsis_interval"

    def calculate(self, problem: IntervalDecisionProblem) -> DecisionResult:
        # 1. 构建区间决策矩阵
        X = self._build_interval_matrix(problem)

        # 2. Vector 标准化
        R = self._vector_normalize(X)

        # 3. 加权标准化
        V = self._weight_normalize(R, problem.weights)

        # 4. 确定区间理想解
        v_plus, v_minus = self._determine_ideal_solutions(V, problem.criteria)

        # 5. 计算区间距离
        D_plus, D_minus = self._calculate_distances(V, v_plus, v_minus)

        # 6. 计算相对贴近度
        C = self._calculate_closeness(D_plus, D_minus)

        # 7. 排序(使用中点)
        rankings = self._rank_by_midpoint(C)

        return DecisionResult(
            rankings=rankings,
            raw_scores={alt: c.midpoint for alt, c in C.items()},
            metrics={"intervals": C},
        )
```

---

### 5. 依赖管理

#### 5.1 核心依赖(无变化)

```
numpy>=1.20.0
pyyaml>=6.0
```

#### 5.2 可选依赖(v0.7+)

```
# 模糊数高级运算(可选)
scipy>=1.7.0  # 特征值分解,数值优化
```

**策略**: 区间/模糊基础功能使用 numpy,高级功能可选 scipy

---

## 权衡分析 (Trade-offs)

### 决策1: 何时引入区间/模糊支持?

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **v0.5 全面支持** | 一步到位 | 工作量大(20+人日),风险高 | ❌ |
| **v0.5 只支持 TOPSIS** | 快速验证,降低风险 | 算法覆盖不全 | ✅ 采用 |
| **推迟到 v1.0** | 避免过早优化 | 延迟用户需求 | ❌ |

**决策**: v0.5 只实现 TOPSIS 区间版本,其他算法延迟到 v0.7

### 决策2: 如何处理区间排序?

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **中点法** | 简单,易理解 | 丢失区间信息 | ✅ Phase1 |
| **可能度法** | 精确,保序 | 计算复杂 | ✅ Phase2 |
| **期望-方差法** | 考虑风险 | 参数敏感 | ⚠️ 可选 |

**决策**: Phase1 使用中点法,Phase2 引入可能度法

### 决策3: 如何与现有算法集成?

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **修改现有算法** | 统一接口 | 破坏现有功能,风险高 | ❌ |
| **继承扩展** | 向后兼容 | 类层次复杂 | ⚠️ |
| **适配器模式** | 解耦,灵活 | 间接调用 | ✅ 采用 |

**决策**: 使用适配器模式,保持现有算法不变

---

## 后果 (Consequences)

### 正面影响 ✅

1. **扩展能力**: 支持不确定性决策,覆盖更多场景
2. **向后兼容**: 不影响现有精确数算法
3. **渐进式**: 分阶段实施,降低风险
4. **学术价值**: 区间/模糊 MCDA 是研究热点

### 负面影响 ⚠️

1. **复杂度增加**: 代码量增加 50%+
2. **学习曲线**: 用户需要理解区间/模糊概念
3. **性能下降**: 区间运算比精确数慢 2-3 倍
4. **测试负担**: 需要大量区间/模糊测试用例

### 缓解措施 🛡️

1. **默认关闭**: 区间/模糊功能显式启用
2. **文档完善**: 提供教程和示例
3. **性能优化**: 使用 numpy 向量化运算
4. **测试覆盖**: 区间/模糊测试覆盖率 >= 80%

---

## 未来演进

### v0.5: 区间数基础
- Interval 数据类型
- 区间算术运算
- TOPSIS 区间版本
- 中点法排序

### v0.6: 模糊数基础
- TriangularFuzzy 数据类型
- 模糊算术运算
- TOPSIS 模糊版本
- 重心法去模糊

### v0.7: 全面扩展
- TODIM/ELECTRE-I/PROMETHEE 区间版本
- 可能度排序
- 性能优化

### v1.0: 生产就绪
- Web UI 支持区间/模糊输入
- 导出报告
- 可视化区间结果

---

## 参考资料

### 学术文献
- [Interval TOPSIS](https://www.sciencedirect.com/science/article/pii/S0957417416306298)
- [Fuzzy TOPSIS](https://www.sciencedirect.com/science/article/pii/S036083521100218X)
- [Interval Arithmetic](https://en.wikipedia.org/wiki/Interval_arithmetic)

### 相关文档
- [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-004: 汇总算法架构设计](./004-mcda-aggregation-algorithms.md)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-02-03
**状态**: ✅ 提议,待批准
**预计工期**: Phase1 (4人日) + Phase2 (5人日) + Phase3 (8人日) = 17 人日
