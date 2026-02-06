"""
MCDA Core - 群决策服务单元测试

测试群决策分析服务的功能。
"""

import pytest

from mcda_core.group.service import GroupDecisionService
from mcda_core.group.models import (
    DecisionMaker,
    GroupDecisionProblem,
    AggregationConfig,
)
from mcda_core.models import Criterion, DecisionProblem


class TestGroupDecisionService:
    """测试群决策服务"""

    @pytest.fixture
    def service(self):
        """创建群决策服务实例"""
        return GroupDecisionService()

    @pytest.fixture
    def sample_criteria(self):
        """创建示例准则"""
        return (
            Criterion(name="成本", weight=0.4, direction="lower_better"),
            Criterion(name="质量", weight=0.3, direction="higher_better"),
            Criterion(name="技术", weight=0.3, direction="higher_better"),
        )

    @pytest.fixture
    def sample_decision_makers(self):
        """创建示例决策者"""
        return (
            DecisionMaker(id="DM1", name="张三", weight=1.0),
            DecisionMaker(id="DM2", name="李四", weight=1.0),
            DecisionMaker(id="DM3", name="王五", weight=0.5),
        )

    @pytest.fixture
    def sample_individual_scores(self):
        """创建示例个人评分"""
        return {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 80.0, "技术": 90.0},
                "Azure": {"成本": 75.0, "质量": 90.0, "技术": 85.0},
            },
            "DM3": {
                "AWS": {"成本": 75.0, "质量": 85.0, "技术": 80.0},
                "Azure": {"成本": 80.0, "质量": 80.0, "技术": 75.0},
            },
        }

    @pytest.fixture
    def sample_problem(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """创建示例群决策问题"""
        return GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

    def test_aggregate_scores_returns_aggregated_matrix(
        self, service, sample_problem
    ):
        """测试评分聚合返回聚合后的评分矩阵"""
        result = service.aggregate_scores(sample_problem)

        assert "AWS" in result
        assert "Azure" in result
        assert "成本" in result["AWS"]
        assert "质量" in result["AWS"]
        assert "技术" in result["AWS"]

    def test_aggregate_scores_with_equal_weights(
        self, service, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试等权重聚合"""
        # 修改为等权重
        dms = (
            DecisionMaker(id="DM1", name="张三", weight=1.0),
            DecisionMaker(id="DM2", name="李四", weight=1.0),
        )
        scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 90.0, "质量": 80.0},
                "Azure": {"成本": 80.0, "质量": 90.0},
            },
        }
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            decision_makers=dms,
            individual_scores=scores
        )

        result = service.aggregate_scores(problem)

        # AWS 成本: (80 + 90) / 2 = 85
        assert result["AWS"]["成本"] == pytest.approx(85.0)
        # AWS 质量: (90 + 80) / 2 = 85
        assert result["AWS"]["质量"] == pytest.approx(85.0)

    def test_aggregate_scores_with_custom_weights(
        self, service, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试自定义权重聚合"""
        # DM1 权重 0.6, DM2 权重 0.4
        dms = (
            DecisionMaker(id="DM1", name="张三", weight=0.6),
            DecisionMaker(id="DM2", name="李四", weight=0.4),
        )
        scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 90.0, "质量": 80.0},
                "Azure": {"成本": 80.0, "质量": 90.0},
            },
        }
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            decision_makers=dms,
            individual_scores=scores
        )

        result = service.aggregate_scores(problem)

        # AWS 成本: 0.6*80 + 0.4*90 = 48 + 36 = 84
        assert result["AWS"]["成本"] == pytest.approx(84.0)
        # AWS 质量: 0.6*90 + 0.4*80 = 54 + 32 = 86
        assert result["AWS"]["质量"] == pytest.approx(86.0)

    def test_aggregate_scores_with_config_method(
        self, service, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试使用配置中的聚合方法"""
        config = AggregationConfig(score_aggregation="weighted_average")
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            decision_makers=sample_decision_makers[:2],
            individual_scores={
                "DM1": {
                    "AWS": {"成本": 80.0, "质量": 90.0},
                    "Azure": {"成本": 70.0, "质量": 85.0},
                },
                "DM2": {
                    "AWS": {"成本": 90.0, "质量": 80.0},
                    "Azure": {"成本": 80.0, "质量": 90.0},
                },
            },
            aggregation_config=config
        )

        result = service.aggregate_scores(problem)
        assert "AWS" in result
        assert "Azure" in result

    def test_compute_consensus_returns_consensus_result(
        self, service, sample_problem
    ):
        """测试共识度计算返回共识度结果"""
        result = service.compute_consensus(sample_problem)

        assert hasattr(result, "overall_consensus")
        assert hasattr(result, "criterion_consensus")
        assert hasattr(result, "threshold_reached")
        assert 0 <= result.overall_consensus <= 1.0

    def test_compute_consensus_with_custom_threshold(
        self, service, sample_problem
    ):
        """测试自定义共识阈值"""
        result = service.compute_consensus(sample_problem, threshold=0.8)

        # 结果应包含阈值判断
        assert isinstance(result.threshold_reached, bool)

    def test_compute_consensus_with_custom_method(
        self, service, sample_problem
    ):
        """测试自定义共识度计算方法"""
        result = service.compute_consensus(sample_problem, method="agreement_rate")

        assert result.overall_consensus >= 0

    def test_to_decision_problem_returns_valid_problem(
        self, service, sample_problem
    ):
        """测试转换为单决策者问题"""
        decision_problem = service.to_decision_problem(sample_problem)

        assert isinstance(decision_problem, DecisionProblem)
        assert decision_problem.alternatives == sample_problem.alternatives
        assert len(decision_problem.criteria) == len(sample_problem.criteria)
        assert decision_problem.scores is not None

    def test_to_decision_problem_with_custom_method(
        self, service, sample_problem
    ):
        """测试使用自定义聚合方法转换"""
        decision_problem = service.to_decision_problem(
            sample_problem,
            aggregation_method="weighted_average"
        )

        assert isinstance(decision_problem, DecisionProblem)
        assert "AWS" in decision_problem.scores
        assert "Azure" in decision_problem.scores

    def test_analyze_returns_both_results(
        self, service, sample_problem
    ):
        """测试分析返回聚合评分和共识度结果"""
        aggregated, consensus = service.analyze(sample_problem)

        assert isinstance(aggregated, dict)
        assert consensus is not None

    def test_analyze_without_consensus_check(
        self, service, sample_problem
    ):
        """测试不检查共识度的分析"""
        aggregated, consensus = service.analyze(
            sample_problem,
            check_consensus=False
        )

        assert isinstance(aggregated, dict)
        assert consensus is None

    def test_aggregate_scores_three_decision_makers(
        self, service, sample_problem
    ):
        """测试三个决策者的评分聚合"""
        result = service.aggregate_scores(sample_problem)

        # 验证结果结构
        for alt in ["AWS", "Azure"]:
            assert alt in result
            for crit in ["成本", "质量", "技术"]:
                assert crit in result[alt]
                # 验证评分在合理范围内
                assert 0 <= result[alt][crit] <= 100

    def test_aggregate_scores_with_zero_weight_decision_maker(
        self, service, sample_criteria
    ):
        """测试包含零权重决策者的聚合"""
        dms = (
            DecisionMaker(id="DM1", name="张三", weight=1.0),
            DecisionMaker(id="DM2", name="李四", weight=0.0),  # 零权重
        )
        scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 0.0, "质量": 0.0},  # 评分不影响结果
                "Azure": {"成本": 0.0, "质量": 0.0},
            },
        }
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            decision_makers=dms,
            individual_scores=scores
        )

        result = service.aggregate_scores(problem)

        # 零权重决策者的评分不影响结果
        # AWS 成本: 1.0*80 / 1.0 = 80
        assert result["AWS"]["成本"] == pytest.approx(80.0)

    def test_compute_consensus_with_config_threshold(
        self, service, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试使用配置中的共识阈值"""
        config = AggregationConfig(
            score_aggregation="weighted_average",
            consensus_strategy="threshold",
            consensus_threshold=0.8
        )
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            decision_makers=sample_decision_makers[:2],
            individual_scores={
                "DM1": {
                    "AWS": {"成本": 80.0, "质量": 90.0},
                    "Azure": {"成本": 70.0, "质量": 85.0},
                },
                "DM2": {
                    "AWS": {"成本": 85.0, "质量": 85.0},
                    "Azure": {"成本": 75.0, "质量": 90.0},
                },
            },
            aggregation_config=config
        )

        result = service.compute_consensus(problem)

        # 应使用配置中的阈值 0.8
        assert isinstance(result.threshold_reached, bool)

    def test_to_decision_problem_has_valid_scores(
        self, service, sample_problem
    ):
        """测试转换后的问题有有效的评分"""
        decision_problem = service.to_decision_problem(sample_problem)

        # 验证评分矩阵结构
        for alt in sample_problem.alternatives:
            assert alt in decision_problem.scores
            for crit in sample_problem.criteria:
                crit_name = crit.name if hasattr(crit, 'name') else str(crit)
                assert crit_name in decision_problem.scores[alt]
