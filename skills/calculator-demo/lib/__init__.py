"""
计算器功能模块

本模块提供基本的数学运算功能，包括加、减、乘、除四种基本运算。

Example:
    >>> from skills.calculator_lib.lib import calculate
    >>> result = calculate(2, 3, "+")
    >>> print(result)
    5.0
"""

from skills.calculator_lib.lib.calculator import Number, calculate
from skills.calculator_lib.lib.exceptions import (
    CalculatorError,
    DivisionByZeroError,
    InvalidOperationError,
    InvalidTypeError,
)

__all__ = [
    "calculate",
    "Number",
    "CalculatorError",
    "DivisionByZeroError",
    "InvalidOperationError",
    "InvalidTypeError",
]

__version__ = "0.1.0"
