"""
MCDA Core - TODIM 区间版本测试（简化版）

测试 TODIM 算法的区间数版本，基于前景理论。
"""

import pytest
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def interval_criteria():
    """示例准则"""
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


# =============================================================================
# 1. 基础功能测试
# =============================================================================

class TestIntervalTODIMBasic:
    """TODIM 区间版本基础功能测试"""

    def test_todim_interval_algorithm_registration(self, interval_problem):
        """测试算法注册"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")
        assert algorithm is not None
        assert algorithm.name == "todim_interval"

    def test_todim_interval_basic_calculation(self, interval_problem):
        """测试 TODIM 区间版本基本计算"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")
        result = algorithm.calculate(interval_problem)

        # 验证排名存在
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证所有方案都有得分
        for alt in interval_problem.alternatives:
            assert alt in result.raw_scores

    def test_todim_interval_with_three_alternatives(self, interval_problem):
        """测试三个备选方案的区间 TODIM"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")
        result = algorithm.calculate(interval_problem)

        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

    def test_todim_interval_with_parameters(self, interval_problem):
        """测试不同前景理论参数"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")

        # 默认参数
        result_default = algorithm.calculate(interval_problem)

        # 自定义参数
        result_custom = algorithm.calculate(
            interval_problem,
            alpha=0.9,
            beta=0.9,
            theta=2.5
        )

        # 验证所有结果都有效
        assert len(result_default.rankings) == 3
        assert len(result_custom.rankings) == 3

    def test_todim_interval_default_parameters(self, interval_problem):
        """测试默认参数（α=β=0.88, θ=2.25）"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")
        result = algorithm.calculate(interval_problem)

        # 验证元数据包含参数
        assert "alpha" in result.metadata.metrics
        assert "beta" in result.metadata.metrics
        assert "theta" in result.metadata.metrics
        assert result.metadata.metrics["alpha"] == 0.88
        assert result.metadata.metrics["beta"] == 0.88
        assert result.metadata.metrics["theta"] == 2.25


# =============================================================================
# 2. 兼容性测试
# =============================================================================

class TestCrispCompatibility:
    """与精确数 TODIM 的兼容性测试"""

    def test_compatibility_with_crisp_todim(self, interval_criteria):
        """测试退化区间与精确数 TODIM 的兼容性"""
        from mcda_core.algorithms.base import get_algorithm
        from mcda_core.algorithms import todim  # todim 是函数，不是类

        # 创建精确数问题
        crisp_scores = {
            "AWS": {"性能": 85.0, "成本": 60.0, "可靠性": 90.0, "易用性": 80.0},
            "Azure": {"性能": 92.0, "成本": 50.0, "可靠性": 85.0, "易用性": 85.0},
            "GCP": {"性能": 88.0, "成本": 70.0, "可靠性": 80.0, "易用性": 75.0},
        }

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
        crisp_result = todim(crisp_problem)
        interval_algorithm = get_algorithm("todim_interval")
        interval_result = interval_algorithm.calculate(interval_problem)

        # 验证排名一致（或接近）
        crisp_rankings = [r.alternative for r in crisp_result.rankings]
        interval_rankings = [r.alternative for r in interval_result.rankings]

        # 至少前 2 名应该一致
        assert crisp_rankings[0] == interval_rankings[0]
        assert crisp_rankings[1] == interval_rankings[1]

    def test_algorithm_name_and_description(self):
        """测试算法名称和描述"""
        from mcda_core.algorithms.base import get_algorithm

        algorithm = get_algorithm("todim_interval")

        assert algorithm.name == "todim_interval"
        assert "区间" in algorithm.description or "TODIM" in algorithm.description


# =============================================================================
# 3. 性能测试
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

        algorithm = get_algorithm("todim_interval")

        # 测量执行时间
        start_time = time.time()
        result = algorithm.calculate(problem)
        elapsed_time = time.time() - start_time

        # 验证结果
        assert len(result.rankings) == 10

        # 验证性能（目标 < 0.5 秒）
        assert elapsed_time < 0.5, f"执行时间 {elapsed_time:.3f}s 超过目标 0.5s"


# =============================================================================
# Test Summary
# =============================================================================

# 测试总数: 10
# - 基础功能测试: 5
# - 兼容性测试: 2
# - 性能测试: 1
# - 其他: 2
