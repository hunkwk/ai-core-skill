"""
Phase 3: YAML 解析器测试

测试 MCDAOrchestrator 的评分规则解析功能。
"""

import sys
from pathlib import Path

# 添加 mcda-core 到路径
mcda_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_path))

import models
from core import MCDAOrchestrator
from validation import MCDAValidationError


def test_parse_linear_rule():
    """测试解析线性评分规则"""
    print("\n[1/10] test_parse_linear_rule")
    orchestrator = MCDAOrchestrator()

    rule_data = {
        "type": "linear",
        "min": 0,
        "max": 100,
        "scale": 100
    }

    rule = orchestrator._parse_linear_rule(rule_data)

    assert rule.type == "linear"
    assert rule.min == 0
    assert rule.max == 100
    assert rule.scale == 100
    print("  OK - Linear rule parsed")


def test_parse_threshold_rule():
    """测试解析阈值评分规则"""
    print("\n[2/10] test_parse_threshold_rule")
    orchestrator = MCDAOrchestrator()

    rule_data = {
        "type": "threshold",
        "ranges": [
            {"max": 100, "score": 40},
            {"min": 100, "max": 500, "score": 60},
            {"min": 500, "score": 80}
        ],
        "default_score": 0
    }

    rule = orchestrator._parse_threshold_rule(rule_data)

    assert rule.type == "threshold"
    assert len(rule.ranges) == 3
    assert rule.default_score == 0
    print("  OK - Threshold rule parsed")


def test_parse_scoring_rule_linear():
    """测试解析评分规则（线性）"""
    print("\n[3/10] test_parse_scoring_rule_linear")
    orchestrator = MCDAOrchestrator()

    rule_data = {
        "type": "linear",
        "min": -20,
        "max": 50,
        "scale": 100
    }

    rule = orchestrator._parse_scoring_rule(rule_data)

    assert isinstance(rule, models.LinearScoringRule)
    assert rule.type == "linear"
    print("  OK - Scoring rule (linear)")


def test_parse_scoring_rule_threshold():
    """测试解析评分规则（阈值）"""
    print("\n[4/10] test_parse_scoring_rule_threshold")
    orchestrator = MCDAOrchestrator()

    rule_data = {
        "type": "threshold",
        "ranges": [
            {"min": 0, "max": 100, "score": 100}
        ]
    }

    rule = orchestrator._parse_scoring_rule(rule_data)

    assert isinstance(rule, models.ThresholdScoringRule)
    assert rule.type == "threshold"
    print("  OK - Scoring rule (threshold)")


def test_parse_scoring_rule_none():
    """测试空评分规则"""
    print("\n[5/10] test_parse_scoring_rule_none")
    orchestrator = MCDAOrchestrator()

    rule = orchestrator._parse_scoring_rule(None)

    assert rule is None
    print("  OK - None scoring rule")


def test_parse_scoring_rule_unsupported_type():
    """测试不支持的评分规则类型"""
    print("\n[6/10] test_parse_scoring_rule_unsupported_type")
    orchestrator = MCDAOrchestrator()

    rule_data = {"type": "unsupported"}

    try:
        orchestrator._parse_scoring_rule(rule_data)
        print("  FAIL - Should raise MCDAValidationError")
        return False
    except MCDAValidationError as e:
        assert "不支持的评分规则类型" in str(e)
        print("  OK - Unsupported type error")
        return True


def test_parse_criteria_with_scoring_rule():
    """测试解析带评分规则的准则"""
    print("\n[7/10] test_parse_criteria_with_scoring_rule")
    orchestrator = MCDAOrchestrator()

    data = {
        "criteria": [
            {
                "name": "增长率",
                "weight": 0.2,
                "direction": "higher_better",
                "scoring_rule": {
                    "type": "linear",
                    "min": -20,
                    "max": 50,
                    "scale": 100
                }
            }
        ]
    }

    criteria = orchestrator._parse_criteria(data, auto_normalize_weights=False)

    assert len(criteria) == 1
    assert criteria[0].name == "增长率"
    assert criteria[0].scoring_rule is not None
    assert criteria[0].scoring_rule.type == "linear"
    print("  OK - Criteria with scoring rule")


def test_parse_criteria_without_scoring_rule():
    """测试解析不带评分规则的准则"""
    print("\n[8/10] test_parse_criteria_without_scoring_rule")
    orchestrator = MCDAOrchestrator()

    data = {
        "criteria": [
            {
                "name": "成本",
                "weight": 0.5,
                "direction": "lower_better"
            }
        ]
    }

    criteria = orchestrator._parse_criteria(data, auto_normalize_weights=False)

    assert len(criteria) == 1
    assert criteria[0].scoring_rule is None
    print("  OK - Criteria without scoring rule")


def test_parse_criteria_with_column():
    """测试解析带列名映射的准则"""
    print("\n[9/10] test_parse_criteria_with_column")
    orchestrator = MCDAOrchestrator()

    data = {
        "criteria": [
            {
                "name": "年采购额",
                "weight": 0.25,
                "direction": "higher_better",
                "column": "annual_purchase"
            }
        ]
    }

    criteria = orchestrator._parse_criteria(data, auto_normalize_weights=False)

    assert len(criteria) == 1
    assert criteria[0].column == "annual_purchase"
    print("  OK - Criteria with column mapping")


def test_parse_criteria_normalization_preserves_scoring_rule():
    """测试权重归一化保留评分规则"""
    print("\n[10/10] test_parse_criteria_normalization_preserves_scoring_rule")
    orchestrator = MCDAOrchestrator()

    data = {
        "criteria": [
            {
                "name": "增长率",
                "weight": 0.2,
                "direction": "higher_better",
                "scoring_rule": {
                    "type": "linear",
                    "min": -20,
                    "max": 50,
                    "scale": 100
                }
            },
            {
                "name": "成本",
                "weight": 0.8,
                "direction": "lower_better"
            }
        ]
    }

    criteria = orchestrator._parse_criteria(data, auto_normalize_weights=True)

    # 检查归一化后的权重
    assert abs(criteria[0].weight - 0.2) < 0.01
    assert abs(criteria[1].weight - 0.8) < 0.01

    # 检查评分规则被保留
    assert criteria[0].scoring_rule is not None
    assert criteria[0].scoring_rule.type == "linear"
    assert criteria[1].scoring_rule is None
    print("  OK - Normalization preserves scoring rule")


def main():
    """主函数"""
    print("="*60)
    print("PHASE 3: YAML PARSER TESTS")
    print("="*60)

    tests = [
        test_parse_linear_rule,
        test_parse_threshold_rule,
        test_parse_scoring_rule_linear,
        test_parse_scoring_rule_threshold,
        test_parse_scoring_rule_none,
        test_parse_scoring_rule_unsupported_type,
        test_parse_criteria_with_scoring_rule,
        test_parse_criteria_without_scoring_rule,
        test_parse_criteria_with_column,
        test_parse_criteria_normalization_preserves_scoring_rule,
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
        print("\nSUCCESS! Phase 3 complete - all tests passed!")
        print("\nAcceptance criteria:")
        print("  [x] _parse_scoring_rule: OK")
        print("  [x] _parse_linear_rule: OK")
        print("  [x] _parse_threshold_rule: OK")
        print("  [x] _parse_criteria integration: OK")
        print("  [x] Column mapping: OK")
        print("  [x] Weight normalization: OK")
        return True
    else:
        print(f"\nFAILED: {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
