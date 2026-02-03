"""
MCDA Core - 区间数数据类型测试

测试区间数（Interval）的基本功能和运算。
"""

import pytest
from mcda_core.interval import Interval, IntervalError


# =============================================================================
# Basic Functionality Tests (8 个)
# =============================================================================

class TestIntervalBasic:
    """区间数基础功能测试"""

    def test_interval_creation(self):
        """测试区间数创建"""
        interval = Interval(1.0, 5.0)

        assert interval.lower == 1.0
        assert interval.upper == 5.0

    def test_interval_midpoint(self):
        """测试区间中点计算"""
        interval = Interval(2.0, 6.0)

        assert interval.midpoint == 4.0

    def test_interval_width(self):
        """测试区间宽度计算"""
        interval = Interval(2.0, 6.0)

        assert interval.width == 4.0

    def test_interval_equality(self):
        """测试区间相等"""
        interval1 = Interval(1.0, 5.0)
        interval2 = Interval(1.0, 5.0)
        interval3 = Interval(1.0, 6.0)

        assert interval1 == interval2
        assert interval1 != interval3

    def test_interval_str_representation(self):
        """测试区间字符串表示"""
        interval = Interval(1.0, 5.0)

        assert str(interval) == "[1.0, 5.0]"
        assert repr(interval) == "Interval(1.0, 5.0)"

    def test_interval_from_tuple(self):
        """测试从元组创建区间"""
        interval = Interval.from_tuple((1.0, 5.0))

        assert interval.lower == 1.0
        assert interval.upper == 5.0

    def test_interval_from_single_value(self):
        """测试从单个值创建区间（退化区间）"""
        interval = Interval.from_single(3.0)

        assert interval.lower == 3.0
        assert interval.upper == 3.0
        assert interval.width == 0.0

    def test_interval_is_degenerate(self):
        """测试退化区间判断"""
        normal_interval = Interval(1.0, 5.0)
        degenerate_interval = Interval(3.0, 3.0)

        assert not normal_interval.is_degenerate()
        assert degenerate_interval.is_degenerate()


# =============================================================================
# Arithmetic Tests (6 个)
# =============================================================================

class TestIntervalArithmetic:
    """区间数算术运算测试"""

    def test_interval_addition(self):
        """测试区间加法"""
        interval1 = Interval(1.0, 3.0)
        interval2 = Interval(2.0, 4.0)

        result = interval1 + interval2

        assert result.lower == 3.0
        assert result.upper == 7.0

    def test_interval_subtraction(self):
        """测试区间减法"""
        interval1 = Interval(5.0, 7.0)
        interval2 = Interval(1.0, 2.0)

        result = interval1 - interval2

        assert result.lower == 3.0
        assert result.upper == 6.0

    def test_interval_multiplication(self):
        """测试区间乘法"""
        interval1 = Interval(2.0, 3.0)
        interval2 = Interval(4.0, 5.0)

        result = interval1 * interval2

        assert result.lower == 8.0
        assert result.upper == 15.0

    def test_interval_scalar_multiplication(self):
        """测试区间标量乘法"""
        interval = Interval(1.0, 2.0)

        result = interval * 3.0

        assert result.lower == 3.0
        assert result.upper == 6.0

    def test_interval_division(self):
        """测试区间除法"""
        interval1 = Interval(6.0, 8.0)
        interval2 = Interval(2.0, 4.0)

        result = interval1 / interval2

        assert result.lower == 1.5  # 6.0 / 4.0
        assert result.upper == 4.0  # 8.0 / 2.0

    def test_interval_division_by_zero_raises_error(self):
        """测试区间除以零（包含零的区间）"""
        interval1 = Interval(1.0, 2.0)
        interval2 = Interval(-1.0, 1.0)  # 包含零

        with pytest.raises(IntervalError, match="除数区间不能包含零"):
            interval1 / interval2


# =============================================================================
# Comparison Tests (2 个)
# =============================================================================

class TestIntervalComparison:
    """区间数比较测试"""

    def test_interval_midpoint_comparison(self):
        """测试基于中点的区间比较"""
        interval1 = Interval(1.0, 5.0)  # 中点 3.0
        interval2 = Interval(4.0, 6.0)  # 中点 5.0

        assert interval1 < interval2
        assert interval2 > interval1

    def test_interval_overlapping_comparison(self):
        """测试重叠区间的比较"""
        interval1 = Interval(1.0, 5.0)
        interval2 = Interval(3.0, 7.0)

        # 重叠区间可以比较（基于中点）
        assert interval1 < interval2

    def test_interval_equal_midpoints(self):
        """测试相同中点的区间"""
        interval1 = Interval(2.0, 4.0)  # 中点 3.0
        interval2 = Interval(1.0, 5.0)  # 中点 3.0

        # 中点相同，则相等
        assert interval1 == interval2

    def test_interval_contains(self):
        """测试区间包含关系"""
        interval = Interval(2.0, 6.0)

        assert 3.0 in interval
        assert 1.0 not in interval
        assert 7.0 not in interval
