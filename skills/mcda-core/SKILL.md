---
name: mcda-core
description: Multi-Criteria Decision Analysis core framework supporting multiple algorithmic models (WSM, AHP, TOPSIS). Use when user needs to make structured decisions between alternatives with conflicting criteria (e.g., vendor selection, product evaluation, hiring decisions, investment choices). Handles decision matrix definition, validation, calculation, and sensitivity analysis. Current algorithms: WSM (Weighted Sum Model).
license: Apache-2.0
---

# MCDA Core

多准则决策分析核心框架，支持可插拔算法模型。

## Quick Start

1. Define decision problem (alternatives, criteria, weights, scores)
2. Validate input: `python lib/core.py validate decision.yaml`
3. Run calculation: `python lib/core.py calculate decision.yaml`
4. Generate report: `python lib/core.py report decision.yaml --output report.md`

## Workflow

**Step 1: Structure Decision Problem**

Ask user:
- What are you choosing between? (alternatives)
- What criteria matter? (criteria with weights)
- How to score each alternative? (1-5 scale)

**Step 2: Create YAML Config**

```yaml
problem: "选择最佳供应商"

alternatives:
  - AWS
  - Azure
  - GCP

criteria:
  - name: 成本
    weight: 0.35
    direction: lower_better
  - name: 功能完整性
    weight: 0.30
    direction: higher_better

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

**Step 3: Validate & Calculate**

```bash
python lib/core.py validate decision.yaml
python lib/core.py calculate decision.yaml
```

**Step 4: Analyze Results**

- Review ranking and scores
- Check sensitivity analysis
- Export report (Markdown)

## Algorithms

**Current**: WSM (Weighted Sum Model)
- Formula: `Score = Σ(weight_i × score_i)`
- Supports: higher_better / lower_better
- Use case: Simple additive weighting

**Planned**: AHP, TOPSIS (see [algorithms.md](references/algorithms.md))

## Advanced

For algorithm details, see [algorithms.md](references/algorithms.md)
For YAML schema, see [yaml-schema.md](references/yaml-schema.md)
For examples, see [examples.md](references/examples.md)
For sensitivity analysis, see [sensitivity.md](references/sensitivity.md)
