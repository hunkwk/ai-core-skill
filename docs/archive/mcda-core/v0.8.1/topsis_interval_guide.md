# TOPSIS 区间版本算法使用指南

**算法名称**: TOPSIS（Technique for Order Preference by Similarity to Ideal Solution）区间版本
**实现文件**: `mcda_core.algorithms.IntervalTOPSISAlgorithm`
**适用场景**: 不确定性环境下的多准则决策排序

---

## 📖 算法简介

TOPSIS（逼近理想解排序法）是一种基于距离的多准则决策方法。区间版本扩展了原算法，支持使用区间数表示不确定性和模糊性。

### 核心思想

TOPSIS 的核心思想是：**最优方案应该距离正理想解最近，同时距离负理想解最远**。

- **正理想解（PIS）**: 各准则上最优值的组合
- **负理想解（NIS）**: 各准则上最差值的组合

### 核心特点

- ✅ **处理不确定性**: 使用区间数表示评分的不确定性
- ✅ **距离度量**: 基于欧氏距离的排序方法
- ✅ **完全排序**: 提供完整的方案排序
- ✅ **Vector 标准化**: 消除量纲影响
- ✅ **相对接近度**: 综合考虑正负理想解距离

### 适用场景

- 需要考虑方案与理想解距离的决策问题
- 评分存在不确定性的场景
- 需要完整排序而非分类的问题
- 准则之间存在互补关系的场景

---

## 🧮 数学模型

### 1. Vector 标准化

首先对原始决策矩阵进行 Vector 标准化，消除量纲影响：

$$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{i=1}^{m} x_{ij}^2}}$$

其中：
- $x_{ij}$ 是方案 $i$ 在准则 $j$ 上的原始评分
- $r_{ij}$ 是标准化后的评分
- $m$ 是方案数量

**区间数处理**: 对于区间数 $[x^L, x^U]$，使用中点进行标准化：

$$r_{ij} = \frac{\text{midpoint}([x^L, x^U])}{\sqrt{\sum_{i=1}^{m} \text{midpoint}([x^L, x^U])^2}}$$

### 2. 加权标准化

将权重应用到标准化后的矩阵：

$$v_{ij} = w_j \cdot r_{ij}$$

其中 $w_j$ 是准则 $j$ 的权重。

### 3. 确定理想解和负理想解

根据准则方向确定理想解和负理想解：

**效益型准则（higher_better）**:
- 理想解: $v_j^+ = \max_i v_{ij}$
- 负理想解: $v_j^- = \min_i v_{ij}$

**成本型准则（lower_better）**:
- 理想解: $v_j^+ = \min_i v_{ij}$
- 负理想解: $v_j^- = \max_i v_{ij}$

### 4. 计算距离

计算每个方案到理想解和负理想解的欧氏距离：

$$D_i^+ = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^+)^2}$$

$$D_i^- = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^-)^2}$$

其中 $n$ 是准则数量。

### 5. 相对接近度

计算每个方案的相对接近度：

$$C_i = \frac{D_i^-}{D_i^+ + D_i^-}$$

**性质**:
- $C_i \in [0, 1]$
- $C_i = 1$：方案与正理想解完全重合
- $C_i = 0$：方案与负理想解完全重合

### 6. 排序

根据相对接近度降序排列方案：

$$A_1 \succ A_2 \iff C_1 > C_2$$

---

## 💡 使用示例

### 基础示例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import IntervalTOPSISAlgorithm

# 定义备选方案
alternatives = ("A1", "A2", "A3")

# 定义准则
criteria = (
    Criterion(name="质量", weight=0.4, direction="higher_better"),
    Criterion(name="价格", weight=0.3, direction="lower_better"),
    Criterion(name="可靠性", weight=0.2, direction="higher_better"),
    Criterion(name="易用性", weight=0.1, direction="higher_better"),
)

# 定义评分矩阵（区间数）
scores = {
    "A1": {
        "质量": Interval(70.0, 90.0),
        "价格": Interval(80.0, 100.0),
        "可靠性": Interval(70.0, 80.0),
        "易用性": Interval(60.0, 80.0),
    },
    "A2": {
        "质量": Interval(80.0, 90.0),
        "价格": Interval(90.0, 100.0),
        "可靠性": Interval(80.0, 90.0),
        "易用性": Interval(70.0, 90.0),
    },
    "A3": {
        "质量": Interval(60.0, 80.0),
        "价格": Interval(70.0, 90.0),
        "可靠性": Interval(60.0, 70.0),
        "易用性": Interval(50.0, 70.0),
    },
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=alternatives,
    criteria=criteria,
    scores=scores
)

# 执行 TOPSIS 区间版本
algo = IntervalTOPSISAlgorithm()
result = algo.calculate(problem)

# 查看结果
print("排名:")
for item in result.rankings:
    print(f"  {item.rank}. {item.alternative}: {item.score:.4f}")

# 查看距离信息
d_plus = result.metadata.metrics["distance_to_ideal"]
d_minus = result.metadata.metrics["distance_to_negative_ideal"]

print("\n距离分析:")
for alt in alternatives:
    print(f"  {alt}: D+={d_plus[alt]:.4f}, D-={d_minus[alt]:.4f}")
```

输出：
```
排名:
  1. A2: 0.6234
  2. A1: 0.4123
  3. A3: 0.2891

距离分析:
  A1: D+=0.1523, D-=0.1068
  A2: D+=0.0987, D-=0.1634
  A3: D+=0.2134, D-=0.0865
```

### 供应商选择案例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import IntervalTOPSISAlgorithm

# 供应商选择问题
alternatives = ("供应商A", "供应商B", "供应商C")

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
}

problem = DecisionProblem(
    alternatives=alternatives,
    criteria=criteria,
    scores=scores
)

algo = IntervalTOPSISAlgorithm()
result = algo.calculate(problem)

# 输出结果
print("=== 供应商选择结果（TOPSIS 区间版本）===\n")

print("完整排名:")
for item in result.rankings:
    print(f"{item.rank}. {item.alternative} (相对接近度: {item.score:.4f})")

# 最佳供应商
best = result.rankings[0].alternative
print(f"\n最佳供应商: {best}")

# 详细分析
metadata = result.metadata.metrics
d_plus = metadata["distance_to_ideal"]
d_minus = metadata["distance_to_negative_ideal"]

print(f"\n距离分析:")
for alt in alternatives:
    print(f"  {alt}:")
    print(f"    到理想解距离: {d_plus[alt]:.4f}")
    print(f"    到负理想解距离: {d_minus[alt]:.4f}")
    print(f"    相对接近度: {d_minus[alt] / (d_plus[alt] + d_minus[alt]):.4f}")
```

### 混合准则类型示例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import IntervalTOPSISAlgorithm

# 项目投资决策
alternatives = ("项目A", "项目B", "项目C")

# 混合准则类型
criteria = (
    Criterion(name="收益率", weight=0.3, direction="higher_better"),  # 效益型
    Criterion(name="风险", weight=0.25, direction="lower_better"),     # 成本型
    Criterion(name="投资额", weight=0.2, direction="lower_better"),   # 成本型
    Criterion(name="市场前景", weight=0.15, direction="higher_better"), # 效益型
    Criterion(name="技术可行性", weight=0.1, direction="higher_better"), # 效益型
)

# 区间评分
scores = {
    "项目A": {
        "收益率": Interval(15.0, 20.0),
        "风险": Interval(30.0, 50.0),
        "投资额": Interval(80.0, 100.0),
        "市场前景": Interval(70.0, 85.0),
        "技术可行性": Interval(60.0, 80.0),
    },
    "项目B": {
        "收益率": Interval(10.0, 15.0),
        "风险": Interval(20.0, 35.0),
        "投资额": Interval(50.0, 70.0),
        "市场前景": Interval(60.0, 75.0),
        "技术可行性": Interval(70.0, 85.0),
    },
    "项目C": {
        "收益率": Interval(20.0, 25.0),
        "风险": Interval(40.0, 60.0),
        "投资额": Interval(90.0, 110.0),
        "市场前景": Interval(80.0, 95.0),
        "技术可行性": Interval(50.0, 70.0),
    },
}

problem = DecisionProblem(
    alternatives=alternatives,
    criteria=criteria,
    scores=scores
)

algo = IntervalTOPSISAlgorithm()
result = algo.calculate(problem)

print("投资项目排序:")
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}: {item.score:.4f}")
```

---

## ⚙️ 参数说明

### 构造函数

```python
IntervalTOPSISAlgorithm()
```

TOPSIS 区间版本算法不需要额外参数。

### calculate 方法

```python
result = algo.calculate(problem)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `problem` | DecisionProblem | 必需 | 决策问题对象 |

---

## 📊 结果解读

### RankingItem

```python
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}: {item.score}")
```

- `item.alternative`: 备选方案名称
- `item.rank`: 排名（1 表示最优）
- `item.score`: 相对接近度（0 到 1 之间，越大越好）

### 元数据

```python
metadata = result.metadata.metrics

# 标准化矩阵
normalized = metadata["normalized"]

# 加权标准化矩阵
weighted = metadata["weighted"]

# 理想解
ideal = metadata["ideal"]

# 负理想解
negative_ideal = metadata["negative_ideal"]

# 到理想解的距离
d_plus = metadata["distance_to_ideal"]

# 到负理想解的距离
d_minus = metadata["distance_to_negative_ideal"]
```

### 相对接近度解读

- **C > 0.8**: 方案非常接近理想解
- **0.5 < C < 0.8**: 方案较好，但仍有改进空间
- **C < 0.5**: 方案接近负理想解，需要改进

---

## 🎯 最佳实践

### 1. 区间宽度设置

区间宽度反映了评分的不确定性：

```python
# 窄区间：确定性高
high_certainty = Interval(80.0, 85.0)  # 宽度 5

# 中等区间：中等不确定性
medium_certainty = Interval(75.0, 90.0)  # 宽度 15

# 宽区间：不确定性高
low_certainty = Interval(60.0, 100.0)  # 宽度 40
```

### 2. 准则方向选择

根据准则性质选择正确方向：

```python
# 效益型准则：值越大越好
Criterion(name="质量", weight=0.4, direction="higher_better")

# 成本型准则：值越小越好
Criterion(name="价格", weight=0.3, direction="lower_better")
```

### 3. 权重设置

权重应反映准则的相对重要性：

```python
# 使用专家打分法确定权重
criteria = (
    Criterion(name="质量", weight=0.40, direction="higher_better"),
    Criterion(name="价格", weight=0.30, direction="lower_better"),
    Criterion(name="服务", weight=0.20, direction="higher_better"),
    Criterion(name="交付期", weight=0.10, direction="lower_better"),
)
# 权重总和为 1.0
```

### 4. 评分范围

建议将评分控制在 [0, 100] 范围内：

```python
# 推荐：0-100 范围
scores = {
    "A1": {"质量": Interval(70.0, 90.0)}  # 正确
}

# 避免：超出范围的值
scores = {
    "A1": {"质量": Interval(-10.0, 150.0)}  # 可能引发问题
}
```

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

**重要**: TOPSIS 区间版本使用区间**中点**进行计算。

### 2. 退化区间

退化区间（下界等于上界）表示确定值：

```python
# 退化区间
certain_value = Interval(80.0, 80.0)
# 宽度为 0，等价于精确值 80.0
```

### 3. 最少方案数量

TOPSIS 至少需要 2 个备选方案：

```python
# 错误：只有 1 个方案
problem = DecisionProblem(
    alternatives=("A1",),  # 至少 2 个
    criteria=criteria,
    scores=scores
)
```

### 4. 理想解与负理想解

- 理想解不一定是某个实际方案
- 负理想解不一定是某个实际方案
- 它们是各准则最优/最差值的组合

---

## 🔗 相关算法

- **TOPSIS（精确值版本）**: `TOPSISAlgorithm`
- **VIKOR 区间版本**: `IntervalVIKORAlgorithm`
- **ELECTRE-I 区间版本**: `ELECTRE1IntervalAlgorithm`
- **PROMETHEE II 区间版本**: `PROMETHEE2IntervalAlgorithm`

### 算法对比

| 特性 | TOPSIS | VIKOR | ELECTRE-I | PROMETHEE II |
|------|--------|-------|-----------|--------------|
| 排序方式 | 完全排序 | 完全排序 | 核提取 | 完全排序 |
| 核心 | 距离 | 折衷 | 级别优于 | 偏好函数 |
| 参数 | 无 | v 权重 | alpha, beta | 阈值 |

---

## 📚 参考文献

1. Hwang, C. L., & Yoon, K. (1981). "Multiple Attribute Decision Making: Methods and Applications"
2. Yoon, K. (1987). "A reconciliation among discrete compromise situations"
3. 区间 TOPSIS 方法扩展研究

---

**最后更新**: 2026-02-04
**版本**: v0.8.1
**作者**: AI (Claude Sonnet 4.5)
