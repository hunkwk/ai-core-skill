from mcda_core.algorithms.electre1 import electre1
from mcda_core.models import DecisionProblem, Criterion

problem = DecisionProblem(
    alternatives=("A1", "A2", "A3"),
    criteria=(
        Criterion(name="C1", weight=0.4, direction="higher_better"),
        Criterion(name="C2", weight=0.3, direction="higher_better"),
        Criterion(name="C3", weight=0.3, direction="higher_better"),
    ),
    scores={
        "A1": {"C1": 10, "C2": 8, "C3": 7},
        "A2": {"C1": 9, "C2": 6, "C3": 8},
        "A3": {"C1": 8, "C2": 7, "C3": 9},
    }
)

try:
    result = electre1(problem, alpha=0.6, beta=0.3)
    print("成功!")
    for r in result.rankings:
        print(f"  {r.alternative}: rank={r.rank}, score={r.score}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
