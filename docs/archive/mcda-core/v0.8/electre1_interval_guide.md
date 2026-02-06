# ELECTRE-I 区间版本算法使用指南

**算法名称**: ELECTRE-I（Elimination Et Choix Traduisant la Réalité）区间版本
**实现文件**: `mcda_core.algorithms.ELECTRE1IntervalAlgorithm`
**适用场景**: 不确定性环境下的多准则决策

---

## 📖 算法简介

ELECTRE-I 是一种基于级别优于关系（Outranking Relation）的多准则决策方法。区间版本扩展了原算法，支持使用区间数表示不确定性和模糊性。

### 核心特点

- ✅ **处理不确定性**: 使用区间数表示评分的不确定性
- ✅ **级别优于关系**: 基于和谐度和不和谐度判断方案的优劣
- ✅ **核提取**: 提供非被优方案集合（核），而不是完全排序
- ✅ **灵活的阈值**: 可调整和谐度和不和谐度阈值
- ✅ **混合准则**: 同时支持效益型和成本型准则

---

## 🧮 数学模型

### 1. 区间和谐指数

对于两个方案 A_i 和 A_j，和谐指数表示 A_i 不劣于 A_j 的程度：

```
C(A_i, A_j) = Σ w_k · c_k(A_i, A_j) / Σ w_k
```

其中：
- `w_k` 是准则 k 的权重
- `c_k(A_i, A_j)` 是指示函数，基于区间中点比较：
  - 如果 A_i 在准则 k 上不劣于 A_j，则 c_k = 1
  - 否则 c_k = 0

### 2. 区间不和谐指数

不和谐指数表示 A_i 在某些准则上劣于 A_j 的最大程度：

```
D(A_i, A_j) = max_k [d_k(A_i, A_j)]
```

其中：
- 对于效益型准则：如果 A_i^L < A_j^U，则 d_k = (A_j^U - A_i^L) / range_k
- 对于成本型准则：如果 A_i^U > A_j^L，则 d_k = (A_i^U - A_j^L) / range_k
- `range_k` 是准则 k 的取值范围

### 3. 可信度

级别优于关系的可信度：

```
σ(A_i, A_j) = 1  如果 C(A_i, A_j) ≥ α 且 D(A_i, A_j) ≤ β
σ(A_i, A_j) = 0  否则
```

参数说明：
- `α` (alpha): 和谐度阈值，推荐值 0.5-0.7
- `β` (beta): 不和谐度阈值，推荐值 0.2-0.4

### 4. 核提取

核（Kernel）是所有非被优方案的集合：

```
Kernel = {A_i | 不存在 j 使得 σ(A_j, A_i) = 1}
```

核中的方案在某种意义上都是"最优"的，它们之间不一定可比较。

---

## 💡 使用示例

### 基础示例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import ELECTRE1IntervalAlgorithm

# 定义备选方案
alternatives = ("A1", "A2", "A3")

# 定义准则
criteria = (
    Criterion(name="质量", weight=0.6, direction="higher_better"),
    Criterion(name="价格", weight=0.4, direction="lower_better"),
)

# 定义评分矩阵（区间数）
scores = {
    "A1": {"质量": Interval(7.0, 9.0), "价格": Interval(80.0, 100.0)},
    "A2": {"质量": Interval(8.0, 9.0), "价格": Interval(90.0, 110.0)},
    "A3": {"质量": Interval(6.0, 8.0), "价格": Interval(70.0, 90.0)},
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=alternatives,
    criteria=criteria,
    scores=scores
)

# 执行 ELECTRE-I 区间版本
algo = ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
result = algo.calculate(problem)

# 查看结果
print("排名:")
for item in result.rankings:
    print(f"  {item.rank}. {item.alternative}: {item.score:.4f}")

print("\n核（非被优方案）:", result.metadata.metrics["kernel"])
```

输出：
```
排名:
  1. A1: 2.0000
  2. A2: 1.0000
  3. A3: 0.0000

核（非被优方案）: ['A1']
```

### 供应商选择案例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import ELECTRE1IntervalAlgorithm

# 供应商选择问题
alternatives = ("供应商A", "供应商B", "供应商C", "供应商D")

criteria = (
    Criterion(name="质量", weight=0.35, direction="higher_better"),
    Criterion(name="价格", weight=0.25, direction="lower_better"),
    Criterion(name="交付期", weight=0.20, direction="lower_better"),
    Criterion(name="服务", weight=0.20, direction="higher_better"),
)

# 区间评分（反映不确定性）
scores = {
    "供应商A": {
        "质量": Interval(70.0, 90.0),
        "价格": Interval(80.0, 100.0),
        "交付期": Interval(5.0, 10.0),
        "服务": Interval(60.0, 80.0),
    },
    "供应商B": {
        "质量": Interval(80.0, 90.0),
        "价格": Interval(90.0, 100.0),
        "交付期": Interval(7.0, 12.0),
        "服务": Interval(70.0, 90.0),
    },
    "供应商C": {
        "质量": Interval(60.0, 80.0),
        "价格": Interval(70.0, 90.0),
        "交付期": Interval(3.0, 7.0),
        "服务": Interval(50.0, 70.0),
    },
    "供应商D": {
        "质量": Interval(70.0, 80.0),
        "价格": Interval(85.0, 100.0),
        "交付期": Interval(6.0, 11.0),
        "服务": Interval(80.0, 90.0),
    },
}

problem = DecisionProblem(
    alternatives=alternatives,
    criteria=criteria,
    scores=scores
)

algo = ELECTRE1IntervalAlgorithm(alpha=0.65, beta=0.35)
result = algo.calculate(problem)

# 输出结果
print("=== 供应商选择结果 ===\n")

print("排名:")
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}")

kernel = result.metadata.metrics["kernel"]
print(f"\n推荐供应商（核）: {', '.join(kernel)}")

if len(kernel) == 1:
    print(f"\n最佳选择: {kernel[0]}")
else:
    print(f"\n核中有 {len(kernel)} 个供应商，建议进一步分析。")
```

---

## ⚙️ 参数说明

### 构造函数参数

```python
ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
```

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `alpha` | float | 0.6 | (0, 1] | 和谐度阈值，值越高越严格 |
| `beta` | float | 0.3 | [0, 1] | 不和谐度阈值，值越低越严格 |

### calculate 方法参数

```python
result = algo.calculate(problem, alpha=None, beta=None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `problem` | DecisionProblem | 必需 | 决策问题 |
| `alpha` | float | None | 和谐度阈值（覆盖构造函数的值） |
| `beta` | float | None | 不和谐度阈值（覆盖构造函数的值） |

---

## 🎯 参数调优建议

### Alpha（和谐度阈值）

- **宽松 (0.5-0.6)**: 容易建立级别优于关系，核较大
- **中等 (0.6-0.7)**: 平衡选择，推荐值
- **严格 (0.7-0.9)**: 难以建立级别优于关系，核较小

### Beta（不和谐度阈值）

- **宽松 (0.3-0.5)**: 容忍较大的不和谐
- **中等 (0.2-0.3)**: 平衡选择，推荐值
- **严格 (0.0-0.2)**: 不容忍不和谐

### 组合策略

| 策略 | Alpha | Beta | 效果 |
|------|-------|------|------|
| 宽松 | 0.5 | 0.4 | 核较大，包含更多方案 |
| 平衡 | 0.6 | 0.3 | 推荐设置 |
| 严格 | 0.7 | 0.2 | 核较小，只包含明显优的方案 |

---

## 📊 结果解读

### RankingItem

```python
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}: {item.score}")
```

- `item.alternative`: 备选方案名称
- `item.rank`: 排名（核内方案排名靠前）
- `item.score`: 优势度（可信度总和，越高越好）

### 元数据

```python
metadata = result.metadata.metrics

# 访问和谐矩阵
concordance = metadata["concordance_matrix"]

# 访问不和谐矩阵
discordance = metadata["discordance_matrix"]

# 访问可信度矩阵
credibility = metadata["credibility_matrix"]

# 访问核
kernel = metadata["kernel"]
```

### 核（Kernel）

核是 ELECTRE-I 的核心概念，表示所有非被优方案的集合：

- **核大小 = 1**: 有明确的最优方案
- **核大小 > 1**: 有多个"最优"方案，需要进一步分析
- **核包含所有方案**: 所有方案都不相上下

---

## ⚠️ 注意事项

### 1. 区间数表示

使用 `Interval` 类表示区间数：

```python
from mcda_core.interval import Interval

# 创建区间
interval = Interval(lower=2.0, upper=5.0)

# 访问属性
print(interval.lower)     # 2.0
print(interval.upper)     # 5.0
print(interval.midpoint)  # 3.5
print(interval.width)     # 3.0
```

### 2. 准则方向

- **higher_better**: 效益型准则，值越大越好（如质量）
- **lower_better**: 成本型准则，值越小越好（如价格）

### 3. 权重归一化

准则权重会自动归一化，无需手动处理：

```python
# 权重会自动归一化
criteria = (
    Criterion(name="C1", weight=0.6, direction="higher_better"),
    Criterion(name="C2", weight=0.4, direction="higher_better"),
)
# 有效权重: C1=0.6, C2=0.4
```

### 4. 评分范围

区间评分应在合理范围内（通常 [0, 100]），超出范围会触发验证错误。

---

## 🔗 相关算法

- **ELECTRE-I（精确值版本）**: `electre1` 函数
- **VIKOR 区间版本**: `IntervalVIKORAlgorithm`
- **PROMETHEE II 区间版本**: `PROMETHEE2IntervalAlgorithm`

---

## 📚 参考文献

1. Roy, B. (1968). "Classement et choix en présence de points de vue multiples"
2. Roy, B., & Bertier, P. (1971). "La méthode ELECTRE II"
3. 区间 ELECTRE 方法扩展研究

---

**最后更新**: 2026-02-04
**版本**: v0.8
**作者**: AI (Claude Sonnet 4.5)
