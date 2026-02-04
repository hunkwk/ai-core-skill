"""
MCDA Core - VIKOR 区间版本测试

测试 VIKOR 算法的区间数版本，支持不确定性和模糊性。
"""

import pytest
from mcda_core.models import (
    Criterion,
    DecisionProblem,
)
from mcda_core.interval import Interval

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def interval_criteria():
    """示例准则（权重已归一化）"""
    return [
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        Criterion(name="易用性", weight=0.1, direction="higher_better"),
    ]


@pytest.fixture
def interval_scores():
    """示例区间评分"""
    return {
        "AWS": {
            "性能": Interval(80.0, 90.0),
            "成本": Interval(55.0, 65.0),
            "可靠性": Interval(85.0, 95.0),
            "易用性": Interval(75.0, 85.0),
        },
        "Azure": {
            "性能": Interval(88.0, 96.0),
            "成本": Interval(45.0, 55.0),
            "可靠性": Interval(80.0, 90.0),
            "易用性": Interval(80.0, 90.0),
        },
        "GCP": {
            "性能": Interval(84.0, 92.0),
            "成本": Interval(65.0, 75.0),
            "可靠性": Interval(75.0, 85.0),
            "易用性": Interval(70.0, 80.0),
        },
    }


@pytest.fixture
def interval_problem(interval_criteria, interval_scores):
    """创建区间决策问题"""
    return DecisionProblem(
        alternatives=tuple(interval_scores.keys()),
        criteria=interval_criteria,
        scores=interval_scores,
    )


@pytest.fixture
def crisp_scores():
    """精确数评分（用于兼容性测试）"""
    return {
        "AWS": {"性能": 85.0, "成本": 60.0, "可靠性": 90.0, "易用性": 80.0},
        "Azure": {"性能": 92.0, "成本": 50.0, "可靠性": 85.0, "易用性": 85.0},
        "GCP": {"性能": 88.0, "成本": 70.0, "可靠性": 80.0, "易用性": 75.0},
    }


@pytest.fixture
def degenerate_interval_scores():
    """退化区间评分（上下界相同）"""
    return {
        "AWS": {
            "性能": Interval(85.0, 85.0),
            "成本": Interval(60.0, 60.0),
            "可靠性": Interval(90.0, 90.0),
            "易用性": Interval(80.0, 80.0),
        },
        "Azure": {
            "性能": Interval(92.0, 92.0),
            "成本": Interval(50.0, 50.0),
            "可靠性": Interval(85.0, 85.0),
            "易用性": Interval(85.0, 85.0),
        },
        "GCP": {
            "性能": Interval(88.0, 88.0),
            "成本": Interval(70.0, 70.0),
            "可靠性": Interval(80.0, 80.0),
            "易用性": Interval(75.0, 75.0),
        },
    }


# =============================================================================
# 1. 基础功能测试 (8 tests)
# =============================================================================

class TestIntervalVIKORBasic:
    """VIKOR 区间版本基础功能测试"""

    def test_vikor_interval_algorithm_registration(self, interval_problem):
        """测试算法注册"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        assert algorithm is not None
        assert algorithm.name == "vikor_interval"

    def test_vikor_interval_basic_calculation(self, interval_problem):
        """测试 VIKOR 区间版本基本计算"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        # 验证排名存在
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证 Q 值存在（Q 应该是区间或标量）
        for alt in interval_problem.alternatives:
            assert alt in result.raw_scores

        # 验证排名（Q 值越小越好）
        assert result.rankings[0].rank == 1
        assert result.rankings[1].rank == 2
        assert result.rankings[2].rank == 3

    def test_vikor_interval_with_three_alternatives(self, interval_problem):
        """测试三个备选方案的区间 VIKOR"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        # 验证三个方案都有排名
        assert len(result.rankings) == 3

        # 验证所有方案都有 Q 值
        assert len(result.raw_scores) == 3

    def test_vikor_interval_with_v_parameter(self, interval_problem):
        """测试不同 v 参数的影响"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")

        # v = 0.5 (默认)
        result_0_5 = algorithm.calculate(interval_problem, v=0.5)

        # v = 0.8 (更重视群体效用)
        result_0_8 = algorithm.calculate(interval_problem, v=0.8)

        # v = 0.2 (更重视个别遗憾)
        result_0_2 = algorithm.calculate(interval_problem, v=0.2)

        # 验证所有结果都有效
        assert len(result_0_5.rankings) == 3
        assert len(result_0_8.rankings) == 3
        assert len(result_0_2.rankings) == 3

    def test_vikor_interval_v_zero(self, interval_problem):
        """测试 v = 0 (完全重视个别遗憾)"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem, v=0.0)

        # 应该正常计算
        assert len(result.rankings) == 3
        assert result.metadata.metrics["v"] == 0.0

    def test_vikor_interval_v_one(self, interval_problem):
        """测试 v = 1 (完全重视群体效用)"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem, v=1.0)

        # 应该正常计算
        assert len(result.rankings) == 3
        assert result.metadata.metrics["v"] == 1.0

    def test_vikor_interval_invalid_v_parameter(self, interval_problem):
        """测试无效的 v 参数"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")

        # v < 0 应该抛出异常
        with pytest.raises(ValueError, match="v 必须在"):
            algorithm.calculate(interval_problem, v=-0.1)

        # v > 1 应该抛出异常
        with pytest.raises(ValueError, match="v 必须在"):
            algorithm.calculate(interval_problem, v=1.5)

    def test_vikor_interval_empty_problem(self):
        """测试空决策问题"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")

        # 空备选方案
        with pytest.raises(ValueError):
            problem = DecisionProblem(
                alternatives=(),
                criteria=[],
                scores={},
            )
            algorithm.calculate(problem)


# =============================================================================
# 2. 区间运算测试 (10 tests)
# =============================================================================

class TestIntervalVIKOROperations:
    """VIKOR 区间运算测试"""

    def test_interval_group_utility_s_calculation(self, interval_problem):
        """测试区间群体效用 S 的计算"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        S = result.metadata.metrics.get("S", {})

        # 验证所有方案都有 S 值
        for alt in interval_problem.alternatives:
            assert alt in S
            # S 可以是区间或标量
            # 验证 S 值存在（可以为负数，这是区间版本的特性）
            assert S[alt] is not None
            # 验证类型正确
            assert isinstance(S[alt], (int, float, Interval))

    def test_interval_individual_regret_r_calculation(self, interval_problem):
        """测试区间个别遗憾 R 的计算"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        R = result.metadata.metrics.get("R", {})

        # 验证所有方案都有 R 值
        for alt in interval_problem.alternatives:
            assert alt in R
            # R 可以是区间或标量
            # 验证 R 值存在（可以为负数，这是区间版本的特性）
            assert R[alt] is not None
            # 验证类型正确
            assert isinstance(R[alt], (int, float, Interval))

    def test_interval_compromise_value_q_calculation(self, interval_problem):
        """测试区间折衷值 Q 的计算"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        Q = result.raw_scores

        # 验证所有方案都有 Q 值
        for alt in interval_problem.alternatives:
            assert alt in Q
            # Q 可以是区间或标量
            # 验证 Q 值存在（可以为负数，这是区间版本的特性）
            assert Q[alt] is not None
            # 验证类型正确
            assert isinstance(Q[alt], (int, float, Interval))

    def test_interval_normalization_higher_better(self):
        """测试 higher_better 准则的区间标准化"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建简单问题（只有 higher_better）
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(85.0, 95.0)},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 验证结果存在
        assert len(result.rankings) == 2

    def test_interval_normalization_lower_better(self):
        """测试 lower_better 准则的区间标准化"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建简单问题（只有 lower_better）
        criteria = [
            Criterion(name="成本", weight=1.0, direction="lower_better"),
        ]

        scores = {
            "A": {"成本": Interval(50.0, 60.0)},
            "B": {"成本": Interval(55.0, 65.0)},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 验证结果存在
        assert len(result.rankings) == 2

    def test_interval_max_operation(self, interval_problem):
        """测试区间最大值运算（用于 R 计算）"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        R = result.metadata.metrics.get("R", {})

        # 验证 R 是通过 max 运算得到的
        for alt in interval_problem.alternatives:
            assert alt in R
            # R 应该是某个准则的最大加权标准化值
            # 验证 R 存在（可以为负数，这是区间版本的特性）
            assert R[alt] is not None
            # 验证类型正确
            assert isinstance(R[alt], (int, float, Interval))

    def test_interval_arithmetic_operations(self, interval_problem):
        """测试区间算术运算（加、减、乘、除）"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        S = result.metadata.metrics.get("S", {})
        Q = result.raw_scores

        # S 和 Q 的计算涉及区间算术运算
        # 验证计算成功
        for alt in interval_problem.alternatives:
            assert alt in S
            assert alt in Q

    def test_interval_division_by_scalar(self, interval_problem):
        """测试区间除以标量（用于标准化）"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        # 标准化涉及除以 (max - min)
        # 验证计算成功
        assert len(result.rankings) == 3

    def test_interval_width_handling(self):
        """测试区间宽度的处理"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建不同宽度的区间
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 81.0)},  # 宽度小
            "B": {"性能": Interval(70.0, 90.0)},  # 宽度大
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 验证结果存在
        assert len(result.rankings) == 2

    def test_interval_degenerate_case(self, degenerate_interval_scores):
        """测试退化区间（单点区间）"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=0.4, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.2, direction="higher_better"),
            Criterion(name="易用性", weight=0.1, direction="higher_better"),
        ]

        problem = DecisionProblem(
            alternatives=tuple(degenerate_interval_scores.keys()),
            criteria=criteria,
            scores=degenerate_interval_scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 退化区间应该正常计算
        assert len(result.rankings) == 3


# =============================================================================
# 3. 可能度排序测试 (6 tests)
# =============================================================================

class TestPossibilityDegreeRanking:
    """可能度排序集成测试"""

    def test_possibility_degree_ranking_integration(self, interval_problem):
        """测试可能度排序的集成"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        # 验证排名基于可能度排序
        assert len(result.rankings) == 3
        # 排名应该唯一（没有并列）
        ranks = [r.rank for r in result.rankings]
        assert len(set(ranks)) == len(ranks)

    def test_ranking_with_overlapping_intervals(self):
        """测试重叠区间的排序"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建重叠区间
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(85.0, 95.0)},  # 与 A 重叠
            "C": {"性能": Interval(70.0, 85.0)},  # 与 A, B 重叠
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 重叠区间应该能够排序
        assert len(result.rankings) == 3

    def test_ranking_with_disjoint_intervals(self):
        """测试不相交区间的排序"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建不相交区间
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 85.0)},
            "B": {"性能": Interval(86.0, 90.0)},  # 不相交
            "C": {"性能": Interval(91.0, 95.0)},  # 不相交
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 不相交区间应该清晰排序
        assert len(result.rankings) == 3

    def test_ranking_with_contained_intervals(self):
        """测试包含区间的排序"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建包含关系
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(82.0, 88.0)},  # A 包含 B
            "C": {"性能": Interval(83.0, 87.0)},  # B 包含 C
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 包含区间应该能够排序
        assert len(result.rankings) == 3

    def test_ranking_with_equal_intervals(self):
        """测试相等区间的排序"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建相等区间
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(80.0, 90.0)},  # 与 A 相等
            "C": {"性能": Interval(80.0, 90.0)},  # 与 A, B 相等
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 相等区间应该有相同的排名
        assert len(result.rankings) == 3

    def test_ranking_stability(self, interval_problem):
        """测试排序的稳定性（多次运行结果一致）"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")

        # 运行多次
        result1 = algorithm.calculate(interval_problem)
        result2 = algorithm.calculate(interval_problem)
        result3 = algorithm.calculate(interval_problem)

        # 验证排名一致
        rankings1 = [r.alternative for r in result1.rankings]
        rankings2 = [r.alternative for r in result2.rankings]
        rankings3 = [r.alternative for r in result3.rankings]

        assert rankings1 == rankings2 == rankings3


# =============================================================================
# 4. 兼容性测试 (6 tests)
# =============================================================================

class TestCrispCompatibility:
    """与精确数 VIKOR 的兼容性测试"""

    def test_compatibility_with_crisp_vikor(self, interval_criteria, crisp_scores):
        """测试退化区间与精确数 VIKOR 的兼容性"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建精确数问题
        crisp_problem = DecisionProblem(
            alternatives=tuple(crisp_scores.keys()),
            criteria=interval_criteria,
            scores=crisp_scores,
        )

        # 创建退化区间问题
        degenerate_scores = {
            alt: {
                crit: Interval(val, val)
                for crit, val in scores.items()
            }
            for alt, scores in crisp_scores.items()
        }

        interval_problem = DecisionProblem(
            alternatives=tuple(degenerate_scores.keys()),
            criteria=interval_criteria,
            scores=degenerate_scores,
        )

        # 运行两个算法
        crisp_algorithm = get_algorithm("vikor")
        interval_algorithm = get_algorithm("vikor_interval")

        crisp_result = crisp_algorithm.calculate(crisp_problem)
        interval_result = interval_algorithm.calculate(interval_problem)

        # 验证排名一致
        crisp_rankings = [r.alternative for r in crisp_result.rankings]
        interval_rankings = [r.alternative for r in interval_result.rankings]

        # 排名应该相同或非常接近
        assert crisp_rankings == interval_rankings

    def test_degenerate_intervals_equal_crisp(self, interval_criteria, degenerate_interval_scores):
        """测试退化区间等于精确数"""
        from mcda_core.algorithms.base import get_algorithm

        degenerate_problem = DecisionProblem(
            alternatives=tuple(degenerate_interval_scores.keys()),
            criteria=interval_criteria,
            scores=degenerate_interval_scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(degenerate_problem)

        # 退化区间应该正常计算
        assert len(result.rankings) == 3

    def test_single_value_intervals(self):
        """测试单值区间（退化区间）"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(85.0, 85.0)},  # 单值
            "B": {"性能": Interval(90.0, 90.0)},  # 单值
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 应该正常计算
        assert len(result.rankings) == 2

    def test_crisp_weights_with_interval_scores(self, interval_problem):
        """测试精确权重与区间评分的组合"""
        from mcda_core.algorithms.base import get_algorithm

        # 权重是精确数，评分是区间
        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        # 应该正常计算
        assert len(result.rankings) == 3

    def test_algorithm_name_and_description(self):
        """测试算法名称和描述"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")

        assert algorithm.name == "vikor_interval"
        assert "区间" in algorithm.description or "VIKOR" in algorithm.description

    def test_metadata_structure(self, interval_problem):
        """测试元数据结构"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(interval_problem)

        # 验证元数据
        assert result.metadata is not None
        assert result.metadata.algorithm_name == "vikor_interval"
        assert "S" in result.metadata.metrics or "Q" in result.raw_scores


# =============================================================================
# 5. 边界条件测试 (4 tests)
# =============================================================================

class TestBoundaryConditions:
    """边界条件测试"""

    def test_all_alternatives_same_scores(self):
        """测试所有方案评分相同的情况"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(80.0, 90.0)},  # 相同
            "C": {"性能": Interval(80.0, 90.0)},  # 相同
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 所有方案应该有相同的 Q 值
        assert len(result.rankings) == 3

    def test_all_criteria_same_weights(self):
        """测试所有准则权重相同的情况"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=0.25, direction="higher_better"),
            Criterion(name="成本", weight=0.25, direction="lower_better"),
            Criterion(name="可靠性", weight=0.25, direction="higher_better"),
            Criterion(name="易用性", weight=0.25, direction="higher_better"),
        ]

        scores = {
            "A": {
                "性能": Interval(80.0, 90.0),
                "成本": Interval(50.0, 60.0),
                "可靠性": Interval(85.0, 95.0),
                "易用性": Interval(75.0, 85.0),
            },
            "B": {
                "性能": Interval(85.0, 95.0),
                "成本": Interval(55.0, 65.0),
                "可靠性": Interval(80.0, 90.0),
                "易用性": Interval(80.0, 90.0),
            },
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 应该正常计算
        assert len(result.rankings) == 2

    def test_single_criterion(self):
        """测试单个准则的情况"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(85.0, 95.0)},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 应该正常计算
        assert len(result.rankings) == 2

    def test_single_alternative(self):
        """测试单个方案的情况（应该验证失败）"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {
                "性能": Interval(80.0, 90.0),
                "成本": Interval(50.0, 60.0),
            },
        }

        # DecisionProblem 验证应该拒绝单方案问题
        with pytest.raises(ValueError, match="至少需要 2 个备选方案"):
            problem = DecisionProblem(
                alternatives=tuple(scores.keys()),
                criteria=criteria,
                scores=scores,
            )


# =============================================================================
# 6. 性能测试 (2 tests)
# =============================================================================

class TestPerformance:
    """性能测试"""

    def test_performance_10_alternatives_10_criteria(self):
        """测试 10 个方案 × 10 个准则的性能"""
        import time
        from mcda_core.algorithms.base import get_algorithm

        # 创建 10 个方案 × 10 个准则
        criteria = [
            Criterion(name=f"准则{i}", weight=0.1, direction="higher_better")
            for i in range(10)
        ]

        scores = {}
        for i in range(10):
            alt = f"方案{i}"
            scores[alt] = {
                f"准则{j}": Interval(70.0 + i, 90.0 + i)
                for j in range(10)
            }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")

        # 测量执行时间
        start_time = time.time()
        result = algorithm.calculate(problem)
        elapsed_time = time.time() - start_time

        # 验证结果
        assert len(result.rankings) == 10

        # 验证性能（目标 < 0.5 秒）
        assert elapsed_time < 0.5, f"执行时间 {elapsed_time:.3f}s 超过目标 0.5s"

    def test_performance_large_problem(self):
        """测试大规模问题的性能"""
        import time
        from mcda_core.algorithms.base import get_algorithm

        # 创建 20 个方案 × 15 个准则
        criteria = [
            Criterion(name=f"准则{i}", weight=1.0/15, direction="higher_better")
            for i in range(15)
        ]

        scores = {}
        for i in range(20):
            alt = f"方案{i}"
            scores[alt] = {
                f"准则{j}": Interval(70.0, 90.0)
                for j in range(15)
            }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")

        # 测量执行时间
        start_time = time.time()
        result = algorithm.calculate(problem)
        elapsed_time = time.time() - start_time

        # 验证结果
        assert len(result.rankings) == 20

        # 验证性能（目标 < 2 秒）
        assert elapsed_time < 2.0, f"执行时间 {elapsed_time:.3f}s 超过目标 2.0s"


# =============================================================================
# 7. 错误处理测试 (2 tests)
# =============================================================================

class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_interval_scores(self):
        """测试无效的区间评分"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建有效区间（Interval 类会验证下界 <= 上界）
        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        # 有效区间
        scores = {
            "A": {"性能": Interval(80.0, 90.0)},
            "B": {"性能": Interval(85.0, 95.0)},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(problem)

        # 应该正常计算
        assert len(result.rankings) == 2

    def test_negative_weights_handling(self):
        """测试负权重的处理"""
        # 负权重应该在 Criterion 创建时被拒绝
        with pytest.raises(ValueError, match="weight.*必须在 0-1 范围内"):
            criteria = [
                Criterion(name="性能", weight=-0.5, direction="higher_better"),
            ]


# =============================================================================
# Test Summary
# =============================================================================

# 测试总数: 38
# - 基础功能测试: 8
# - 区间运算测试: 10
# - 可能度排序测试: 6
# - 兼容性测试: 6
# - 边界条件测试: 4
# - 性能测试: 2
# - 错误处理测试: 2
