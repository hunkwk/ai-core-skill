"""
MCDA Core - GroupDecisionProblem 数据模型单元测试

测试群决策问题数据模型的创建、验证和功能。
"""

import pytest

from mcda_core.group.models import (
    DecisionMaker,
    GroupDecisionProblem,
    AggregationConfig,
)
from mcda_core.models import Criterion


class TestGroupDecisionProblem:
    """测试 GroupDecisionProblem 数据模型"""

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

    def test_create_valid_group_decision_problem(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试创建有效的群决策问题"""
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

        assert len(problem.alternatives) == 2
        assert len(problem.criteria) == 3
        assert len(problem.decision_makers) == 3
        assert problem.aggregation_config is None

    def test_group_decision_problem_with_aggregation_config(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试带聚合配置的群决策问题"""
        config = AggregationConfig(
            score_aggregation="weighted_average",
            consensus_strategy="threshold",
            consensus_threshold=0.7
        )
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores,
            aggregation_config=config
        )

        assert problem.aggregation_config is not None
        assert problem.aggregation_config.score_aggregation == "weighted_average"
        assert problem.aggregation_config.consensus_threshold == 0.7

    def test_less_than_2_alternatives_raises_error(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试少于 2 个备选方案抛出异常"""
        with pytest.raises(ValueError, match="至少需要 2 个备选方案"):
            GroupDecisionProblem(
                alternatives=("AWS",),
                criteria=sample_criteria,
                decision_makers=sample_decision_makers,
                individual_scores=sample_individual_scores
            )

    def test_less_than_1_criterion_raises_error(
        self, sample_decision_makers, sample_individual_scores
    ):
        """测试少于 1 个准则抛出异常"""
        with pytest.raises(ValueError, match="至少需要 1 个评价准则"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=(),
                decision_makers=sample_decision_makers,
                individual_scores=sample_individual_scores
            )

    def test_less_than_2_decision_makers_raises_error(
        self, sample_criteria, sample_individual_scores
    ):
        """测试少于 2 个决策者抛出异常"""
        with pytest.raises(ValueError, match="至少需要 2 个决策者"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=(DecisionMaker(id="DM1", name="张三"),),
                individual_scores=sample_individual_scores
            )

    def test_duplicate_decision_maker_ids_raises_error(
        self, sample_criteria, sample_individual_scores
    ):
        """测试重复决策者 ID 抛出异常"""
        duplicate_dms = (
            DecisionMaker(id="DM1", name="张三"),
            DecisionMaker(id="DM1", name="李四"),  # 重复 ID
        )
        with pytest.raises(ValueError, match="决策者 ID 必须唯一"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=duplicate_dms,
                individual_scores=sample_individual_scores
            )

    def test_missing_decision_maker_scores_raises_error(
        self, sample_criteria, sample_decision_makers
    ):
        """测试缺少决策者评分抛出异常"""
        incomplete_scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0},
            },
            # 缺少 DM2 和 DM3 的评分
        }
        with pytest.raises(ValueError, match="缺少决策者 'DM2' 的评分"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=sample_decision_makers,
                individual_scores=incomplete_scores
            )

    def test_extra_decision_maker_in_scores_raises_error(
        self, sample_criteria, sample_decision_makers
    ):
        """测试评分中存在未定义的决策者抛出异常"""
        extra_scores = {
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
            "DM4": {  # 未定义的决策者
                "AWS": {"成本": 70.0, "质量": 80.0, "技术": 75.0},
                "Azure": {"成本": 65.0, "质量": 85.0, "技术": 70.0},
            },
        }
        with pytest.raises(ValueError, match="评分中存在未定义的决策者 'DM4'"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=sample_decision_makers,
                individual_scores=extra_scores
            )

    def test_missing_alternative_scores_raises_error(
        self, sample_criteria, sample_decision_makers
    ):
        """测试缺少方案评分抛出异常"""
        incomplete_scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                # 缺少 Azure 的评分
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
        with pytest.raises(ValueError, match="决策者 'DM1' 缺少方案 'Azure' 的评分"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=sample_decision_makers,
                individual_scores=incomplete_scores
            )

    def test_invalid_score_type_raises_error(
        self, sample_criteria, sample_decision_makers
    ):
        """测试无效评分类型抛出异常"""
        invalid_scores = {
            "DM1": {
                "AWS": {"成本": "高", "质量": 90.0, "技术": 85.0},  # 字符串
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
        with pytest.raises(ValueError, match="评分必须是数值类型"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=sample_decision_makers,
                individual_scores=invalid_scores
            )

    def test_score_out_of_range_raises_error(
        self, sample_criteria, sample_decision_makers
    ):
        """测试评分超出范围抛出异常"""
        out_of_range_scores = {
            "DM1": {
                "AWS": {"成本": 150.0, "质量": 90.0, "技术": 85.0},  # 超出 100
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
        with pytest.raises(ValueError, match="评分必须在 0-100 范围内"):
            GroupDecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria,
                decision_makers=sample_decision_makers,
                individual_scores=out_of_range_scores
            )

    def test_get_decision_maker(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试获取指定决策者"""
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

        dm = problem.get_decision_maker("DM2")
        assert dm is not None
        assert dm.id == "DM2"
        assert dm.name == "李四"

        # 测试不存在的决策者
        dm = problem.get_decision_maker("DM999")
        assert dm is None

    def test_get_decision_maker_weights(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试获取决策者权重"""
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

        weights = problem.get_decision_maker_weights()
        assert weights == {"DM1": 1.0, "DM2": 1.0, "DM3": 0.5}

    def test_problem_immutability(
        self, sample_criteria, sample_decision_makers, sample_individual_scores
    ):
        """测试群决策问题不可变性"""
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria,
            decision_makers=sample_decision_makers,
            individual_scores=sample_individual_scores
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            problem.alternatives = ("AWS", "Azure", "GCP")

    def test_three_decision_makers_three_alternatives(
        self, sample_criteria
    ):
        """测试三个决策者和三个备选方案的场景"""
        dms = (
            DecisionMaker(id="DM1", name="张三"),
            DecisionMaker(id="DM2", name="李四"),
            DecisionMaker(id="DM3", name="王五"),
        )
        scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0, "技术": 85.0},
                "Azure": {"成本": 70.0, "质量": 85.0, "技术": 80.0},
                "GCP": {"成本": 75.0, "质量": 80.0, "技术": 90.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 80.0, "技术": 90.0},
                "Azure": {"成本": 75.0, "质量": 90.0, "技术": 85.0},
                "GCP": {"成本": 80.0, "质量": 85.0, "技术": 80.0},
            },
            "DM3": {
                "AWS": {"成本": 75.0, "质量": 85.0, "技术": 80.0},
                "Azure": {"成本": 80.0, "质量": 80.0, "技术": 75.0},
                "GCP": {"成本": 85.0, "质量": 90.0, "技术": 85.0},
            },
        }

        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=sample_criteria,
            decision_makers=dms,
            individual_scores=scores
        )

        assert len(problem.alternatives) == 3
        assert len(problem.decision_makers) == 3
