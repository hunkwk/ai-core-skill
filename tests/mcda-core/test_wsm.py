"""
MCDA Core - WSM 算法测试

测试加权算术平均模型（Weighted Sum Model）。
"""

import pytest
import math
from skills.mcda_core.lib.models import (
    Criterion,
    Direction,
)
from skills.mcda_core.lib.algorithms.wsm import WSMAlgorithm


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
        criteria=tuple(sample_criteria),
        scores=sample_scores,
    )


# =============================================================================
# WSM Algorithm Tests
# =============================================================================

class TestWSMAlgorithm:
    """WSM 算法测试"""

    def test_wsm_basic_calculation(self, sample_problem):
        """测试 WSM 基本计算"""
        algorithm = WSMAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证排名存在
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证分数计算（手动计算期望值）
        # AWS: 0.4*85 + 0.3*(100-60) + 0.2*90 + 0.1*80
        #     = 34.0 + 12.0 + 18.0 + 8.0 = 72.0
        # Azure: 0.4*92 + 0.3*(100-50) + 0.2*85 + 0.1*85
        #       = 36.8 + 15.0 + 17.0 + 8.5 = 77.3
        # GCP: 0.4*88 + 0.3*(100-70) + 0.2*80 + 0.1*75
        #     = 35.2 + 9.0 + 16.0 + 7.5 = 67.7

        expected_scores = {
            "AWS": 72.0,
            "Azure": 77.3,
            "GCP": 67.7,
        }

        for alt, expected_score in expected_scores.items():
            actual_score = result.raw_scores[alt]
            assert abs(actual_score - expected_score) < 0.01, \
                f"{alt}: 期望 {expected_score}, 实际 {actual_score}"

        # 验证排名：Azure > AWS > GCP
        assert result.rankings[0].alternative == "Azure"
        assert result.rankings[0].rank == 1
        assert result.rankings[1].alternative == "AWS"
        assert result.rankings[1].rank == 2
        assert result.rankings[2].alternative == "GCP"
        assert result.rankings[2].rank == 3

    def test_wsm_all_higher_better(self):
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
            criteria=tuple(criteria),
            scores=scores,
        )

        algorithm = WSMAlgorithm()
        result = algorithm.calculate(problem)

        # A: 0.5*90 + 0.5*80 = 85.0
        # B: 0.5*70 + 0.5*95 = 82.5
        assert result.raw_scores["A"] == pytest.approx(85.0)
        assert result.raw_scores["B"] == pytest.approx(82.5)
        assert result.rankings[0].alternative == "A"

    def test_wsm_all_lower_better(self):
        """测试所有准则都是 lower_better"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="成本", weight=0.6, direction="lower_better"),
            Criterion(name="延迟", weight=0.4, direction="lower_better"),
        ]

        scores = {
            "A": {"成本": 80.0, "延迟": 60.0},
            "B": {"成本": 50.0, "延迟": 90.0},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=tuple(criteria),
            scores=scores,
        )

        algorithm = WSMAlgorithm()
        result = algorithm.calculate(problem)

        # A: 0.6*(100-80) + 0.4*(100-60) = 12.0 + 16.0 = 28.0
        # B: 0.6*(100-50) + 0.4*(100-90) = 30.0 + 4.0 = 34.0
        assert result.raw_scores["A"] == pytest.approx(28.0)
        assert result.raw_scores["B"] == pytest.approx(34.0)
        assert result.rankings[0].alternative == "B"

    def test_wsm_metadata(self, sample_problem):
        """测试元数据"""
        algorithm = WSMAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert result.metadata.algorithm_name == "wsm"
        assert result.metadata.problem_size == (3, 4)  # 3 个备选方案，4 个准则

    def test_wsm_metrics(self, sample_problem):
        """测试算法指标"""
        algorithm = WSMAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert "weighted_sums" in result.metadata.metrics
        assert isinstance(result.metadata.metrics["weighted_sums"], dict)

        # 验证指标分数与 raw_scores 一致
        for alt in sample_problem.alternatives:
            assert alt in result.metadata.metrics["weighted_sums"]
            assert result.metadata.metrics["weighted_sums"][alt] == \
                pytest.approx(result.raw_scores[alt])


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestWSMEdgeCases:
    """WSM 边界情况测试"""

    def test_wsm_two_alternatives(self):
        """测试只有 2 个备选方案"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 80.0, "成本": 60.0},
            "B": {"性能": 90.0, "成本": 70.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = WSMAlgorithm()
        result = algorithm.calculate(problem)

        assert len(result.rankings) == 2
        assert set(result.raw_scores.keys()) == {"A", "B"}

    def test_wsm_many_alternatives(self):
        """测试多个备选方案"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            f"方案{i}": {"性能": float(i * 10)}
            for i in range(1, 11)  # 10 个方案
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = WSMAlgorithm()
        result = algorithm.calculate(problem)

        assert len(result.rankings) == 10
        # 验证排名正确（性能越高越好）
        assert result.rankings[0].alternative == "方案10"
        assert result.rankings[-1].alternative == "方案1"

    def test_wsm_zero_scores(self):
        """测试零值评分"""
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

        algorithm = WSMAlgorithm()
        result = algorithm.calculate(problem)

        # A: 0.5*0 + 0.5*(100-50) = 0 + 25 = 25
        # B: 0.5*50 + 0.5*(100-100) = 25 + 0 = 25
        # 两者应该相等
        assert abs(result.raw_scores["A"] - result.raw_scores["B"]) < 0.01

    def test_wsm_equal_weights(self):
        """测试所有权重相等"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.25, direction="higher_better"),
            Criterion(name="成本", weight=0.25, direction="lower_better"),
            Criterion(name="可靠性", weight=0.25, direction="higher_better"),
            Criterion(name="易用性", weight=0.25, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": 80.0, "成本": 60.0, "可靠性": 70.0, "易用性": 75.0},
            "B": {"性能": 85.0, "成本": 55.0, "可靠性": 75.0, "易用性": 70.0},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=tuple(criteria),
            scores=scores,
        )

        algorithm = WSMAlgorithm()
        result = algorithm.calculate(problem)

        # 计算简单平均值应该得到相同结果
        # A: 0.25*80 + 0.25*(100-60) + 0.25*70 + 0.25*75 = 20 + 10 + 17.5 + 18.75 = 66.25
        # B: 0.25*85 + 0.25*(100-55) + 0.25*75 + 0.25*70 = 21.25 + 11.25 + 18.75 + 17.5 = 68.75
        assert result.raw_scores["A"] == pytest.approx(66.25)
        assert result.raw_scores["B"] == pytest.approx(68.75)


# =============================================================================
# Property Tests
# =============================================================================

class TestWSMProperties:
    """WSM 算法属性测试"""

    def test_wsm_algorithm_name(self):
        """测试算法名称"""
        algorithm = WSMAlgorithm()
        assert algorithm.name == "wsm"

    def test_wsm_description(self):
        """测试算法描述"""
        algorithm = WSMAlgorithm()
        assert len(algorithm.description) > 0
        assert "加权" in algorithm.description or "Weighted" in algorithm.description
