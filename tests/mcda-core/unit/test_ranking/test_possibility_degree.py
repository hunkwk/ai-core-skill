"""
MCDA Core - 可能度排序测试

测试基于可能度的区间排序方法。
"""

import pytest
from mcda_core.interval import Interval
from mcda_core.ranking import PossibilityDegree


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def possibility_degree():
    """创建可能度排序实例"""
    return PossibilityDegree()


@pytest.fixture
def sample_intervals():
    """示例区间"""
    return {
        "A": Interval(2.0, 5.0),   # [2, 5]
        "B": Interval(3.0, 6.0),   # [3, 6]
        "C": Interval(1.0, 4.0),   # [1, 4]
        "D": Interval(4.0, 7.0),   # [4, 7]
    }


# =============================================================================
# 基础功能测试
# =============================================================================

class TestPossibilityDegreeCalculation:
    """测试可能度计算"""

    def test_completely_greater(self, possibility_degree):
        """测试完全大于的情况"""
        a = Interval(5.0, 7.0)  # [5, 7]
        b = Interval(2.0, 4.0)  # [2, 4]

        prob = possibility_degree.calculate(a, b)

        assert prob == 1.0, "完全大于时，可能度应为 1.0"

    def test_completely_less(self, possibility_degree):
        """测试完全小于的情况"""
        a = Interval(2.0, 4.0)  # [2, 4]
        b = Interval(5.0, 7.0)  # [5, 7]

        prob = possibility_degree.calculate(a, b)

        assert prob == 0.0, "完全小于时，可能度应为 0.0"

    def test_equal_intervals(self, possibility_degree):
        """测试相等区间"""
        a = Interval(3.0, 6.0)  # [3, 6]
        b = Interval(3.0, 6.0)  # [3, 6]

        prob_a_ge_b = possibility_degree.calculate(a, b)
        prob_b_ge_a = possibility_degree.calculate(b, a)

        assert prob_a_ge_b == 0.5, "相等区间，可能度应为 0.5"
        assert prob_b_ge_a == 0.5, "相等区间，可能度应为 0.5"

    def test_overlapping_intervals(self, possibility_degree):
        """测试重叠区间"""
        a = Interval(2.0, 5.0)  # [2, 5]
        b = Interval(3.0, 6.0)  # [3, 6]

        prob = possibility_degree.calculate(a, b)

        # 手工计算: (5 - 3) / ((5 - 2) + (6 - 3)) = 2 / (3 + 3) = 2/6 = 1/3
        expected = 2.0 / (3.0 + 3.0)
        assert abs(prob - expected) < 1e-6, f"重叠区间可能度计算错误: {prob} ≠ {expected}"

    def test_degenerate_intervals(self, possibility_degree):
        """测试退化区间（单点区间）"""
        a = Interval(4.0, 4.0)  # [4, 4]
        b = Interval(3.0, 5.0)  # [3, 5]

        prob = possibility_degree.calculate(a, b)

        # 手工计算: (4 - 3) / ((4 - 4) + (5 - 3)) = 1 / (0 + 2) = 0.5
        expected = (4.0 - 3.0) / (0.0 + (5.0 - 3.0))
        assert abs(prob - expected) < 1e-6, f"退化区间可能度计算错误: {prob} ≠ {expected}"

    def test_contained_intervals(self, possibility_degree):
        """测试包含关系（中心对齐的特殊情况）"""
        a = Interval(3.0, 5.0)  # [3, 5] - 被包含，中心 = 4.0
        b = Interval(2.0, 6.0)  # [2, 6] - 包含，中心 = 4.0

        prob_a_ge_b = possibility_degree.calculate(a, b)
        prob_b_ge_a = possibility_degree.calculate(b, a)

        # a 和 b 中心对齐时，P(a ≥ b) = P(b ≥ a) = 0.5
        # 这是特殊情况：虽然 a 被包含在 b 中，但由于中心对齐，可能度相等
        assert prob_a_ge_b == 0.5, f"中心对齐时，可能度应为 0.5，实际: {prob_a_ge_b}"
        assert prob_b_ge_a == 0.5, f"中心对齐时，可能度应为 0.5，实际: {prob_b_ge_a}"
        assert abs(prob_a_ge_b + prob_b_ge_a - 1.0) < 1e-6, "P(a≥b) + P(b≥a) 应等于 1"

    def test_contained_intervals_offset(self, possibility_degree):
        """测试偏移的包含关系（中心不对齐）"""
        # a 完全被包含在 b 中，但 a 的中心偏左
        a = Interval(2.5, 4.5)  # [2.5, 4.5] - 中心 = 3.5
        b = Interval(2.0, 6.0)  # [2, 6] - 中心 = 4.0

        prob_a_ge_b = possibility_degree.calculate(a, b)
        prob_b_ge_a = possibility_degree.calculate(b, a)

        # a 的中心偏左，所以 P(a ≥ b) < 0.5
        assert prob_a_ge_b < 0.5, "中心偏左的被包含区间的可能度应小于 0.5"
        assert prob_b_ge_a > 0.5, "包含区间的可能度应大于 0.5"
        assert abs(prob_a_ge_b + prob_b_ge_a - 1.0) < 1e-6, "P(a≥b) + P(b≥a) 应等于 1"


# =============================================================================
# 排序功能测试
# =============================================================================

class TestPossibilityDegreeRanking:
    """测试可能度排序"""

    def test_rank_intervals(self, possibility_degree, sample_intervals):
        """测试区间排序"""
        rankings = possibility_degree.rank(sample_intervals)

        # 验证返回格式
        assert isinstance(rankings, list), "返回值应为列表"
        assert len(rankings) == len(sample_intervals), "应返回所有区间"

        # 验证每个元素是元组
        for name, score in rankings:
            assert isinstance(name, str), "名称应为字符串"
            assert isinstance(score, (int, float)), "分数应为数值"

    def test_rank_order(self, possibility_degree, sample_intervals):
        """测试排序顺序"""
        rankings = possibility_degree.rank(sample_intervals)

        # 验证分数降序排列
        scores = [score for _, score in rankings]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], "分数应降序排列"

    def test_rank_comprehensive_scores(self, possibility_degree, sample_intervals):
        """测试综合可能度计算"""
        rankings = possibility_degree.rank(sample_intervals)

        # 验证综合可能度计算
        # 对于 4 个区间，每个区间的综合可能度是它与另外 3 个区间的可能度之和
        # 理论范围: [0, 3] (因为每个可能度在 [0, 1])
        for name, score in rankings:
            assert 0 <= score <= 3, f"综合可能度应在 [0, 3] 范围内: {name} = {score}"

    def test_rank_single_interval(self, possibility_degree):
        """测试单个区间排序"""
        intervals = {"A": Interval(2.0, 5.0)}

        rankings = possibility_degree.rank(intervals)

        assert len(rankings) == 1, "应返回 1 个区间"
        assert rankings[0][0] == "A", "区间名称应正确"
        assert rankings[0][1] == 0.0, "单个区间综合可能度应为 0"

    def test_rank_empty_intervals(self, possibility_degree):
        """测试空字典排序"""
        intervals = {}

        rankings = possibility_degree.rank(intervals)

        assert len(rankings) == 0, "空字典应返回空列表"


# =============================================================================
# 比较功能测试
# =============================================================================

class TestPossibilityDegreeCompare:
    """测试区间比较"""

    def test_compare_greater(self, possibility_degree):
        """测试大于比较"""
        a = Interval(5.0, 7.0)  # [5, 7]
        b = Interval(2.0, 4.0)  # [2, 4]

        result = possibility_degree.compare(a, b)

        assert result == "a > b", f"比较结果错误: {result}"

    def test_compare_less(self, possibility_degree):
        """测试小于比较"""
        a = Interval(2.0, 4.0)  # [2, 4]
        b = Interval(5.0, 7.0)  # [5, 7]

        result = possibility_degree.compare(a, b)

        assert result == "a < b", f"比较结果错误: {result}"

    def test_compare_equal(self, possibility_degree):
        """测试相等比较"""
        a = Interval(3.0, 6.0)  # [3, 6]
        b = Interval(3.0, 6.0)  # [3, 6]

        result = possibility_degree.compare(a, b)

        assert result == "a = b", f"比较结果错误: {result}"

    def test_compare_overlapping(self, possibility_degree):
        """测试重叠比较"""
        a = Interval(2.0, 5.0)  # [2, 5]
        b = Interval(3.0, 6.0)  # [3, 6]

        result = possibility_degree.compare(a, b)

        assert result == "a ≈ b", f"比较结果错误: {result}"


# =============================================================================
# 边界条件测试
# =============================================================================

class TestPossibilityDegreeBoundary:
    """测试边界条件"""

    def test_zero_width_interval(self, possibility_degree):
        """测试零宽度区间"""
        a = Interval(5.0, 5.0)  # [5, 5]
        b = Interval(5.0, 5.0)  # [5, 5]

        prob = possibility_degree.calculate(a, b)

        assert prob == 0.5, "零宽度相等区间的可能度应为 0.5"

    def test_touching_intervals(self, possibility_degree):
        """测试相切区间"""
        a = Interval(2.0, 5.0)  # [2, 5]
        b = Interval(5.0, 8.0)  # [5, 8]

        prob_a_ge_b = possibility_degree.calculate(a, b)
        prob_b_ge_a = possibility_degree.calculate(b, a)

        # a 和 b 在 5 处相切
        # P(a ≥ b) = (5 - 5) / ((5-2) + (8-5)) = 0 / 6 = 0
        # P(b ≥ a) = (8 - 5) / ((8-5) + (5-2)) = 3 / 6 = 0.5
        assert prob_a_ge_b == 0.0, "相切区间 a≥b 的可能度应为 0.0"
        assert prob_b_ge_a > 0.0, "相切区间 b≥a 的可能度应大于 0.0"

    def test_very_small_overlap(self, possibility_degree):
        """测试极小重叠"""
        a = Interval(2.0, 5.0)      # [2, 5]
        b = Interval(4.999, 7.0)    # [4.999, 7]

        prob = possibility_degree.calculate(a, b)

        # 应该有一个很小的可能度（但不为0）
        assert 0.0 < prob < 0.1, "极小重叠应产生较小的可能度"

    def test_negative_intervals(self, possibility_degree):
        """测试负数区间"""
        a = Interval(-5.0, -2.0)  # [-5, -2]
        b = Interval(-3.0, -1.0)  # [-3, -1]

        prob = possibility_degree.calculate(a, b)

        # 手工计算: (-2 - (-3)) / ((-2 - (-5)) + ((-1) - (-3)))
        #             = (1) / (3 + 2) = 1/5 = 0.2
        expected = ( -2.0 - (-3.0) ) / ((-2.0 - (-5.0)) + ((-1.0) - (-3.0)))
        assert abs(prob - expected) < 1e-6, f"负数区间可能度计算错误: {prob} ≠ {expected}"


# =============================================================================
# 性能测试
# =============================================================================

class TestPossibilityDegreePerformance:
    """测试性能"""

    def test_rank_10_intervals(self, possibility_degree):
        """测试 10 个区间排序性能"""
        import time

        # 生成 10 个随机区间
        intervals = {}
        for i in range(10):
            intervals[f"Interval{i}"] = Interval(float(i), float(i + 10))

        # 测量排序时间
        start = time.time()
        rankings = possibility_degree.rank(intervals)
        elapsed = time.time() - start

        # 验证结果正确性
        assert len(rankings) == 10, "应返回 10 个区间"

        # 性能断言: 10 个区间排序应 < 0.01 秒
        assert elapsed < 0.01, f"10 个区间排序时间应 < 0.01 秒，实际: {elapsed:.4f} 秒"

    def test_rank_100_intervals(self, possibility_degree):
        """测试 100 个区间排序性能"""
        import time

        # 生成 100 个随机区间
        intervals = {}
        for i in range(100):
            intervals[f"Interval{i}"] = Interval(float(i), float(i + 10))

        # 测量排序时间
        start = time.time()
        rankings = possibility_degree.rank(intervals)
        elapsed = time.time() - start

        # 验证结果正确性
        assert len(rankings) == 100, "应返回 100 个区间"

        # 性能断言: 100 个区间排序应 < 1 秒
        assert elapsed < 1.0, f"100 个区间排序时间应 < 1 秒，实际: {elapsed:.4f} 秒"


# =============================================================================
# 数学性质测试
# =============================================================================

class TestPossibilityDegreeProperties:
    """测试数学性质"""

    def test_complementarity(self, possibility_degree):
        """测试互补性: P(A ≥ B) + P(B ≥ A) = 1"""
        test_cases = [
            (Interval(2.0, 5.0), Interval(3.0, 6.0)),
            (Interval(1.0, 4.0), Interval(4.0, 7.0)),
            (Interval(5.0, 8.0), Interval(1.0, 3.0)),
            (Interval(3.0, 6.0), Interval(3.0, 6.0)),
        ]

        for a, b in test_cases:
            prob_a_ge_b = possibility_degree.calculate(a, b)
            prob_b_ge_a = possibility_degree.calculate(b, a)

            assert abs(prob_a_ge_b + prob_b_ge_a - 1.0) < 1e-6, \
                f"P(a≥b) + P(b≥a) 应等于 1: {prob_a_ge_b} + {prob_b_ge_a} = {prob_a_ge_b + prob_b_ge_a}"

    def test_reflexivity(self, possibility_degree):
        """测试自反性: P(A ≥ A) = 0.5"""
        a = Interval(2.0, 5.0)

        prob = possibility_degree.calculate(a, a)

        assert prob == 0.5, "P(A ≥ A) 应等于 0.5"

    def test_transitivity_approximation(self, possibility_degree):
        """测试传递性（近似）"""
        # A = [1, 3], B = [2, 4], C = [3, 5]
        # P(A ≥ B) < 0.5, P(B ≥ C) < 0.5, P(A ≥ C) 应该更小
        a = Interval(1.0, 3.0)
        b = Interval(2.0, 4.0)
        c = Interval(3.0, 5.0)

        prob_a_ge_b = possibility_degree.calculate(a, b)
        prob_b_ge_c = possibility_degree.calculate(b, c)
        prob_a_ge_c = possibility_degree.calculate(a, c)

        # 验证传递性关系
        assert prob_a_ge_b < 0.5, "A < B"
        assert prob_b_ge_c < 0.5, "B < C"
        assert prob_a_ge_c < prob_a_ge_b, "A < C 的可能度应更小"
