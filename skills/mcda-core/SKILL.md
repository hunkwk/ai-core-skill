---
name: mcda-core
description: Multi-Criteria Decision Analysis core framework supporting multiple algorithmic models (WSM, WPM, TOPSIS, VIKOR). Use when user needs to make structured decisions between alternatives with conflicting criteria (e.g., vendor selection, product evaluation, hiring decisions, investment choices). Handles decision matrix definition, validation, calculation, and sensitivity analysis.
license: Apache-2.0
---

# MCDA Core

多准则决策分析核心框架，支持可插拔算法模型。

## Quick Start

1. Define decision problem (alternatives, criteria, weights, scores)
2. Validate input: `mcda validate config.yaml`
3. Run calculation: `mcda analyze config.yaml`
4. Generate report: `mcda analyze config.yaml -o report.md`

## Workflow

**Step 1: Structure Decision Problem**

Ask user:
- What are you choosing between? (alternatives)
- What criteria matter? (criteria with weights)
- How to score each alternative? (scores 0-100)

**Step 2: Create YAML Config**

```yaml
name: 供应商选择

alternatives:
  - 供应商A
  - 供应商B
  - 供应商C

criteria:
  - name: 成本
    weight: 0.35
    direction: lower_better
  - name: 质量
    weight: 0.30
    direction: higher_better
  - name: 交付期
    weight: 0.20
    direction: lower_better
  - name: 服务
    weight: 0.15
    direction: higher_better

scores:
  供应商A:
    成本: 50
    质量: 80
    交付期: 30
    服务: 70
  供应商B:
    成本: 70
    质量: 60
    交付期: 20
    服务: 80
  供应商C:
    成本: 60
    质量: 90
    交付期: 40
    服务: 60

algorithm:
  name: topsis
```

**Step 3: Validate & Calculate**

```bash
mcda validate config.yaml
mcda analyze config.yaml
```

**Step 4: Analyze Results**

- Review ranking and scores
- Check sensitivity analysis (optional: `mcda analyze config.yaml --sensitivity`)
- Export report (Markdown/JSON)

## Algorithms

**Available Algorithms**:

1. **WSM** (Weighted Sum Model)
   - Formula: `Score = Σ(weight_i × score_i)`
   - Use case: Simple additive weighting
   - Pros: Simple, intuitive, easy to understand

2. **WPM** (Weighted Product Model)
   - Formula: `Score = ∏(score_i ^ weight_i)`
   - Use case: Multiplicative decision making
   - Pros: Penalizes low scores more heavily

3. **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution)
   - Formula: Based on distance to positive/negative ideal solutions
   - Use case: Multi-criteria ranking with conflicting criteria
   - Pros: Handles trade-offs well, widely used

4. **VIKOR** (VIseKriterijumska Optimizacija I Kompromisno Resenje)
   - Formula: Based on utility measure and regret measure
   - Parameter: v (0 to 1, default 0.5)
   - Use case: Compromise decision making
   - Pros: Balances group utility and individual regret

## Advanced

**CLI Commands**:
```bash
mcda analyze <config> [-o OUTPUT] [-a ALGORITHM] [-f FORMAT] [-s]
mcda validate <config>
mcda --help
mcda --version
```

**Report Formats**: markdown, json

**Algorithms**: wsm, wpm, topsis, vikor
