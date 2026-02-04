"""
Phase 1: 数据模型验证脚本

验证现有数据模型是否满足评分应用器需求。
"""

import sys
from pathlib import Path

# 添加 mcda-core 到路径
mcda_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_path))

# 直接导入（避免包依赖）
import models


def test_linear_scoring_rule():
    """测试 LinearScoringRule 模型"""
    print("\n[TEST] LinearScoringRule")

    # 测试基本创建
    rule = models.LinearScoringRule(min=0, max=100)
    assert rule.min == 0
    assert rule.max == 100
    assert rule.scale == 100.0
    assert rule.type == "linear"
    print("  [OK] Basic creation")

    # 测试带 scale 的创建
    rule = models.LinearScoringRule(min=-20, max=50, scale=100)
    assert rule.min == -20
    assert rule.max == 50
    print("  [OK] Creation with scale")

    # 测试验证逻辑
    try:
        models.LinearScoringRule(min=10, max=10)
        print("  [FAIL] min == max validation")
        return False
    except ValueError:
        print("  [OK] min == max validation")

    try:
        models.LinearScoringRule(min=0, max=100, scale=0)
        print("  [FAIL] scale <= 0 validation")
        return False
    except ValueError:
        print("  [OK] scale <= 0 validation")

    return True


def test_threshold_range():
    """测试 ThresholdRange 模型"""
    print("\n[TEST] ThresholdRange")

    # 测试只有 max
    range_rule = models.ThresholdRange(max=100, score=100)
    assert range_rule.min is None
    assert range_rule.max == 100
    print("  ✓ 只有 max 创建成功")

    # 测试只有 min
    range_rule = models.ThresholdRange(min=500, score=40)
    assert range_rule.min == 500
    assert range_rule.max is None
    print("  ✓ 只有 min 创建成功")

    # 测试 min 和 max
    range_rule = models.ThresholdRange(min=100, max=500, score=80)
    assert range_rule.min == 100
    assert range_rule.max == 500
    print("  ✓ min 和 max 创建成功")

    # 测试验证逻辑
    try:
        models.ThresholdRange(min=500, max=100)
        print("  ✗ min >= max 验证失败")
        return False
    except ValueError:
        print("  ✓ min >= max 验证成功")

    return True


def test_threshold_scoring_rule():
    """测试 ThresholdScoringRule 模型"""
    print("\n[TEST] ThresholdScoringRule")

    # 测试基本创建
    ranges = (
        models.ThresholdRange(max=100, score=40),
        models.ThresholdRange(min=100, max=500, score=60),
        models.ThresholdRange(min=500, score=80),
    )
    rule = models.ThresholdScoringRule(ranges=ranges)
    assert len(rule.ranges) == 3
    assert rule.default_score == 0.0
    assert rule.type == "threshold"
    print("  ✓ 基本创建成功")

    # 测试带 default_score
    rule = models.ThresholdScoringRule(
        ranges=ranges,
        default_score=50
    )
    assert rule.default_score == 50
    print("  ✓ 带 default_score 创建成功")

    # 测试验证逻辑
    try:
        models.ThresholdScoringRule(ranges=())
        print("  ✗ 空 ranges 验证失败")
        return False
    except ValueError:
        print("  ✓ 空 ranges 验证成功")

    return True


def test_criterion_with_scoring_rule():
    """测试 Criterion 与评分规则集成"""
    print("\n[TEST] Criterion with ScoringRule")

    # 测试不带评分规则
    criterion = models.Criterion(
        name="成本",
        weight=0.35,
        direction="lower_better"
    )
    assert criterion.scoring_rule is None
    print("  ✓ 不带评分规则创建成功")

    # 测试带线性评分规则
    linear_rule = models.LinearScoringRule(min=0, max=100)
    criterion = models.Criterion(
        name="增长率",
        weight=0.20,
        direction="higher_better",
        scoring_rule=linear_rule
    )
    assert criterion.scoring_rule == linear_rule
    assert criterion.scoring_rule.type == "linear"
    print("  ✓ 带线性评分规则创建成功")

    # 测试带阈值评分规则
    ranges = (models.ThresholdRange(min=0, max=100, score=100),)
    threshold_rule = models.ThresholdScoringRule(ranges=ranges)
    criterion = models.Criterion(
        name="年采购额",
        weight=0.25,
        direction="higher_better",
        scoring_rule=threshold_rule
    )
    assert criterion.scoring_rule == threshold_rule
    assert criterion.scoring_rule.type == "threshold"
    print("  ✓ 带阈值评分规则创建成功")

    # 测试 column 字段
    criterion = models.Criterion(
        name="年采购额",
        weight=0.25,
        direction="higher_better",
        column="annual_purchase"
    )
    assert criterion.column == "annual_purchase"
    print("  ✓ column 字段创建成功")

    return True


def test_decision_problem_raw_data():
    """测试 DecisionProblem 的 raw_data 字段"""
    print("\n[TEST] DecisionProblem raw_data")

    # 测试带 raw_data 的创建
    problem = models.DecisionProblem(
        alternatives=("A", "B"),
        criteria=(
            models.Criterion(
                name="成本",
                weight=0.5,
                direction="lower_better"
            ),
        ),
        scores={"A": {"成本": 10}, "B": {"成本": 20}},
        raw_data={"A": {"成本": 10}, "B": {"成本": 20}}
    )
    assert problem.raw_data is not None
    print("  ✓ raw_data 字段存在")

    # 测试不带 raw_data 的创建
    problem = models.DecisionProblem(
        alternatives=("A", "B"),
        criteria=(
            models.Criterion(
                name="成本",
                weight=0.5,
                direction="lower_better"
            ),
        ),
        scores={"A": {"成本": 10}, "B": {"成本": 20}}
    )
    assert problem.raw_data is None
    print("  ✓ raw_data 字段可选")

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("PHASE 1: 数据模型验证")
    print("=" * 60)

    results = []

    # 运行所有测试
    results.append(("LinearScoringRule", test_linear_scoring_rule()))
    results.append(("ThresholdRange", test_threshold_range()))
    results.append(("ThresholdScoringRule", test_threshold_scoring_rule()))
    results.append(("Criterion with ScoringRule", test_criterion_with_scoring_rule()))
    results.append(("DecisionProblem raw_data", test_decision_problem_raw_data()))

    # 统计结果
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:30s} {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 Phase 1 完成！所有模型测试通过！")
        print("\n✅ 验收标准:")
        print("  - LinearScoringRule 模型完整")
        print("  - ThresholdScoringRule 模型完整")
        print("  - Criterion.scoring_rule 字段存在")
        print("  - DecisionProblem.raw_data 字段存在")
        print("  - 所有验证逻辑正确")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
