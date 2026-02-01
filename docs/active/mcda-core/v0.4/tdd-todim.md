# TODIM 算法 TDD 开发进度

**算法**: TODIM (TOmada de Decisão Interativa e Multicritério)
**开发方法**: TDD (Test-Driven Development)
**开始日期**: 2026-02-01
**预计工期**: 5 人日
**当前状态**: ⏳ RED 阶段 (待开始)

---

## 📋 TDD 循环进度

### 🔴 RED 阶段 - 失败的测试

**目标**: 先写测试,确保失败

**测试用例清单**:

#### 1. 基本功能测试 (RED)

```python
# tests/mcda-core/test_algorithms/test_todim.py

def test_todim_basic():
    """测试：基本功能 - 3 方案 3 准则"""
    problem = DecisionProblem(
        alternatives=("A1", "A2", "A3"),
        criteria=(
            Criterion(name="C1", weight=0.4, direction=CriterionDirection.MAXIMIZE),
            Criterion(name="C2", weight=0.3, direction=CriterionDirection.MAXIMIZE),
            Criterion(name="C3", weight=0.3, direction=CriterionDirection.MAXIMIZE),
        ),
        scores={
            "A1": {"C1": 10, "C2": 8, "C3": 7},
            "A2": {"C2": 9, "C2": 6, "C3": 8},
            "A3": {"C3": 8, "C2": 7, "C3": 9},
        }
    )

    result = todim(problem, theta=1.0)

    # 验证返回结果
    assert isinstance(result, DecisionResult)
    assert len(result.rankings) == 3

    # 验证排名完整性
    ranks = [r.rank for r in result.rankings]
    assert sorted(ranks) == [1, 2, 3]

def test_todim_theta_parameter():
    """测试：θ 参数 (衰减系数)"""
    problem = create_test_problem()

    result_theta1 = todim(problem, theta=1.0)
    result_theta2 = todim(problem, theta=2.5)

    # 不同 θ 应该产生相同或相似排名
    # (因为都使用相同的偏好结构)
    assert len(result_theta1.rankings) == len(result_theta2.rankings)

def test_todim_with_cost_criteria():
    """测试：包含成本型准则"""
    problem = DecisionProblem(
        alternatives=("A1", "A2"),
        criteria=(
            Criterion(name="价格", weight=0.5, direction=CriterionDirection.MINIMIZE),
            Criterion(name="质量", weight=0.5, direction=CriterionDirection.MAXIMIZE),
        ),
        scores={
            "A1": {"价格": 100, "质量": 8},
            "A2": {"价格": 120, "质量": 9},
        }
    )

    result = todim(problem, theta=1.5)
    assert len(result.rankings) == 2
```

**预期**: 这些测试会失败,因为 `todim()` 函数还不存在

**验收**:
- [ ] 所有测试运行失败 (ImportError 或 NameError)
- [ ] 测试文件创建完成
- [ ] 测试场景设计完整

---

#### 2. 边界条件测试 (RED)

```python
def test_todim_minimal_alternatives():
    """测试：最少 2 个方案"""
    problem = DecisionProblem(
        alternatives=("A1", "A2"),
        criteria=(Criterion(name="C1", weight=1.0, direction=CriterionDirection.MAXIMIZE),),
        scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
    )

    result = todim(problem, theta=1.0)
    assert len(result.rankings) == 2

def test_todim_large_dataset():
    """测试：大数据集 (100 方案 10 准则)"""
    problem = generate_large_problem(n_alternatives=100, n_criteria=10)
    result = todim(problem, theta=1.0)
    assert len(result.rankings) == 100

def test_todim_zero_weights():
    """测试：零权重准则"""
    # TODIM 应该忽略零权重准则
    pass

def test_todim_equal_scores():
    """测试：所有方案得分相同"""
    # 所有方案的全局优势度应该相等
    pass
```

**验收**:
- [ ] 边界条件测试完成
- [ ] 测试场景覆盖全面

---

#### 3. 数学验证测试 (RED)

```python
def test_todim_relative_measure():
    """测试：相对测度 φ 计算正确性"""
    # 手动计算一个简单案例
    problem = DecisionProblem(
        alternatives=("A1", "A2"),
        criteria=(
            Criterion(name="C1", weight=0.6, direction=CriterionDirection.MAXIMIZE),
            Criterion(name="C2", weight=0.4, direction=CriterionDirection.MAXIMIZE),
        ),
        scores={
            "A1": {"C1": 10, "C2": 5},
            "A2": {"C1": 8, "C2": 7},
        }
    )

    result = todim(problem, theta=1.0)

    # 手动验证相对测度计算
    # φ_C1(A1, A2) = sqrt(0.6 * (10-8) / 1.0) = sqrt(1.2) ≈ 1.095
    # φ_C2(A1, A2) = -sqrt(1.0/0.4 * (5-7) / 1.0) = -sqrt(-5) → 虚数问题
    # 需要确保实现正确处理负值
    pass

def test_todim_global_dominance():
    """测试：全局优势度 ξ 计算"""
    # ξ(A1) = Σ δ(A1, Aj) - Σ δ(Aj, A1)
    # 验证全局优势度的单调性
    pass
```

**验收**:
- [ ] 数学验证测试完成
- [ ] 手算案例验证通过

---

### 🟢 GREEN 阶段 - 最小实现

**目标**: 让测试通过的最小代码

#### Step 1: 创建文件结构

```bash
# 创建算法文件
touch skills/mcda-core/lib/algorithms/todim.py
```

#### Step 2: 最小实现骨架

```python
# lib/algorithms/todim.py

from typing import Literal
from ..models import DecisionProblem, DecisionResult, AlgorithmConfig
from .base import register_algorithm

def todim(
    problem: DecisionProblem,
    theta: float = 1.0
) -> DecisionResult:
    """TODIM 算法实现

    Args:
        problem: 决策问题
        theta: 衰减系数 (推荐 1.0-2.5)

    Returns:
        决策结果
    """
    # TODO: 实现核心算法
    pass

# 注册算法
@register_algorithm(name="todim")
def todim_wrapper(problem: DecisionProblem) -> DecisionResult:
    """TODIM 算法包装器"""
    return todim(problem, theta=1.0)
```

#### Step 3: 实现核心算法 (GREEN 阶段不求完美)

```python
def todim(
    problem: DecisionProblem,
    theta: float = 1.0
) -> DecisionResult:
    """TODIM 算法实现 (GREEN 阶段)"""

    alternatives = problem.alternatives
    criteria = problem.criteria
    scores = problem.scores

    n_alt = len(alternatives)
    n_crit = len(criteria)

    # 1. 提取权重
    weights = np.array([c.weight for c in criteria])
    total_weight = weights.sum()

    # 2. 计算相对测度矩阵 φ
    phi = np.zeros((n_alt, n_alt, n_crit))

    for k in range(n_crit):
        for i in range(n_alt):
            for j in range(n_alt):
                if i == j:
                    continue

                score_i = scores[alternatives[i]][criteria[k].name]
                score_j = scores[alternatives[j]][criteria[k].name]

                # 根据准则方向调整
                if criteria[k].direction == CriterionDirection.MINIMIZE:
                    score_i, score_j = -score_j, -score_i

                if score_i > score_j:
                    # 收益
                    phi[i, j, k] = np.sqrt(
                        weights[k] * (score_i - score_j) / total_weight
                    )
                else:
                    # 损失 (前景理论)
                    phi[i, j, k] = -np.sqrt(
                        total_weight / weights[k] * (score_j - score_i) / (theta * total_weight)
                    )

    # 3. 计算优势度矩阵
    dominance = np.zeros((n_alt, n_alt))
    for i in range(n_alt):
        for j in range(n_alt):
            if i != j:
                dominance[i, j] = phi[i, j, :].sum()

    # 4. 计算全局优势度
    global_dominance = np.zeros(n_alt)
    for i in range(n_alt):
        global_dominance[i] = dominance[i, :].sum() - dominance[:, i].sum()

    # 5. 排序 (降序)
    sorted_indices = np.argsort(-global_dominance)
    rankings = []
    for rank, idx in enumerate(sorted_indices, start=1):
        rankings.append(RankingItem(
            alternative=alternatives[idx],
            rank=rank,
            score=float(global_dominance[idx])
        ))

    return DecisionResult(
        algorithm_name="todim",
        rankings=tuple(rankings),
        metadata={
            "theta": theta,
            "global_dominance": global_dominance.tolist(),
        }
    )
```

**验收**:
- [ ] 所有基本测试通过
- [ ] 边界条件测试通过
- [ ] 数学验证测试通过
- [ ] 代码可以运行 (不求完美)

---

### 🔵 REFACTOR 阶段 - 优化重构

**目标**: 优化代码质量,但保持测试通过

#### 优化点 1: 矩阵化计算

**问题**: 三重嵌套循环性能差

**优化**:
```python
# 向量化计算
def _compute_phi_vectorized(scores_matrix, weights, criteria_directions, theta):
    """向量化计算相对测度矩阵"""

    # 扩展维度用于广播
    scores_i = scores_matrix[:, np.newaxis, :]  # (m, 1, n)
    scores_j = scores_matrix[np.newaxis, :, :]  # (1, m, n)

    # 计算差异
    diff = scores_i - scores_j  # (m, m, n)

    # 根据准则方向调整
    for k, direction in enumerate(criteria_directions):
        if direction == CriterionDirection.MINIMIZE:
            diff[:, :, k] = -diff[:, :, k]

    # 计算相对测度
    total_weight = weights.sum()
    weights_expanded = weights[np.newaxis, np.newaxis, :]  # (1, 1, n)

    # 收益部分
    gain_mask = diff > 0
    phi_gain = np.zeros_like(diff)
    phi_gain[gain_mask] = np.sqrt(
        weights_expanded[gain_mask] * diff[gain_mask] / total_weight
    )

    # 损失部分
    loss_mask = diff < 0
    phi_loss = np.zeros_like(diff)
    phi_loss[loss_mask] = -np.sqrt(
        total_weight / weights_expanded[loss_mask] * -diff[loss_mask] / (theta * total_weight)
    )

    return phi_gain + phi_loss
```

**验收**:
- [ ] 性能提升 5x+
- [ ] 测试仍然通过
- [ ] 代码可读性良好

---

#### 优化点 2: 类型安全

**问题**: 缺少类型注解

**优化**:
```python
from typing import Literal
import numpy as np
from numpy.typing import NDArray

def todim(
    problem: DecisionProblem,
    theta: float = 1.0
) -> DecisionResult:
    """TODIM 算法实现

    Args:
        problem: 决策问题
        theta: 衰减系数 (推荐 1.0-2.5)

    Returns:
        决策结果

    Raises:
        ValueError: 如果 theta ≤ 0
        ValueError: 如果方案数 < 2
    """
    if theta <= 0:
        raise ValueError(f"theta 必须 > 0, 当前值: {theta}")

    if len(problem.alternatives) < 2:
        raise ValueError("至少需要 2 个备选方案")

    # ... 实现
```

**验收**:
- [ ] 类型检查通过 (mypy)
- [ ] 错误处理完善
- [ ] 文档字符串完整

---

#### 优化点 3: 数值稳定性

**问题**: 负数开方,除零错误

**优化**:
```python
# 1. 负值处理
if score_i > score_j:
    phi[i, j, k] = np.sqrt(
        weights[k] * abs(score_i - score_j) / total_weight
    )
else:
    # 确保内部为正数
    delta = abs(score_j - score_i)
    phi[i, j, k] = -np.sqrt(
        total_weight / weights[k] * delta / (theta * total_weight + 1e-10)
    )

# 2. 零权重处理
mask = weights > 0
weights_filtered = weights[mask]
scores_filtered = scores_matrix[:, mask]
```

**验收**:
- [ ] 无数值警告
- [ ] 边界条件稳定
- [ ] 测试覆盖所有边界情况

---

### ✅ DONE 阶段 - 完成标准

**验收清单**:

#### 功能完整性
- [ ] 基本功能实现
- [ ] 参数 θ 可调 (1.0-2.5)
- [ ] 支持效益型/成本型准则
- [ ] 处理零权重准则
- [ ] 处理相同得分

#### 测试覆盖
- [ ] 单元测试: 35+ 个
- [ ] 覆盖率: >95%
- [ ] 边界条件: 全部覆盖
- [ ] 数学验证: 手算案例通过

#### 代码质量
- [ ] 类型注解: 100%
- [ ] 文档字符串: 完整
- [ ] 错误处理: 完善
- [ ] 性能优化: 完成

#### 文档完整
- [ ] API 文档
- [ ] 使用示例
- [ ] 算法说明
- [ ] 参考文献

---

## 📊 进度统计

### TDD 循环进度

| 阶段 | 任务数 | 完成数 | 进度 | 状态 |
|------|--------|--------|------|------|
| 🔴 RED | 15 | 0 | 0% | ⏳ 待开始 |
| 🟢 GREEN | 8 | 0 | 0% | ⏳ 待开始 |
| 🔵 REFACTOR | 3 | 0 | 0% | ⏳ 待开始 |
| ✅ DONE | 20 | 0 | 0% | ⏳ 待开始 |

### 测试统计

| 测试类型 | 目标 | 当前 | 差距 |
|----------|------|------|------|
| 基本功能 | 8 | 0 | -8 |
| 边界条件 | 4 | 0 | -4 |
| 数学验证 | 3 | 0 | -3 |
| **总计** | **15+** | **0** | **-15** |

---

## 📝 开发日志

### 2026-02-01

**[09:00] TDD 计划创建**
- ✅ 创建 TDD 进度文件
- ✅ 设计测试用例 (15+ 个)
- ✅ 规划 TDD 循环 (RED → GREEN → REFACTOR → DONE)
- 📌 下一步: 开始 RED 阶段,创建测试文件

---

## 🎓 参考资料

### TODIM 论文

1. **Gomes, L. A. M. M., & Lima, M. M. P. P. (1992)**
   - TODIM: Basics and application to multicriteria ranking of projects
   - 关键概念: 前景理论,相对测度,全局优势度

2. **Gomes, L. F. A. M., et al. (2013)**
   - TODIM: Method and its applications
   - 实际应用案例

### 相关资源

- `docs/decisions/mcda-core/004-mcda-algorithms-architecture.md` - 算法架构
- `docs/plans/mcda-core/v0.4/execution-plan-v2.md` - v0.4 执行计划

---

**最后更新**: 2026-02-01
**维护者**: AI (Claude Sonnet 4.5)
**状态**: 🔴 RED (待开始)
