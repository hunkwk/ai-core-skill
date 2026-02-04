---
name: mcda-core
description: 多准则决策分析核心框架，支持多种算法模型（WSM、AHP、TOPSIS）。当用户需要在多个备选方案之间做结构化决策时使用（如供应商选择、产品评估、招聘决策、投资选择）。处理决策矩阵定义、验证、计算和敏感性分析。当前支持算法：WSM（加权汇总模型）。
license: Apache-2.0
---

# MCDA Core

多准则决策分析核心框架，支持可插拔算法模型。

## 快速开始

1. 定义决策问题（备选方案、准则、权重、评分）
2. 验证输入：`python lib/core.py validate decision.yaml`
3. 运行计算：`python lib/core.py calculate decision.yaml`
4. 生成报告：`python lib/core.py report decision.yaml --output report.md`

## 工作流程

**步骤 1：构建决策问题**

询问用户：
- 在哪些方案中选择？（备选方案）
- 哪些准则重要？（准则及权重）
- 如何对每个方案评分？（1-5 分制）

**步骤 2：创建 YAML 配置**

```yaml
problem: "选择最佳供应商"

alternatives:
  - AWS
  - Azure
  - GCP

criteria:
  - name: 成本
    weight: 0.35
    direction: lower_better    # 越低越好
  - name: 功能完整性
    weight: 0.30
    direction: higher_better   # 越高越好

scores:
  AWS:
    成本: 3
    功能完整性: 5
  Azure:
    成本: 4
    功能完整性: 4

algorithm:
  name: wsm
```

**步骤 3：验证与计算**

```bash
python lib/core.py validate decision.yaml
python lib/core.py calculate decision.yaml
```

**步骤 4：分析结果**

- 查看排名和得分
- 检查敏感性分析
- 导出报告（Markdown）

## 算法

**当前支持**：WSM（加权汇总模型）
- 公式：`得分 = Σ(权重_i × 评分_i)`
- 支持：higher_better / lower_better
- 用途：简单加权和

**计划支持**：AHP、TOPSIS（见 [algorithms.md](references/algorithms.md)）

## 高级功能

算法详情，参见 [algorithms.md](references/algorithms.md)
YAML 模式，参见 [yaml-schema.md](references/yaml-schema.md)
使用案例，参见 [examples.md](references/examples.md)
敏感性分析，参见 [sensitivity.md](references/sensitivity.md)
