---
name: mcda-core
description: 多准则决策分析核心框架，支持 14 种算法（WSM、WPM、TOPSIS、VIKOR、TODIM、ELECTRE-I、PROMETHEE II）及区间数支持。当用户需要在多个备选方案之间做结构化决策时使用（如供应商选择、产品评估、招聘决策、投资选择）。处理决策矩阵定义、验证、计算、敏感性分析、排名和可视化。
license: Apache-2.0
---

# MCDA Core

多准则决策分析核心框架，支持 14 种算法和区间数决策。

## 快速开始

1. 定义决策问题（备选方案、准则、权重、评分）
2. 加载数据：JSON/CSV/Excel/YAML
3. 运行计算：`algorithm.calculate(problem)`
4. 导出结果：Markdown/JSON/ASCII/图表

## 工作流程

**步骤 1：定义决策问题**

询问用户：
- 在哪些方案中选择？（备选方案）
- 哪些准则重要？（准则及权重、方向）
- 如何对每个方案评分？（0-100 或区间 [最小值, 最大值]）

**步骤 2：加载数据**

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.loaders import JSONLoader

# JSON 格式
loader = JSONLoader("decision.json")
problem = loader.load()
```

**步骤 3：运行算法**

```python
from mcda_core.algorithms import get_algorithm

# 获取算法
algo = get_algorithm("topsis")  # 或 vikor, todim, wsm, wpm 等

# 计算
result = algo.calculate(problem)

# 查看排名
for r in result.rankings:
    print(f"{r.rank}. {r.alternative}: {r.score:.4f}")
```

**步骤 4：导出结果**

```python
from mcda_core.export import MarkdownExporter, JSONExporter

# 导出报告
exporter = MarkdownExporter()
exporter.export(result, "report.md")
```

## 算法列表

**精确数算法**（7 种）：

1. **WSM**（加权求和法）
   - 公式：`得分 = Σ(权重_i × 评分_i)`
   - 用途：简单加权和
   - 优点：直观易懂

2. **WPM**（加权乘积法）
   - 公式：`得分 = ∏(评分_i ^ 权重_i)`
   - 用途：乘法决策
   - 优点：对低分惩罚更重

3. **TOPSIS**（逼近理想解排序法）
   - 公式：距正负理想解的距离
   - 用途：冲突准则权衡
   - 优点：广泛使用，处理权衡效果好

4. **VIKOR**（折衷排序法）
   - 公式：效用测度 + 遗憾测度
   - 参数：`v`（0-1，默认 0.5）
   - 用途：折衷决策
   - 优点：平衡群体效用和个人遗憾

5. **TODIM**（前景理论决策法）
   - 公式：前景价值函数，损失厌恶
   - 参数：`theta`（损失厌恶系数，默认 2.25）
   - 用途：风险规避决策
   - 优点：建模心理行为

6. **ELECTRE-I**（级别优先关系法）
   - 公式：一致性/不一致性矩阵
   - 参数：`c_hat`（一致性阈值）
   - 用途：成对比较
   - 优点：处理不可比性

7. **PROMETHEE II**（偏好排序组织法）
   - 公式：正负偏好流
   - 参数：每个准则的偏好函数
   - 用途：带偏好的排名
   - 优点：灵活的偏好建模

**区间数算法**（5 种）：

8. **区间 TOPSIS** - 不确定性数据 [最小值, 最大值]
9. **区间 VIKOR** - 区间数 + 可能度排序
10. **区间 TODIM** - 区间前景理论
11. **ELECTRE-I 区间** - 区间比较
12. **PROMETHEE II 区间** - 区间偏好流

**权重计算方法**（5 种）：

- **AHP** - 层次分析法
- **熵权法** - 信息熵权重
- **CRITIC** - CRITIC 权重法
- **变异系数** - CV 权重法
- **博弈论组合** - 组合赋权

## 高级功能

**输入格式**：JSON、CSV、Excel、YAML、Python 字典

**导出格式**：Markdown、JSON、ASCII 表格、图表（matplotlib）

**数据类型**：精确数（浮点）、区间数 [最小值, 最大值]

**敏感性分析**：`algorithm.sensitivity(problem)`

**CLI 使用**：
```bash
mcda validate config.yaml
mcda analyze config.yaml -o report.md
mcda analyze config.yaml --algorithm vikor_interval --sensitivity
```

**错误处理**：所有函数抛出 `ValidationError`，提供清晰错误信息

**资源管理**：所有加载器/导出器使用上下文管理器
