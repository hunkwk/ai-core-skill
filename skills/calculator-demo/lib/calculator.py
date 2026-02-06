"""计算器核心实现模块

本模块实现基本的四则运算功能。
"""

from typing import Union

from skills.calculator_lib.lib.exceptions import (
    DivisionByZeroError,
    InvalidOperationError,
    InvalidTypeError,
)

# 支持的数字类型
Number = Union[int, float]

# 有效的运算符
VALID_OPERATIONS = {"+", "-", "*", "/"}


def _validate_number(value: any, param_name: str) -> float:
    """验证参数是否为数字类型

    Args:
        value: 待验证的值
        param_name: 参数名称（用于错误消息）

    Returns:
        转换为 float 的值

    Raises:
        InvalidTypeError: 当值不是数字类型时
    """
    if not isinstance(value, (int, float)):
        raise InvalidTypeError(param_name, value)
    return float(value)


def _validate_operation(operation: str) -> None:
    """验证运算符是否有效

    Args:
        operation: 运算符

    Raises:
        InvalidOperationError: 当运算符无效时
    """
    if operation not in VALID_OPERATIONS:
        raise InvalidOperationError(operation)


def calculate(a: Number, b: Number, operation: str) -> float:
    """执行基本数学运算

    支持加、减、乘、除四种基本运算。

    Args:
        a: 第一个操作数
        b: 第二个操作数
        operation: 运算符，支持 "+", "-", "*", "/"

    Returns:
        运算结果，始终为 float 类型

    Raises:
        InvalidTypeError: 当参数不是数字类型时
        InvalidOperationError: 当运算符无效时
        DivisionByZeroError: 当除数为零时

    Examples:
        >>> calculate(2, 3, "+")
        5.0
        >>> calculate(5, 3, "-")
        2.0
        >>> calculate(4, 3, "*")
        12.0
        >>> calculate(6, 2, "/")
        3.0
    """
    # 验证输入类型
    num_a = _validate_number(a, "a")
    num_b = _validate_number(b, "b")

    # 验证运算符
    _validate_operation(operation)

    # 执行运算
    if operation == "+":
        return num_a + num_b
    elif operation == "-":
        return num_a - num_b
    elif operation == "*":
        return num_a * num_b
    elif operation == "/":
        if num_b == 0:
            raise DivisionByZeroError()
        return num_a / num_b

    # 这行理论上不会执行，因为前面已经验证了运算符
    raise InvalidOperationError(operation)
