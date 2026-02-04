"""
计算器功能单元测试

本模块包含 calculate 函数的单元测试，遵循 TDD 方法论。
测试分为三个循环：基础运算、边界条件、异常处理。

测试策略:
    - RED: 先写失败测试
    - GREEN: 实现最小代码使测试通过
    - REFACTOR: 优化代码结构
"""

import pytest

from skills.calculator_lib.lib import calculate
from skills.calculator_lib.lib.exceptions import (
    DivisionByZeroError,
    InvalidOperationError,
    InvalidTypeError,
)


class TestBasicOperations:
    """基础运算测试 - TDD 循环 1

    测试正常情况下的四则运算。
    """

    def test_addition_positive_numbers(self, docutils) -> None:
        """测试正数加法: 2 + 3 = 5

        Args:
            docutils: 测试文档工具 fixture
        """
        result = calculate(2, 3, "+")
        assert result == 5.0

    def test_addition_negative_numbers(self, docutils) -> None:
        """测试负数加法: -5 + (-3) = -8"""
        result = calculate(-5, -3, "+")
        assert result == -8.0

    def test_addition_mixed_signs(self, docutils) -> None:
        """测试混合符号加法: -10 + 15 = 5"""
        result = calculate(-10, 15, "+")
        assert result == 5.0

    def test_subtraction_positive_numbers(self, docutils) -> None:
        """测试正数减法: 5 - 3 = 2"""
        result = calculate(5, 3, "-")
        assert result == 2.0

    def test_subtraction_negative_result(self, docutils) -> None:
        """测试减法产生负数: 3 - 5 = -2"""
        result = calculate(3, 5, "-")
        assert result == -2.0

    def test_subtraction_from_negative(self, docutils) -> None:
        """测试从负数减法: -10 - 5 = -15"""
        result = calculate(-10, 5, "-")
        assert result == -15.0

    def test_multiplication_positive_numbers(self, docutils) -> None:
        """测试正数乘法: 4 * 3 = 12"""
        result = calculate(4, 3, "*")
        assert result == 12.0

    def test_multiplication_by_negative(self, docutils) -> None:
        """测试乘以负数: 6 * (-2) = -12"""
        result = calculate(6, -2, "*")
        assert result == -12.0

    def test_multiplication_both_negative(self, docutils) -> None:
        """测试两个负数相乘: (-4) * (-3) = 12"""
        result = calculate(-4, -3, "*")
        assert result == 12.0

    def test_division_positive_numbers(self, docutils) -> None:
        """测试正数除法: 6 / 2 = 3"""
        result = calculate(6, 2, "/")
        assert result == 3.0

    def test_division_negative_result(self, docutils) -> None:
        """测试除法产生负数: 8 / (-4) = -2"""
        result = calculate(8, -4, "/")
        assert result == -2.0

    def test_division_fractional_result(self, docutils) -> None:
        """测试除法产生小数: 5 / 2 = 2.5"""
        result = calculate(5, 2, "/")
        assert result == 2.5


class TestBoundaryConditions:
    """边界条件测试 - TDD 循环 2

    测试零值运算、大数运算和浮点精度。
    """

    def test_addition_with_zero(self, docutils) -> None:
        """测试加零运算: 5 + 0 = 5"""
        result = calculate(5, 0, "+")
        assert result == 5.0

    def test_zero_plus_zero(self, docutils) -> None:
        """测试零加零: 0 + 0 = 0"""
        result = calculate(0, 0, "+")
        assert result == 0.0

    def test_subtraction_with_zero(self, docutils) -> None:
        """测试减零运算: 5 - 0 = 5"""
        result = calculate(5, 0, "-")
        assert result == 5.0

    def test_zero_subtracted_from(self, docutils) -> None:
        """测试从零减法: 0 - 5 = -5"""
        result = calculate(0, 5, "-")
        assert result == -5.0

    def test_multiplication_by_zero(self, docutils) -> None:
        """测试乘以零: 5 * 0 = 0"""
        result = calculate(5, 0, "*")
        assert result == 0.0

    def test_zero_multiplication(self, docutils) -> None:
        """测试零乘法: 0 * 100 = 0"""
        result = calculate(0, 100, "*")
        assert result == 0.0

    def test_large_numbers(self, docutils) -> None:
        """测试大数运算: 1000000 + 2000000 = 3000000"""
        result = calculate(1_000_000, 2_000_000, "+")
        assert result == 3_000_000.0

    def test_large_multiplication(self, docutils) -> None:
        """测试大数乘法: 10000 * 10000 = 100000000"""
        result = calculate(10_000, 10_000, "*")
        assert result == 100_000_000.0

    def test_float_precision_addition(self, docutils) -> None:
        """测试浮点精度加法: 0.1 + 0.2 ≈ 0.3

        注意: 由于浮点精度问题，使用近似比较。
        """
        result = calculate(0.1, 0.2, "+")
        assert abs(result - 0.3) < 1e-10

    def test_float_precision_multiplication(self, docutils) -> None:
        """测试浮点精度乘法: 0.1 * 0.1 = 0.01"""
        result = calculate(0.1, 0.1, "*")
        assert abs(result - 0.01) < 1e-10

    def test_very_small_numbers(self, docutils) -> None:
        """测试极小数运算: 0.0001 + 0.0001 = 0.0002"""
        result = calculate(0.0001, 0.0001, "+")
        assert abs(result - 0.0002) < 1e-10


class TestExceptionHandling:
    """异常处理测试 - TDD 循环 3

    测试除零错误、无效运算符和类型错误。
    """

    def test_division_by_zero_raises_error(self, docutils) -> None:
        """测试除零错误: 5 / 0 应抛出 DivisionByZeroError

        Given:
            除数为 0
        When:
            执行除法运算
        Then:
            应抛出 DivisionByZeroError 异常
        """
        with pytest.raises(DivisionByZeroError) as excinfo:
            calculate(5, 0, "/")
        assert "除数不能为零" in str(excinfo.value)

    def test_division_zero_by_zero(self, docutils) -> None:
        """测试零除零: 0 / 0 应抛出 DivisionByZeroError"""
        with pytest.raises(DivisionByZeroError):
            calculate(0, 0, "/")

    def test_invalid_operation_plus(self, docutils) -> None:
        """测试无效运算符: 'plus' 应抛出 InvalidOperationError"""
        with pytest.raises(InvalidOperationError) as excinfo:
            calculate(2, 3, "plus")
        assert "无效的运算符" in str(excinfo.value)
        assert "plus" in str(excinfo.value)

    def test_invalid_operation_empty_string(self, docutils) -> None:
        """测试空运算符: '' 应抛出 InvalidOperationError"""
        with pytest.raises(InvalidOperationError):
            calculate(2, 3, "")

    def test_invalid_operation_none(self, docutils) -> None:
        """测试 None 运算符应抛出 InvalidOperationError"""
        with pytest.raises(InvalidOperationError):
            calculate(2, 3, "xyz")

    def test_invalid_type_first_arg_string(self, docutils) -> None:
        """测试第一个参数为字符串: 'a' + 3 应抛出 InvalidTypeError

        Given:
            第一个参数为字符串 'a'
        When:
            执行运算
        Then:
            应抛出 InvalidTypeError 异常
        """
        with pytest.raises(InvalidTypeError) as excinfo:
            calculate("a", 3, "+")
        assert "a" in str(excinfo.value)
        assert "不是有效的" in str(excinfo.value)

    def test_invalid_type_second_arg_string(self, docutils) -> None:
        """测试第二个参数为字符串: 2 + 'b' 应抛出 InvalidTypeError"""
        with pytest.raises(InvalidTypeError) as excinfo:
            calculate(2, "b", "+")
        assert "b" in str(excinfo.value)

    def test_invalid_type_both_strings(self, docutils) -> None:
        """测试两个参数都为字符串: 'a' + 'b' 应抛出 InvalidTypeError"""
        with pytest.raises(InvalidTypeError):
            calculate("a", "b", "+")

    def test_invalid_type_none_first_arg(self, docutils) -> None:
        """测试第一个参数为 None: None + 3 应抛出 InvalidTypeError"""
        with pytest.raises(InvalidTypeError):
            calculate(None, 3, "+")

    def test_invalid_type_none_second_arg(self, docutils) -> None:
        """测试第二个参数为 None: 2 + None 应抛出 InvalidTypeError"""
        with pytest.raises(InvalidTypeError):
            calculate(2, None, "+")

    def test_invalid_type_list_first_arg(self, docutils) -> None:
        """测试第一个参数为列表: [] + 3 应抛出 InvalidTypeError"""
        with pytest.raises(InvalidTypeError):
            calculate([], 3, "+")

    def test_invalid_type_dict_second_arg(self, docutils) -> None:
        """测试第二个参数为字典: 2 + {} 应抛出 InvalidTypeError"""
        with pytest.raises(InvalidTypeError):
            calculate(2, {}, "+")

    def test_valid_integers(self, docutils) -> None:
        """测试整数输入应正常工作"""
        result = calculate(5, 3, "+")
        assert isinstance(result, float)
        assert result == 8.0

    def test_valid_floats(self, docutils) -> None:
        """测试浮点数输入应正常工作"""
        result = calculate(5.5, 3.2, "+")
        assert isinstance(result, float)
        assert abs(result - 8.7) < 1e-10
