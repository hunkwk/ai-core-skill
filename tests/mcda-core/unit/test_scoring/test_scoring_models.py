"""
MCDA Core 评分模型测试

测试 LinearScoringRule, ThresholdScoringRule, ThresholdRange 等数据模型。
"""

import pytest
from mcda_core.models import (
    LinearScoringRule,
    ThresholdScoringRule,
    ThresholdRange,
    Criterion,
    Direction,
    ScoringRule,
)


class TestLinearScoringRule:
    """测试 LinearScoringRule 模型"""

    def test_create_linear_rule_basic(self):
        """测试创建基本的线性评分规则"""
        rule = LinearScoringRule(min=0, max=100)
        assert rule.min == 0
        assert rule.max == 100
        assert rule.scale == 100.0
        assert rule.type == "linear"

    def test_create_linear_rule_with_scale(self):
        """测试创建带自定义 scale 的线性评分规则"""
        rule = LinearScoringRule(min=-20, max=50, scale=100)
        assert rule.min == -20
        assert rule.max == 50
        assert rule.scale == 100

    def test_linear_rule_validation_min_equal_max(self):
        """测试 min == max 时抛出异常"""
        with pytest.raises(ValueError, match="min.*必须小于 max"):
            LinearScoringRule(min=10, max=10)

    def test_linear_rule_validation_min_greater_than_max(self):
        """测试 min > max 时抛出异常"""
        with pytest.raises(ValueError, match="min.*必须小于 max"):
            LinearScoringRule(min=100, max=50)

    def test_linear_rule_validation_invalid_scale(self):
        """测试 scale <= 0 时抛出异常"""
        with pytest.raises(ValueError, match="scale.*必须大于 0"):
            LinearScoringRule(min=0, max=100, scale=0)

        with pytest.raises(ValueError, match="scale.*必须大于 0"):
            LinearScoringRule(min=0, max=100, scale=-10)

    def test_linear_rule_immutable(self):
        """测试 LinearScoringRule 不可变性"""
        rule = LinearScoringRule(min=0, max=100)
        with pytest.raises(Exception):  # frozen dataclass
            rule.min = 10


class TestThresholdRange:
    """测试 ThresholdRange 模型"""

    def test_create_range_max_only(self):
        """测试创建只有 max 的区间"""
        range_rule = ThresholdRange(max=100, score=100)
        assert range_rule.min is None
        assert range_rule.max == 100
        assert range_rule.score == 100

    def test_create_range_min_only(self):
        """测试创建只有 min 的区间"""
        range_rule = ThresholdRange(min=500, score=40)
        assert range_rule.min == 500
        assert range_rule.max is None
        assert range_rule.score == 40

    def test_create_range_min_and_max(self):
        """测试创建有 min 和 max 的区间"""
        range_rule = ThresholdRange(min=100, max=500, score=80)
        assert range_rule.min == 100
        assert range_rule.max == 500
        assert range_rule.score == 80

    def test_create_range_default_score(self):
        """测试默认评分"""
        range_rule = ThresholdRange(min=100, max=500)
        assert range_rule.score == 100.0

    def test_range_validation_min_greater_than_max(self):
        """测试 min >= max 时抛出异常"""
        with pytest.raises(ValueError, match="min.*必须小于 max"):
            ThresholdRange(min=500, max=100)

    def test_range_validation_invalid_score_negative(self):
        """测试 score < 0 时抛出异常"""
        with pytest.raises(ValueError, match="score.*必须在 0-100 范围内"):
            ThresholdRange(min=0, max=100, score=-10)

    def test_range_validation_invalid_score_over_100(self):
        """测试 score > 100 时抛出异常"""
        with pytest.raises(ValueError, match="score.*必须在 0-100 范围内"):
            ThresholdRange(min=0, max=100, score=150)

    def test_range_immutable(self):
        """测试 ThresholdRange 不可变性"""
        range_rule = ThresholdRange(min=100, max=500, score=80)
        with pytest.raises(Exception):  # frozen dataclass
            range_rule.score = 90


class TestThresholdScoringRule:
    """测试 ThresholdScoringRule 模型"""

    def test_create_threshold_rule_basic(self):
        """测试创建基本的阈值评分规则"""
        ranges = (
            ThresholdRange(max=100, score=40),
            ThresholdRange(min=100, max=500, score=60),
            ThresholdRange(min=500, score=80),
        )
        rule = ThresholdScoringRule(ranges=ranges)
        assert len(rule.ranges) == 3
        assert rule.default_score == 0.0
        assert rule.type == "threshold"

    def test_create_threshold_rule_with_default(self):
        """测试创建带默认评分的阈值规则"""
        ranges = (ThresholdRange(min=0, max=100, score=100),)
        rule = ThresholdScoringRule(ranges=ranges, default_score=50)
        assert rule.default_score == 50

    def test_threshold_rule_validation_empty_ranges(self):
        """测试空 ranges 时抛出异常"""
        with pytest.raises(ValueError, match="ranges 不能为空"):
            ThresholdScoringRule(ranges=())

    def test_threshold_rule_validation_invalid_default_score(self):
        """测试无效的 default_score"""
        ranges = (ThresholdRange(min=0, max=100, score=100),)

        with pytest.raises(ValueError, match="default_score.*必须在 0-100 范围内"):
            ThresholdScoringRule(ranges=ranges, default_score=-10)

        with pytest.raises(ValueError, match="default_score.*必须在 0-100 范围内"):
            ThresholdScoringRule(ranges=ranges, default_score=150)

    def test_threshold_rule_immutable(self):
        """测试 ThresholdScoringRule 不可变性"""
        ranges = (ThresholdRange(min=0, max=100, score=100),)
        rule = ThresholdScoringRule(ranges=ranges)
        with pytest.raises(Exception):  # frozen dataclass
            rule.default_score = 50


class TestCriterion:
    """测试 Criterion 模型与评分规则集成"""

    def test_create_criterion_without_scoring_rule(self):
        """测试创建不带评分规则的准则"""
        criterion = Criterion(
            name="成本",
            weight=0.35,
            direction="lower_better",
            description="月度成本（万元）"
        )
        assert criterion.name == "成本"
        assert criterion.weight == 0.35
        assert criterion.direction == "lower_better"
        assert criterion.scoring_rule is None
        assert criterion.column is None

    def test_create_criterion_with_linear_rule(self):
        """测试创建带线性评分规则的准则"""
        scoring_rule = LinearScoringRule(min=0, max=100, scale=100)
        criterion = Criterion(
            name="增长率",
            weight=0.20,
            direction="higher_better",
            scoring_rule=scoring_rule
        )
        assert criterion.scoring_rule == scoring_rule
        assert criterion.scoring_rule.type == "linear"

    def test_create_criterion_with_threshold_rule(self):
        """测试创建带阈值评分规则的准则"""
        ranges = (
            ThresholdRange(max=100, score=40),
            ThresholdRange(min=100, max=500, score=60),
            ThresholdRange(min=500, score=80),
        )
        scoring_rule = ThresholdScoringRule(ranges=ranges)
        criterion = Criterion(
            name="年采购额",
            weight=0.25,
            direction="higher_better",
            scoring_rule=scoring_rule
        )
        assert criterion.scoring_rule == scoring_rule
        assert criterion.scoring_rule.type == "threshold"

    def test_create_criterion_with_column_mapping(self):
        """测试创建带列名映射的准则"""
        criterion = Criterion(
            name="年采购额",
            weight=0.25,
            direction="higher_better",
            column="annual_purchase"
        )
        assert criterion.column == "annual_purchase"

    def test_criterion_validation_empty_name(self):
        """测试空名称时抛出异常"""
        with pytest.raises(ValueError, match="name 不能为空"):
            Criterion(name="", weight=0.5, direction="higher_better")

    def test_criterion_validation_invalid_weight_negative(self):
        """测试负权重时抛出异常"""
        with pytest.raises(ValueError, match="weight.*必须在 0-1 范围内"):
            Criterion(name="成本", weight=-0.1, direction="lower_better")

    def test_criterion_validation_invalid_weight_over_1(self):
        """测试权重 > 1 时抛出异常"""
        with pytest.raises(ValueError, match="weight.*必须在 0-1 范围内"):
            Criterion(name="成本", weight=1.5, direction="lower_better")

    def test_criterion_validation_invalid_direction(self):
        """测试无效的方向时抛出异常"""
        with pytest.raises(ValueError, match="direction.*必须是.*higher_better.*lower_better"):
            Criterion(name="成本", weight=0.5, direction="invalid")

    def test_criterion_immutable(self):
        """测试 Criterion 不可变性"""
        criterion = Criterion(name="成本", weight=0.5, direction="lower_better")
        with pytest.raises(Exception):  # frozen dataclass
            criterion.weight = 0.6


class TestScoringRuleUnion:
    """测试 ScoringRule 联合类型"""

    def test_scoring_rule_accepts_linear(self):
        """测试 ScoringRule 类型接受 LinearScoringRule"""
        rule: ScoringRule = LinearScoringRule(min=0, max=100)
        assert rule.type == "linear"

    def test_scoring_rule_accepts_threshold(self):
        """测试 ScoringRule 类型接受 ThresholdScoringRule"""
        ranges = (ThresholdRange(min=0, max=100, score=100),)
        rule: ScoringRule = ThresholdScoringRule(ranges=ranges)
        assert rule.type == "threshold"

    def test_scoring_rule_type_checking(self):
        """测试评分规则类型判断"""
        linear_rule = LinearScoringRule(min=0, max=100)
        threshold_rule = ThresholdScoringRule(
            ranges=(ThresholdRange(min=0, max=100, score=100),)
        )

        # 判断类型
        assert linear_rule.type == "linear"
        assert threshold_rule.type == "threshold"

        # 使用 isinstance 判断
        assert isinstance(linear_rule, LinearScoringRule)
        assert isinstance(threshold_rule, ThresholdScoringRule)
