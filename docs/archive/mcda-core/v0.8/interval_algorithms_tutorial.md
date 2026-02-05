# MCDA Core 区间算法使用教程

**版本**: v0.8
**目标**: 掌握不确定性环境下的多准则决策分析

---

## 📚 教程目录

1. [快速开始](#1-快速开始)
2. [区间数基础](#2-区间数基础)
3. [算法选择指南](#3-算法选择指南)
4. [完整案例：供应商选择](#4-完整案例供应商选择)
5. [高级技巧](#5-高级技巧)
6. [最佳实践](#6-最佳实践)

---

## 1. 快速开始

### 安装

```bash
# 安装 MCDA Core
pip install mcda-core
```

### 基础示例

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import ELECTRE1IntervalAlgorithm

# 定义决策问题
alternatives = ("A", "B", "C")
criteria = (
    Criterion(name="质量", weight=0.6, direction="higher_better"),
    Criterion(name="价格", weight=0.4, direction="lower_better"),
)

scores = {
    "A": {"质量": Interval(7.0, 9.0), "价格": Interval(80.0, 100.0)},
    "B": {"质量": Interval(8.0, 9.0), "价格": Interval(90.0, 110.0)},
    "C": {"质量": Interval(6.0, 8.0), "价格": Interval(70.0, 90.0)},
}

# 创建问题并求解
problem = DecisionProblem(alternatives=alternatives, criteria=criteria, scores=scores)
algo = ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
result = algo.calculate(problem)

# 查看结果
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}")
```

---

## 2. 区间数基础

### 什么是区间数？

区间数用于表示不确定性和模糊性：

```python
from mcda_core.interval import Interval

# 创建区间
quality_score = Interval(7.0, 9.0)

# 含义：质量得分在 7.0 到 9.0 之间
# - 反映评估的不确定性
# - 反映专家意见的分歧
# - 反映未来的波动范围
```

### 区间数的属性

```python
interval = Interval(2.0, 5.0)

print(f"下界: {interval.lower}")    # 2.0
print(f"上界: {interval.upper}")    # 5.0
print(f"中点: {interval.midpoint}") # 3.5
print(f"宽度: {interval.width}")    # 3.0
```

### 区间数运算

```python
a = Interval(2.0, 5.0)
b = Interval(1.0, 3.0)

# 加法
c = a + b  # [3.0, 8.0]

# 减法
d = a - b  # [-1.0, 4.0]

# 乘法
e = a * 2  # [4.0, 10.0]

# 比较
print(a.midpoint > b.midpoint)  # True
```

---

## 3. 算法选择指南

### ELECTRE-I 区间版本

**适用场景**:
- ✅ 需要识别最优方案集合（核）
- ✅ 不需要完全排序
- ✅ 关注方案之间的级别优于关系

**特点**:
- 提供核（非被优方案集合）
- 参数：α（和谐度阈值），β（不和谐度阈值）
- 输出：部分排序

**示例**:

```python
from mcda_core.algorithms import ELECTRE1IntervalAlgorithm

algo = ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
result = algo.calculate(problem)

# 查看核
kernel = result.metadata.metrics["kernel"]
print(f"推荐方案: {kernel}")
```

### PROMETHEE II 区间版本

**适用场景**:
- ✅ 需要完整的方案排序
- ✅ 需要了解方案的相对优势
- ✅ 需要灵活的偏好函数

**特点**:
- 提供完全排序
- 参数：偏好函数类型，阈值
- 输出：净流量排名

**示例**:

```python
from mcda_core.algorithms import PROMETHEE2IntervalAlgorithm

algo = PROMETHEE2IntervalAlgorithm(
    preference_function="v_shape",
    threshold=5.0
)
result = algo.calculate(problem)

# 查看完整排名
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}: {item.score:.4f}")
```

### 算法对比

| 需求 | 推荐算法 |
|------|---------|
| 需要最优方案集合 | ELECTRE-I |
| 需要完整排序 | PROMETHEE II |
| 需要折衷解 | VIKOR 区间版本 |
| 前景理论决策 | TODIM 区间版本 |

---

## 4. 完整案例：供应商选择

### 问题描述

某公司需要从 4 家供应商中选择一家合作伙伴。评估准则包括：

1. **质量** (35%): 产品质量，越高越好
2. **价格** (25%): 采购价格，越低越好
3. **交付期** (20%): 交付时间，越短越好
4. **服务** (20%): 售后服务，越高越好

由于市场不确定性，所有评分用区间数表示。

### 数据准备

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval

# 备选方案
suppliers = ("供应商A", "供应商B", "供应商C", "供应商D")

# 评估准则
criteria = (
    Criterion(name="质量", weight=0.35, direction="higher_better"),
    Criterion(name="价格", weight=0.25, direction="lower_better"),
    Criterion(name="交付期", weight=0.20, direction="lower_better"),
    Criterion(name="服务", weight=0.20, direction="higher_better"),
)

# 区间评分（经过专家评估）
scores = {
    "供应商A": {
        "质量": Interval(75, 85),   # 75-85分
        "价格": Interval(80, 100),  # 80-100元
        "交付期": Interval(5, 10),  # 5-10天
        "服务": Interval(65, 75),   # 65-75分
    },
    "供应商B": {
        "质量": Interval(80, 90),
        "价格": Interval(90, 110),
        "交付期": Interval(7, 12),
        "服务": Interval(70, 80),
    },
    "供应商C": {
        "质量": Interval(70, 80),
        "价格": Interval(70, 90),
        "交付期": Interval(3, 7),
        "服务": Interval(60, 70),
    },
    "供应商D": {
        "质量": Interval(75, 85),
        "价格": Interval(85, 100),
        "交付期": Interval(6, 11),
        "服务": Interval(75, 85),
    },
}
```

### 方法一：ELECTRE-I

```python
from mcda_core.algorithms import ELECTRE1IntervalAlgorithm

# 创建决策问题
problem = DecisionProblem(
    alternatives=suppliers,
    criteria=criteria,
    scores=scores
)

# 使用 ELECTRE-I
algo = ELECTRE1IntervalAlgorithm(alpha=0.65, beta=0.35)
result = algo.calculate(problem)

# 输出结果
print("=== ELECTRE-I 分析结果 ===\n")

# 核分析
kernel = result.metadata.metrics["kernel"]
print(f"核（推荐供应商）: {', '.join(kernel)}")

if len(kernel) == 1:
    print(f"\n✅ 明确推荐: {kernel[0]}")
elif len(kernel) == 2:
    print(f"\n⚠️  两个供应商在核中，建议进一步比较")
else:
    print(f"\n❓ {len(kernel)}个供应商在核中，差异不明显")

# 排名
print("\n排名（核内优先）:")
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}")
```

### 方法二：PROMETHEE II

```python
from mcda_core.algorithms import PROMETHEE2IntervalAlgorithm

# 使用 PROMETHEE II
algo = PROMETHEE2IntervalAlgorithm(
    preference_function="v_shape",
    threshold=5.0
)
result = algo.calculate(problem)

# 输出结果
print("\n=== PROMETHEE II 分析结果 ===\n")

# 完整排名
print("完整排名:")
for item in result.rankings:
    print(f"{item.rank}. {item.alternative}")

# 流量分析
net_flow = result.metadata.metrics["net_flow"]
print("\n净流量分析:")
for supplier, flow in sorted(
    net_flow.items(),
    key=lambda x: x[1],
    reverse=True
):
    status = "✅" if flow > 0 else "⚠️" if flow > -0.1 else "❌"
    print(f"  {status} {supplier}: {flow:.4f}")

# 推荐
best = result.rankings[0].alternative
print(f"\n✅ 推荐供应商: {best}")
```

### 综合分析

```python
# 结合两种方法
print("\n=== 综合建议 ===\n")

electre_kernel = set(result_electre.metadata.metrics["kernel"])
promethee_best = result_promethee.rankings[0].alternative

print(f"ELECTRE-I 核: {', '.join(electre_kernel)}")
print(f"PROMETHEE II 最佳: {promethee_best}")

if promethee_best in electre_kernel:
    print(f"\n✅ 一致推荐: {promethee_best}")
else:
    print(f"\n⚠️  方法结果不一致，建议:")
    print(f"  - 优先考虑 ELECTRE-I 的核: {', '.join(electre_kernel)}")
    print(f"  - 参考 PROMETHEE II 的完整排序")
```

---

## 5. 高级技巧

### 技巧 1: 敏感性分析

```python
# 测试不同参数下的结果稳定性
alphas = [0.5, 0.6, 0.7, 0.8]
betas = [0.2, 0.3, 0.4]

results = {}
for alpha in alphas:
    for beta in betas:
        algo = ELECTRE1IntervalAlgorithm(alpha=alpha, beta=beta)
        result = algo.calculate(problem)
        kernel = tuple(result.metadata.metrics["kernel"])
        results[(alpha, beta)] = kernel

# 分析稳定性
from collections import Counter
kernels = list(results.values())
common = Counter(kernels).most_common(1)

print(f"最稳定的核: {common[0][0]}")
print(f"出现频率: {common[0][1]}/{len(results)}")
```

### 技巧 2: 区间宽度分析

```python
# 分析不确定性对决策的影响
def analyze_uncertainty(scores):
    """分析区间宽度"""
    for supplier, scores_dict in scores.items():
        total_width = 0
        count = 0
        for criterion, interval in scores_dict.items():
            total_width += interval.width
            count += 1
        avg_width = total_width / count
        print(f"{supplier}: 平均区间宽度 = {avg_width:.2f}")

analyze_uncertainty(scores)
```

### 技巧 3: 多方法验证

```python
from mcda_core.algorithms import (
    ELECTRE1IntervalAlgorithm,
    PROMETHEE2IntervalAlgorithm,
    IntervalVIKORAlgorithm
)

# 使用三种方法分析
methods = {
    "ELECTRE-I": ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3),
    "PROMETHEE II": PROMETHEE2IntervalAlgorithm(preference_function="v_shape", threshold=5.0),
    "VIKOR": IntervalVIKORAlgorithm(v=0.5),
}

results = {}
for name, algo in methods.items():
    result = algo.calculate(problem)
    results[name] = result

# 比较结果
print("=== 多方法比较 ===\n")
for name, result in results.items():
    top3 = [item.alternative for item in result.rankings[:3]]
    print(f"{name}: {', '.join(top3)}")

# 找出一致的最佳选择
from collections import Counter
all_top1 = [result.rankings[0].alternative for result in results.values()]
consensus = Counter(all_top1).most_common(1)

print(f"\n共识最佳: {consensus[0][0]} ({consensus[0][1]}/{len(results)}个方法支持)")
```

### 技巧 4: 权重敏感性

```python
# 测试不同权重组合的影响
weight_scenarios = [
    {"质量": 0.5, "价格": 0.3, "交付期": 0.1, "服务": 0.1},  # 质量优先
    {"质量": 0.2, "价格": 0.5, "交付期": 0.2, "服务": 0.1},  # 价格优先
    {"质量": 0.25, "价格": 0.25, "交付期": 0.25, "服务": 0.25},  # 平衡
]

for i, weights in enumerate(weight_scenarios, 1):
    # 创建新准则
    criteria_scenario = tuple(
        Criterion(name=k, weight=v, direction="higher_better" if k in ["质量", "服务"] else "lower_better")
        for k, v in weights.items()
    )

    # 创建新问题
    problem_scenario = DecisionProblem(
        alternatives=suppliers,
        criteria=criteria_scenario,
        scores=scores
    )

    # 求解
    algo = PROMETHEE2IntervalAlgorithm()
    result = algo.calculate(problem_scenario)

    print(f"场景 {i}: {result.rankings[0].alternative}")
```

---

## 6. 最佳实践

### 6.1 数据收集

**区间宽度建议**:

| 不确定性程度 | 宽度（相对值） | 示例 |
|------------|--------------|------|
| 低 | ±5% | [76, 84] |
| 中 | ±10% | [72, 88] |
| 高 | ±20% | [64, 96] |

**原则**:
- ✅ 区间应反映真实的不确定性
- ✅ 专家评估时保留分歧
- ❌ 避免过宽的区间（失去区分度）

### 6.2 参数选择

**ELECTRE-I**:

```python
# 保守策略（严格）
alpha = 0.7
beta = 0.2

# 平衡策略（推荐）
alpha = 0.6
beta = 0.3

# 宽松策略（宽松）
alpha = 0.5
beta = 0.4
```

**PROMETHEE II**:

```python
# 根据评分规模选择阈值
score_range = max_score - min_score
threshold = score_range / 10  # 推荐
```

### 6.3 结果解释

**ELECTRE-I**:
- 核大小 = 1: 明确的最优解 ✅
- 核大小 = 2-3: 需要进一步分析 ⚠️
- 核大小 > 3: 差异不明显，考虑收集更多信息 ❓

**PROMETHEE II**:
- 净流量差距 > 0.2: 明显优势 ✅
- 净流量差距 0.1-0.2: 有一定优势 ⚠️
- 净流量差距 < 0.1: 方案相似 ❓

### 6.4 文档化

**完整的决策报告应包括**:

```python
report = f"""
=== 多准则决策分析报告 ===

## 问题描述
{description}

## 备选方案
{', '.join(alternatives)}

## 评估准则
{criteria_summary}

## 评分数据
{scores_summary}

## 分析方法
- 方法 1: ELECTRE-I (α={alpha}, β={beta})
- 方法 2: PROMETHEE II ({preference_function}, p={threshold})

## 结果
### ELECTRE-I
核: {kernel}

### PROMETHEE II
排名: {rankings}

## 建议
{recommendation}

## 不确定性分析
{uncertainty_analysis}

---
生成时间: {timestamp}
分析工具: MCDA Core v0.8
"""
```

---

## 🎓 进阶学习

### 延伸阅读

1. **区间数理论**: Moore, R. E. (1979). "Methods and Applications of Interval Analysis"
2. **ELECTRE 方法**: Roy, B. (1991). "The outranking approach and the foundations of ELECTRE methods"
3. **PROMETHEE 方法**: Brans, J. P., & Mareschal, B. (2005). "PROMETHEE methods"

### 实践项目

1. **投资决策**: 使用区间数评估投资回报率
2. **供应商选择**: 评估供应商的质量、价格、交付等
3. **人才招聘**: 综合评估候选人的各项能力
4. **项目优先级**: 确定项目的实施优先级

---

## 📞 获取帮助

- **文档**: 查看 `docs/` 目录下的详细文档
- **测试**: 参考 `tests/mcda-core/` 下的测试用例
- **Issues**: 在 GitHub 上提交问题

---

**最后更新**: 2026-02-04
**版本**: v0.8
**作者**: AI (Claude Sonnet 4.5)
