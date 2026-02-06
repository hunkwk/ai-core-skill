"""
TOPSIS 区间版本 - 基础示例

这是一个简单的入门示例，展示如何使用 TOPSIS 区间版本算法
进行多准则决策分析。

运行方式（从项目根目录）：
    python skills/mcda-core/examples/topsis_interval_basic.py
"""

import sys
from pathlib import Path

# 添加 skills 目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
skills_path = project_root / "skills"
sys.path.insert(0, str(skills_path))

# 使用 mcda_core 模块（通过属性访问，兼容符号链接）
import mcda_core
DecisionProblem = mcda_core.models.DecisionProblem
Criterion = mcda_core.models.Criterion
Interval = mcda_core.interval.Interval
IntervalTOPSISAlgorithm = mcda_core.algorithms.IntervalTOPSISAlgorithm


def main():
    """主函数"""
    print("=" * 60)
    print("TOPSIS 区间版本算法 - 基础示例")
    print("=" * 60)
    print()

    # 步骤 1: 定义备选方案
    print("步骤 1: 定义备选方案")
    alternatives = ("方案A", "方案B", "方案C")
    print(f"  备选方案: {alternatives}")
    print()

    # 步骤 2: 定义准则
    print("步骤 2: 定义准则")
    criteria = (
        Criterion(name="质量", weight=0.4, direction="higher_better"),
        Criterion(name="价格", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        Criterion(name="易用性", weight=0.1, direction="higher_better"),
    )
    print("  准则:")
    for c in criteria:
        direction_str = "越高越好" if c.direction == "higher_better" else "越低越好"
        print(f"    - {c.name}: 权重={c.weight}, 方向={direction_str}")
    print()

    # 步骤 3: 定义区间评分
    print("步骤 3: 定义区间评分（反映不确定性）")
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

    print("  评分矩阵:")
    for alt in alternatives:
        print(f"    {alt}:")
        for crit_name, value in scores[alt].items():
            print(f"      {crit_name}: {value}")

    print()
    print("  注: 区间表示不确定性，如 [70, 90] 表示值在 70 到 90 之间")
    print()

    # 步骤 4: 创建决策问题
    print("步骤 4: 创建决策问题")
    problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=scores
    )
    print("  决策问题已创建")
    print()

    # 步骤 5: 执行 TOPSIS 计算
    print("步骤 5: 执行 TOPSIS 区间版本计算")
    algo = IntervalTOPSISAlgorithm()
    result = algo.calculate(problem)
    print("  计算完成")
    print()

    # 步骤 6: 输出结果
    print("=" * 60)
    print("计算结果")
    print("=" * 60)
    print()

    print("方案排名:")
    for item in result.rankings:
        print(f"  第 {item.rank} 名: {item.alternative} (相对接近度: {item.score:.4f})")
    print()

    # 详细分析
    print("距离分析:")
    d_plus = result.metadata.metrics["distance_to_ideal"]
    d_minus = result.metadata.metrics["distance_to_negative_ideal"]

    for alt in alternatives:
        print(f"  {alt}:")
        print(f"    到正理想解距离 (D+): {d_plus[alt]:.4f}")
        print(f"    到负理想解距离 (D-): {d_minus[alt]:.4f}")
        print(f"    相对接近度: {d_minus[alt] / (d_plus[alt] + d_minus[alt]):.4f}")
    print()

    # 结论
    print("=" * 60)
    print("结论")
    print("=" * 60)
    best = result.rankings[0]
    print(f"最佳方案: {best.alternative}")
    print(f"理由: 相对接近度最高 ({best.score:.4f})")
    print()

    # 相对接近度解读
    print("相对接近度解读:")
    for item in result.rankings:
        if item.score > 0.6:
            level = "优秀"
        elif item.score > 0.4:
            level = "良好"
        else:
            level = "一般"
        print(f"  {item.alternative}: {level} ({item.score:.4f})")


if __name__ == "__main__":
    main()
