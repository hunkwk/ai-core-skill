"""
MCDA Core - WPM 算法测试

测试加权几何平均模型（Weighted Product Model）。
"""

import pytest
import math
from skills.mcda_core.lib.models import (
    Criterion,
    Direction,
)
from skills.mcda_core.lib.algorithms.wpm import WPMAlgorithm


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_criteria():
    """示例准则（权重已归一化）"""
    return [
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        Criterion(name="易用性", weight=0.1, direction="higher_better"),
    ]


@pytest.fixture
def sample_scores():
    """示例评分（已标准化到 0-100）"""
    return {
        "AWS": {"性能": 85.0, "成本": 60.0, "可靠性": 90.0, "易用性": 80.0},
        "Azure": {"性能": 92.0, "成本": 50.0, "可靠性": 85.0, "易用性": 85.0},
        "GCP": {"性能": 88.0, "成本": 70.0, "可靠性": 80.0, "易用性": 75.0},
    }


@pytest.fixture
def sample_problem(sample_criteria, sample_scores):
    """创建示例决策问题"""
    from skills.mcda_core.lib.models import DecisionProblem

    return DecisionProblem(
        
        alternatives=tuple(sample_scores.keys()),
        criteria=sample_criteria,
        scores=sample_scores,
    )


# =============================================================================
# WPM Algorithm Tests
# =============================================================================

class TestWPMAlgorithm:
    """WPM 算法测试"""

    def test_wpm_basic_calculation(self, sample_problem):
        """测试 WPM 基本计算"""
        algorithm = WPMAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证排名存在
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证分数计算（手动计算期望值）
        # AWS: 85^0.4 * 40^0.3 * 90^0.2 * 80^0.1
        # Azure: 92^0.4 * 50^0.3 * 85^0.2 * 85^0.1
        # GCP: 88^0.4 * 30^0.3 * 80^0.2 * 75^0.1
        # 注意：成本方向反转 (100 - cost)

        import math
        expected_aws = (85 ** 0.4) * (40 ** 0.3) * (90 ** 0.2) * (80 ** 0.1)
        expected_azure = (92 ** 0.4) * (50 ** 0.3) * (85 ** 0.2) * (85 ** 0.1)
        expected_gcp = (88 ** 0.4) * (30 ** 0.3) * (80 ** 0.2) * (75 ** 0.1)

        assert abs(result.raw_scores["AWS"] - expected_aws) < 0.1
        assert abs(result.raw_scores["Azure"] - expected_azure) < 0.1
        assert abs(result.raw_scores["GCP"] - expected_gcp) < 0.1

        # 验证排名顺序
        assert result.rankings[0].alternative == "Azure"
        assert result.rankings[0].rank == 1
        assert result.rankings[1].alternative in ["AWS", "GCP"]
        assert result.rankings[2].alternative in ["AWS", "GCP"]

    def test_wpm_all_higher_better(self):
        """测试所有准则都是 higher_better"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="可靠性", weight=0.5, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": 90.0, "可靠性": 80.0},
            "B": {"性能": 70.0, "可靠性": 95.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = WPMAlgorithm()
        result = algorithm.calculate(problem)

        # A: 90^0.5 * 80^0.5 = 84.85
        # B: 70^0.5 * 95^0.5 = 81.54
        assert result.raw_scores["A"] == pytest.approx(84.85, abs=0.1)
        assert result.raw_scores["B"] == pytest.approx(81.54, abs=0.1)
        assert result.rankings[0].alternative == "A"

    def test_wpm_metadata(self, sample_problem):
        """测试元数据"""
        algorithm = WPMAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert result.metadata.algorithm_name == "wpm"
        assert result.metadata.problem_size == (3, 4)

    def test_wpm_metrics(self, sample_problem):
        """测试算法指标"""
        algorithm = WPMAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert "products" in result.metadata.metrics
        assert isinstance(result.metadata.metrics["products"], dict)

        # 验证指标分数与 raw_scores 一致
        for alt in sample_problem.alternatives:
            assert alt in result.metadata.metrics["products"]
            assert result.metadata.metrics["products"][alt] == \
                pytest.approx(result.raw_scores[alt])


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestWPMEdgeCases:
    """WPM 边界情况测试"""

    def test_wpm_zero_value_handling(self):
        """测试零值处理（应该加小常数避免）"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 0.0, "成本": 50.0},
            "B": {"性能": 50.0, "成本": 100.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = WPMAlgorithm()
        result = algorithm.calculate(problem)

        # 零值应该被处理（加小常数）
        # 不应该抛出异常或返回 inf/nan
        assert result.raw_scores["A"] > 0
        assert result.raw_scores["B"] > 0
        assert not math.isinf(result.raw_scores["A"])
        assert not math.isinf(result.raw_scores["B"])
        assert not math.isnan(result.raw_scores["A"])
        assert not math.isnan(result.raw_scores["B"])

    def test_wpm_small_values(self):
        """测试小数值"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": 1.0},
            "B": {"性能": 10.0},
            "C": {"性能": 100.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = WPMAlgorithm()
        result = algorithm.calculate(problem)

        # 验证排名：C > B > A
        assert result.rankings[0].alternative == "C"
        assert result.rankings[1].alternative == "B"
        assert result.rankings[2].alternative == "A"

    def test_wpm_equal_weights(self):
        """测试所有权重相等"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 80.0, "成本": 60.0},
            "B": {"性能": 85.0, "成本": 55.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = WPMAlgorithm()
        result = algorithm.calculate(problem)

        # A: 80^0.5 * 40^0.5 = 56.57
        # B: 85^0.5 * 45^0.5 = 61.85
        assert result.raw_scores["A"] == pytest.approx(56.57, abs=0.1)
        assert result.raw_scores["B"] == pytest.approx(61.85, abs=0.1)
        assert result.rankings[0].alternative == "B"


# =============================================================================
# Property Tests
# =============================================================================

class TestWPMProperties:
    """WPM 算法属性测试"""

    def test_wpm_algorithm_name(self):
        """测试算法名称"""
        algorithm = WPMAlgorithm()
        assert algorithm.name == "wpm"

    def test_wpm_description(self):
        """测试算法描述"""
        algorithm = WPMAlgorithm()
        assert len(algorithm.description) > 0
        assert "几何" in algorithm.description or "Product" in algorithm.description
