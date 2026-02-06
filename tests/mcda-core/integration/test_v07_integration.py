"""
MCDA Core - v0.7 集成测试

测试 VIKOR、TODIM 区间版本和可能度排序的集成。
"""

import pytest
import time
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def comprehensive_criteria():
    """综合准则（多类型）"""
    return [
        Criterion(name="性能", weight=0.35, direction="higher_better"),
        Criterion(name="成本", weight=0.25, direction="lower_better"),
        Criterion(name="可靠性", weight=0.20, direction="higher_better"),
        Criterion(name="易用性", weight=0.12, direction="higher_better"),
        Criterion(name="安全性", weight=0.08, direction="higher_better"),
    ]


@pytest.fixture
def comprehensive_interval_scores():
    """综合区间评分"""
    return {
        "方案A": {
            "性能": Interval(85.0, 92.0),
            "成本": Interval(40.0, 50.0),
            "可靠性": Interval(88.0, 95.0),
            "易用性": Interval(82.0, 90.0),
            "安全性": Interval(90.0, 98.0),
        },
        "方案B": {
            "性能": Interval(90.0, 95.0),
            "成本": Interval(45.0, 55.0),
            "可靠性": Interval(85.0, 92.0),
            "易用性": Interval(78.0, 85.0),
            "安全性": Interval(92.0, 96.0),
        },
        "方案C": {
            "性能": Interval(82.0, 88.0),
            "成本": Interval(35.0, 45.0),
            "可靠性": Interval(90.0, 96.0),
            "易用性": Interval(80.0, 88.0),
            "安全性": Interval(88.0, 94.0),
        },
    }


@pytest.fixture
def comprehensive_problem(comprehensive_criteria, comprehensive_interval_scores):
    """创建综合区间决策问题"""
    return DecisionProblem(
        alternatives=tuple(comprehensive_interval_scores.keys()),
        criteria=comprehensive_criteria,
        scores=comprehensive_interval_scores,
    )


# =============================================================================
# 1. 集成测试
# =============================================================================

class TestIntegration:
    """集成测试"""

    def test_vikor_with_possibility_degree_ranking(self, comprehensive_problem):
        """测试 VIKOR 与可能度排序的集成"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("vikor_interval")
        result = algorithm.calculate(comprehensive_problem)

        # 验证排名生成
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证 Q 值（可能是区间）
        for alt in comprehensive_problem.alternatives:
            assert alt in result.raw_scores
            q_value = result.raw_scores[alt]
            # Q 值可以是区间或标量
            assert isinstance(q_value, (int, float, Interval))

        # 验证元数据包含 S, R, Q
        assert "S" in result.metadata.metrics
        assert "R" in result.metadata.metrics
        assert "Q" in result.metadata.metrics

    def test_todim_with_possibility_degree_ranking(self, comprehensive_problem):
        """测试 TODIM 与可能度排序的集成"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")
        result = algorithm.calculate(comprehensive_problem)

        # 验证排名生成
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证全局优势度
        for alt in comprehensive_problem.alternatives:
            assert alt in result.raw_scores
            delta_value = result.raw_scores[alt]
            # δ 值可以是标量
            assert isinstance(delta_value, (int, float))

        # 验证元数据包含参数
        assert "global_dominance" in result.metadata.metrics
        assert "alpha" in result.metadata.metrics
        assert "beta" in result.metadata.metrics
        assert "theta" in result.metadata.metrics

    def test_interval_vs_crisp_comparison(self):
        """测试区间版本与精确数版本的结果对比"""
        from mcda_core.algorithms.base import get_algorithm
        from mcda_core.algorithms import todim

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        # 精确数评分（使用不同的分数避免并列）
        crisp_scores = {
            "A": {"性能": 85.0, "成本": 60.0},
            "B": {"性能": 92.0, "成本": 45.0},
            "C": {"性能": 78.0, "成本": 50.0},
        }

        # 退化区间评分（等于精确数）
        interval_scores = {
            alt: {
                crit: Interval(val, val)
                for crit, val in scores.items()
            }
            for alt, scores in crisp_scores.items()
        }

        # 创建两个问题
        crisp_problem = DecisionProblem(
            alternatives=tuple(crisp_scores.keys()),
            criteria=criteria,
            scores=crisp_scores,
        )

        interval_problem = DecisionProblem(
            alternatives=tuple(interval_scores.keys()),
            criteria=criteria,
            scores=interval_scores,
        )

        # 运行两个算法
        crisp_result = todim(crisp_problem)
        interval_algorithm = get_algorithm("todim_interval")
        interval_result = interval_algorithm.calculate(interval_problem)

        # 验证排名完全一致
        crisp_rankings = [r.alternative for r in crisp_result.rankings]
        interval_rankings = [r.alternative for r in interval_result.rankings]

        assert crisp_rankings == interval_rankings

    def test_multiple_algorithms_consistency(self, comprehensive_problem):
        """测试多个算法的一致性"""
        from mcda_core.algorithms.base import get_algorithm

        vikor = get_algorithm("vikor_interval")
        todim = get_algorithm("todim_interval")

        vikor_result = vikor.calculate(comprehensive_problem)
        todim_result = todim.calculate(comprehensive_problem)

        # 两个算法都应该产生结果
        assert len(vikor_result.rankings) == 3
        assert len(todim_result.rankings) == 3

        # 验证最优方案相同（或至少在前2名）
        vikor_best = vikor_result.rankings[0].alternative
        todim_best = todim_result.rankings[0].alternative

        # 最优方案应该相同，或者至少都在前2名
        assert (
            vikor_best == todim_best or
            vikor_best in [r.alternative for r in todim_result.rankings[:2]]
        )

    def test_degenerate_intervals_behavior(self):
        """测试退化区间的行为"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        # 退化区间（单点）
        scores = {
            "A": {"性能": Interval(85.0, 85.0)},
            "B": {"性能": Interval(90.0, 90.0)},
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        # 测试 VIKOR
        vikor = get_algorithm("vikor_interval")
        vikor_result = vikor.calculate(problem)

        assert len(vikor_result.rankings) == 2
        # 退化区间应该正常排序

        # 测试 TODIM
        todim = get_algorithm("todim_interval")
        todim_result = todim.calculate(problem)

        assert len(todim_result.rankings) == 2

    def test_edge_case_single_criterion(self):
        """测试边界情况：单个准则"""
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

        # VIKOR
        vikor = get_algorithm("vikor_interval")
        vikor_result = vikor.calculate(problem)

        assert len(vikor_result.rankings) == 2

        # TODIM
        todim = get_algorithm("todim_interval")
        todim_result = todim.calculate(problem)

        assert len(todim_result.rankings) == 2

    def test_edge_case_equal_weights(self):
        """测试边界情况：所有准则权重相同"""
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

        vikor = get_algorithm("vikor_interval")
        result = vikor.calculate(problem)

        # 应该正常计算
        assert len(result.rankings) == 2


# =============================================================================
# 2. 性能测试
# =============================================================================

class TestPerformance:
    """性能测试"""

    def test_large_scale_performance(self):
        """测试大规模问题的性能"""
        from mcda_core.algorithms.base import get_algorithm

        # 创建 50 个方案 × 20 个准则
        criteria = [
            Criterion(name=f"准则{i}", weight=1.0/20, direction="higher_better")
            for i in range(20)
        ]

        scores = {}
        for i in range(50):
            alt = f"方案{i}"
            scores[alt] = {
                f"准则{j}": Interval(70.0, 90.0)
                for j in range(20)
            }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        # 测试 VIKOR 性能
        vikor = get_algorithm("vikor_interval")
        start_time = time.time()
        vikor_result = vikor.calculate(problem)
        vikor_time = time.time() - start_time

        # 测试 TODIM 性能
        todim = get_algorithm("todim_interval")
        start_time = time.time()
        todim_result = todim.calculate(problem)
        todim_time = time.time() - start_time

        # 验证结果
        assert len(vikor_result.rankings) == 50
        assert len(todim_result.rankings) == 50

        # 验证性能（目标 < 5 秒）
        assert vikor_time < 5.0, f"VIKOR 耗时 {vikor_time:.3f}s 超过目标 5s"
        assert todim_time < 5.0, f"TODIM 耗时 {todim_time:.3f}s 超过目标 5s"

        print(f"\n性能测试结果 (50方案 × 20准则):")
        print(f"  VIKOR: {vikor_time:.3f}s")
        print(f"  TODIM: {todim_time:.3f}s")

    def test_interval_vs_crisp_performance(self):
        """对比区间运算和精确数运算的性能"""
        from mcda_core.algorithms.base import get_algorithm
        from mcda_core.algorithms import todim

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        # 精确数问题
        crisp_scores = {
            f"方案{i}": {
                "性能": 70.0 + i,
                "成本": 80.0 - i,
            }
            for i in range(20)
        }

        # 区间问题
        interval_scores = {
            f"方案{i}": {
                "性能": Interval(70.0 + i, 75.0 + i),
                "成本": Interval(75.0 - i, 80.0 - i),
            }
            for i in range(20)
        }

        crisp_problem = DecisionProblem(
            alternatives=tuple(crisp_scores.keys()),
            criteria=criteria,
            scores=crisp_scores,
        )

        interval_problem = DecisionProblem(
            alternatives=tuple(interval_scores.keys()),
            criteria=criteria,
            scores=interval_scores,
        )

        # 测试精确数 TODIM 性能
        start_time = time.time()
        crisp_result = todim(crisp_problem)
        crisp_time = time.time() - start_time

        # 测试区间 TODIM 性能
        interval_algorithm = get_algorithm("todim_interval")
        start_time = time.time()
        interval_result = interval_algorithm.calculate(interval_problem)
        interval_time = time.time() - start_time

        # 验证结果
        assert len(crisp_result.rankings) == 20
        assert len(interval_result.rankings) == 20

        # 性能对比：区间运算应该慢于精确数，但仍应在合理范围
        print(f"\n性能对比测试 (20方案 × 2准则):")
        print(f"  精确数 TODIM: {crisp_time:.3f}s")
        print(f"  区间数 TODIM: {interval_time:.3f}s")
        print(f"  性能比率: {interval_time / crisp_time:.2f}x")

        # 区间运算不应超过精确数的 3 倍
        assert interval_time / crisp_time < 3.0, \
            f"区间运算过慢: {interval_time:.3f}s vs {crisp_time:.3f}s"


# =============================================================================
# 3. 边界条件测试
# =============================================================================

class TestEdgeCases:
    """边界条件测试"""

    def test_boundary_zero_width_intervals(self):
        """测试零宽度区间（退化区间）"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        # 混合退化区间和正常区间
        scores = {
            "A": {"性能": Interval(85.0, 85.0)},  # 零宽度
            "B": {"性能": Interval(80.0, 90.0)},  # 正常区间
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        vikor = get_algorithm("vikor_interval")
        result = vikor.calculate(problem)

        # 应该正常计算并排序
        assert len(result.rankings) == 2

    def test_negative_interval_handling(self):
        """测试负区间处理（虽然评分范围是 0-100，但标准化后可能为负）"""
        from mcda_core.algorithms.base import get_algorithm

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
            Criterion(name="成本", weight=1.0, direction="lower_better"),
        ]

        scores = {
            "A": {
                "性能": Interval(80.0, 90.0),
                "成本": Interval(50.0, 60.0),
            },
            "B": {
                "性能": Interval(85.0, 95.0),
                "成本": Interval(55.0, 65.0),
            },
        }

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        # VIKOR 和 TODIM 都应该正常处理
        vikor = get_algorithm("vikor_interval")
        vikor_result = vikor.calculate(problem)

        todim = get_algorithm("todim_interval")
        todim_result = todim.calculate(problem)

        assert len(vikor_result.rankings) == 2
        assert len(todim_result.rankings) == 2


# =============================================================================
# Test Summary
# =============================================================================

# 测试总数: 10
# - 集成测试: 6
# - 性能测试: 2
# - 边界条件: 2
