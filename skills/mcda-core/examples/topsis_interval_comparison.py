"""
TOPSIS 精确值版本 vs 区间版本对比

对比 TOPSIS 精确值版本和区间版本的计算结果差异。

运行方式（从项目根目录）：
    python skills/mcda-core/examples/topsis_interval_comparison.py
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
TOPSISAlgorithm = mcda_core.algorithms.TOPSISAlgorithm
IntervalTOPSISAlgorithm = mcda_core.algorithms.IntervalTOPSISAlgorithm


def create_comparison_problem():
    """创建对比问题"""
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

    return alternatives, criteria, interval_scores, exact_scores


def print_header(title):
    """打印标题"""
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_comparison_table(interval_scores, exact_scores, alternatives, criteria):
    """打印对比表"""
    print("\n评分数据对比:")
    print("-" * 70)

    # 表头
    header = "方案".ljust(10)
    for crit in criteria:
        header += f" {crit.name.ljust(20)}"
    print(header)
    print("-" * 70)

    # 数据行
    for alt in alternatives:
        row = alt.ljust(10)
        for crit in criteria:
            interval = interval_scores[alt][crit.name]
            exact = exact_scores[alt][crit.name]
            row += f" {str(interval).ljust(12)} ({exact:.1f})  "
        print(row)

    print()
    print("说明: [区间] (中点值)")
    print()


def calculate_and_compare(alternatives, criteria, interval_scores, exact_scores):
    """计算并对比两种版本"""
    # TOPSIS 精确值版本
    exact_problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=exact_scores
    )
    exact_algo = TOPSISAlgorithm()
    exact_result = exact_algo.calculate(exact_problem)

    # TOPSIS 区间版本
    interval_problem = DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=interval_scores
    )
    interval_algo = IntervalTOPSISAlgorithm()
    interval_result = interval_algo.calculate(interval_problem)

    return exact_result, interval_result


def print_ranking_comparison(exact_result, interval_result, alternatives):
    """打印排名对比"""
    print("排名对比:")
    print("-" * 70)

    print(f"{'排名':<8} {'精确值版本':<20} {'区间版本':<20} {'差异':<10}")
    print("-" * 70)

    for i in range(len(alternatives)):
        exact_item = exact_result.rankings[i]
        interval_item = interval_result.rankings[i]

        exact_alt = exact_item.alternative
        interval_alt = interval_item.alternative
        diff = "✓" if exact_alt == interval_alt else "✗"

        print(f"{i+1:<8} {exact_alt:<20} {interval_alt:<20} {diff:<10}")

    print()


def print_score_comparison(exact_result, interval_result, alternatives):
    """打印分数对比"""
    print("相对接近度对比:")
    print("-" * 70)

    print(f"{'方案':<12} {'精确值版本':<20} {'区间版本':<20} {'差异':<10}")
    print("-" * 70)

    for alt in alternatives:
        exact_score = next(item.score for item in exact_result.rankings if item.alternative == alt)
        interval_score = next(item.score for item in interval_result.rankings if item.alternative == alt)
        diff = abs(exact_score - interval_score)

        print(f"{alt:<12} {exact_score:<20.4f} {interval_score:<20.4f} {diff:.4f}")

    print()


def print_distance_analysis(interval_result):
    """打印距离分析"""
    print("区间版本距离分析:")
    print("-" * 70)

    d_plus = interval_result.metadata.metrics["distance_to_ideal"]
    d_minus = interval_result.metadata.metrics["distance_to_negative_ideal"]

    print(f"{'方案':<12} {'到理想解 (D+)':<20} {'到负理想解 (D-)':<20} {'相对接近度':<15}")
    print("-" * 70)

    for alt in interval_result.raw_scores.keys():
        closeness = d_minus[alt] / (d_plus[alt] + d_minus[alt])
        print(f"{alt:<12} {d_plus[alt]:<20.4f} {d_minus[alt]:<20.4f} {closeness:<15.4f}")

    print()


def algorithm_comparison():
    """算法特性对比"""
    print("算法特性对比:")
    print("-" * 70)

    features = [
        ("处理不确定性", "精确值版本", "✗", "✓"),
        ("使用中点计算", "精确值版本", "N/A", "✓"),
        ("保留区间信息", "精确值版本", "✗", "部分"),
        ("输入类型", "精确值版本", "精确值", "区间数"),
        ("计算复杂度", "精确值版本", "O(mn)", "O(mn)"),
        ("排名稳定性", "精确值版本", "高", "中"),
    ]

    print(f"{'特性':<20} {'精确值版本':<20} {'区间版本':<20}")
    print("-" * 70)

    # 重新组织数据
    feature_set = set(f[0] for f in features)
    for feature in sorted(feature_set):
        exact_val = next(f[2] for f in features if f[0] == feature and f[1] == "精确值版本")
        interval_val = next(f[3] for f in features if f[0] == feature and f[1] == "精确值版本")
        print(f"{feature:<20} {exact_val:<20} {interval_val:<20}")

    print()


def main():
    """主函数"""
    print_header("TOPSIS 精确值版本 vs 区间版本对比")

    # 创建对比数据
    alternatives, criteria, interval_scores, exact_scores = create_comparison_problem()

    # 打印数据对比
    print_comparison_table(interval_scores, exact_scores, alternatives, criteria)

    # 计算两种版本
    exact_result, interval_result = calculate_and_compare(
        alternatives, criteria, interval_scores, exact_scores
    )

    # 打印排名对比
    print_ranking_comparison(exact_result, interval_result, alternatives)

    # 打印分数对比
    print_score_comparison(exact_result, interval_result, alternatives)

    # 打印距离分析
    print_distance_analysis(interval_result)

    # 算法特性对比
    algorithm_comparison()

    # 结论
    print_header("结论")
    print()
    print("1. 当区间评分为确定值（上下界相等）时，")
    print("   两个版本的排名和分数完全一致。")
    print()
    print("2. 当区间评分存在不确定性时，")
    print("   区间版本使用中点进行计算，结果可能略有差异。")
    print()
    print("3. 区间版本的优势:")
    print("   - 可以表示评分的不确定性")
    print("   - 更符合实际决策场景")
    print("   - 区间宽度可用于风险评估")
    print()
    print("4. 选择建议:")
    print("   - 数据精确时：使用精确值版本")
    print("   - 数据有不确定性时：使用区间版本")
    print()


if __name__ == "__main__":
    main()
