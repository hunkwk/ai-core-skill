"""
Phase 2: 评分应用器测试

测试 ScoringApplier 类的所有方法。
"""

import sys
from pathlib import Path

# 添加 mcda-core 到路径
mcda_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_path))

import models
from scoring import ScoringApplier


def test_apply_threshold_basic():
    """测试基本阈值评分"""
    print("\n[1/20] test_apply_threshold_basic")
    applier = ScoringApplier()

    ranges = (
        models.ThresholdRange(max=100, score=40),
        models.ThresholdRange(min=100, max=500, score=60),
        models.ThresholdRange(min=500, score=80),
    )
    rule = models.ThresholdScoringRule(ranges=ranges)

    # 测试各个区间
    assert applier.apply_threshold(50, rule, "higher_better") == 40
    assert applier.apply_threshold(100, rule, "higher_better") == 40
    assert applier.apply_threshold(300, rule, "higher_better") == 60
    assert applier.apply_threshold(500, rule, "higher_better") == 60
    assert applier.apply_threshold(800, rule, "higher_better") == 80
    print("  OK - Basic threshold scoring")


def test_apply_threshold_default():
    """测试默认评分"""
    print("\n[2/20] test_apply_threshold_default")
    applier = ScoringApplier()

    ranges = (models.ThresholdRange(min=100, max=500, score=60),)
    rule = models.ThresholdScoringRule(ranges=ranges, default_score=30)

    # 测试超出范围的情况
    assert applier.apply_threshold(50, rule, "higher_better") == 30
    assert applier.apply_threshold(600, rule, "higher_better") == 30
    print("  OK - Default score")


def test_apply_threshold_open_ended():
    """测试开放式区间"""
    print("\n[3/20] test_apply_threshold_open_ended")
    applier = ScoringApplier()

    ranges = (
        models.ThresholdRange(max=100, score=40),
        models.ThresholdRange(min=100, max=500, score=60),
        models.ThresholdRange(min=500, score=80),
    )
    rule = models.ThresholdScoringRule(ranges=ranges)

    # value < 100
    assert applier.apply_threshold(50, rule, "higher_better") == 40
    # value >= 500
    assert applier.apply_threshold(1000, rule, "higher_better") == 80
    print("  OK - Open-ended ranges")


def test_apply_linear_basic():
    """测试基本线性评分"""
    print("\n[4/20] test_apply_linear_basic")
    applier = ScoringApplier()

    rule = models.LinearScoringRule(min=0, max=100, scale=100)

    # 测试 higher_better
    assert applier.apply_linear(0, rule, "higher_better") == 0
    assert applier.apply_linear(50, rule, "higher_better") == 50
    assert applier.apply_linear(100, rule, "higher_better") == 100

    # 测试 lower_better
    assert applier.apply_linear(0, rule, "lower_better") == 100
    assert applier.apply_linear(50, rule, "lower_better") == 50
    assert applier.apply_linear(100, rule, "lower_better") == 0
    print("  OK - Basic linear scoring")


def test_apply_linear_clamping():
    """测试边界值限制"""
    print("\n[5/20] test_apply_linear_clamping")
    applier = ScoringApplier()

    rule = models.LinearScoringRule(min=0, max=100, scale=100)

    # 测试超出范围的情况
    assert applier.apply_linear(-10, rule, "higher_better") == 0
    assert applier.apply_linear(150, rule, "higher_better") == 100
    print("  OK - Value clamping")


def test_apply_linear_negative_range():
    """测试负数范围"""
    print("\n[6/20] test_apply_linear_negative_range")
    applier = ScoringApplier()

    rule = models.LinearScoringRule(min=-20, max=50, scale=100)

    # 测试负数范围
    assert applier.apply_linear(-20, rule, "higher_better") == 0
    # (0 - (-20)) / (50 - (-20)) * 100 = 20/70 * 100 = 28.57
    score = applier.apply_linear(0, rule, "higher_better")
    assert abs(score - 28.57) < 0.01  # 允许浮点误差
    assert applier.apply_linear(50, rule, "higher_better") == 100
    print("  OK - Negative range")


def test_apply_rule_type_linear():
    """测试 apply_rule 识别 linear 类型"""
    print("\n[7/20] test_apply_rule_type_linear")
    applier = ScoringApplier()

    rule = models.LinearScoringRule(min=0, max=100, scale=100)
    score = applier.apply_rule(50, rule, "higher_better")

    assert score == 50
    print("  OK - Linear type recognition")


def test_apply_rule_type_threshold():
    """测试 apply_rule 识别 threshold 类型"""
    print("\n[8/20] test_apply_rule_type_threshold")
    applier = ScoringApplier()

    ranges = (models.ThresholdRange(min=0, max=100, score=100),)
    rule = models.ThresholdScoringRule(ranges=ranges)
    score = applier.apply_rule(50, rule, "higher_better")

    assert score == 100
    print("  OK - Threshold type recognition")


def test_apply_rule_unsupported_type():
    """测试不支持的评分规则类型"""
    print("\n[9/20] test_apply_rule_unsupported_type")
    applier = ScoringApplier()

    # 创建一个伪造的不支持的规则类型
    class FakeRule:
        type = "fake"

    rule = FakeRule()

    try:
        applier.apply_rule(50, rule, "higher_better")
        print("  FAIL - Should raise ValueError")
        return False
    except ValueError as e:
        assert "不支持的评分规则类型" in str(e)
        print("  OK - Unsupported type error")
        return True


def test_calculate_scores_simple():
    """测试简单的批量计算"""
    print("\n[10/20] test_calculate_scores_simple")
    applier = ScoringApplier()

    raw_data = {
        "A": {"成本": 10},
        "B": {"成本": 20},
    }

    criteria = (
        models.Criterion(name="成本", weight=0.5, direction="lower_better"),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert scores["A"]["成本"] == 10
    assert scores["B"]["成本"] == 20
    print("  OK - Simple batch calculation")


def test_calculate_scores_with_linear_rule():
    """测试带线性评分规则的批量计算"""
    print("\n[11/20] test_calculate_scores_with_linear_rule")
    applier = ScoringApplier()

    raw_data = {
        "A": {"增长率": 0},
        "B": {"增长率": 50},
        "C": {"增长率": 100},
    }

    scoring_rule = models.LinearScoringRule(min=0, max=100, scale=100)
    criteria = (
        models.Criterion(
            name="增长率",
            weight=0.5,
            direction="higher_better",
            scoring_rule=scoring_rule
        ),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert scores["A"]["增长率"] == 0
    assert scores["B"]["增长率"] == 50
    assert scores["C"]["增长率"] == 100
    print("  OK - Batch with linear rule")


def test_calculate_scores_with_threshold_rule():
    """测试带阈值评分规则的批量计算"""
    print("\n[12/20] test_calculate_scores_with_threshold_rule")
    applier = ScoringApplier()

    raw_data = {
        "A": {"采购额": 50},
        "B": {"采购额": 300},
        "C": {"采购额": 800},
    }

    ranges = (
        models.ThresholdRange(max=100, score=40),
        models.ThresholdRange(min=100, max=500, score=60),
        models.ThresholdRange(min=500, score=80),
    )
    scoring_rule = models.ThresholdScoringRule(ranges=ranges)
    criteria = (
        models.Criterion(
            name="采购额",
            weight=0.5,
            direction="higher_better",
            scoring_rule=scoring_rule
        ),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert scores["A"]["采购额"] == 40
    assert scores["B"]["采购额"] == 60
    assert scores["C"]["采购额"] == 80
    print("  OK - Batch with threshold rule")


def test_calculate_scores_mixed_rules():
    """测试混合评分规则"""
    print("\n[13/20] test_calculate_scores_mixed_rules")
    applier = ScoringApplier()

    raw_data = {
        "A": {"增长率": 50, "采购额": 300},
        "B": {"增长率": 80, "采购额": 600},
    }

    linear_rule = models.LinearScoringRule(min=0, max=100, scale=100)
    ranges = (
        models.ThresholdRange(max=100, score=40),
        models.ThresholdRange(min=100, max=500, score=60),
        models.ThresholdRange(min=500, score=80),
    )
    threshold_rule = models.ThresholdScoringRule(ranges=ranges)

    criteria = (
        models.Criterion(
            name="增长率",
            weight=0.5,
            direction="higher_better",
            scoring_rule=linear_rule
        ),
        models.Criterion(
            name="采购额",
            weight=0.5,
            direction="higher_better",
            scoring_rule=threshold_rule
        ),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert scores["A"]["增长率"] == 50
    assert scores["A"]["采购额"] == 60
    assert scores["B"]["增长率"] == 80
    assert scores["B"]["采购额"] == 80
    print("  OK - Mixed scoring rules")


def test_calculate_scores_with_column_mapping():
    """测试列名映射"""
    print("\n[14/20] test_calculate_scores_with_column_mapping")
    applier = ScoringApplier()

    raw_data = {
        "A": {"annual_purchase": 800},
    }

    scoring_rule = models.LinearScoringRule(min=0, max=1000, scale=100)
    criteria = (
        models.Criterion(
            name="年采购额",
            weight=0.5,
            direction="higher_better",
            scoring_rule=scoring_rule,
            column="annual_purchase"  # 列名映射
        ),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert scores["A"]["年采购额"] == 80
    print("  OK - Column mapping")


def test_calculate_scores_missing_data():
    """测试缺少数据列的错误处理"""
    print("\n[15/20] test_calculate_scores_missing_data")
    applier = ScoringApplier()

    raw_data = {
        "A": {},  # 空数据
    }

    criteria = (
        models.Criterion(name="成本", weight=0.5, direction="lower_better"),
    )

    try:
        applier.calculate_scores(raw_data, criteria)
        print("  FAIL - Should raise ValueError")
        return False
    except ValueError as e:
        assert "缺少数据列" in str(e)
        print("  OK - Missing data error")
        return True


def test_calculate_scores_no_scoring_rule():
    """测试没有评分规则的情况"""
    print("\n[16/20] test_calculate_scores_no_scoring_rule")
    applier = ScoringApplier()

    raw_data = {
        "A": {"成本": 10},
        "B": {"成本": 20},
    }

    # 没有评分规则
    criteria = (
        models.Criterion(name="成本", weight=0.5, direction="lower_better"),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    # 应该直接使用原始值
    assert scores["A"]["成本"] == 10
    assert scores["B"]["成本"] == 20
    print("  OK - No scoring rule")


def test_apply_threshold_direction_independent():
    """测试阈值评分与方向无关"""
    print("\n[17/20] test_apply_threshold_direction_independent")
    applier = ScoringApplier()

    ranges = (models.ThresholdRange(min=0, max=100, score=50),)
    rule = models.ThresholdScoringRule(ranges=ranges)

    # 阈值评分与方向无关
    score_higher = applier.apply_threshold(50, rule, "higher_better")
    score_lower = applier.apply_threshold(50, rule, "lower_better")

    assert score_higher == score_lower
    print("  OK - Direction independent")


def test_apply_linear_edge_case():
    """测试线性评分边界情况"""
    print("\n[18/20] test_apply_linear_edge_case")
    applier = ScoringApplier()

    # min == max 的情况（虽然验证器会阻止，但防御性编程）
    try:
        rule = models.LinearScoringRule(min=10, max=10, scale=100)
    except ValueError:
        print("  OK - Edge case prevented by validation")
        return True

    # 测试 scale 不是 100 的情况
    rule = models.LinearScoringRule(min=0, max=100, scale=50)
    score = applier.apply_linear(50, rule, "higher_better")
    assert score == 25
    print("  OK - Custom scale")


def test_calculate_scores_multiple_alternatives():
    """测试多个备选方案"""
    print("\n[19/20] test_calculate_scores_multiple_alternatives")
    applier = ScoringApplier()

    raw_data = {
        f"Cust_{i:03d}": {"score": float(i)}
        for i in range(100)
    }

    criteria = (
        models.Criterion(name="score", weight=1.0, direction="higher_better"),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert len(scores) == 100
    assert scores["Cust_000"]["score"] == 0
    assert scores["Cust_099"]["score"] == 99
    print("  OK - Multiple alternatives (100)")


def test_calculate_scores_multiple_criteria():
    """测试多个准则"""
    print("\n[20/20] test_calculate_scores_multiple_criteria")
    applier = ScoringApplier()

    raw_data = {
        "A": {
            "成本": 50,
            "质量": 80,
            "交付": 60
        }
    }

    criteria = (
        models.Criterion(name="成本", weight=0.3, direction="lower_better"),
        models.Criterion(name="质量", weight=0.5, direction="higher_better"),
        models.Criterion(name="交付", weight=0.2, direction="higher_better"),
    )

    scores = applier.calculate_scores(raw_data, criteria)

    assert len(scores["A"]) == 3
    assert scores["A"]["成本"] == 50
    assert scores["A"]["质量"] == 80
    assert scores["A"]["交付"] == 60
    print("  OK - Multiple criteria")


def main():
    """主函数"""
    print("="*60)
    print("PHASE 2: SCORING APPLIER TESTS")
    print("="*60)

    tests = [
        test_apply_threshold_basic,
        test_apply_threshold_default,
        test_apply_threshold_open_ended,
        test_apply_linear_basic,
        test_apply_linear_clamping,
        test_apply_linear_negative_range,
        test_apply_rule_type_linear,
        test_apply_rule_type_threshold,
        test_apply_rule_unsupported_type,
        test_calculate_scores_simple,
        test_calculate_scores_with_linear_rule,
        test_calculate_scores_with_threshold_rule,
        test_calculate_scores_mixed_rules,
        test_calculate_scores_with_column_mapping,
        test_calculate_scores_missing_data,
        test_calculate_scores_no_scoring_rule,
        test_apply_threshold_direction_independent,
        test_apply_linear_edge_case,
        test_calculate_scores_multiple_alternatives,
        test_calculate_scores_multiple_criteria,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result is False:
                failed += 1
            else:
                passed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\nSUCCESS! Phase 2 complete - all tests passed!")
        print("\nAcceptance criteria:")
        print("  [x] Threshold scoring: OK")
        print("  [x] Linear scoring: OK")
        print("  [x] Batch calculation: OK")
        print("  [x] Error handling: OK")
        print("  [x] Column mapping: OK")
        print("  [x] Mixed rules: OK")
        return True
    else:
        print(f"\nFAILED: {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
