---
name: mcda-core
description: Multi-Criteria Decision Analysis (MCDA) framework supporting 14 algorithms (WSM, WPM, TOPSIS, VIKOR, TODIM, ELECTRE-I, PROMETHEE II) with interval number support. Use for structured decisions between alternatives with conflicting criteria (vendor selection, product evaluation, hiring, investment). Handles decision matrix definition, validation, calculation, sensitivity analysis, ranking, and visualization.
license: Apache-2.0
---

# MCDA Core

Multi-Criteria Decision Analysis core framework with 14 algorithms and interval number support.

## Quick Start

1. Define decision problem (alternatives, criteria, weights, scores)
2. Load data: JSON/CSV/Excel/YAML
3. Run calculation: `algorithm.calculate(problem)`
4. Export results: Markdown/JSON/ASCII/Charts

## Workflow

**Step 1: Define Decision Problem**

Ask user:
- What are you choosing between? (alternatives)
- What criteria matter? (criteria with weights, directions)
- How to score each alternative? (0-100 or intervals [min, max])

**Step 2: Load Data**

```python
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.loaders import JSONLoader

# JSON format
loader = JSONLoader("decision.json")
problem = loader.load()
```

**Step 3: Run Algorithm**

```python
from mcda_core.algorithms import get_algorithm

# Get algorithm
algo = get_algorithm("topsis")  # or vikor, todim, wsm, wpm, etc.

# Calculate
result = algo.calculate(problem)

# View ranking
for r in result.rankings:
    print(f"{r.rank}. {r.alternative}: {r.score:.4f}")
```

**Step 4: Export Results**

```python
from mcda_core.export import MarkdownExporter, JSONExporter

# Export report
exporter = MarkdownExporter()
exporter.export(result, "report.md")
```

## Algorithms

**Exact Value Algorithms** (7):

1. **WSM** (Weighted Sum Model)
   - Formula: `Score = Σ(weight_i × score_i)`
   - Use: Simple additive weighting
   - Pros: Intuitive, easy to understand

2. **WPM** (Weighted Product Model)
   - Formula: `Score = ∏(score_i ^ weight_i)`
   - Use: Multiplicative decisions
   - Pros: Penalizes low scores heavily

3. **TOPSIS** (Technique for Order Preference)
   - Formula: Distance to positive/negative ideal solutions
   - Use: Conflicting criteria trade-offs
   - Pros: Widely used, handles trade-offs well

4. **VIKOR** (Compromise Ranking)
   - Formula: Utility + regret measures
   - Params: `v` (0-1, default 0.5)
   - Use: Compromise decisions
   - Pros: Balances group utility and individual regret

5. **TODIM** (Prospect Theory)
   - Formula: Prospect value function with loss aversion
   - Params: `theta` (loss aversion, default 2.25)
   - Use: Risk-averse decisions
   - Pros: Models psychological behavior

6. **ELECTRE-I** (Outranking Relations)
   - Formula: Concordance/discordance matrices
   - Params: `c_hat` (concordance threshold)
   - Use: Pairwise comparisons
   - Pros: Handles incomparability

7. **PROMETHEE II** (Preference Ranking)
   - Formula: Positive/negative preference flows
   - Params: Preference functions per criterion
   - Use: Ranking with preferences
   - Pros: Flexible preference modeling

**Interval Number Algorithms** (4):

8. **Interval TOPSIS** - TOPSIS with uncertain data [min, max]
9. **Interval VIKOR** - VIKOR with intervals and possibility degree
10. **Interval TODIM** - TODIM with interval prospect theory
11. **ELECTRE-I Interval** - ELECTRE-I with interval comparisons
12. **PROMETHEE II Interval** - PROMETHEE II with interval flows

**Weighting Methods** (5):

- **AHP** - Analytic Hierarchy Process
- **Entropy** - Information entropy weighting
- **CRITIC** - CRITIC weighting method
- **CV** - Coefficient of variation
- **Game Theory** - Combination weighting

## Advanced

**Input Formats**: JSON, CSV, Excel, YAML, Python dict

**Export Formats**: Markdown, JSON, ASCII table, Charts (matplotlib)

**Data Types**: Exact (float), Interval [min, max]

**Sensitivity Analysis**: `algorithm.sensitivity(problem)`

**CLI Usage**:
```bash
mcda validate config.yaml
mcda analyze config.yaml -o report.md
mcda analyze config.yaml --algorithm vikor_interval --sensitivity
```

**Error Handling**: All functions raise `ValidationError` with clear messages

**Resource Management**: All loaders/exporters use context managers
