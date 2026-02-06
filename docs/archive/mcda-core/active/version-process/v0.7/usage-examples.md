# MCDA Core v0.7 使用示例

**版本**: v0.7 - 区间数决策支持
**最后更新**: 2026-02-04

---

## 目录

1. [快速开始](#快速开始)
2. [VIKOR 区间版本](#vikor-区间版本)
3. [TODIM 区间版本](#todim-区间版本)
4. [可能度排序](#可能度排序)
5. [完整决策流程](#完整决策流程)
6. [性能优化](#性能优化)

---

## 快速开始

### 安装

```bash
pip install mcda-core
```

### 基础用法

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval
from mcda_core.algorithms.base import get_algorithm

# 定义准则
criteria = [
    Criterion(name="性能", weight=0.4, direction="higher_better"),
    Criterion(name="成本", weight=0.3, direction="lower_better"),
    Criterion(name="可靠性", weight=0.2, direction="higher_better"),
    Criterion(name="易用性", weight=0.1, direction="higher_better"),
]

# 定义区间评分
scores = {
    "方案A": {
        "性能": Interval(85.0, 92.0),
        "成本": Interval(40.0, 50.0),
        "可靠性": Interval(88.0, 95.0),
        "易用性": Interval(82.0, 90.0),
    },
    "方案B": {
        "性能": Interval(90.0, 95.0),
        "成本": Interval(45.0, 55.0),
        "可靠性": Interval(85.0, 92.0),
        "易用性": Interval(78.0, 85.0),
    },
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

# 运行 VIKOR 区间算法
algorithm = get_algorithm("vikor_interval")
result = algorithm.calculate(problem)

# 查看结果
for ranking in result.rankings:
    print(f"第 {ranking.rank} 名: {ranking.alternative}")
```

---

## VIKOR 区间版本

### 基本用法

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval
from mcda_core.algorithms.base import get_algorithm

# 定义准则
criteria = [
    Criterion(name="投资成本", weight=0.3, direction="lower_better"),
    Criterion(name="预期收益", weight=0.4, direction="higher_better"),
    Criterion(name="风险水平", weight=0.2, direction="lower_better"),
    Criterion(name="回收期", weight=0.1, direction="lower_better"),
]

# 定义区间评分
scores = {
    "项目A": {
        "投资成本": Interval(100, 120),
        "预期收益": Interval(150, 180),
        "风险水平": Interval(0.3, 0.5),
        "回收期": Interval(2, 3),
    },
    "项目B": {
        "投资成本": Interval(80, 100),
        "预期收益": Interval(130, 150),
        "风险水平": Interval(0.2, 0.4),
        "回收期": Interval(1.5, 2.5),
    },
    "项目C": {
        "投资成本": Interval(90, 110),
        "预期收益": Interval(140, 170),
        "风险水平": Interval(0.25, 0.45),
        "回收期": Interval(1.8, 2.8),
    },
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

# 运行 VIKOR 区间算法
algorithm = get_algorithm("vikor_interval")
result = algorithm.calculate(problem, v=0.5)

# 查看排名
print("=== VIKOR 区间版本排名 ===")
for ranking in result.rankings:
    print(f"第 {ranking.rank} 名: {ranking.alternative} (得分: {ranking.score:.4f})")

# 查看详细指标
print("\n=== 详细指标 ===")
for alt in problem.alternatives:
    S = result.metadata.metrics["S"][alt]
    R = result.metadata.metrics["R"][alt]
    Q = result.metadata.metrics["Q"][alt]
    print(f"{alt}:")
    print(f"  群体效用 S = {S}")
    print(f"  个别遗憾 R = {R}")
    print(f"  折衷值 Q = {Q}")
```

### 调整决策策略

VIKOR 的参数 `v` 控制决策策略：

```python
# 保守策略（重视个别遗憾）
result_conservative = algorithm.calculate(problem, v=0.2)

# 折衷策略（平衡）
result_balanced = algorithm.calculate(problem, v=0.5)

# 激进策略（重视群体效用）
result_aggressive = algorithm.calculate(problem, v=0.8)

print("保守策略排名:", [r.alternative for r in result_conservative.rankings])
print("折衷策略排名:", [r.alternative for r in result_balanced.rankings])
print("激进策略排名:", [r.alternative for r in result_aggressive.rankings])
```

---

## TODIM 区间版本

### 基本用法

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval
from mcda_core.algorithms.base import get_algorithm

# 定义准则
criteria = [
    Criterion(name="质量", weight=0.35, direction="higher_better"),
    Criterion(name="价格", weight=0.25, direction="lower_better"),
    Criterion(name="交期", weight=0.20, direction="lower_better"),
    Criterion(name="服务", weight=0.12, direction="higher_better"),
    Criterion(name="信誉", weight=0.08, direction="higher_better"),
]

# 定义区间评分
scores = {
    "供应商A": {
        "质量": Interval(85, 92),
        "价格": Interval(45, 55),
        "交期": Interval(7, 14),
        "服务": Interval(80, 90),
        "信誉": Interval(85, 95),
    },
    "供应商B": {
        "质量": Interval(88, 95),
        "价格": Interval(40, 50),
        "交期": Interval(10, 21),
        "服务": Interval(75, 85),
        "信誉": Interval(82, 92),
    },
    "供应商C": {
        "质量": Interval(82, 88),
        "价格": Interval(50, 60),
        "交期": Interval(5, 10),
        "服务": Interval(85, 95),
        "信誉": Interval(88, 98),
    },
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

# 运行 TODIM 区间算法
algorithm = get_algorithm("todim_interval")
result = algorithm.calculate(problem)

# 查看排名
print("=== TODIM 区间版本排名 ===")
for ranking in result.rankings:
    print(f"第 {ranking.rank} 名: {ranking.alternative} (优势度: {ranking.score:.4f})")

# 查看前景理论参数
print(f"\n=== 前景理论参数 ===")
print(f"alpha (收益): {result.metadata.metrics['alpha']}")
print(f"beta (损失): {result.metadata.metrics['beta']}")
print(f"theta (损失厌恶): {result.metadata.metrics['theta']}")
```

### 自定义前景理论参数

```python
# 风险中性（默认参数）
result_neutral = algorithm.calculate(
    problem,
    alpha=0.88,
    beta=0.88,
    theta=2.25
)

# 风险规避（更厌恶损失）
result_aversion = algorithm.calculate(
    problem,
    alpha=0.90,
    beta=0.90,
    theta=3.0
)

# 风险偏好（较少厌恶损失）
result_seeking = algorithm.calculate(
    problem,
    alpha=0.85,
    beta=0.85,
    theta=1.5
)

print("风险中性排名:", [r.alternative for r in result_neutral.rankings])
print("风险规避排名:", [r.alternative for r in result_aversion.rankings])
print("风险偏好排名:", [r.alternative for r in result_seeking.rankings])
```

---

## 可能度排序

### 直接使用

```python
from mcda_core.interval import Interval, PossibilityDegree

# 创建区间
a = Interval(3, 7)
b = Interval(5, 9)
c = Interval(4, 6)

# 计算可能度
pd = PossibilityDegree()

# P(a ≥ b)
p_ab = pd.possibility_degree(a, b)
print(f"P({a} ≥ {b}) = {p_ab:.4f}")

# P(b ≥ a)
p_ba = pd.possibility_degree(b, a)
print(f"P({b} ≥ {a}) = {p_ba:.4f}")

# 排序区间列表
intervals = [a, b, c]
sorted_intervals = pd.sort_intervals(intervals)
print("排序前:", [str(i) for i in intervals])
print("排序后:", [str(i) for i in sorted_intervals])
```

### 集成到决策流程

```python
from mcda_core.interval import PossibilityDegree

# 假设有多个备选方案的 Q 值（区间）
q_values = {
    "方案A": Interval(0.2, 0.5),
    "方案B": Interval(0.3, 0.6),
    "方案C": Interval(0.15, 0.45),
}

# 使用可能度排序
pd = PossibilityDegree()
ranked = pd.sort_dict(q_values)

print("=== 可能度排序结果 ===")
for rank, (alt, q) in enumerate(ranked.items(), 1):
    print(f"第 {rank} 名: {alt}, Q = {q}")
```

---

## 完整决策流程

### 场景：云服务提供商选择

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval
from mcda_core.algorithms.base import get_algorithm
import json

# 1. 定义决策准则
criteria = [
    Criterion(name="性能", weight=0.30, direction="higher_better"),
    Criterion(name="成本", weight=0.25, direction="lower_better"),
    Criterion(name="可靠性", weight=0.20, direction="higher_better"),
    Criterion(name="安全性", weight=0.15, direction="higher_better"),
    Criterion(name="易用性", weight=0.10, direction="higher_better"),
]

# 2. 收集数据（区间表示不确定性）
scores = {
    "AWS": {
        "性能": Interval(88, 95),
        "成本": Interval(45, 65),
        "可靠性": Interval(90, 98),
        "安全性": Interval(92, 96),
        "易用性": Interval(85, 92),
    },
    "Azure": {
        "性能": Interval(85, 93),
        "成本": Interval(40, 60),
        "可靠性": Interval(88, 95),
        "安全性": Interval(90, 94),
        "易用性": Interval(82, 90),
    },
    "GCP": {
        "性能": Interval(90, 96),
        "成本": Interval(50, 70),
        "可靠性": Interval(85, 92),
        "安全性": Interval(88, 93),
        "易用性": Interval(78, 88),
    },
}

# 3. 创建决策问题
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

# 4. 运行多个算法
algorithms = ["vikor_interval", "todim_interval"]
results = {}

for alg_name in algorithms:
    algorithm = get_algorithm(alg_name)
    results[alg_name] = algorithm.calculate(problem)

# 5. 汇总结果
print("=" * 60)
print("云服务提供商选择 - 决策分析报告")
print("=" * 60)

for alg_name, result in results.items():
    print(f"\n=== {alg_name.upper()} 排名 ===")
    for ranking in result.rankings:
        print(f"第 {ranking.rank} 名: {ranking.alternative}")

# 6. 一致性分析
vikor_best = results["vikor_interval"].rankings[0].alternative
todim_best = results["todim_interval"].rankings[0].alternative

print(f"\n=== 推荐方案 ===")
if vikor_best == todim_best:
    print(f"✓ 所有算法一致推荐: {vikor_best}")
else:
    print(f"VIKOR 推荐: {vikor_best}")
    print(f"TODIM 推荐: {todim_best}")
    print("建议: 进一步分析两个方案的差异")

# 7. 导出结果（可选）
output = {
    "criteria": [c.name for c in criteria],
    "alternatives": list(scores.keys()),
    "results": {
        alg_name: [
            {
                "rank": r.rank,
                "alternative": r.alternative,
                "score": r.score
            }
            for r in result.rankings
        ]
        for alg_name, result in results.items()
    }
}

# print("\n=== JSON 格式结果 ===")
# print(json.dumps(output, indent=2, ensure_ascii=False))
```

---

## 性能优化

### 大规模问题优化

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval
from mcda_core.algorithms.base import get_algorithm
import time

# 生成大规模问题（50 个方案 × 20 个准则）
def generate_large_problem(n_alternatives=50, n_criteria=20):
    criteria = [
        Criterion(name=f"准则{i}", weight=1.0/n_criteria, direction="higher_better")
        for i in range(n_criteria)
    ]

    scores = {}
    for i in range(n_alternatives):
        alt = f"方案{i}"
        scores[alt] = {
            f"准则{j}": Interval(70.0 + i, 90.0 + i)
            for j in range(n_criteria)
        }

    return DecisionProblem(
        alternatives=tuple(scores.keys()),
        criteria=criteria,
        scores=scores,
    )

# 测试性能
problem = generate_large_problem(50, 20)

algorithms = ["vikor_interval", "todim_interval"]

print("=== 性能测试 ===")
for alg_name in algorithms:
    algorithm = get_algorithm(alg_name)

    start_time = time.time()
    result = algorithm.calculate(problem)
    elapsed_time = time.time() - start_time

    print(f"{alg_name}:")
    print(f"  方案数: {len(problem.alternatives)}")
    print(f"  准则数: {len(problem.criteria)}")
    print(f"  执行时间: {elapsed_time:.3f}s")
    print(f"  目标: < 5.0s")
    print(f"  状态: {'✓ 通过' if elapsed_time < 5.0 else '✗ 失败'}")
```

### 批量分析

```python
# 批量运行多个决策场景
scenarios = [
    {
        "name": "乐观估计",
        "scores": {
            "方案A": {"性能": Interval(90, 95), "成本": Interval(40, 45)},
            "方案B": {"性能": Interval(88, 93), "成本": Interval(42, 48)},
        }
    },
    {
        "name": "悲观估计",
        "scores": {
            "方案A": {"性能": Interval(80, 85), "成本": Interval(50, 55)},
            "方案B": {"性能": Interval(82, 87), "成本": Interval(48, 53)},
        }
    },
]

criteria = [
    Criterion(name="性能", weight=0.6, direction="higher_better"),
    Criterion(name="成本", weight=0.4, direction="lower_better"),
]

algorithm = get_algorithm("vikor_interval")

print("=== 场景分析 ===")
for scenario in scenarios:
    problem = DecisionProblem(
        alternatives=tuple(scenario["scores"].keys()),
        criteria=criteria,
        scores=scenario["scores"],
    )

    result = algorithm.calculate(problem)
    best = result.rankings[0].alternative

    print(f"\n{scenario['name']}:")
    print(f"  最优方案: {best}")
    print(f"  排名: {' → '.join([r.alternative for r in result.rankings])}")
```

---

## 高级用法

### 混合区间和精确数

```python
from mcda_core.interval import Interval

# 可以混合使用区间数和精确数
scores = {
    "方案A": {
        "性能": Interval(85, 92),  # 区间
        "成本": 50.0,              # 精确数
    },
    "方案B": {
        "性能": 90.0,              # 精确数
        "成本": Interval(45, 55),  # 区间
    },
}

# 系统会自动处理
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)
```

### 敏感性分析

```python
# 分析权重变化对结果的影响
def sensitivity_analysis(problem, criterion_name, weight_range):
    """敏感性分析：改变某个准则的权重"""
    base_algorithm = get_algorithm("vikor_interval")

    results = []
    for weight in weight_range:
        # 调整权重
        new_criteria = []
        for c in problem.criteria:
            if c.name == criterion_name:
                new_criteria.append(Criterion(
                    name=c.name,
                    weight=weight,
                    direction=c.direction
                ))
            else:
                # 按比例调整其他权重
                scale = (1 - weight) / (1 - c.weight)
                new_criteria.append(Criterion(
                    name=c.name,
                    weight=c.weight * scale,
                    direction=c.direction
                ))

        # 创建新问题
        new_problem = DecisionProblem(
            alternatives=problem.alternatives,
            criteria=new_criteria,
            scores=problem.scores,
        )

        # 运行算法
        result = base_algorithm.calculate(new_problem)
        best = result.rankings[0].alternative
        results.append((weight, best))

    return results

# 运行敏感性分析
weights = [0.1, 0.2, 0.3, 0.4, 0.5]
sensitivity = sensitivity_analysis(problem, "性能", weights)

print("=== 敏感性分析 ===")
for weight, best in sensitivity:
    print(f"性能权重 = {weight:.1f}: 最优方案 = {best}")
```

---

## 常见问题

### Q1: 如何选择合适的算法？

- **VIKOR**: 适用于需要折衷解的场景，能同时优化群体效用和个别遗憾
- **TODIM**: 适用于考虑决策者心理行为的场景，支持损失厌恶建模

### Q2: 区间宽度如何影响结果？

区间宽度越大，不确定性越高，排名区分度可能降低。建议：
- 保持数据一致性
- 避免过宽的区间
- 考虑使用敏感性分析

### Q3: 如何处理不同量纲的准则？

系统会自动进行标准化处理，无需手动归一化。但建议：
- 保持评分范围合理（如 0-100）
- 使用区间表示不确定性范围

---

## 更多资源

- [API 文档](../api/)
- [VIKOR 算法详解](../algorithms/vikor.md)
- [TODIM 算法详解](../algorithms/todim.md)
- [可能度排序详解](../methods/possibility-degree.md)

---

**最后更新**: 2026-02-04
**版本**: v0.7
