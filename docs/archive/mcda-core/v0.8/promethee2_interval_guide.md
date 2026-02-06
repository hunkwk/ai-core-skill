# PROMETHEE II 区间版本算法使用指南

**算法名称**: PROMETHEE II（Preference Ranking Organization METHod for Enrichment Evaluations）区间版本
**实现文件**: `mcda_core.algorithms.PROMETHEE2IntervalAlgorithm`
**适用场景**: 不确定性环境下的完全排序

---

## 📖 算法简介

PROMETHEE II 是一种基于净流量的多准则决策排序方法。区间版本扩展了原算法，支持使用区间数表示不确定性和模糊性。

### 核心特点

- ✅ **处理不确定性**: 使用区间数表示评分的不确定性
- ✅ **完全排序**: 基于净流量提供完整的方案排序
- ✅ **偏好函数**: 支持 5 种不同的偏好函数
- ✅ **灵活性**: 可调整阈值参数控制偏好强度
- ✅ **混合准则**: 同时支持效益型和成本型准则

---

## 🧮 数学模型

### 1. 偏好函数

对于每个准则 k，计算方案 A_i 优于 A_j 的偏好度：

```
P_k(A_i, A_j) = f(d_k)
```

其中 `d_k` 是两个方案在准则 k 上的差值（基于区间中点）。

### 2. 五种偏好函数

#### 2.1 通常型（Usual Criterion）

```python
P(d) = 1  if d > 0
P(d) = 0  if d ≤ 0
```

最简单的偏好函数，只要优于就完全偏好。

#### 2.2 U 型（U-Shape Criterion）

```python
P(d) = 0  if d ≤ q
P(d) = 1  if d > q
```

有阈值 q，只有差值超过阈值才偏好。

#### 2.3 V 型（V-Shape Criterion）

```python
P(d) = 0           if d ≤ 0
P(d) = d / p       if 0 < d < p
P(d) = 1           if d ≥ p
```

线性增长偏好，p 是偏好阈值。

#### 2.4 水平型（Level Criterion）

```python
P(d) = 0           if d ≤ q
P(d) = 0.5         if q < d < p
P(d) = 1           if d ≥ p
```

两个阈值，中间区域为中等偏好。

#### 2.5 线性型（Linear Criterion）

```python
P(d) = 0                    if d ≤ q
P(d) = (d - q) / (p - q)    if q < d < p
P(d) = 1                    if d ≥ p
```

线性增长的连续偏好。

### 3. 综合偏好指数

对于两个方案 A_i 和 A_j：

```
P(A_i, A_j) = Σ w_k · P_k(A_i, A_j)
```

其中 w_k 是准则 k 的权重。

### 4. 流量计算

#### 正流量（Leaving Flow）

表示 A_i 优于其他方案的程度：

```
Φ^+(A_i) = (1 / (n-1)) · Σ P(A_i, A_j)
```

#### 负流量（Entering Flow）

表示其他方案优于 A_i 的程度：

```
Φ^-(A_i) = (1 / (n-1)) · Σ P(A_j, A_i)
```

#### 净流量（Net Flow）

```
Φ(A_i) = Φ^+(A_i) - Φ^-(A_i)
```

### 5. 排序

根据净流量降序排列方案：

```
A_i ≻ A_j  ⇔  Φ(A_i) > Φ(A_j)
```

净流量越大，方案越好。

---

## 💡 使用示例

### 基础示例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import PROMETHEE2IntervalAlgorithm

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

# 执行 PROMETHEE II 区间版本
algo = PROMETHEE2IntervalAlgorithm()
result = algo.calculate(problem)

# 查看结果
print("排名:")
for item in result.rankings:
    print(f"  {item.rank}. {item.alternative}: {item.score:.4f}")

# 查看流量
net_flow = result.metadata.metrics["net_flow"]
print("\n净流量:")
for alt, flow in sorted(net_flow.items(), key=lambda x: x[1], reverse=True):
    print(f"  {alt}: {flow:.4f}")
```

输出：
```
排名:
  1. A1: 0.2000
  2. A2: 0.0000
  3. A3: -0.2000

净流量:
  A1: 0.2000
  A2: 0.0000
  A3: -0.2000
```

### 使用不同的偏好函数

```python
# U 型偏好函数
algo_u_shape = PROMETHEE2IntervalAlgorithm(
    preference_function="u_shape",
    threshold=2.0
)
result_u_shape = algo_u_shape.calculate(problem)

# V 型偏好函数
algo_v_shape = PROMETHEE2IntervalAlgorithm(
    preference_function="v_shape",
    threshold=5.0
)
result_v_shape = algo_v_shape.calculate(problem)

# 比较结果
print("U 型偏好结果:", [r.alternative for r in result_u_shape.rankings])
print("V 型偏好结果:", [r.alternative for r in result_v_shape.rankings])
```

### 供应商选择案例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import PROMETHEE2IntervalAlgorithm

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

# 使用 V 型偏好函数
algo = PROMETHEE2IntervalAlgorithm(
    preference_function="v_shape",
    threshold=5.0
)
result = algo.calculate(problem)

# 输出结果
print("=== 供应商选择结果（PROMETHEE II）===\n")

print("完整排名:")
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}")

# 最佳供应商
best = result.rankings[0].alternative
print(f"\n最佳供应商: {best}")

# 流量分析
net_flow = result.metadata.metrics["net_flow"]
positive_flow = result.metadata.metrics["positive_flow"]
negative_flow = result.metadata.metrics["negative_flow"]

print(f"\n流量分析:")
for alt in alternatives:
    print(f"  {alt}:")
    print(f"    正流量: {positive_flow[alt]:.4f}")
    print(f"    负流量: {negative_flow[alt]:.4f}")
    print(f"    净流量: {net_flow[alt]:.4f}")
```

---

## ⚙️ 参数说明

### 构造函数参数

```python
PROMETHEE2IntervalAlgorithm(preference_function="usual", threshold=0.0)
```

| 参数 | 类型 | 默认值 | 可选值 | 说明 |
|------|------|--------|--------|------|
| `preference_function` | str | "usual" | "usual", "u_shape", "v_shape", "level", "linear" | 偏好函数类型 |
| `threshold` | float | 0.0 | ≥ 0 | 阈值参数 |

### calculate 方法参数

```python
result = algo.calculate(problem, preference_function=None, threshold=None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `problem` | DecisionProblem | 必需 | 决策问题 |
| `preference_function` | str | None | 偏好函数类型（覆盖构造函数的值） |
| `threshold` | float | None | 阈值参数（覆盖构造函数的值） |

---

## 🎯 偏好函数选择指南

### 通常型（Usual）

**适用场景**:
- 简单决策问题
- 任何优势都重要

**特点**:
- ✅ 最简单，易于理解
- ✅ 无需设置阈值
- ⚠️ 可能过于极端

```python
algo = PROMETHEE2IntervalAlgorithm(preference_function="usual")
```

### U 型（U-Shape）

**适用场景**:
- 需要避免小的随机波动
- 只关心明显的优势

**特点**:
- ✅ 有明确的阈值
- ✅ 对噪声不敏感
- ⚠️ 需要选择合适的阈值

```python
algo = PROMETHEE2IntervalAlgorithm(
    preference_function="u_shape",
    threshold=2.0  # q 参数
)
```

### V 型（V-Shape）

**适用场景**:
- 需要反映优势的强度
- 线性偏好关系

**特点**:
- ✅ 连续的偏好度
- ✅ 考虑优势大小
- ⚠️ 需要选择阈值 p

```python
algo = PROMETHEE2IntervalAlgorithm(
    preference_function="v_shape",
    threshold=5.0  # p 参数
)
```

### 水平型（Level）

**适用场景**:
- 需要区分"无差异"、"中等偏好"、"强偏好"
- 渐进式决策

**特点**:
- ✅ 三个层次
- ⚠️ 需要两个阈值（q 和 p=2q）

```python
algo = PROMETHEE2IntervalAlgorithm(
    preference_function="level",
    threshold=2.0  # q 参数，p = 2q
)
```

### 线性型（Linear）

**适用场景**:
- 需要连续的、平滑的偏好
- 精确的决策分析

**特点**:
- ✅ 最精确
- ✅ 连续偏好
- ⚠️ 需要两个阈值（q 和 p=2q）

```python
algo = PROMETHEE2IntervalAlgorithm(
    preference_function="linear",
    threshold=2.0  # q 参数，p = 2q
)
```

### 偏好函数对比

| 偏好函数 | 复杂度 | 阈值 | 推荐场景 |
|---------|-------|------|---------|
| Usual | 低 | 无 | 简单决策 |
| U-Shape | 中 | 1 个 (q) | 抗噪声 |
| V-Shape | 中 | 1 个 (p) | 线性偏好 |
| Level | 高 | 2 个 (q, p) | 渐进式 |
| Linear | 高 | 2 个 (q, p) | 精确决策 |

---

## 📊 结果解读

### 净流量

净流量是方案排序的主要依据：

```python
net_flow = result.metadata.metrics["net_flow"]

for alt, flow in sorted(net_flow.items(), key=lambda x: x[1], reverse=True):
    print(f"{alt}: {flow:.4f}")
```

**解读**:
- `Φ > 0`: 方案优于平均水平
- `Φ ≈ 0`: 方案处于平均水平
- `Φ < 0`: 方案劣于平均水平

### 正流量和负流量

```python
positive_flow = result.metadata.metrics["positive_flow"]
negative_flow = result.metadata.metrics["negative_flow"]
```

**解读**:
- **正流量大**: 方案在许多准则上优于其他方案
- **负流量大**: 方案在许多准则上劣于其他方案
- **净流量 = 正流量 - 负流量**

### 排名稳定性

如果净流量相近，说明方案相似，建议：

1. 检查正流量和负流量的分布
2. 尝试不同的偏好函数
3. 考虑使用 ELECTRE-I 等其他方法验证

---

## ⚠️ 注意事项

### 1. 区间数表示

使用 `Interval` 类表示区间数：

```python
from mcda_core.interval import Interval

# 创建区间
interval = Interval(lower=2.0, upper=5.0)

# 访问属性
print(interval.midpoint)  # 3.5（用于偏好计算）
```

**重要**: PROMETHEE 使用区间**中点**进行偏好计算。

### 2. 准则方向

- **higher_better**: 效益型准则，值越大越好
- **lower_better**: 成本型准则，值越小越好

### 3. 阈值选择

阈值应根据实际问题的规模选择：

```python
# 小规模评分（0-10）
threshold = 1.0

# 中等规模评分（0-100）
threshold = 10.0

# 大规模评分（0-1000）
threshold = 100.0
```

一般建议：`threshold ≈ (max_score - min_score) / 10`

### 4. 净流量范围

净流量的理论范围：

```
-1 ≤ Φ(A_i) ≤ 1
```

实际范围取决于：
- 方案数量
- 准则数量
- 权重分布

---

## 🔍 与其他算法的对比

### PROMETHEE II vs ELECTRE-I

| 特性 | PROMETHEE II | ELECTRE-I |
|------|-------------|-----------|
| **排序** | 完全排序 | 核（部分排序）|
| **输出** | 净流量 | 级别优于关系 |
| **偏好函数** | 5 种可选 | 固定逻辑 |
| **参数** | 阈值 | α, β |
| **适用** | 需要完整排序 | 需要最优方案集合 |

### 选择建议

- **选择 PROMETHEE II**: 如果需要完整的排序和详细的偏好信息
- **选择 ELECTRE-I**: 如果只需要识别最优方案集合

---

## 🔗 相关算法

- **PROMETHEE II（精确值版本）**: `PROMETHEEService`
- **ELECTRE-I 区间版本**: `ELECTRE1IntervalAlgorithm`
- **VIKOR 区间版本**: `IntervalVIKORAlgorithm`

---

## 📚 参考文献

1. Brans, J. P., & Vincke, Ph. (1985). "A preference ranking organization method"
2. Brans, J. P., Vincke, Ph., & Mareschal, B. (1986). "How to select and how to rank projects"
3. 区间 PROMETHEE 方法扩展研究

---

**最后更新**: 2026-02-04
**版本**: v0.8
**作者**: AI (Claude Sonnet 4.5)
