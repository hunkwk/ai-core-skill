# ADR-007: 区间数/模糊数 MCDA 架构设计

## 状态
**已接受 (Accepted) - 2026-02-04 更新**

## 日期
- **创建日期**: 2026-02-03
- **更新日期**: 2026-02-04
- **更新原因**: v0.7 规划调整（架构师审查）

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

### 1. 分阶段实施策略 (已更新)

采用**5 阶段渐进式实施**,降低风险和复杂度:

#### ✅ Phase 1: 区间数基础 (v0.5, 4 人日) - 已完成

**目标**: 建立区间数数据模型和基础运算

**交付物**:
1. ✅ **区间数数据类型** (`Interval`)
   - 冻结 dataclass 设计
   - 区间算术运算 (+, -, ×, ÷)
   - 区间属性（中点、宽度、退化判断）
   - 16 个测试,100% 通过

2. ✅ **区间排序方法**
   - 中点法: 按 (a+b)/2 排序
   - 基于 `__lt__`, `__gt__` 等魔术方法

3. ✅ **TOPSIS 区间版本**
   - 通过中点法集成
   - 20 个测试
   - 执行时间 < 1 秒

**状态**: ✅ **100% 完成** (2026-02-03)

---

#### 🔄 Phase 2: 模糊数基础 (v0.6, 5 人日) - 已调整

**原计划**:
- TriangularFuzzy 数据类型
- 模糊算术运算
- TOPSIS 模糊版本

**实际执行**: v0.6 实现了**群决策功能**而非模糊数

**调整原因** (ADR-010):
- 群决策功能优先级更高（用户需求明确）
- 模糊数基础工作量被低估（需要 7-8 人日）
- 技术验证不足（模糊数去模糊化策略未确定）

**新计划**: Phase 2 延迟到 **v0.8**

**状态**: ⏸️ **已调整，延迟到 v0.8**

---

#### 🔥 Phase 3: 渐进式扩展 (v0.7, 11 人日) - 2026-02-04 更新

**目标**: 聚焦核心算法区间扩展 + 可能度排序

**调整原因** (架构师审查):
- 工作量重新评估: 原计划 15 人日 → 实际需要 19-24 人日
- 功能优先级调整: VIKOR > 可能度 > TODIM > 模糊数
- 技术风险控制: 增加 Phase 0 验证阶段

**交付物**:

**Phase 0: 技术验证** (2 人日) 🔬
- VIKOR 区间可行性验证
- 可能度排序原型开发
- ELECTRE-I 区间学术调研
- 成功标准: 验证通过,风险可控

**Phase 1: VIKOR 区间版本** (3 人日) 🎯
- IntervalVIKOR 算法实现
- 群体效用 S 和个别遗憾 R 的区间版本
- 折衷值 Q 的区间计算
- 28 个测试

**Phase 2: 可能度排序** (4 人日) 📊
- `PossibilityDegree` 类实现
- P(A ≥ B) 计算方法
- 集成到现有区间算法（VIKOR, TODIM）
- 替代中点法,提升排序质量
- 24 个测试

**Phase 3: TODIM 区间版本** (4 人日) 🎲
- IntervalTODIM 算法实现
- 前景理论 + 区间数融合
- 区间收益/损失计算
- 32 个测试

**Phase 4: 集成与文档** (2 人日) 📝
- 集成测试 (10+ 个)
- 性能测试
- API 文档更新

**总工期**: **11 人日** (vs 原计划 15 人日)

**优势**:
- ✅ 补全 VIKOR 区间版本（v0.5 遗留）
- ✅ 实现可能度排序（比中点法更精确）
- ✅ TODIM 区间版本（前景理论价值）
- ✅ 风险可控,工期合理
- ✅ 为 v0.8 模糊数铺路

**状态**: ⏳ **待开始**

---

#### 📋 Phase 4: 模糊数基础 (v0.8, 7-8 人日) - 已规划

**目标**: 补完 Phase 2（模糊数基础）

**交付物**:
1. **TriangularFuzzy 数据类型**
   - 三角模糊数定义
   - 隶属度函数 μ(x)
   - 去模糊化方法（重心法、α-截集法）

2. **模糊算术运算**
   - 加法: (a1, b1, c1) + (a2, b2, c2) = (a1+a2, b1+b2, c1+c2)
   - 数乘: k × (a, b, c) = (ka, kb, kc)
   - 距离测度（用于 TOPSIS）

3. **TOPSIS 模糊版本**
   - FuzzyTOPSIS 算法
   - 基于距离测度的模糊 TOPSIS
   - 35 个测试

**状态**: 📋 **已规划，待启动**

---

#### 🚀 Phase 5: 全面扩展 (v0.9+, 可选)

**目标**: 所有算法支持区间/模糊输入

**交付物**:
- ELECTRE-I 区间版本（如果学术支持充足）
- PROMETHEE 区间版本（如果学术支持充足）
- 其他算法模糊版本

**状态**: 📋 **可选，根据用户需求决定**

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

        # 策略1: 中点法(最简单) - v0.5 已实现
        crisp_problem = self._to_midpoint_problem(problem)
        return self.crisp.calculate(crisp_problem)

        # 策略2: 可能度法(更精确) - v0.7 实现
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

### 4. 可能度排序方法 (v0.7 新增)

#### 4.1 数学模型

**可能度定义**: P(A ≥ B) 表示区间 A 大于等于区间 B 的可能度

**计算公式**:
```
P(A ≥ B) = {
    1,                    if A^L ≥ B^U
    0,                    if A^U ≤ B^L
    (A^U - B^L) / ((A^U - A^L) + (B^U - B^L)),  otherwise
}
```

**性质**:
- P(A ≥ B) + P(B ≥ A) = 1
- P(A ≥ B) = 1 当且仅当 A ≥ B
- P(A ≥ B) = 0.5 当 A = B

**排序方法**:
```
对于多个区间 {A1, A2, ..., An}:
1. 计算两两可能度矩阵 P = [P(Ai ≥ Aj)]
2. 计算综合可能度: Si = Σ P(Ai ≥ Aj)
3. 按 Si 排序（越大越好）
```

#### 4.2 代码框架

```python
@dataclass
class PossibilityDegree:
    """可能度排序工具"""

    @staticmethod
    def calculate(a: Interval, b: Interval) -> float:
        """计算 P(a ≥ b)"""
        if a.lower >= b.upper:
            return 1.0
        if a.upper <= b.lower:
            return 0.0
        return (a.upper - b.lower) / (a.width + b.width)

    @staticmethod
    def rank(intervals: dict[str, Interval]) -> list[tuple[str, float]]:
        """对多个区间排序"""
        n = len(intervals)
        scores = {name: 0.0 for name in intervals}

        # 计算两两可能度
        for name_i, interval_i in intervals.items():
            for name_j, interval_j in intervals.items():
                if name_i != name_j:
                    scores[name_i] += PossibilityDegree.calculate(
                        interval_i, interval_j
                    )

        # 排序
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

---

### 5. 依赖管理

#### 5.1 核心依赖(无变化)

```
numpy>=1.20.0
pyyaml>=6.0
```

#### 5.2 可选依赖(v0.8+)

```
# 模糊数高级运算(可选)
scipy>=1.7.0  # 特征值分解,数值优化
```

**策略**: 区间/模糊基础功能使用 numpy,高级功能可选 scipy

---

## 权衡分析 (Trade-offs)

### 决策1: v0.7 功能范围调整 (2026-02-04)

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **原计划(全部算法区间版本)** | 功能完整 | 工作量大(19-24人日),风险高 | ❌ |
| **聚焦核心(VIKOR+可能度+TODIM)** | 风险可控,工期合理 | ELECTRE-I/PROMETHEE延迟 | ✅ 采用 |
| **聚焦模糊数** | 完成Phase2 | 区间扩展不完整 | ⚠️ 备选 |

**决策**: 聚焦核心(VIKOR+可能度+TODIM),工期11人日

### 决策2: Phase 2 (模糊数基础) 调整 (2026-02-04)

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **v0.6 按原计划执行** | 完成Phase2 | 群决策功能延迟 | ❌ |
| **v0.6 优先群决策** | 满足用户需求 | Phase2延迟 | ✅ 采用 |
| **Phase2 拆分到 v0.6-v0.7** | 渐进式实施 | 工期管理复杂 | ⚠️ |

**决策**: Phase 2 延迟到 v0.8,v0.6 优先群决策

### 决策3: 何时引入区间/模糊支持?

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **v0.5 全面支持** | 一步到位 | 工作量大(20+人日),风险高 | ❌ |
| **v0.5 只支持 TOPSIS** | 快速验证,降低风险 | 算法覆盖不全 | ✅ Phase1 采用 |
| **推迟到 v1.0** | 避免过早优化 | 延迟用户需求 | ❌ |

**决策**: 分阶段实施,v0.5 TOPSIS, v0.7 VIKOR/TODIM, v0.8 模糊数

### 决策4: 如何处理区间排序?

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **中点法** | 简单,易理解 | 丢失区间信息 | ✅ Phase1 采用 |
| **可能度法** | 精确,保序 | 计算复杂 | ✅ Phase2 (v0.7) 采用 |
| **期望-方差法** | 考虑风险 | 参数敏感 | ⚠️ 可选 |

**决策**: Phase1 使用中点法,Phase2 (v0.7) 引入可能度法

### 决策5: 如何与现有算法集成?

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
5. **灵活调整**: v0.7 聚焦核心,风险可控

### 负面影响 ⚠️

1. **复杂度增加**: 代码量增加 50%+
2. **学习曲线**: 用户需要理解区间/模糊概念
3. **性能下降**: 区间运算比精确数慢 2-3 倍
4. **测试负担**: 需要大量区间/模糊测试用例
5. **功能延迟**: ELECTRE-I/PROMETHEE 区间版本延迟到 v0.9

### 缓解措施 🛡️

1. **默认关闭**: 区间/模糊功能显式启用
2. **文档完善**: 提供教程和示例
3. **性能优化**: 使用 numpy 向量化运算
4. **测试覆盖**: 区间/模糊测试覆盖率 >= 80%
5. **技术验证**: Phase 0 验证关键风险点

---

## 未来演进

### ✅ v0.5: 区间数基础 (已完成)
- Interval 数据类型
- 区间算术运算
- TOPSIS 区间版本
- 中点法排序

### ✅ v0.6: 群决策功能 (已完成)
- 群决策基础模型
- PCA 主成分分析
- 高级聚合方法
- 德尔菲法

### 🔥 v0.7: 渐进式扩展 (当前版本)
- Phase 0: 技术验证 (2人日)
- Phase 1: VIKOR 区间版本 (3人日)
- Phase 2: 可能度排序 (4人日)
- Phase 3: TODIM 区间版本 (4人日)
- Phase 4: 集成与文档 (2人日)
- **总工期**: 11 人日

### 📋 v0.8: 模糊数基础 (已规划)
- TriangularFuzzy 数据类型
- 模糊算术运算
- TOPSIS 模糊版本
- 重心法去模糊

### 🚀 v0.9+: 全面扩展 (可选)
- ELECTRE-I 区间版本
- PROMETHEE 区间版本
- 其他算法模糊版本

### 🎯 v1.0: 生产就绪
- Web UI 支持区间/模糊输入
- 导出报告
- 可视化区间结果

---

## 变更历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2026-02-03 | v1.0 | 初始版本,提出3阶段架构 | AI architect |
| 2026-02-04 | v2.0 | 更新v0.7规划,调整功能范围,增加可能度排序,调整工期估算 | AI architect |

---

## 参考资料

### 学术文献
- [Interval TOPSIS](https://www.sciencedirect.com/science/article/pii/S0957417416306298)
- [Fuzzy TOPSIS](https://www.sciencedirect.com/science/article/pii/S036083521100218X)
- [Interval Arithmetic](https://en.wikipedia.org/wiki/Interval_arithmetic)
- [Possibility Degree for Interval Ranking](https://www.sciencedirect.com/science/article/pii/S036083521100218X)

### 相关文档
- [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-004: 汇总算法架构设计](./004-mcda-aggregation-algorithms.md)
- [ADR-009: v0.5 版本规划调整](./009-v0.5-roadmap-adjustment.md)
- [ADR-010: v0.7 规划调整](./010-v0.7-roadmap-adjustment.md) (待创建)
- [v0.7 执行计划](../plans/mcda-core/v0.7/execution-plan.md)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-02-03
**更新日期**: 2026-02-04
**状态**: ✅ 已接受 (v2.0)
**预计工期**: Phase1 (4人日) ✅ + Phase2 (调整到v0.8) + Phase3 (11人日) = 15 人日
