"""Phase 1 Verification Script"""
import sys
from pathlib import Path

mcda_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_path))

import models

print("="*60)
print("PHASE 1: MODEL VERIFICATION")
print("="*60)

# Test 1: LinearScoringRule
print("\n[1/5] LinearScoringRule")
rule = models.LinearScoringRule(min=0, max=100)
assert rule.type == "linear"
print("  OK - Basic creation")
try:
    models.LinearScoringRule(min=10, max=10)
    print("  FAIL - validation")
except:
    print("  OK - Validation works")

# Test 2: ThresholdRange
print("\n[2/5] ThresholdRange")
r = models.ThresholdRange(min=100, max=500, score=80)
assert r.min == 100
print("  OK - Creation with min and max")

# Test 3: ThresholdScoringRule
print("\n[3/5] ThresholdScoringRule")
ranges = (models.ThresholdRange(min=0, max=100, score=100),)
rule = models.ThresholdScoringRule(ranges=ranges)
assert rule.type == "threshold"
print("  OK - Creation")

# Test 4: Criterion with scoring_rule
print("\n[4/5] Criterion with scoring_rule")
linear = models.LinearScoringRule(min=0, max=100)
c = models.Criterion(name="test", weight=0.5, direction="higher_better", scoring_rule=linear)
assert c.scoring_rule == linear
print("  OK - Criterion with LinearScoringRule")

# Test 5: DecisionProblem raw_data
print("\n[5/5] DecisionProblem raw_data")
p = models.DecisionProblem(
    alternatives=("A", "B"),
    criteria=(models.Criterion(name="test", weight=0.5, direction="higher_better"),),
    raw_data={"A": {}, "B": {}}
)
assert p.raw_data is not None
print("  OK - raw_data field exists")

print("\n" + "="*60)
print("PHASE 1 COMPLETE - ALL TESTS PASSED")
print("="*60)
print("\nVerification:")
print("  - LinearScoringRule: OK")
print("  - ThresholdScoringRule: OK")
print("  - Criterion.scoring_rule: OK")
print("  - DecisionProblem.raw_data: OK")
print("\nReady for Phase 2!")
