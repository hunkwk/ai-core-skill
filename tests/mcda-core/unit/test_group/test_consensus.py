"""
MCDA Core - 共识度测量单元测试

测试群决策共识度计算功能。
"""

import pytest
import math

from mcda_core.group.consensus import (
    ConsensusMeasure,
    ConsensusResult,
)
from mcda_core.group.models import (
    DecisionMaker,
    GroupDecisionProblem,
    AggregationConfig,
)
from mcda_core.models import Criterion


class TestConsensusMeasure:
    """测试共识度测量"""

    def test_compute_standard_deviation(self):
        """测试计算标准差"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        mean, std = ConsensusMeasure.compute_standard_deviation(scores)

        # 均值 = (80 + 90 + 85) / 3 = 85
        assert mean == pytest.approx(85.0)
        # 方差 = ((80-85)^2 + (90-85)^2 + (85-85)^2) / 3 = 50/3 ≈ 16.67
        # 标准差 = sqrt(16.67) ≈ 4.08
        assert std == pytest.approx(4.082, rel=1e-3)

    def test_compute_standard_deviation_single_value(self):
        """测试单个值的标准差"""
        scores = {"DM1": 85.0}
        mean, std = ConsensusMeasure.compute_standard_deviation(scores)

        assert mean == 85.0
        assert std == 0.0

    def test_compute_standard_deviation_empty(self):
        """测试空字典的标准差"""
        mean, std = ConsensusMeasure.compute_standard_deviation({})
        assert mean == 0.0
        assert std == 0.0

    def test_compute_standard_devision_identical_values(self):
        """测试相同值的标准差为零"""
        scores = {"DM1": 85.0, "DM2": 85.0, "DM3": 85.0}
        mean, std = ConsensusMeasure.compute_standard_deviation(scores)

        assert mean == 85.0
        assert std == 0.0

    def test_compute_coefficient_of_variation(self):
        """测试变异系数计算"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        cv = ConsensusMeasure.compute_coefficient_of_variation(scores)

        # 标准差 ≈ 4.08, 均值 = 85, cv ≈ 0.048
        assert cv == pytest.approx(0.048, rel=1e-2)

    def test_compute_coefficient_of_variation_zero_mean(self):
        """测试零均值的变异系数"""
        scores = {"DM1": 0.0, "DM2": 0.0}
        cv = ConsensusMeasure.compute_coefficient_of_variation(scores)

        # 均值为 0 时应返回 0（标准差也为 0）
        assert cv == 0.0

    def test_compute_euclidean_distance(self):
        """测试欧氏距离计算"""
        scores1 = {"成本": 80.0, "质量": 90.0, "技术": 85.0}
        scores2 = {"成本": 85.0, "质量": 80.0, "技术": 90.0}

        distance = ConsensusMeasure.compute_euclidean_distance(scores1, scores2)

        # sqrt((80-85)^2 + (90-80)^2 + (85-90)^2)
        # = sqrt(25 + 100 + 25) = sqrt(150) ≈ 12.25
        assert distance == pytest.approx(12.247, rel=1e-3)

    def test_compute_euclidean_distance_identical(self):
        """测试相同向量的欧氏距离为零"""
        scores = {"成本": 80.0, "质量": 90.0}
        distance = ConsensusMeasure.compute_euclidean_distance(scores, scores)

        assert distance == 0.0

    def test_compute_euclidean_distance_different_keys(self):
        """测试不同键的欧氏距离"""
        scores1 = {"成本": 80.0, "质量": 90.0}
        scores2 = {"成本": 85.0, "质量": 80.0, "技术": 90.0}

        # 技术: 0 vs 90, 差异 = 90
        distance = ConsensusMeasure.compute_euclidean_distance(scores1, scores2)
        expected = math.sqrt((80-85)**2 + (90-80)**2 + (0-90)**2)

        assert distance == pytest.approx(expected)

    def test_compute_agreement_rate(self):
        """测试同意率计算"""
        scores = {"DM1": 80.0, "DM2": 85.0, "DM3": 90.0, "DM4": 95.0}
        # 均值 = 87.5, 容差 10: [77.5, 97.5]
        # 全部在范围内，同意率 = 1.0
        rate = ConsensusMeasure.compute_agreement_rate(scores, tolerance=10.0)
        assert rate == pytest.approx(1.0)

    def test_compute_agreement_rate_partial(self):
        """测试部分同意率"""
        scores = {"DM1": 70.0, "DM2": 85.0, "DM3": 90.0}
        # 均值 ≈ 81.67, 容差 10: [71.67, 91.67]
        # DM1: 70 不在范围内
        rate = ConsensusMeasure.compute_agreement_rate(scores, tolerance=10.0)
        assert rate == pytest.approx(2/3, rel=1e-3)

    def test_compute_agreement_rate_single_value(self):
        """测试单个值的同意率为 1"""
        scores = {"DM1": 85.0}
        rate = ConsensusMeasure.compute_agreement_rate(scores)
        assert rate == 1.0

    def test_compute_criterion_consensus_standard_deviation(self):
        """测试标准差法计算准则共识度"""
        # 相同评分，共识度为 1
        scores = {"DM1": 85.0, "DM2": 85.0, "DM3": 85.0}
        consensus = ConsensusMeasure.compute_criterion_consensus(
            scores, method="standard_deviation"
        )
        assert consensus == 1.0

    def test_compute_criterion_consensus_some_variation(self):
        """测试有差异的共识度"""
        scores = {"DM1": 75.0, "DM2": 85.0, "DM3": 95.0}
        consensus = ConsensusMeasure.compute_criterion_consensus(
            scores, method="standard_deviation"
        )
        # 标准差 ≈ 8.16, 共识度 = 1 - 8.16/50 ≈ 0.837
        assert consensus == pytest.approx(0.837, rel=1e-2)

    def test_compute_criterion_consensus_coefficient_of_variation(self):
        """测试变异系数法计算准则共识度"""
        scores = {"DM1": 80.0, "DM2": 85.0, "DM3": 90.0}
        consensus = ConsensusMeasure.compute_criterion_consensus(
            scores, method="coefficient_of_variation"
        )
        # 变异系数 ≈ 0.048, 共识度 = 1 - 0.048 ≈ 0.952
        assert 0 < consensus <= 1.0

    def test_compute_criterion_consensus_agreement_rate(self):
        """测试同意率法计算准则共识度"""
        scores = {"DM1": 80.0, "DM2": 85.0, "DM3": 90.0}
        consensus = ConsensusMeasure.compute_criterion_consensus(
            scores, method="agreement_rate"
        )
        assert 0 <= consensus <= 1.0

    def test_compute_criterion_consensus_invalid_method_raises_error(self):
        """测试无效方法抛出异常"""
        scores = {"DM1": 85.0, "DM2": 85.0}
        with pytest.raises(ValueError, match="未知的共识度计算方法"):
            ConsensusMeasure.compute_criterion_consensus(scores, method="invalid")

    def test_compute_criterion_consensus_single_decision_maker(self):
        """测试单个决策者的共识度为 1"""
        scores = {"DM1": 85.0}
        consensus = ConsensusMeasure.compute_criterion_consensus(scores)
        assert consensus == 1.0


class TestConsensusResult:
    """测试共识度结果"""

    def test_create_valid_consensus_result(self):
        """测试创建有效的共识度结果"""
        result = ConsensusResult(
            overall_consensus=0.85,
            criterion_consensus={"成本": 0.8, "质量": 0.9},
            decision_maker_distances={},
            threshold_reached=True
        )

        assert result.overall_consensus == 0.85
        assert result.criterion_consensus == {"成本": 0.8, "质量": 0.9}
        assert result.threshold_reached is True

    def test_consensus_result_overall_out_of_range_high_raises_error(self):
        """测试整体共识度超出上限抛出异常"""
        with pytest.raises(ValueError, match="overall_consensus.*必须在 0-1 范围内"):
            ConsensusResult(
                overall_consensus=1.5,
                criterion_consensus={},
                decision_maker_distances={},
                threshold_reached=False
            )

    def test_consensus_result_overall_out_of_range_low_raises_error(self):
        """测试整体共识度超出下限抛出异常"""
        with pytest.raises(ValueError, match="overall_consensus.*必须在 0-1 范围内"):
            ConsensusResult(
                overall_consensus=-0.1,
                criterion_consensus={},
                decision_maker_distances={},
                threshold_reached=False
            )

    def test_consensus_result_criterion_out_of_range_raises_error(self):
        """测试准则共识度超出范围抛出异常"""
        with pytest.raises(ValueError, match="criterion_consensus.*必须在 0-1 范围内"):
            ConsensusResult(
                overall_consensus=0.8,
                criterion_consensus={"成本": 1.5},
                decision_maker_distances={},
                threshold_reached=False
            )

    def test_consensus_result_immutability(self):
        """测试共识度结果不可变性"""
        result = ConsensusResult(
            overall_consensus=0.85,
            criterion_consensus={},
            decision_maker_distances={},
            threshold_reached=True
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            result.overall_consensus = 0.9


class TestComputeConsensus:
    """测试完整共识度计算"""

    @pytest.fixture
    def sample_problem(self):
        """创建示例群决策问题"""
        criteria = (
            Criterion(name="成本", weight=0.5, direction="lower_better"),
            Criterion(name="质量", weight=0.5, direction="higher_better"),
        )
        decision_makers = (
            DecisionMaker(id="DM1", name="张三"),
            DecisionMaker(id="DM2", name="李四"),
        )
        individual_scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 85.0},
                "Azure": {"成本": 75.0, "质量": 90.0},
            },
        }

        return GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=individual_scores
        )

    def test_compute_consensus_returns_valid_result(self, sample_problem):
        """测试共识度计算返回有效结果"""
        measure = ConsensusMeasure()
        result = measure.compute_consensus(
            individual_scores=sample_problem.individual_scores,
            alternatives=sample_problem.alternatives,
            criteria=sample_problem.criteria,
            threshold=0.7
        )

        assert isinstance(result, ConsensusResult)
        assert 0 <= result.overall_consensus <= 1.0
        assert isinstance(result.threshold_reached, bool)

    def test_compute_consensus_with_high_agreement(self):
        """测试高同意率的共识度计算"""
        criteria = (
            Criterion(name="成本", weight=0.5, direction="lower_better"),
            Criterion(name="质量", weight=0.5, direction="higher_better"),
        )
        # 评分非常接近
        individual_scores = {
            "DM1": {
                "AWS": {"成本": 85.0, "质量": 85.0},
                "Azure": {"成本": 80.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 86.0, "质量": 84.0},
                "Azure": {"成本": 81.0, "质量": 86.0},
            },
        }

        measure = ConsensusMeasure()
        result = measure.compute_consensus(
            individual_scores=individual_scores,
            alternatives=("AWS", "Azure"),
            criteria=criteria,
            threshold=0.7
        )

        # 高同意率应该产生较高的共识度
        assert result.overall_consensus > 0.7

    def test_compute_consensus_includes_distances(self, sample_problem):
        """测试共识度计算包含决策者距离"""
        measure = ConsensusMeasure()
        result = measure.compute_consensus(
            individual_scores=sample_problem.individual_scores,
            alternatives=sample_problem.alternatives,
            criteria=sample_problem.criteria,
            threshold=0.7
        )

        # 应该包含决策者距离
        assert "DM1" in result.decision_maker_distances
        assert "DM2" in result.decision_maker_distances
        # 距离是对称的
        assert result.decision_maker_distances["DM1"]["DM2"] == \
            result.decision_maker_distances["DM2"]["DM1"]
        # 自己到自己的距离为 0
        assert result.decision_maker_distances["DM1"]["DM1"] == 0.0
