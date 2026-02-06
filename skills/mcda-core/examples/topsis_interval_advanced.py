"""
TOPSIS 区间版本 - 供应商选择进阶示例

这是一个更实际的供应商选择决策示例，包含敏感性分析。

运行方式（从项目根目录）：
    python skills/mcda-core/examples/topsis_interval_advanced.py
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


def create_supplier_problem():
    """创建供应商选择决策问题"""
    alternatives = ("供应商A", "供应商B", "供应商C", "供应商D")

    criteria = (
        Criterion(name="质量", weight=0.30, direction="higher_better"),
        Criterion(name="价格", weight=0.25, direction="lower_better"),
        Criterion(name="交付期", weight=0.20, direction="lower_better"),
        Criterion(name="服务", weight=0.15, direction="higher_better"),
        Criterion(name="稳定性", weight=0.10, direction="higher_better"),
    )

    # 区间评分反映市场波动和评估不确定性
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

    return DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=scores
    )


def print_header(title):
    """打印标题"""
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_scores(problem):
    """打印评分矩阵"""
    print("\n评分矩阵（区间）:")
    print("-" * 70)

    # 表头
    header = "供应商".ljust(12)
    for crit in problem.criteria:
        header += f" {crit.name.ljust(15)}"
    print(header)
    print("-" * 70)

    # 数据行
    for alt in problem.alternatives:
        row = alt.ljust(12)
        for crit in problem.criteria:
            value = problem.scores[alt][crit.name]
            row += f" {str(value).ljust(15)}"
        print(row)

    print()


def analyze_uncertainty(problem):
    """分析不确定性"""
    print("不确定性分析:")
    print("-" * 70)

    for alt in problem.alternatives:
        widths = []
        for crit in problem.criteria:
            value = problem.scores[alt][crit.name]
            if isinstance(value, Interval):
                widths.append(value.width)

        avg_width = sum(widths) / len(widths)
        max_width = max(widths)

        print(f"  {alt}:")
        print(f"    平均区间宽度: {avg_width:.2f}")
        print(f"    最大区间宽度: {max_width:.2f}")

        # 不确定性等级
        if avg_width < 10:
            level = "低"
        elif avg_width < 20:
            level = "中"
        else:
            level = "高"
        print(f"    不确定性等级: {level}")
    print()


def sensitivity_analysis(problem):
    """权重敏感性分析"""
    print("权重敏感性分析:")
    print("-" * 70)
    print("分析不同权重配置对排名的影响...\n")

    # 原始权重
    original_weights = {c.name: c.weight for c in problem.criteria}

    # 测试不同的权重场景
    scenarios = [
        ("原始权重", original_weights),
        ("质量优先", {"质量": 0.50, "价格": 0.15, "交付期": 0.15, "服务": 0.10, "稳定性": 0.10}),
        ("价格优先", {"质量": 0.20, "价格": 0.45, "交付期": 0.15, "服务": 0.10, "稳定性": 0.10}),
        ("平衡配置", {"质量": 0.25, "价格": 0.25, "交付期": 0.20, "服务": 0.15, "稳定性": 0.15}),
    ]

    results = []

    for scenario_name, weights in scenarios:
        # 创建新准则（修改权重）
        new_criteria = []
        for crit in problem.criteria:
            new_criteria.append(Criterion(
                name=crit.name,
                weight=weights[crit.name],
                direction=crit.direction
            ))

        # 创建新问题
        new_problem = DecisionProblem(
            alternatives=problem.alternatives,
            criteria=tuple(new_criteria),
            scores=problem.scores
        )

        # 计算
        algo = IntervalTOPSISAlgorithm()
        result = algo.calculate(new_problem)

        # 提取排名
        ranking = [r.alternative for r in result.rankings]
        results.append((scenario_name, ranking))

    # 打印结果
    print(f"{'场景':<15} {'排名':<40}")
    print("-" * 70)
    for scenario_name, ranking in results:
        ranking_str = " > ".join(ranking)
        print(f"{scenario_name:<15} {ranking_str:<40}")
    print()


def detailed_analysis(problem):
    """详细分析"""
    print("详细分析:")
    print("-" * 70)

    algo = IntervalTOPSISAlgorithm()
    result = algo.calculate(problem)

    d_plus = result.metadata.metrics["distance_to_ideal"]
    d_minus = result.metadata.metrics["distance_to_negative_ideal"]

    # 理想解和负理想解
    ideal = result.metadata.metrics["ideal"]
    negative_ideal = result.metadata.metrics["negative_ideal"]

    print("\n理想解和负理想解:")
    for i, crit in enumerate(problem.criteria):
        direction_str = "效益型" if crit.direction == "higher_better" else "成本型"
        print(f"  {crit.name} ({direction_str}):")
        print(f"    理想解: {ideal[i]:.4f}")
        print(f"    负理想解: {negative_ideal[i]:.4f}")

    print("\n各方案距离分析:")
    for item in result.rankings:
        alt = item.alternative
        print(f"  {alt}:")
        print(f"    排名: {item.rank}")
        print(f"    相对接近度: {item.score:.4f}")
        print(f"    到理想解距离: {d_plus[alt]:.4f}")
        print(f"    到负理想解距离: {d_minus[alt]:.4f}")
    print()


def main():
    """主函数"""
    print_header("TOPSIS 区间版本 - 供应商选择分析")

    # 创建决策问题
    problem = create_supplier_problem()

    # 打印评分矩阵
    print_scores(problem)

    # 不确定性分析
    analyze_uncertainty(problem)

    # 详细分析
    detailed_analysis(problem)

    # 敏感性分析
    sensitivity_analysis(problem)

    # 最终推荐
    print_header("最终推荐")

    algo = IntervalTOPSISAlgorithm()
    result = algo.calculate(problem)

    best = result.rankings[0]
    print(f"\n推荐供应商: {best.alternative}")
    print(f"相对接近度: {best.score:.4f}")

    print("\n推荐理由:")
    print("  1. 在综合评估中得分最高")
    print("  2. 距离理想解最近")
    print("  3. 距离负理想解最远")

    # 第二名分析
    runner_up = result.rankings[1]
    print(f"\n次优选择: {runner_up.alternative}")
    print(f"相对接近度: {runner_up.score:.4f}")

    print("\n决策建议:")
    if best.score - runner_up.score > 0.1:
        print(f"  - {best.alternative} 明显优于其他供应商，强烈推荐")
    elif best.score - runner_up.score > 0.05:
        print(f"  - {best.alternative} 略优于 {runner_up.alternative}，推荐选择")
        print(f"  - 建议进一步考察两者的具体差异")
    else:
        print(f"  - {best.alternative} 与 {runner_up.alternative} 相近")
        print(f"  - 建议结合其他因素（如合作关系、特殊需求等）进行决策")

    print()


if __name__ == "__main__":
    main()
