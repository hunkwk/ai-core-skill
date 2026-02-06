# TDD: ELECTRE-I 区间版本

**版本**: v0.8
**阶段**: Phase 2.1 - ELECTRE-I 区间版本
**开始日期**: 2026-02-04
**状态**: ⏳ 待开始
**TDD 循环**: RED → GREEN → REFACTOR → DONE

---

## 📊 目标

实现 ELECTRE-I 算法的区间数版本，支持不确定性和模糊性决策。

### 工期: 4 人日

---

## 🚧 技术背景

### ELECTRE-I 算法回顾

**核心思想**: 级别优先关系（Outranking Relations）

**关键概念**:
- **和谐指数 (Concordance Index)**: 方案 a 在准则 j 上优于方案 b 的程度
- **不和谐指数 (Discordance Index)**: 方案 a 在准则 j 上劣于方案 b 的程度
- **级别优于关系**: a S b ⇔ C(a,b) ≥ λ 且 D(a,b) ≤ λ

### 区间扩展挑战

**数学模型**:
```
区间和谐指数: c_j(a,b) = f([a_j^L, a_j^U], [b_j^L, b_j^U])
区间不和谐指数: d_j(a,b) = g([a_j^L, a_j^U], [b_j^L, b_j^U])
```

**关键难点**:
1. 区间和谐/不和谐计算
2. 阈值 λ 的确定
3. 核提取算法的区间扩展

---

## 🚀 任务清单

### Phase 1: RED - 测试先行（0.5 人日）

**测试用例**（预估 20 个）:

#### 基础功能测试
- [ ] test_electre1_interval_algorithm_registration
- [ ] test_electre1_interval_basic_calculation
- [ ] test_electre1_interval_with_three_alternatives
- [ ] test_electre1_interval_with_four_criteria

#### 区间运算测试
- [ ] test_concordance_index_calculation
- [ ] test_discordance_index_calculation
- [ ] test_outranking_determination
- [ ] test_threshold_sensitivity

#### 可能度排序集成
- [ ] test_possibility_degree_integration
- [ ] test_ranking_with_intervals
- [ ] test_degenerate_intervals

#### 兼容性测试
- [ ] test_compatibility_with_crisp_electre1
- [ ] test_degenerate_intervals_act_like_crisp

#### 边界条件测试
- [ ] test_single_criterion
- [ ] test_equal_weights
- [ ] test_all_identical_scores
- [ ] test_extreme_intervals

#### 错误处理
- [ ] test_empty_weights
- [ ] test_invalid_intervals
- [ ] test_nan_values

**预期文件**:
- `tests/mcda-core/unit/test_algorithms/test_electre1_interval.py`

**验收**: 测试文件创建完成，所有测试失败（RED 状态）

---

### Phase 2: GREEN - 实现算法（2 人日）

**实现步骤**:

#### 步骤 1: 创建算法框架（0.3 人日）
```python
from .base import MCDAAlgorithm, register_algorithm
from .electre1 import ELECTRE1Error

@register_algorithm("electre1_interval")
class IntervalELECTRE1Algorithm(MCDAAlgorithm):
    """ELECTRE-I 区间版本算法"""

    def __init__(self, lambda_threshold: float = 0.5):
        self.lambda_threshold = lambda_threshold

    @property
    def name(self) -> str:
        return "electre1_interval"
```

#### 步骤 2: 实现区间和谐指数（0.5 人日）
```python
def _concordance_index(
    a_interval: Interval,
    b_interval: Interval,
    p_j: float,
    direction: str
) -> float:
    """计算单个准则的和谐指数"""
    if direction == "higher_better":
        # 计算 a 优于 b 的程度
        pass
    else:  # lower_better
        # 计算 a 优于 b 的程度（成本型）
        pass
```

#### 步骤 3: 实现区间不和谐指数（0.5 人日）
```python
def _discordance_index(
    a_interval: Interval,
    b_interval: Interval,
    p_j: float,
    direction: str,
    scale: float
) -> float:
    """计算单个准则的不和谐指数"""
    # 基于区间差不和谐度
    pass
```

#### 步骤 4: 实现核心算法（0.7 人日）
```python
def calculate(
    self,
    problem: "DecisionProblem",
    lambda_threshold: float = None,
    **kwargs
) -> "DecisionResult":
    """ELECTRE-I 区间版本计算"""
    # 1. 计算和谐指数矩阵
    # 2. 计算不和谐指数矩阵
    # 3. 确定级别优于关系
    # 4. 核提取
    # 5. 可能度排序
    pass
```

**验收**: 所有测试通过（GREEN 状态）

---

### Phase 3: REFACTOR - 重构优化（1 人日）

**重构任务**:
- [ ] 代码优化
- [ ] 性能优化（向量化）
- [ ] 边界条件处理
- [ ] 错误消息完善

**验收**: 代码质量提升，测试依然通过

---

### Phase 4: 集成与文档（0.5 人日）

**集成测试**:
- [ ] 与可能度排序集成
- [ ] 与其他算法对比
- [ ] 性能测试

**文档**:
- [ ] API 文档
- [ ] 使用示例
- [ ] 数学公式说明

**验收**: 集成测试通过，文档完整

---

## 📋 详细技术设计

### 数学模型

#### 1. 区间和谐指数

对于准则 j，方案 a 对 b 的和谐指数：

```
c_j(a,b) =
  if a_j^L ≥ b_j^L:
    min(1, (a_j^L - b_j^U) / (a_j^L - b_j^L + ε))
  else:
    min(1, (a_j^U - b_j^L) / (a_j^U - a_j^L + ε))
```

#### 2. 区间不和谐指数

```
d_j(a,b) =
  if a_j^L ≥ b_j^U:
    0  # 完全和谐
  elif a_j^U ≤ b_j^L:
    1  # 完全不和谐
  else:
    (b_j^L - a_j^U) / (b_j^L - a_j^L + ε)  # 部分不和谐
```

#### 3. 级别优于关系

```
a S b ⇔ C(a,b) ≥ λ 且 D(a,b) ≤ δ

其中:
- C(a,b) = Σ w_j · c_j(a,b)  (加权和谐指数)
- D(a,b) = Σ w_j · d_j(a,b)  (加权不和谐指数)
- λ: 阈值（通常 0.5-0.7）
- δ: 不和谐阈值（通常 0.2-0.3）
```

#### 4. 核提取

```
寻找最小支配集:
1. 计算所有方案的净优势
2. 选择优势最大的方案
3. 移除被支配方案
4. 重复直到找到核
```

---

## 🧪 测试策略

### 单元测试覆盖

| 类别 | 测试数 | 覆盖内容 |
|------|--------|----------|
| 基础功能 | 8 | 算法注册、基本计算 |
| 区间运算 | 6 | 和谐/不和谐指数计算 |
| 核提取 | 3 | 级优于关系、核提取 |
| 兼容性 | 2 | 精确数兼容 |
| 边界条件 | 4 | 单准则、等权重等 |
| 错误处理 | 2 | 异常输入 |
| **总计** | **25** | - |

### 性能测试

| 规模 | 目标 |
|------|------|
| 10 方案 × 10 准则 | < 1s |
| 50 方案 × 20 准则 | < 5s |

---

## ⚠️ 风险与缓解

### 风险 1: 学术支持不足

**描述**: ELECTRE-I 区间版本的学术文献可能不足

**缓解措施**:
- 参考 ELECTRE-I 精确数版本实现
- 与 ELECTRE-I 区间理论对照
- 如确实不可行，报告并调整方案

### 风险 2: 区间运算复杂度

**描述**: 区间和谐/不和谐指数计算可能复杂

**缓解措施**:
- 使用 NumPy 向量化
- 添加数值稳定性检查
- 充分的单元测试

---

## 📈 质量指标

### 测试目标
- 单元测试: ≥ 20 个
- 测试覆盖率: ≥ 85%
- 测试通过率: 100%

### 性能目标
- 10×10: < 1s
- 50×20: < 5s

### 代码质量
- 类型注解: 100%
- 代码规范: PEP 8
- 文档字符串: 完整

---

## 🚧 执行记录

### 2026-02-04 - 计划创建

**Action**: 创建 ELECTRE-I 区间版本 TDD 计划
**Status**: ⏳ 待开始
**Next**: 等待 Phase 1 完成后开始

---

## 🔗 相关链接

- [v0.8 执行计划](../../../plans/mcda-core/v0.8/execution-plan.md)
- [进度总结](./progress-summary.md)
- [Phase 1 验证](./tdd-phase1-validation.md)

---

**最后更新**: 2026-02-04
**更新者**: AI (Claude Sonnet 4.5)
**当前状态**: ⏳ 待开始 - 等待前置阶段完成
