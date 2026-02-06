# MCDA-Core 用户手册 (User Manual)

**版本**: v1.0.0
**更新日期**: 2026-02-06
**作者**: MCDA-Core 开发团队

---

## 📚 目录 (Table of Contents)

1. [项目简介](#1-项目简介)
2. [安装指南](#2-安装指南)
3. [快速开始](#3-快速开始)
4. [核心概念](#4-核心概念)
5. [数据模型](#5-数据模型)
6. [决策算法](#6-决策算法)
7. [权重计算](#7-权重计算)
8. [评分规则](#8-评分规则)
9. [群决策聚合](#9-群决策聚合)
10. [约束否决](#10-约束否决)
11. [数据加载](#11-数据加载)
12. [可视化](#12-可视化)
13. [CLI 使用](#13-cli-使用)
14. [API 参考](#14-api-参考)
15. [示例](#15-示例)
16. [常见问题](#16-常见问题)
17. [最佳实践](#17-最佳实践)
18. [性能优化](#18-性能优化)

---

## 1. 项目简介

### 1.1 什么是 MCDA-Core?

MCDA-Core 是一个**多准则决策分析(Multi-Criteria Decision Analysis, MCDA)** Python 库,提供:

- **14 种决策算法**: TOPSIS, VIKOR, TODIM, ELECTRE, PROMETHEE 等
- **6 种权重计算方法**: CV, CRITIC, 熵权法, AHP, PCA, 博弈论
- **群决策聚合**: 加权平均, Borda 计数, Copeland 法
- **约束否决机制**: 硬否决, 软否决, 分级否决
- **灵活评分规则**: 线性评分, 阈值评分
- **多种数据格式**: YAML, JSON, CSV, Excel
- **丰富可视化**: ASCII 图表, HTML 报告

### 1.2 适用场景

- **供应商选择**: 综合评估成本、质量、服务等多维度
- **项目优先级排序**: 平衡收益、风险、资源等因素
- **投资决策分析**: 综合考虑回报率、风险、流动性
- **产品方案评估**: 从性能、成本、市场等多角度决策
- **人事选拔**: 综合能力、经验、文化匹配度等

### 1.3 主要特性

✅ **功能完整**: 覆盖 MCDA 决策全流程
✅ **易于使用**: 简洁的 API 设计,丰富的文档
✅ **灵活扩展**: 模块化架构,易于自定义
✅ **性能优秀**: 快速算法,支持大规模数据
✅ **生产就绪**: 90%+ 测试覆盖率,严格代码审查

---

## 2. 安装指南

### 2.1 系统要求

- **Python**: 3.10+
- **操作系统**: Windows, Linux, macOS
- **内存**: 建议 2GB+
- **磁盘**: 100MB+

### 2.2 安装方法

#### 方法 1: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-org/ai_core_skills.git
cd ai_core_skills

# 创建虚拟环境
python3.12 -m venv .venv_linux
source .venv_linux/bin/activate  # Linux/macOS
# 或
.venv_linux\Scripts\activate  # Windows

# 安装 MCDA-Core
cd skills/mcda-core
pip install -e .
```

#### 方法 2: 安装依赖

```bash
pip install -r requirements.txt
```

### 2.3 验证安装

```python
# 测试导入
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion

print("MCDA-Core 安装成功!")
```

```bash
# 运行测试
pytest tests/mcda-core/ -v

# 查看版本
mcda-core --version
```

---

## 3. 快速开始

### 3.1 五分钟入门

```python
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion

# 1. 定义决策问题
problem = DecisionProblem(
    alternatives=("方案A", "方案B", "方案C"),
    criteria=(
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="质量", weight=0.3, direction="higher_better"),
    ),
    scores={
        "方案A": {"性能": 85, "成本": 50, "质量": 80},
        "方案B": {"性能": 90, "成本": 60, "质量": 85},
        "方案C": {"性能": 78, "成本": 45, "质量": 90},
    }
)

# 2. 创建分析器
orchestrator = MCDAOrchestrator()

# 3. 运行分析
result = orchestrator.analyze(problem, algorithm_name="topsis")

# 4. 查看结果
print(f"最佳方案: {result.rankings[0].alternative}")
print(f"得分: {result.rankings[0].score:.2f}")

# 5. 生成报告
report = orchestrator.generate_report(problem, result, format="markdown")
print(report)
```

**输出**:
```
最佳方案: 方案C
得分: 0.78

# TOPSIS 决策分析报告

## 排名结果
| 排名 | 方案 | 得分 |
|------|------|------|
| 1 | 方案C | 0.78 |
| 2 | 方案A | 0.65 |
| 3 | 方案B | 0.52 |
```

### 3.2 使用 YAML 配置文件

**decision.yaml**:
```yaml
name: 供应商选择
alternatives:
  - 供应商A
  - 供应商B
  - 供应商C
criteria:
  - name: 性能
    weight: 0.4
    direction: higher_better
  - name: 成本
    weight: 0.3
    direction: lower_better
  - name: 质量
    weight: 0.3
    direction: higher_better
scores:
  供应商A:
    性能: 85
    成本: 50
    质量: 80
  供应商B:
    性能: 90
    成本: 60
    质量: 85
  供应商C:
    性能: 78
    成本: 45
    质量: 90
algorithm:
  name: topsis
```

**Python 代码**:
```python
from mcda_core.core import MCDAOrchestrator

orchestrator = MCDAOrchestrator()

# 从 YAML 加载
problem = orchestrator.load_from_yaml("decision.yaml")

# 分析
result = orchestrator.analyze(problem)

# 生成报告
report = orchestrator.generate_report(problem, result)
print(report)
```

---

## 4. 核心概念

### 4.1 MCDA 基本原理

多准则决策分析(MCDA)是一种在多个冲突准则下评估和选择备选方案的系统性方法。

**核心要素**:
1. **备选方案 (Alternatives)**: 待评估的选项
2. **评估准则 (Criteria)**: 用于评估方案的标准
3. **权重 (Weights)**: 准则的相对重要性
4. **评分 (Scores)**: 方案在各准则下的表现
5. **决策算法 (Algorithms)**: 综合评估的方法

### 4.2 决策矩阵

决策矩阵是 MCDA 的核心数据结构:

| 方案 | 性能 (0.4) | 成本 (0.3) | 质量 (0.3) |
|------|-----------|-----------|-----------|
| 方案A | 85 | 50 | 80 |
| 方案B | 90 | 60 | 85 |
| 方案C | 78 | 45 | 90 |

**说明**:
- 行: 备选方案
- 列: 评估准则
- 单元格: 评分(越高越好或越低越好)
- 括号内: 准则权重

### 4.3 标准化

不同准则的评分单位和范围不同,需要标准化到统一范围:

**常用标准化方法**:
- **Min-Max**: 线性映射到 [0, 1]
- **Vector**: 向量归一化
- **Logarithmic**: 对数标准化
- **Sigmoid**: S 形曲线标准化

**示例**:
```python
# Min-Max 标准化
normalized = (value - min_value) / (max_value - min_value)

# Vector 标准化
normalized = value / sqrt(sum(value^2))
```

### 4.4 准则方向

- **higher_better**: 越高越好(如性能、质量)
- **lower_better**: 越低越好(如成本、风险)

---

## 5. 数据模型

### 5.1 DecisionProblem (决策问题)

```python
from mcda_core.models import DecisionProblem, Criterion

problem = DecisionProblem(
    alternatives=("方案A", "方案B", "方案C"),  # 备选方案
    criteria=(  # 评估准则
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
    ),
    scores={  # 评分
        "方案A": {"性能": 85, "成本": 50},
        "方案B": {"性能": 90, "成本": 60},
        "方案C": {"性能": 78, "成本": 45},
    },
    algorithm="topsis"  # 可选: 默认算法
)
```

### 5.2 Criterion (准则)

```python
from mcda_core.models import Criterion

criterion = Criterion(
    name="性能",                    # 准则名称
    weight=0.4,                     # 权重 (0-1)
    direction="higher_better",      # 方向: higher_better 或 lower_better
    description="产品性能指标",      # 描述 (可选)
    veto=None                       # 否决配置 (可选)
)
```

### 5.3 DecisionResult (决策结果)

```python
result = orchestrator.analyze(problem, algorithm_name="topsis")

# 访问排名
for ranking in result.rankings:
    print(f"排名 {ranking.rank}: {ranking.alternative}")
    print(f"得分: {ranking.score:.4f}")
    print(f"归一化得分: {ranking.normalized_score:.4f}")

# 访问元数据
print(f"算法: {result.metadata.algorithm_name}")
print(f"执行时间: {result.metadata.execution_time:.2f}ms")

# 访问敏感性分析
if result.sensitivity_analysis:
    print(f"稳定性: {result.sensitivity_analysis.stability}")
```

---

## 6. 决策算法

MCDA-Core 支持 14 种决策算法:

### 6.1 WSM (Weighted Sum Model)

**特点**: 最简单直观,加权求和

```python
result = orchestrator.analyze(problem, algorithm_name="wsm")
```

**适用场景**:
- 准则间独立
- 数据线性可加
- 快速决策

### 6.2 WPM (Weighted Product Model)

**特点**: 加权乘积,适合比率数据

```python
result = orchestrator.analyze(problem, algorithm_name="wpm")
```

**适用场景**:
- 准则间有倍数关系
- 需要平衡各准则

### 6.3 TOPSIS

**特点**: 距离理想解最近,距离负理想解最远

```python
result = orchestrator.analyze(problem, algorithm_name="topsis")
```

**适用场景**:
- 最常用算法
- 需要距离度量
- 平衡型决策

### 6.4 VIKOR

**特点**: 群体效用最大,个体遗憾最小

```python
result = orchestrator.analyze(problem, algorithm_name="vikor")
```

**适用场景**:
- 需要折中解
- 冲突准则多
- 群体决策

### 6.5 TODIM

**特点**: 考虑决策者心理行为(前景理论)

```python
result = orchestrator.analyze(problem, algorithm_name="todim")
```

**适用场景**:
- 考虑风险偏好
- 不确定决策
- 行为经济学

### 6.6 ELECTRE-I

**特点**: 级别优于关系,构造性方法

```python
result = orchestrator.analyze(problem, algorithm_name="electre1")
```

**适用场景**:
- 需要部分排序
- 不确定性高
- 定性定量混合

### 6.7 PROMETHEE-II

**特点**: 优先级关系,净流排序

```python
result = orchestrator.analyze(problem, algorithm_name="promethee2")
```

**适用场景**:
- 完全排序
- 偏好函数灵活
- 比较决策

### 6.8 算法对比

| 算法 | 复杂度 | 适用场景 | 优势 |
|------|--------|----------|------|
| **WSM** | 低 | 快速决策 | 简单直观 |
| **WPM** | 低 | 比率数据 | 平衡性好 |
| **TOPSIS** | 中 | 通用场景 | 距离度量 |
| **VIKOR** | 中 | 折中决策 | 群体效用 |
| **TODIM** | 高 | 风险决策 | 心理行为 |
| **ELECTRE-I** | 高 | 部分排序 | 不确定性 |
| **PROMETHEE-II** | 中 | 完全排序 | 偏好函数 |

---

## 7. 权重计算

### 7.1 CV (Coefficient of Variation)

**变异系数法**: 基于数据离散程度赋权

```python
from mcda_core.weighting import cv_weighting

weights = cv_weighting(decision_matrix)
```

**原理**: 离散程度越大,权重越高

### 7.2 CRITIC

**CRITIC 法**: 基于对比强度和冲突性赋权

```python
from mcda_core.weighting import critic_weighting

weights = critic_weighting(decision_matrix)
```

**原理**: 综合考虑标准差和相关系数

### 7.3 Entropy (熵权法)

**熵权法**: 基于信息熵赋权

```python
from mcda_core.services import EntropyWeightService

service = EntropyWeightService()
weights = service.calculate_weights(decision_matrix)
```

**原理**: 信息熵越小,差异越大,权重越高

### 7.4 AHP (层次分析法)

**AHP**: 基于成对比较赋权

```python
from mcda_core.services import AHPService

service = AHPService()

# 构造判断矩阵
judgment_matrix = [
    [1, 3, 5],    # 准则1 vs 准则1,2,3
    [1/3, 1, 3],  # 准则2 vs 准则1,2,3
    [1/5, 1/3, 1] # 准则3 vs 准则1,2,3
]

weights = service.calculate_weights(judgment_matrix)

# 一致性检验
cr = service.calculate_consistency_ratio(judgment_matrix)
if cr < 0.1:
    print("一致性良好")
```

**原理**: 专家判断,层次化分析

### 7.5 PCA (主成分分析)

**PCA**: 基于方差贡献赋权

```python
from mcda_core.weighting import pca_weighting

weights = pca_weighting(decision_matrix)
```

**原理**: 主成分贡献率作为权重

### 7.6 Game Theory (博弈论)

**博弈论组合权重**: 综合多种赋权方法

```python
from mcda_core.weighting import GameTheoryWeighting

gt = GameTheoryWeighting()

# 多种方法计算的权重矩阵
weights_matrix = {
    "CV": cv_weights,
    "CRITIC": critic_weights,
    "Entropy": entropy_weights,
}

# 博弈论组合
combined_weights = gt.combine_weights(weights_matrix)
```

**原理**: 纳什均衡,综合优化

---

## 8. 评分规则

### 8.1 线性评分 (Linear Scoring)

**线性映射**: 将原始值线性映射到 0-100

```python
from mcda_core.models import LinearScoringRule
from mcda_core.scoring import ScoringApplier

# 定义规则: 将 0-1000 映射到 0-100
rule = LinearScoringRule(min=0, max=1000, scale=100)

applier = ScoringApplier()

# 越高越好
score = applier.apply_linear(500, rule, "higher_better")
print(score)  # 50.0

# 越低越好
score = applier.apply_linear(500, rule, "lower_better")
print(score)  # 50.0
```

### 8.2 阈值评分 (Threshold Scoring)

**分段评分**: 根据阈值区间赋予固定分值

```python
from mcda_core.models import ThresholdScoringRule, ThresholdRange
from mcda_core.scoring import ScoringApplier

# 定义规则
rule = ThresholdScoringRule(
    ranges=(
        ThresholdRange(max=100, score=100),      # < 100: 100分
        ThresholdRange(min=100, max=300, score=80),  # 100-300: 80分
        ThresholdRange(min=300, max=600, score=60),  # 300-600: 60分
        ThresholdRange(min=600, score=40),      # > 600: 40分
    ),
    default_score=0
)

applier = ScoringApplier()

# 应用评分
score = applier.apply_threshold(200, rule, "lower_better")
print(score)  # 80
```

### 8.3 评分规则应用

**完整示例**:

```python
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.models import LinearScoringRule, ThresholdScoringRule
from mcda_core.scoring import ScoringApplier

# 原始数据
raw_data = {
    "供应商A": {"价格": 800, "质量": 85},
    "供应商B": {"价格": 1200, "质量": 92},
    "供应商C": {"价格": 650, "质量": 78},
}

# 定义评分规则
applier = ScoringApplier()

price_rule = LinearScoringRule(min=500, max=1500, scale=100)
quality_rule = ThresholdScoringRule(
    ranges=(
        ThresholdRange(max=70, score=60),
        ThresholdRange(min=70, max=85, score=80),
        ThresholdRange(min=85, score=100),
    ),
    default_score=0
)

# 应用评分规则
scores = {}
for alt, raw_scores in raw_data.items():
    scores[alt] = {
        "价格": applier.apply_linear(raw_scores["价格"], price_rule, "lower_better"),
        "质量": applier.apply_threshold(raw_scores["质量"], quality_rule, "higher_better"),
    }

# 创建决策问题
criteria = [
    Criterion(name="价格", weight=0.4, direction="lower_better"),
    Criterion(name="质量", weight=0.6, direction="higher_better"),
]

problem = DecisionProblem(
    alternatives=("供应商A", "供应商B", "供应商C"),
    criteria=tuple(criteria),
    scores=scores,
)

# 分析
orchestrator = MCDAOrchestrator()
result = orchestrator.analyze(problem, algorithm_name="wsm")

print(f"最佳供应商: {result.rankings[0].alternative}")
```

---

## 9. 群决策聚合

### 9.1 加权平均聚合

**Weighted Average**: 加权平均聚合多个决策者的意见

```python
from mcda_core.aggregation import WeightedAverageAggregation

# 构造评分矩阵
score_matrix = {
    "供应商A": {
        "成本": {"DM1": 60, "DM2": 65},
        "质量": {"DM1": 85, "DM2": 80},
    },
    "供应商B": {
        "成本": {"DM1": 70, "DM2": 75},
        "质量": {"DM1": 90, "DM2": 88},
    },
}

# 决策者权重
dm_weights = {"DM1": 0.6, "DM2": 0.4}

aggregator = WeightedAverageAggregation()
aggregated_scores = aggregator.aggregate_matrix(score_matrix, dm_weights)

print(aggregated_scores)
# {'供应商A': {'成本': 62.0, '质量': 83.0}, ...}
```

### 9.2 Borda 计数聚合

**Borda Count**: 基于排序的聚合方法

```python
from mcda_core.aggregation import BordaCountAggregation

aggregator = BordaCountAggregation()
aggregated_scores = aggregator.aggregate_matrix(score_matrix)
```

**原理**: 每个决策者对方案排序,按排名赋分(第1名得n-1分,第2名得n-2分,...)

### 9.3 Copeland 聚合

**Copeland**: 基于成对比较的聚合

```python
from mcda_core.aggregation import CopelandAggregation

aggregator = CopelandAggregation()
aggregated_scores = aggregator.aggregate_matrix(score_matrix)
```

**原理**: 方案间成对比较,胜者得1分,败者得0分,平局得0.5分

### 9.4 完整群决策示例

```python
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.aggregation import WeightedAverageAggregation

# 1. 3个决策者的评分矩阵
score_matrix = {
    "项目A": {
        "成本": {"DM1": 60, "DM2": 65, "DM3": 70},
        "效益": {"DM1": 85, "DM2": 80, "DM3": 82},
    },
    "项目B": {
        "成本": {"DM1": 70, "DM2": 75, "DM3": 68},
        "效益": {"DM1": 90, "DM2": 88, "DM3": 85},
    },
}

# 2. 聚合
aggregator = WeightedAverageAggregation()
dm_weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
aggregated_scores = aggregator.aggregate_matrix(score_matrix, dm_weights)

# 3. 创建决策问题
criteria = [
    Criterion(name="成本", weight=0.4, direction="lower_better"),
    Criterion(name="效益", weight=0.6, direction="higher_better"),
]

problem = DecisionProblem(
    alternatives=("项目A", "项目B"),
    criteria=tuple(criteria),
    scores=aggregated_scores,
)

# 4. 分析
orchestrator = MCDAOrchestrator()
result = orchestrator.analyze(problem, algorithm_name="wsm")

print(f"最佳项目: {result.rankings[0].alternative}")
```

---

## 10. 约束否决

### 10.1 硬否决 (Hard Veto)

**硬否决**: 条件不满足时直接拒绝方案

```python
from mcda_core.models import Criterion, VetoConfig, VetoCondition

criteria = [
    Criterion(
        name="成本",
        weight=0.5,
        direction="lower_better",
        veto=VetoConfig(
            type="hard",
            condition=VetoCondition(
                operator="<=",
                value=80,
                action="reject"
            ),
            reject_reason="成本超过 80 被拒绝"
        )
    )
]
```

**说明**: 如果成本 ≤ 80,通过;否则拒绝

### 10.2 软否决 (Soft Veto)

**软否决**: 条件满足时警告并惩罚

```python
criteria = [
    Criterion(
        name="风险",
        weight=0.3,
        direction="lower_better",
        veto=VetoConfig(
            type="soft",
            condition=VetoCondition(
                operator=">=",
                value=60,
                action="warn"
            ),
            penalty=0.2,  # 惩罚 20%
            warning_message="风险较高,请注意"
        )
    )
]
```

**说明**: 如果风险 ≥ 60,警告并扣 20% 分

### 10.3 分级否决 (Tiered Veto)

**分级否决**: 多档位惩罚

```python
from mcda_core.models import TieredVetoCondition

veto_config = VetoConfig(
    type="tiered",
    condition=TieredVetoCondition(
        tiers=(
            VetoCondition(operator=">=", value=80, action="penalty", penalty=0.1),
            VetoCondition(operator=">=", value=90, action="penalty", penalty=0.3),
            VetoCondition(operator=">=", value=95, action="reject"),
        )
    )
)
```

**说明**:
- 80-90: 惩罚 10%
- 90-95: 惩罚 30%
- ≥95: 拒绝

### 10.4 否决评估

```python
from mcda_core.constraints import VetoEvaluator

evaluator = VetoEvaluator()

# 评估单个方案
veto_result = evaluator.evaluate(
    alternative_id="方案A",
    scores={"成本": 85, "质量": 90},
    criteria=criteria
)

if veto_result.rejected:
    print(f"方案被拒绝: {veto_result.reject_reason}")
else:
    print(f"方案通过,总惩罚: {veto_result.total_penalty}")

# 在编排器中使用
orchestrator = MCDAOrchestrator()
result = orchestrator.analyze(problem, algorithm_name="topsis")

# 查看否决结果
if result.veto_results:
    for alt, veto_res in result.veto_results.items():
        print(f"{alt}: {veto_res.status}")
```

---

## 11. 数据加载

### 11.1 YAML 格式

**decision.yaml**:
```yaml
name: 供应商选择
alternatives:
  - 供应商A
  - 供应商B
criteria:
  - name: 性能
    weight: 0.4
    direction: higher_better
  - name: 成本
    weight: 0.3
    direction: lower_better
scores:
  供应商A:
    性能: 85
    成本: 50
  供应商B:
    性能: 90
    成本: 60
algorithm:
  name: topsis
```

**加载**:
```python
from mcda_core.core import MCDAOrchestrator

orchestrator = MCDAOrchestrator()
problem = orchestrator.load_from_yaml("decision.yaml")
result = orchestrator.analyze(problem)
```

### 11.2 JSON 格式

**decision.json**:
```json
{
  "name": "供应商选择",
  "alternatives": ["供应商A", "供应商B"],
  "criteria": [
    {"name": "性能", "weight": 0.4, "direction": "higher_better"},
    {"name": "成本", "weight": 0.3, "direction": "lower_better"}
  ],
  "scores": {
    "供应商A": {"性能": 85, "成本": 50},
    "供应商B": {"性能": 90, "成本": 60}
  },
  "algorithm": {"name": "topsis"}
}
```

**加载**:
```python
from mcda_core.loaders import JSONLoader

loader = JSONLoader()
config = loader.load("decision.json")
```

### 11.3 CSV 格式

**decision.csv**:
```csv
方案A,方案B,方案C
性能,0.4,higher,85,90,88
成本,0.3,lower,5000,6000,5500
质量,0.3,higher,80,85,82
```

**格式说明**:
- 第 1 行: 方案名称
- 后续行: 每行一个准则
  - 第 1 列: 准则名称
  - 第 2 列: 权重
  - 第 3 列: 方向(higher/lower)
  - 后续列: 各方案的评分

**加载**:
```python
from mcda_core.loaders import CSVLoader

loader = CSVLoader()
config = loader.load("decision.csv")

# CSV 返回 matrix 格式
matrix = config['matrix']  # [criterion][alternative]
alternatives = config['alternatives']
criteria = config['criteria']
```

### 11.4 CSV 区间数格式

**decision_interval.csv**:
```csv
方案A,方案B
性能,0.6,higher,"80,90","85,95"
成本,0.4,lower,"40,50","30,40"
```

**说明**: 每个方案的评分为区间数(最小值,最大值)

**加载**:
```python
from mcda_core.loaders import CSVLoader

loader = CSVLoader()
config = loader.load("decision_interval.csv")

# 区间数自动转换为 Interval 对象
from mcda_core.interval import Interval
assert config['matrix'][0][0] == Interval(80, 90)
```

### 11.5 Excel 格式

**decision.xlsx**:
- 格式与 CSV 相同
- 第一个 sheet 作为数据源

**加载**:
```python
from mcda_core.loaders import ExcelLoader

loader = ExcelLoader()
config = loader.load("decision.xlsx")
```

### 11.6 加载器工厂

**自动检测文件格式**:

```python
from mcda_core.loaders import LoaderFactory

# 根据文件扩展名自动选择加载器
loader = LoaderFactory.get_loader("decision.yaml")  # YAMLLoader
loader = LoaderFactory.get_loader("decision.json")  # JSONLoader
loader = LoaderFactory.get_loader("decision.csv")   # CSVLoader
loader = LoaderFactory.get_loader("decision.xlsx")  # ExcelLoader
```

---

## 12. 可视化

### 12.1 ASCII 柱状图

```python
from mcda_core.visualization.ascii_visualizer import ASCIIVisualizer

visualizer = ASCIIVisualizer()

# 准备数据
ranking_data = {
    "方案C": 78.5,
    "方案A": 65.2,
    "方案B": 52.1,
}

# 生成柱状图
chart = visualizer.bar_chart(
    ranking_data,
    title="决策分析排名",
    width=50,
    height=8
)

print(chart)
```

**输出**:
```
决策分析排名
方案C ███████████████████████████████████████████████████ 78.5
方案A ██████████████████████████████████████ 65.2
方案B ████████████████████████████ 52.1
```

### 12.2 ASCII 雷达图

```python
# 准备数据
labels = ["性能", "成本", "质量", "服务"]
scores = [0.85, 0.78, 0.92, 0.80]

# 生成雷达图
chart = visualizer.radar_chart(scores, labels)
print(chart)
```

### 12.3 排名显示

```python
rankings = [
    (1, "方案C", 78.5),
    (2, "方案A", 65.2),
    (3, "方案B", 52.1),
]

for rank, alt, score in rankings:
    bar_length = int(score / 100 * 40)
    bar = "█" * bar_length
    print(f"{rank}. {alt:8s} {score:5.1f} {bar}")
```

### 12.4 表格显示

```python
# 生成对比表
headers = ["方案", "排名", "得分", "性能", "成本", "质量"]
rows = []
for ranking in result.rankings:
    alt = ranking.alternative
    scores = problem.scores[alt]
    rows.append([
        alt,
        ranking.rank,
        f"{ranking.score:.2f}",
        scores["性能"],
        scores["成本"],
        scores["质量"]
    ])

# 打印表格
print(" | ".join(f"{h:^10}" for h in headers))
print("-" * 70)
for row in rows:
    print(" | ".join(f"{str(val):^10}" for val in row))
```

### 12.5 HTML 报告

```python
# 生成 HTML 报告
report = orchestrator.generate_report(
    problem,
    result,
    format="html",
    output_file="report.html"
)

# HTML 报告包含:
# - 排名表格
# - 柱状图
# - 详细评分
# - 算法说明
```

---

## 13. CLI 使用

### 13.1 安装 CLI

```bash
# 安装 MCDA-Core 后即可使用
mcda-core --help
```

### 13.2 基本命令

**分析决策问题**:
```bash
mcda-core analyze decision.yaml --algorithm topsis
```

**比较多个算法**:
```bash
mcda-core compare decision.yaml --algorithms wsm,topsis,vikor
```

**生成可视化**:
```bash
mcda-core visualize decision.yaml --output result.html
```

**查看帮助**:
```bash
mcda-core --help
mcda-core analyze --help
mcda-core compare --help
```

### 13.3 CLI 示例

**示例 1: 基本分析**:
```bash
mcda-core analyze decision.yaml
```

**示例 2: 指定算法**:
```bash
mcda-core analyze decision.yaml --algorithm topsis
```

**示例 3: 多算法对比**:
```bash
mcda-core compare decision.yaml --algorithms wsm,wpm,topsis,vikor
```

**示例 4: 生成报告**:
```bash
mcda-core analyze decision.yaml --output report.md --format markdown
```

**示例 5: 敏感性分析**:
```bash
mcda-core analyze decision.yaml --sensitivity
```

---

## 14. API 参考

### 14.1 MCDAOrchestrator

**核心编排器类**

```python
from mcda_core.core import MCDAOrchestrator

orchestrator = MCDAOrchestrator()
```

**方法**:

- **load_from_yaml(path, auto_normalize_weights=True, apply_scoring=True)**
  ```python
  problem = orchestrator.load_from_yaml("decision.yaml")
  ```

- **analyze(problem, algorithm_name=None, run_sensitivity=False)**
  ```python
  result = orchestrator.analyze(
      problem,
      algorithm_name="topsis",
      run_sensitivity=True
  )
  ```

- **generate_report(problem, result, format="markdown", output_file=None)**
  ```python
  report = orchestrator.generate_report(
      problem,
      result,
      format="markdown",  # markdown, html, json
      output_file="report.md"
  )
  ```

### 14.2 DecisionProblem

**决策问题模型**

```python
from mcda_core.models import DecisionProblem

problem = DecisionProblem(
    alternatives=("方案A", "方案B"),
    criteria=(criterion1, criterion2),
    scores={"方案A": {"性能": 85}, "方案B": {"性能": 90}}
)
```

**属性**:
- `alternatives`: Tuple[str, ...] - 备选方案
- `criteria`: Tuple[Criterion, ...] - 评估准则
- `scores`: Dict[str, Dict[str, float]] - 评分
- `algorithm`: Optional[str] - 默认算法

### 14.3 Criterion

**准则模型**

```python
from mcda_core.models import Criterion

criterion = Criterion(
    name="性能",
    weight=0.4,
    direction="higher_better",
    description="产品性能指标",
    veto=None
)
```

**属性**:
- `name`: str - 准则名称
- `weight`: float - 权重 (0-1)
- `direction`: str - 方向 ("higher_better" 或 "lower_better")
- `description`: Optional[str] - 描述
- `veto`: Optional[VetoConfig] - 否决配置

### 14.4 DecisionResult

**决策结果模型**

```python
result = orchestrator.analyze(problem)
```

**属性**:
- `rankings`: List[Ranking] - 排名列表
- `metadata`: ResultMetadata - 元数据
- `sensitivity_analysis`: Optional[SensitivityAnalysis] - 敏感性分析
- `veto_results`: Optional[Dict[str, VetoResult]] - 否决结果

**Ranking 属性**:
- `rank`: int - 排名
- `alternative`: str - 方案名称
- `score`: float - 原始得分
- `normalized_score`: float - 归一化得分 (0-100)

**ResultMetadata 属性**:
- `algorithm_name`: str - 算法名称
- `execution_time`: float - 执行时间(ms)
- `timestamp`: str - 时间戳

---

## 15. 示例

### 15.1 供应商选择

**场景**: 从多个供应商中选择最优供应商

**准则**: 成本、质量、交期、服务

**代码**:
```python
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion

problem = DecisionProblem(
    alternatives=("供应商A", "供应商B", "供应商C", "供应商D"),
    criteria=(
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="质量", weight=0.3, direction="higher_better"),
        Criterion(name="交期", weight=0.2, direction="lower_better"),
        Criterion(name="服务", weight=0.2, direction="higher_better"),
    ),
    scores={
        "供应商A": {"成本": 5000, "质量": 85, "交期": 7, "服务": 80},
        "供应商B": {"成本": 6000, "质量": 90, "交期": 5, "服务": 85},
        "供应商C": {"成本": 4500, "质量": 80, "交期": 10, "服务": 75},
        "供应商D": {"成本": 5500, "质量": 88, "交期": 6, "服务": 82},
    }
)

orchestrator = MCDAOrchestrator()
result = orchestrator.analyze(problem, algorithm_name="topsis")

print(f"最佳供应商: {result.rankings[0].alternative}")
report = orchestrator.generate_report(problem, result)
print(report)
```

### 15.2 项目优先级排序

**场景**: 对多个项目进行优先级排序

**准则**: 收益、成本、风险、战略契合度

**代码**:
```python
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion

problem = DecisionProblem(
    alternatives=("项目A", "项目B", "项目C"),
    criteria=(
        Criterion(name="收益", weight=0.35, direction="higher_better"),
        Criterion(name="成本", weight=0.25, direction="lower_better"),
        Criterion(name="风险", weight=0.20, direction="lower_better"),
        Criterion(name="战略", weight=0.20, direction="higher_better"),
    ),
    scores={
        "项目A": {"收益": 90, "成本": 60, "风险": 40, "战略": 85},
        "项目B": {"收益": 85, "成本": 50, "风险": 30, "战略": 90},
        "项目C": {"收益": 95, "成本": 70, "风险": 50, "战略": 75},
    }
)

orchestrator = MCDAOrchestrator()

# 比较多个算法
algorithms = ["wsm", "topsis", "vikor"]
for algo in algorithms:
    result = orchestrator.analyze(problem, algorithm_name=algo)
    print(f"{algo.upper()}: {result.rankings[0].alternative}")
```

### 15.3 群决策

**场景**: 3 位专家对 5 个方案进行评估

**代码**:
```python
from mcda_core.aggregation import WeightedAverageAggregation
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion

# 专家评分矩阵
score_matrix = {
    "方案A": {
        "收益": {"专家1": 85, "专家2": 80, "专家3": 82},
        "成本": {"专家1": 60, "专家2": 65, "专家3": 62},
    },
    "方案B": {
        "收益": {"专家1": 90, "专家2": 88, "专家3": 85},
        "成本": {"专家1": 70, "专家2": 68, "专家3": 72},
    },
}

# 聚合
aggregator = WeightedAverageAggregation()
dm_weights = {"专家1": 0.4, "专家2": 0.35, "专家3": 0.25}
aggregated_scores = aggregator.aggregate_matrix(score_matrix, dm_weights)

# 分析
criteria = [
    Criterion(name="收益", weight=0.6, direction="higher_better"),
    Criterion(name="成本", weight=0.4, direction="lower_better"),
]

problem = DecisionProblem(
    alternatives=("方案A", "方案B"),
    criteria=tuple(criteria),
    scores=aggregated_scores,
)

orchestrator = MCDAOrchestrator()
result = orchestrator.analyze(problem, algorithm_name="wsm")

print(f"最佳方案: {result.rankings[0].alternative}")
```

### 15.4 使用约束否决

**场景**: 拒绝成本过高或风险过大的方案

**代码**:
```python
from mcda_core.models import Criterion, VetoConfig, VetoCondition
from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem

criteria = [
    Criterion(
        name="成本",
        weight=0.4,
        direction="lower_better",
        veto=VetoConfig(
            type="hard",
            condition=VetoCondition(operator="<=", value=80, action="reject"),
            reject_reason="成本超过 80 被拒绝"
        )
    ),
    Criterion(
        name="风险",
        weight=0.3,
        direction="lower_better",
        veto=VetoConfig(
            type="soft",
            condition=VetoCondition(operator=">=", value=60, action="warn"),
            penalty=0.2,
            warning_message="风险较高"
        )
    ),
    Criterion(name="收益", weight=0.3, direction="higher_better"),
]

problem = DecisionProblem(
    alternatives=("方案A", "方案B", "方案C"),
    criteria=tuple(criteria),
    scores={
        "方案A": {"成本": 85, "风险": 50, "收益": 90},  # 成本过高,被拒绝
        "方案B": {"成本": 70, "风险": 65, "收益": 85},  # 风险高,警告
        "方案C": {"成本": 60, "风险": 40, "收益": 80},  # 通过
    }
)

orchestrator = MCDAOrchestrator()
result = orchestrator.analyze(problem, algorithm_name="wsm")

# 查看否决结果
for alt, veto_res in result.veto_results.items():
    print(f"{alt}: {veto_res.status}")
    if veto_res.rejected:
        print(f"  拒绝原因: {veto_res.reject_reason}")
    if veto_res.warnings:
        print(f"  警告: {veto_res.warnings}")
```

---

## 16. 常见问题

### 16.1 安装问题

**Q: pip install 失败?**

A: 检查 Python 版本:
```bash
python --version  # 需要 3.10+
```

**Q: 导入模块失败?**

A: 确保 MCDA-Core 在 Python 路径中:
```python
import sys
print(sys.path)  # 检查路径
```

### 16.2 使用问题

**Q: 如何选择合适的算法?**

A: 参考以下原则:
- **快速决策**: WSM, WPM
- **通用场景**: TOPSIS
- **折中决策**: VIKOR
- **风险决策**: TODIM
- **不确定决策**: ELECTRE-I

**Q: 权重如何确定?**

A: 三种方法:
1. **主观赋权**: 专家判断, AHP
2. **客观赋权**: CV, CRITIC, 熵权法
3. **组合赋权**: 博弈论组合

**Q: 评分范围有限制吗?**

A: 是的,评分必须在 0-100 范围内。如果原始数据超出范围,使用评分规则进行映射。

### 16.3 性能问题

**Q: 如何处理大规模数据(>1000 方案)?**

A: 使用更快的算法(WSM, WPM),并考虑:
```python
# 禁用敏感性分析
result = orchestrator.analyze(problem, run_sensitivity=False)

# 使用更简单的标准化方法
```

**Q: 如何提高分析速度?**

A:
1. 使用更快的算法
2. 减少准则数量
3. 禁用敏感性分析
4. 使用 NumPy 优化

### 16.4 结果解释

**Q: 得分是相对的还是绝对的?**

A: 得分是相对的,用于排序。不同算法的得分不可直接比较。

**Q: 为什么不同算法得到不同结果?**

A: 不同算法的原理不同:
- TOPSIS 基于距离
- VIKOR 基于折中
- TODIM 考虑心理行为

建议使用多个算法,综合判断。

---

## 17. 最佳实践

### 17.1 数据准备

**1. 标准化评分范围**
```python
# 使用评分规则映射到 0-100
from mcda_core.scoring import ScoringApplier
applier = ScoringApplier()
score = applier.apply_linear(raw_value, rule, "higher_better")
```

**2. 确保权重归一化**
```python
# 权重和应为 1.0
total_weight = sum(c.weight for c in criteria)
assert abs(total_weight - 1.0) < 1e-6
```

**3. 处理缺失数据**
```python
# 方法 1: 填充默认值
scores[alt][criterion] = scores[alt].get(criterion, 0)

# 方法 2: 插值
import numpy as np
scores[alt][criterion] = np.mean([s for s in scores[alt].values()])
```

### 17.2 算法选择

**1. 根据场景选择**
```python
# 快速决策 → WSM
if need_speed:
    algorithm = "wsm"

# 通用场景 → TOPSIS
else:
    algorithm = "topsis"

# 风险决策 → TODIM
if consider_risk:
    algorithm = "todim"
```

**2. 多算法验证**
```python
# 使用多个算法验证结果
algorithms = ["wsm", "topsis", "vikor"]
results = {}
for algo in algorithms:
    results[algo] = orchestrator.analyze(problem, algo)

# 检查一致性
winners = [r.rankings[0].alternative for r in results.values()]
if len(set(winners)) == 1:
    print("结果一致")
else:
    print("结果不一致,需要进一步分析")
```

### 17.3 结果解释

**1. 生成完整报告**
```python
# 包含排名、评分、敏感性分析
report = orchestrator.generate_report(
    problem,
    result,
    format="markdown",
    include_sensitivity=True,
    include_details=True
)
```

**2. 可视化**
```python
# 使用可视化帮助理解
from mcda_core.visualization.ascii_visualizer import ASCIIVisualizer
visualizer = ASCIIVisualizer()
chart = visualizer.bar_chart(ranking_data, title="排名")
print(chart)
```

**3. 敏感性分析**
```python
# 分析权重变化的影响
result = orchestrator.analyze(problem, run_sensitivity=True)
if result.sensitivity_analysis:
    print(f"稳定性: {result.sensitivity_analysis.stability}")
```

### 17.4 代码质量

**1. 类型注解**
```python
from mcda_core.models import DecisionProblem, DecisionResult

def analyze_problem(problem: DecisionProblem) -> DecisionResult:
    orchestrator = MCDAOrchestrator()
    return orchestrator.analyze(problem)
```

**2. 错误处理**
```python
from mcda_core.exceptions import ConfigLoadError

try:
    problem = orchestrator.load_from_yaml("decision.yaml")
except ConfigLoadError as e:
    print(f"加载失败: {e}")
    # 处理错误
```

**3. 日志记录**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("开始分析...")
result = orchestrator.analyze(problem)
logger.info(f"分析完成,最佳方案: {result.rankings[0].alternative}")
```

---

## 18. 性能优化

### 18.1 大规模数据

**问题**: 方案数 >1000 时性能下降

**解决方案**:
```python
# 1. 使用快速算法
result = orchestrator.analyze(problem, algorithm_name="wsm")

# 2. 禁用敏感性分析
result = orchestrator.analyze(problem, run_sensitivity=False)

# 3. 批量处理
batch_size = 100
for i in range(0, len(alternatives), batch_size):
    batch_alternatives = alternatives[i:i+batch_size]
    # 处理批次
```

### 18.2 内存优化

**问题**: 大数据集占用内存过多

**解决方案**:
```python
# 1. 使用生成器
def score_generator(alternatives):
    for alt in alternatives:
        yield calculate_score(alt)

# 2. 及时释放内存
import gc
result = orchestrator.analyze(problem)
del problem
gc.collect()
```

### 18.3 并行计算

**问题**: 单线程处理慢

**解决方案**:
```python
from concurrent.futures import ProcessPoolExecutor

def analyze_with_algo(algo):
    return orchestrator.analyze(problem, algo)

algorithms = ["wsm", "topsis", "vikor", "todim"]

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(analyze_with_algo, algorithms))
```

### 18.4 性能监控

```python
import time

start = time.time()
result = orchestrator.analyze(problem)
end = time.time()

print(f"执行时间: {end - start:.2f}秒")
print(f"元数据: {result.metadata.execution_time}ms")
```

---

## 附录

### A. 完整示例代码

参见 `examples/` 目录:
- `basic_usage.py`: 基本使用
- `supplier_selection.py`: 供应商选择
- `group_decision.py`: 群决策
- `constraint_veto.py`: 约束否决

### B. API 完整参考

参见 [docs/mcda-core/api_reference.md](api_reference.md)

### C. 算法数学原理

参见 [docs/mcda-core/algorithms.md](algorithms.md)

### D. 更新日志

参见 [CHANGELOG.md](../../../CHANGELOG.md)

### E. 贡献指南

参见 [CONTRIBUTING.md](../../../CONTRIBUTING.md)

---

## 联系我们

- **GitHub**: https://github.com/your-org/ai_core_skills
- **Issues**: https://github.com/your-org/ai_core_skills/issues
- **Email**: support@example.com

---

**用户手册版本**: v1.0.0
**最后更新**: 2026-02-06
**维护者**: MCDA-Core 开发团队

🎉 **感谢使用 MCDA-Core!** 🎉
