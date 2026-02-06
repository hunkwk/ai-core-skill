"""
MCDA Core - 评分规则 E2E 测试

测试评分规则应用器的端到端功能。
"""

import pytest

from mcda_core.core import MCDAOrchestrator
from mcda_core.models import (
    DecisionProblem,
    Criterion,
    LinearScoringRule,
    ThresholdScoringRule,
    ThresholdRange,
)
from mcda_core.scoring import ScoringApplier


class TestScoringRules:
    """评分规则端到端测试"""

    def test_linear_scoring_higher_better(self):
        """测试: 线性评分 - 越高越好"""
        # 线性评分规则: 将 0-1000 映射到 0-100
        rule = LinearScoringRule(min=0, max=1000, scale=100)

        applier = ScoringApplier()

        # 测试不同值
        score_0 = applier.apply_linear(0, rule, "higher_better")
        score_500 = applier.apply_linear(500, rule, "higher_better")
        score_1000 = applier.apply_linear(1000, rule, "higher_better")

        assert score_0 == 0.0
        assert score_500 == 50.0
        assert score_1000 == 100.0

    def test_linear_scoring_lower_better(self):
        """测试: 线性评分 - 越低越好"""
        # 线性评分规则: 将 0-1000 映射到 0-100
        rule = LinearScoringRule(min=0, max=1000, scale=100)

        applier = ScoringApplier()

        # 测试不同值（越低越好）
        score_0 = applier.apply_linear(0, rule, "lower_better")
        score_500 = applier.apply_linear(500, rule, "lower_better")
        score_1000 = applier.apply_linear(1000, rule, "lower_better")

        assert score_0 == 100.0
        assert score_500 == 50.0
        assert score_1000 == 0.0

    def test_linear_scoring_clamping(self):
        """测试: 线性评分 - 超出范围限制"""
        rule = LinearScoringRule(min=100, max=500, scale=100)

        applier = ScoringApplier()

        # 测试超出范围的值
        score_under = applier.apply_linear(50, rule, "higher_better")
        score_over = applier.apply_linear(600, rule, "higher_better")

        # 应该被限制在范围内
        assert score_under == 0.0  # 小于 min，按 min 计算
        assert score_over == 100.0  # 大于 max，按 max 计算

    def test_threshold_scoring(self):
        """测试: 阈值分段评分"""
        # 阈值评分规则
        rule = ThresholdScoringRule(
            ranges=(
                ThresholdRange(max=100, score=100),      # < 100: 100分
                ThresholdRange(min=100, max=300, score=80),  # 100-300: 80分
                ThresholdRange(min=300, max=600, score=60),  # 300-600: 60分
                ThresholdRange(min=600, max=1000, score=40),  # 600-1000: 40分
                ThresholdRange(min=1000, score=20),      # > 1000: 20分
            ),
            default_score=0
        )

        applier = ScoringApplier()

        # 测试不同区间
        score_50 = applier.apply_threshold(50, rule, "lower_better")
        score_200 = applier.apply_threshold(200, rule, "lower_better")
        score_500 = applier.apply_threshold(500, rule, "lower_better")
        score_800 = applier.apply_threshold(800, rule, "lower_better")
        score_1500 = applier.apply_threshold(1500, rule, "lower_better")

        assert score_50 == 100
        assert score_200 == 80
        assert score_500 == 60
        assert score_800 == 40
        assert score_1500 == 20

    def test_threshold_scoring_with_gaps(self):
        """测试: 阈值分段评分 - 有区间间隙"""
        rule = ThresholdScoringRule(
            ranges=(
                ThresholdRange(max=50, score=100),
                ThresholdRange(min=100, max=200, score=80),
                ThresholdRange(min=300, score=60),
            ),
            default_score=0
        )

        applier = ScoringApplier()

        # 测试区间间隙中的值
        score_75 = applier.apply_threshold(75, rule, "higher_better")  # 间隙中
        score_250 = applier.apply_threshold(250, rule, "higher_better")  # 间隙中

        # 应该返回默认评分
        assert score_75 == 0
        assert score_250 == 0

    def test_scoring_rule_unified_interface(self):
        """测试: 评分规则统一接口"""
        linear_rule = LinearScoringRule(min=0, max=100, scale=100)
        threshold_rule = ThresholdScoringRule(
            ranges=(
                ThresholdRange(max=30, score=40),
                ThresholdRange(min=30, max=70, score=70),
                ThresholdRange(min=70, score=100),
            ),
            default_score=0
        )

        applier = ScoringApplier()

        # 使用统一接口 apply_rule
        linear_score = applier.apply_rule(50, linear_rule, "higher_better")
        threshold_score = applier.apply_rule(50, threshold_rule, "higher_better")

        assert linear_score == 50.0
        assert threshold_score == 70.0

    def test_scoring_with_orchestrator_integration(self):
        """测试: 评分规则与编排器集成"""
        # 1. 原始数据
        raw_data = {
            "供应商A": {"价格": 800, "质量": 85},
            "供应商B": {"价格": 1200, "质量": 92},
            "供应商C": {"价格": 650, "质量": 78},
        }

        # 2. 定义评分规则
        applier = ScoringApplier()

        # 价格：越低越好，线性评分 500-1500 → 0-100
        price_rule = LinearScoringRule(min=500, max=1500, scale=100)

        # 质量：越高越好，阈值分段评分
        quality_rule = ThresholdScoringRule(
            ranges=(
                ThresholdRange(max=70, score=60),
                ThresholdRange(min=70, max=85, score=80),
                ThresholdRange(min=85, score=100),
            ),
            default_score=0
        )

        # 3. 应用评分规则
        scores = {}
        for alt, raw_scores in raw_data.items():
            scores[alt] = {
                "价格": applier.apply_linear(raw_scores["价格"], price_rule, "lower_better"),
                "质量": applier.apply_threshold(raw_scores["质量"], quality_rule, "higher_better"),
            }

        # 4. 创建决策问题
        criteria = [
            Criterion(name="价格", weight=0.4, direction="lower_better"),
            Criterion(name="质量", weight=0.6, direction="higher_better"),
        ]

        problem = DecisionProblem(
            alternatives=("供应商A", "供应商B", "供应商C"),
            criteria=tuple(criteria),
            scores=scores,
        )

        # 5. 使用编排器分析
        orchestrator = MCDAOrchestrator()
        result = orchestrator.analyze(problem, algorithm_name="wsm")

        # 验证分析结果
        assert result is not None
        assert len(result.rankings) == 3

        # 验证评分在合理范围内
        for ranking in result.rankings:
            assert 0 <= ranking.score <= 100

    def test_multiple_scoring_rules_comparison(self):
        """测试: 多种评分规则对比"""
        raw_value = 65

        # 线性评分: 0-100 → 0-100
        linear_rule = LinearScoringRule(min=0, max=100, scale=100)

        # 阈值评分
        threshold_rule = ThresholdScoringRule(
            ranges=(
                ThresholdRange(max=50, score=40),
                ThresholdRange(min=50, max=75, score=70),
                ThresholdRange(min=75, score=100),
            ),
            default_score=0
        )

        applier = ScoringApplier()

        linear_score = applier.apply_rule(raw_value, linear_rule, "higher_better")
        threshold_score = applier.apply_rule(raw_value, threshold_rule, "higher_better")

        # 验证评分在合理范围内
        assert 0 <= linear_score <= 100
        assert 0 <= threshold_score <= 100

        # 两种方法给出不同评分
        assert linear_score != threshold_score

    def test_scoring_for_cost_criteria(self):
        """测试: 成本类准则的评分"""
        # 成本数据（越低越好）
        costs = {
            "方案A": 5000,
            "方案B": 8000,
            "方案C": 3000,
        }

        # 线性评分规则: 2000-10000 → 0-100
        rule = LinearScoringRule(min=2000, max=10000, scale=100)

        applier = ScoringApplier()

        scores = {alt: applier.apply_linear(cost, rule, "lower_better") for alt, cost in costs.items()}

        # 验证：成本越低，评分越高
        assert scores["方案C"] > scores["方案A"] > scores["方案B"]
        assert all(0 <= s <= 100 for s in scores.values())
