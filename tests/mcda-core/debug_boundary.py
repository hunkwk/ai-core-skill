"""调试边界测试"""
import sys
from pathlib import Path

mcda_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_path))

import models
from scoring import ScoringApplier

criteria = (
    models.Criterion(
        name="阈值指标",
        weight=0.5,
        direction="higher_better",
        scoring_rule=models.ThresholdScoringRule(
            ranges=(
                models.ThresholdRange(max=50, score=40),
                models.ThresholdRange(min=50, max=80, score=70),
                models.ThresholdRange(min=80, score=100),
            ),
            default_score=20
        )
    ),
)

raw_data = {
    "VAL_50": {"阈值指标": 50},
    "VAL_80": {"阈值指标": 80},
    "VAL_79": {"阈值指标": 79},
    "VAL_81": {"阈值指标": 81},
}

applier = ScoringApplier()
scores = applier.calculate_scores(raw_data, criteria)

print("阈值评分结果:")
for alt, alt_scores in scores.items():
    value = raw_data[alt]["阈值指标"]
    score = alt_scores["阈值指标"]
    print(f"  {alt}: value={value}, score={score}")

print("\n预期:")
print("  VAL_50: value=50, score=40 (max=50区间)")
print("  VAL_79: value=79, score=70 (50-80区间)")
print("  VAL_80: value=80, score=100 (min=80区间)")
print("  VAL_81: value=81, score=100 (min=80区间)")
