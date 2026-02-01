import sys
sys.path.insert(0, 'skills')
sys.path.insert(0, 'skills/mcda-core/lib')

from algorithms.electre1 import electre1
from models import DecisionProblem, Criterion

problem = DecisionProblem(
    alternatives=("A1", "A2"),
    criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
    scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
)

try:
    result = electre1(problem, alpha=0.6, beta=0.3)
    print("成功!排名:")
    for r in result.rankings:
        print(f"  {r.alternative}: rank={r.rank}")
    
    ranks = [r.rank for r in result.rankings]
    print(f"排名列表: {ranks}")
    print(f"排序后: {sorted(ranks)}")
    print(f"期望: {list(range(1, len(ranks) + 1))}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
