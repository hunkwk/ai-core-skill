"""
测试 TOPSIS 区间版本示例代码

从项目根目录运行: python skills/mcda-core/examples/run_examples.py
"""

import sys
from pathlib import Path

# 添加 mcda-core 目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
skills_path = project_root / "skills"
sys.path.insert(0, str(skills_path))

# 使用 mcda_core 模块（通过属性访问，兼容符号链接）
import mcda_core
DecisionProblem = mcda_core.models.DecisionProblem
Criterion = mcda_core.models.Criterion
Interval = mcda_core.interval.Interval
IntervalTOPSISAlgorithm = mcda_core.algorithms.IntervalTOPSISAlgorithm
TOPSISAlgorithm = mcda_core.algorithms.TOPSISAlgorithm


def test_basic_example():
    """测试基础示例代码"""
    print("=" * 70)
    print("测试基础示例")
    print("=" * 70)

    # 定义备选方案
    alternatives = ("方案A", "方案B", "方案C")

    # 定义准则
    criteria = (
        Criterion(name="质量", weight=0.4, direction="higher_better"),
        Criterion(name="价格", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        Criterion(name="易用性", weight=0.1, direction="higher_better"),
    )

    # 定义区间评分
    scores = {
        "方案A": {
            "质量": Interval(70.0, 90.0),
            "价格": Interval(80.0, 100.0),
            "可靠性": Interval(70.0, 80.0),
            "易用性": Interval(60.0, 80.0),
        },
        "方案B": {
            "质量": Interval(80.0, 90.0),
            "价格": Interval(90.0, 100.0),
            "可靠性": Interval(80.0, 90.0),
            "易用性": Interval(70.0, 90.0),
        },
        "方案C": {
            "质量": Interval(60.0, 80.0),
            "价格": Interval(70.0, 90.0),
            "可靠性": Interval(60.0, 70.0),
            "易用性": Interval(50.0, 70.0),
        },
    }

    # 创建决策问题
    problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=scores
    )

    # 执行 TOPSIS 计算
    algo = IntervalTOPSISAlgorithm()
    result = algo.calculate(problem)

    # 输出结果
    print("\n方案排名:")
    for item in result.rankings:
        print(f"  第 {item.rank} 名: {item.alternative} (相对接近度: {item.score:.4f})")

    print("\n基础示例测试通过!")
    return True


def test_advanced_example():
    """测试进阶示例代码"""
    print("\n" + "=" * 70)
    print("测试进阶示例 - 供应商选择")
    print("=" * 70)

    alternatives = ("供应商A", "供应商B", "供应商C", "供应商D")

    criteria = (
        Criterion(name="质量", weight=0.30, direction="higher_better"),
        Criterion(name="价格", weight=0.25, direction="lower_better"),
        Criterion(name="交付期", weight=0.20, direction="lower_better"),
        Criterion(name="服务", weight=0.15, direction="higher_better"),
        Criterion(name="稳定性", weight=0.10, direction="higher_better"),
    )

    scores = {
        "供应商A": {
            "质量": Interval(75.0, 90.0),
            "价格": Interval(75.0, 90.0),
            "交付期": Interval(5.0, 10.0),
            "服务": Interval(65.0, 80.0),
            "稳定性": Interval(70.0, 85.0),
        },
        "供应商B": {
            "质量": Interval(85.0, 95.0),
            "价格": Interval(85.0, 95.0),
            "交付期": Interval(7.0, 12.0),
            "服务": Interval(75.0, 90.0),
            "稳定性": Interval(80.0, 90.0),
        },
        "供应商C": {
            "质量": Interval(65.0, 80.0),
            "价格": Interval(60.0, 75.0),
            "交付期": Interval(3.0, 7.0),
            "服务": Interval(55.0, 70.0),
            "稳定性": Interval(60.0, 75.0),
        },
        "供应商D": {
            "质量": Interval(70.0, 85.0),
            "价格": Interval(70.0, 85.0),
            "交付期": Interval(6.0, 11.0),
            "服务": Interval(80.0, 95.0),
            "稳定性": Interval(75.0, 88.0),
        },
    }

    problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=scores
    )

    algo = IntervalTOPSISAlgorithm()
    result = algo.calculate(problem)

    print("\n供应商选择结果:")
    for item in result.rankings:
        print(f"  第 {item.rank} 名: {item.alternative} (相对接近度: {item.score:.4f})")

    print("\n进阶示例测试通过!")
    return True


def test_comparison_example():
    """测试对比示例代码"""
    print("\n" + "=" * 70)
    print("测试对比示例 - 精确值 vs 区间版本")
    print("=" * 70)

    alternatives = ("方案A", "方案B", "方案C")

    criteria = (
        Criterion(name="质量", weight=0.4, direction="higher_better"),
        Criterion(name="价格", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        Criterion(name="易用性", weight=0.1, direction="higher_better"),
    )

    # 区间评分
    interval_scores = {
        "方案A": {
            "质量": Interval(70.0, 90.0),
            "价格": Interval(75.0, 85.0),
            "可靠性": Interval(70.0, 80.0),
            "易用性": Interval(60.0, 80.0),
        },
        "方案B": {
            "质量": Interval(80.0, 90.0),
            "价格": Interval(85.0, 95.0),
            "可靠性": Interval(80.0, 90.0),
            "易用性": Interval(70.0, 90.0),
        },
        "方案C": {
            "质量": Interval(60.0, 80.0),
            "价格": Interval(65.0, 75.0),
            "可靠性": Interval(60.0, 70.0),
            "易用性": Interval(50.0, 70.0),
        },
    }

    # 精确值评分（使用区间中点）
    exact_scores = {}
    for alt, scores in interval_scores.items():
        exact_scores[alt] = {
            crit: value.midpoint if isinstance(value, Interval) else value
            for crit, value in scores.items()
        }

    # 精确值版本
    exact_problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=exact_scores
    )
    exact_result = TOPSISAlgorithm().calculate(exact_problem)

    # 区间版本
    interval_problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=interval_scores
    )
    interval_result = IntervalTOPSISAlgorithm().calculate(interval_problem)

    print("\n排名对比:")
    print(f"{'排名':<8} {'精确值版本':<20} {'区间版本':<20}")
    print("-" * 50)

    for i in range(len(alternatives)):
        exact_item = exact_result.rankings[i]
        interval_item = interval_result.rankings[i]
        print(f"{i+1:<8} {exact_item.alternative:<20} {interval_item.alternative:<20}")

    print("\n对比示例测试通过!")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("TOPSIS 区间版本示例代码测试")
    print("=" * 70)

    all_passed = True

    try:
        all_passed = test_basic_example() and all_passed
    except Exception as e:
        print(f"\n基础示例测试失败: {e}")
        all_passed = False

    try:
        all_passed = test_advanced_example() and all_passed
    except Exception as e:
        print(f"\n进阶示例测试失败: {e}")
        all_passed = False

    try:
        all_passed = test_comparison_example() and all_passed
    except Exception as e:
        print(f"\n对比示例测试失败: {e}")
        all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("所有测试通过!")
    else:
        print("部分测试失败!")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
