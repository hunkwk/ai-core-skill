#!/usr/bin/env python
"""简单的语法检查脚本"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'mcda-core', 'lib'))

try:
    # 测试导入
    from algorithms.todim import todim, TODIMError
    print("✅ TODIM 导入成功")

    from models import DecisionProblem, Criterion
    print("✅ Models 导入成功")

    # 测试创建简单对象
    problem = DecisionProblem(
        alternatives=("A1", "A2"),
        criteria=(
            Criterion(name="C1", weight=0.5, direction="higher_better"),
            Criterion(name="C2", weight=0.5, direction="higher_better"),
        ),
        scores={
            "A1": {"C1": 10, "C2": 5},
            "A2": {"C1": 8, "C2": 7},
        }
    )
    print("✅ DecisionProblem 创建成功")

    # 测试 TODIM 调用
    result = todim(problem, theta=1.0)
    print(f"✅ TODIM 运行成功 - 排名数: {len(result.rankings)}")

    for r in result.rankings:
        print(f"  - {r['alternative']}: Rank {r['rank']}, Score {r['score']:.4f}")

    print("\n✅ 所有测试通过!")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
