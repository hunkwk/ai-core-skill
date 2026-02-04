"""
计算器测试配置和共享 fixtures

本模块提供测试所需的共享 fixtures 和配置。
"""

import pytest
from typing import Any


@pytest.fixture
def docutils(request) -> Any:
    """文档工具 fixture

    用于在测试中添加文档字符串或元数据。
    目前作为占位符，可扩展用于文档生成。

    Args:
        request: pytest request 对象

    Returns:
        文档工具对象（当前为 None，可扩展）
    """
    return None


@pytest.fixture
def valid_operators() -> list[str]:
    """有效的运算符列表

    Returns:
        包含所有支持运算符的列表
    """
    return ["+", "-", "*", "/"]


@pytest.fixture
def invalid_operators() -> list[str]:
    """无效的运算符列表

    Returns:
        包含无效运算符的列表，用于测试异常处理
    """
    return ["", "x", "mod", "power", "%", "&", "|"]


@pytest.fixture
def boundary_numbers() -> dict[str, dict[str, float]]:
    """边界测试数值

    Returns:
        包含各种边界值的字典
    """
    return {
        "zero": 0.0,
        "small_positive": 0.0001,
        "small_negative": -0.0001,
        "large_positive": 1_000_000.0,
        "large_negative": -1_000_000.0,
        "fraction": 0.5,
    }
