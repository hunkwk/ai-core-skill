"""
区间数（Interval）数据类型

用于处理不确定性和模糊性的 MCDA 分析。
"""

from dataclasses import dataclass
from typing import Union
import numpy as np


class IntervalError(Exception):
    """区间数错误

    当区间数操作无效时抛出。
    """
    pass


@dataclass(frozen=True)
class Interval:
    """区间数数据类型

    表示一个区间 [lower, upper]，用于处理不确定性和模糊性。

    Attributes:
        lower: 区间下界
        upper: 区间上界

    Example:
        ```python
        # 创建区间
        interval = Interval(1.0, 5.0)

        # 访问属性
        print(interval.lower)  # 1.0
        print(interval.upper)  # 5.0
        print(interval.midpoint)  # 3.0
        print(interval.width)  # 4.0

        # 区间运算
        result = interval + Interval(2.0, 3.0)  # [3.0, 8.0]
        result = interval * 2.0  # [2.0, 10.0]
        ```
    """

    lower: float
    upper: float

    def __post_init__(self):
        """验证区间数"""
        if self.lower > self.upper:
            raise IntervalError(
                f"区间下界必须小于等于上界，当前: lower={self.lower}, upper={self.upper}"
            )

    @property
    def midpoint(self) -> float:
        """区间中点

        Returns:
            区间的中点值
        """
        return (self.lower + self.upper) / 2.0

    @property
    def width(self) -> float:
        """区间宽度

        Returns:
            区间的宽度（不确定性度量）
        """
        return self.upper - self.lower

    def is_degenerate(self) -> bool:
        """判断是否为退化区间

        退化区间是指下界等于上界的区间（单点区间）。

        Returns:
            如果是退化区间返回 True，否则返回 False
        """
        return self.lower == self.upper

    def __add__(self, other: "Interval") -> "Interval":
        """区间加法

        Args:
            other: 另一个区间

        Returns:
            两个区间的和
        """
        if not isinstance(other, Interval):
            raise TypeError(f"只能与区间相加，当前类型: {type(other)}")

        return Interval(
            self.lower + other.lower,
            self.upper + other.upper
        )

    def __sub__(self, other: "Interval") -> "Interval":
        """区间减法

        Args:
            other: 另一个区间

        Returns:
            两个区间的差
        """
        if not isinstance(other, Interval):
            raise TypeError(f"只能与区间相减，当前类型: {type(other)}")

        return Interval(
            self.lower - other.upper,
            self.upper - other.lower
        )

    def __mul__(self, other: Union["Interval", float]) -> "Interval":
        """区间乘法

        Args:
            other: 另一个区间或标量

        Returns:
            乘积区间
        """
        if isinstance(other, (int, float)):
            # 标量乘法
            scalar = float(other)
            if scalar >= 0:
                return Interval(
                    self.lower * scalar,
                    self.upper * scalar
                )
            else:
                return Interval(
                    self.upper * scalar,
                    self.lower * scalar
                )
        elif isinstance(other, Interval):
            # 区间乘法
            products = [
                self.lower * other.lower,
                self.lower * other.upper,
                self.upper * other.lower,
                self.upper * other.upper,
            ]
            return Interval(min(products), max(products))
        else:
            raise TypeError(f"只能与区间或标量相乘，当前类型: {type(other)}")

    def __truediv__(self, other: Union["Interval", float]) -> "Interval":
        """区间除法

        Args:
            other: 另一个区间或标量

        Returns:
            商区间

        Raises:
            IntervalError: 除数区间包含零
        """
        if isinstance(other, (int, float)):
            # 标量除法
            scalar = float(other)
            if scalar == 0:
                raise IntervalError("除数不能为零")
            return self * (1.0 / scalar)
        elif isinstance(other, Interval):
            # 区间除法
            if other.lower <= 0 <= other.upper:
                raise IntervalError("除数区间不能包含零")

            # 区间除法等价于乘以倒数
            reciprocal = Interval(1.0 / other.upper, 1.0 / other.lower)
            return self * reciprocal
        else:
            raise TypeError(f"只能与区间或标量相除，当前类型: {type(other)}")

    def __contains__(self, value: float) -> bool:
        """判断值是否在区间内

        Args:
            value: 要检查的值

        Returns:
            如果值在区间内返回 True，否则返回 False
        """
        return self.lower <= value <= self.upper

    def __eq__(self, other: object) -> bool:
        """区间相等比较

        基于中点比较。

        Args:
            other: 另一个区间

        Returns:
            如果中点相等返回 True，否则返回 False
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self.midpoint == other.midpoint

    def __lt__(self, other: object) -> bool:
        """区间小于比较

        基于中点比较。

        Args:
            other: 另一个区间

        Returns:
            如果当前中点小于另一个中点返回 True
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self.midpoint < other.midpoint

    def __le__(self, other: object) -> bool:
        """区间小于等于比较

        Args:
            other: 另一个区间

        Returns:
            如果当前中点小于等于另一个中点返回 True
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self.midpoint <= other.midpoint

    def __gt__(self, other: object) -> bool:
        """区间大于比较

        Args:
            other: 另一个区间

        Returns:
            如果当前中点大于另一个中点返回 True
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self.midpoint > other.midpoint

    def __ge__(self, other: object) -> bool:
        """区间大于等于比较

        Args:
            other: 另一个区间

        Returns:
            如果当前中点大于等于另一个中点返回 True
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self.midpoint >= other.midpoint

    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.lower}, {self.upper}]"

    def __repr__(self) -> str:
        """对象表示"""
        return f"Interval({self.lower}, {self.upper})"

    @classmethod
    def from_tuple(cls, values: tuple[float, float]) -> "Interval":
        """从元组创建区间

        Args:
            values: (lower, upper) 元组

        Returns:
            区间对象
        """
        return cls(values[0], values[1])

    @classmethod
    def from_single(cls, value: float) -> "Interval":
        """从单个值创建退化区间

        Args:
            value: 区间的值（下界和上界相同）

        Returns:
            退化区间对象
        """
        return cls(value, value)
