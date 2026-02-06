"""
MCDA Core - TOPSIS 算法测试

测试逼近理想解排序法（Technique for Order Preference by Similarity to Ideal Solution）。
"""

import pytest
import math
from mcda_core.models import (
    Criterion,
    Direction,
)
from mcda_core.algorithms.topsis import TOPSISAlgorithm


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
    """示例评分（原始数据，未标准化）"""
    return {
        "AWS": {"性能": 85.0, "成本": 60.0, "可靠性": 90.0, "易用性": 80.0},
        "Azure": {"性能": 92.0, "成本": 50.0, "可靠性": 85.0, "易用性": 85.0},
        "GCP": {"性能": 88.0, "成本": 70.0, "可靠性": 80.0, "易用性": 75.0},
    }


@pytest.fixture
def sample_problem(sample_criteria, sample_scores):
    """创建示例决策问题"""
    from mcda_core.models import DecisionProblem

    return DecisionProblem(

        alternatives=tuple(sample_scores.keys()),
        criteria=sample_criteria,
        scores=sample_scores,
    )


# =============================================================================
# TOPSIS Algorithm Tests
# =============================================================================

class TestTOPSISAlgorithm:
    """TOPSIS 算法测试"""

    def test_topsis_basic_calculation(self, sample_problem):
        """测试 TOPSIS 基本计算"""
        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证排名存在
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证相对接近度在 [0, 1] 范围内
        for alt, score in result.raw_scores.items():
            assert 0 <= score <= 1, f"{alt} 的接近度 {score} 不在 [0, 1] 范围内"

        # 验证排名
        assert result.rankings[0].rank == 1
        assert result.rankings[1].rank == 2
        assert result.rankings[2].rank == 3

    def test_topsis_closeness_coefficient(self, sample_problem):
        """测试相对接近度计算"""
        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证相对接近度计算公式：C = D^- / (D^+ + D^-)
        d_plus = result.metadata.metrics["d_plus"]
        d_minus = result.metadata.metrics["d_minus"]

        for alt in sample_problem.alternatives:
            expected_c = d_minus[alt] / (d_plus[alt] + d_minus[alt])
            actual_c = result.raw_scores[alt]

            assert abs(actual_c - expected_c) < 0.001, \
                f"{alt}: 接近度计算错误"

    def test_topsis_distance_calculation(self, sample_problem):
        """测试距离计算"""
        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证距离存在且为正数
        d_plus = result.metadata.metrics["d_plus"]
        d_minus = result.metadata.metrics["d_minus"]

        for alt in sample_problem.alternatives:
            assert alt in d_plus
            assert alt in d_minus
            assert d_plus[alt] >= 0
            assert d_minus[alt] >= 0

            # D^- 应该大于等于 D^+（因为越接近负理想解，D^- 越大）
            # 但这不是绝对规则，因为取决于标准化后的数据分布

    def test_topsis_metadata(self, sample_problem):
        """测试元数据"""
        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert result.metadata.algorithm_name == "topsis"
        assert result.metadata.problem_size == (3, 4)

    def test_topsis_metrics(self, sample_problem):
        """测试算法指标"""
        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证指标包含
        assert "closeness" in result.metadata.metrics
        assert "d_plus" in result.metadata.metrics
        assert "d_minus" in result.metadata.metrics

        # 验证指标类型
        assert isinstance(result.metadata.metrics["closeness"], dict)
        assert isinstance(result.metadata.metrics["d_plus"], dict)
        assert isinstance(result.metadata.metrics["d_minus"], dict)


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestTOPSISEdgeCases:
    """TOPSIS 边界情况测试"""

    def test_topsis_two_alternatives(self):
        """测试只有 2 个备选方案"""
        from mcda_core.models import DecisionProblem

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

        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(problem)

        assert len(result.rankings) == 2
        assert set(result.raw_scores.keys()) == {"A", "B"}

        # 验证接近度在 [0, 1]
        for score in result.raw_scores.values():
            assert 0 <= score <= 1

    def test_topsis_many_alternatives(self):
        """测试多个备选方案"""
        from mcda_core.models import DecisionProblem

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

        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(problem)

        assert len(result.rankings) == 10
        # 验证排名正确（性能越高越好）
        assert result.rankings[0].alternative == "方案10"
        assert result.rankings[-1].alternative == "方案1"

    def test_topsis_equal_scores(self):
        """测试所有方案评分相同"""
        from mcda_core.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 80.0, "成本": 60.0},
            "B": {"性能": 80.0, "成本": 60.0},
        }

        problem = DecisionProblem(

            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(problem)

        # 所有方案应该有相同的接近度（距离理想解和负理想解相同）
        assert abs(result.raw_scores["A"] - result.raw_scores["B"]) < 0.001

    def test_topsis_single_criterion(self):
        """测试单个准则"""
        from mcda_core.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": 80.0},
            "B": {"性能": 90.0},
            "C": {"性能": 85.0},
        }

        problem = DecisionProblem(

            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = TOPSISAlgorithm()
        result = algorithm.calculate(problem)

        # 最高分应该排名第一
        assert result.rankings[0].alternative == "B"
        assert result.raw_scores["B"] > result.raw_scores["A"]
        assert result.raw_scores["B"] > result.raw_scores["C"]


# =============================================================================
# Property Tests
# =============================================================================

class TestTOPSISProperties:
    """TOPSIS 算法属性测试"""

    def test_topsis_algorithm_name(self):
        """测试算法名称"""
        algorithm = TOPSISAlgorithm()
        assert algorithm.name == "topsis"

    def test_topsis_description(self):
        """测试算法描述"""
        algorithm = TOPSISAlgorithm()
        assert len(algorithm.description) > 0
        assert "理想解" in algorithm.description or "Ideal" in algorithm.description


# =============================================================================
# TOPSIS Specific Tests
# =============================================================================

class TestTOPSISSpecific:
    """TOPSIS 特定测试"""

    def test_topsis_requires_vector_normalization(self):
        """测试 TOPSIS 需要 Vector 标准化"""
        algorithm = TOPSISAlgorithm()

        # TOPSIS 内部应该使用 Vector 标准化
        # 这可以通过检查中间结果来验证
        # 但这里我们只验证输入输出正确性

        from mcda_core.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.6, direction="higher_better"),
            Criterion(name="延迟", weight=0.4, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 85.0, "延迟": 60.0},
            "B": {"性能": 75.0, "延迟": 80.0},
        }

        problem = DecisionProblem(

            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        result = algorithm.calculate(problem)

        # 验证结果合理性
        assert len(result.rankings) == 2
        for score in result.raw_scores.values():
            assert 0 <= score <= 1
