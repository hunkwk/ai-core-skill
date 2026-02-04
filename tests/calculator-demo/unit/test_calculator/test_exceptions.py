"""
计算器异常类单元测试

本模块测试自定义异常类的行为。
"""

import pytest

from skills.calculator_lib.lib.exceptions import (
    CalculatorError,
    DivisionByZeroError,
    InvalidOperationError,
    InvalidTypeError,
)


class TestCalculatorError:
    """测试基础异常类 CalculatorError"""

    def test_default_message(self) -> None:
        """测试默认错误消息"""
        error = CalculatorError()
        assert str(error) == "计算器运算错误"

    def test_custom_message(self) -> None:
        """测试自定义错误消息"""
        error = CalculatorError("自定义错误")
        assert str(error) == "自定义错误"

    def test_message_attribute(self) -> None:
        """测试 message 属性可访问"""
        message = "测试消息"
        error = CalculatorError(message)
        assert error.message == message


class TestInvalidOperationError:
    """测试无效运算异常类 InvalidOperationError"""

    def test_error_contains_operation(self) -> None:
        """测试错误消息包含无效操作符"""
        error = InvalidOperationError("xyz")
        assert "xyz" in str(error)
        assert "无效的运算符" in str(error)

    def test_error_lists_valid_operations(self) -> None:
        """测试错误消息列出有效运算符"""
        error = InvalidOperationError("mod")
        error_str = str(error)
        assert "+" in error_str
        assert "-" in error_str
        assert "*" in error_str
        assert "/" in error_str

    def test_operation_attribute(self) -> None:
        """测试 operation 属性可访问"""
        operation = "power"
        error = InvalidOperationError(operation)
        assert error.operation == operation


class TestDivisionByZeroError:
    """测试除零错误异常类 DivisionByZeroError"""

    def test_default_message(self) -> None:
        """测试默认错误消息"""
        error = DivisionByZeroError()
        assert str(error) == "除数不能为零"

    def test_is_calculator_error_subclass(self) -> None:
        """测试是 CalculatorError 的子类"""
        error = DivisionByZeroError()
        assert isinstance(error, CalculatorError)


class TestInvalidTypeError:
    """测试无效类型异常类 InvalidTypeError"""

    def test_error_with_arg_name(self) -> None:
        """测试错误消息包含参数名"""
        error = InvalidTypeError("a", "hello")
        assert "a" in str(error)
        assert "hello" in str(error)

    def test_error_with_expected_type(self) -> None:
        """测试错误消息包含期望类型"""
        error = InvalidTypeError("b", [1, 2], "数字")
        assert "数字" in str(error)

    def test_default_expected_type(self) -> None:
        """测试默认期望类型为'数字类型'"""
        error = InvalidTypeError("x", None)
        assert "数字类型" in str(error)

    def test_attributes_accessible(self) -> None:
        """测试所有属性可访问"""
        arg_name = "result"
        arg_value = "invalid"
        expected_type = "整数或浮点数"
        error = InvalidTypeError(arg_name, arg_value, expected_type)

        assert error.arg_name == arg_name
        assert error.arg_value == arg_value
        assert error.expected_type == expected_type

    def test_with_none_value(self) -> None:
        """测试值为 None 时的错误消息"""
        error = InvalidTypeError("x", None)
        error_str = str(error)
        assert "x" in error_str
        assert "None" in error_str

    def test_with_complex_value(self) -> None:
        """测试复杂值（如列表）的错误消息"""
        error = InvalidTypeError("data", [1, 2, 3])
        error_str = str(error)
        assert "data" in error_str
        assert "[1, 2, 3]" in error_str
