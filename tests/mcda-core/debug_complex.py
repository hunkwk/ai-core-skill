"""调试 complex_scenario 测试"""
import sys
from pathlib import Path

mcda_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_path))

import models
from scoring import ScoringApplier

def apply_scoring_rules(
    problem: models.DecisionProblem
) -> models.DecisionProblem:
    """应用评分规则到原始数据"""
    if not problem.raw_data:
        return problem

    has_scoring_rules = any(
        c.scoring_rule is not None
        for c in problem.criteria
    )

    if not has_scoring_rules:
        return problem

    applier = ScoringApplier()

    try:
        scores = applier.calculate_scores(
            raw_data=problem.raw_data,
            criteria=problem.criteria
        )
    except Exception as e:
        raise ValueError(
            f"评分规则应用失败: {str(e)}"
        ) from e

    return models.DecisionProblem(
        alternatives=problem.alternatives,
        criteria=problem.criteria,
        scores=scores,
        algorithm=problem.algorithm,
        data_source=problem.data_source,
        raw_data=problem.raw_data,
        score_range=problem.score_range
    )

# 创建问题
problem = models.DecisionProblem(
    alternatives=("Cust_A", "Cust_B"),
    criteria=(
        models.Criterion(
            name="年度采购额",
            weight=0.6,
            direction="higher_better",
            column="purchase",
            scoring_rule=models.ThresholdScoringRule(
                ranges=(
                    models.ThresholdRange(max=500, score=60),
                    models.ThresholdRange(min=500, score=80),
                ),
                default_score=40
            )
        ),
        models.Criterion(
            name="增长率",
            weight=0.4,
            direction="higher_better",
            column="growth",
            scoring_rule=models.LinearScoringRule(min=-20, max=50, scale=100)
        ),
    ),
    raw_data={
        "Cust_A": {"purchase": 800, "growth": 30},
        "Cust_B": {"purchase": 300, "growth": -10}
    }
)

# 应用评分规则
new_problem = apply_scoring_rules(problem)

# 输出结果
print("评分结果:")
for alt, alt_scores in new_problem.scores.items():
    print(f"\n{alt}:")
    for crit, score in alt_scores.items():
        print(f"  {crit}: {score}")

# 检查断言
print("\n\n检查断言:")
print(f"Cust_A 年度采购额: {new_problem.scores['Cust_A']['年度采购额']} (期望: 80)")
print(f"Cust_A 增长率: {new_problem.scores['Cust_A']['增长率']} (期望: 71.43)")
print(f"Cust_B 年度采购额: {new_problem.scores['Cust_B']['年度采购额']} (期望: 60)")
print(f"Cust_B 增长率: {new_problem.scores['Cust_B']['增长率']} (期望: 14.29)")
