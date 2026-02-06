"""
计算器异常类定义

本模块定义了计算器功能相关的自定义异常类。


.. _CALC_ZERO_DIVISION:
"""

from typing import Any, Optional


class CalculatorError(Exception):
    """计算器基础异常类

    所有计算器相关异常的父类。

    Attributes:
        message: 错误消息
    """

    def __init__(self, message: str = "计算器运算错误") -> None:
        """初始化计算器异常

        Args:
            message: 错误消息，默认为"计算器运算错误"
        """
        self.message = message
        super().__init__(self.message)


class InvalidOperationError(CalculatorError):
    """无效运算异常

    当传入不支持的操作符时抛出。

    Example:
        >>> raise InvalidOperationError("xyz")
        InvalidOperationError: 无效的运算符: xyz
    """

    def __init__(self, operation: str) -> None:
        """初始化无效运算异常

        Args:
            operation: 无效的操作符
        """
        self.operation = operation
        message = f"无效的运算符: {operation}。支持的运算符: +, -, *, /"
        super().__init__(message)


class DivisionByZeroError(CalculatorError):
    """除零错误异常

    当尝试除以零时抛出。

    Example:
        >>> raise DivisionByZeroError()
        DivisionByZeroError: 除数不能为零
    """

    def __init__(self) -> None:
        """初始化除零错误异常"""
        message = "除数不能为零"
        super().__init__(message)


class InvalidTypeError(CalculatorError):
    """无效类型异常

    当传入的参数不是数字类型时抛出。

    Attributes:
        arg_name: 参数名称
        arg_value: 参数值
        expected_type: 期望的类型描述

    Example:
        >>> raise InvalidTypeError("a", "hello", "数字类型")
        InvalidTypeError: 参数 'a' 的值 'hello' 不是有效的数字类型
    """

    def __init__(self, arg_name: str, arg_value: Any, expected_type: str = "数字类型") -> None:
        """初始化无效类型异常

        Args:
            arg_name: 参数名称
            arg_value: 参数值
            expected_type: 期望的类型描述
        """
        self.arg_name = arg_name
        self.arg_value = arg_value
        self.expected_type = expected_type
        message = f"参数 '{arg_name}' 的值 '{arg_value}' 不是有效的{expected_type}"
        super().__init__(message)
