"""
MCDA Core - 评分聚合模块

提供群决策中多个决策者评分的聚合方法。
"""

from .base import (
    AggregationMethod,
    AggregationRegistry,
    _register_builtin_methods,
)
from .weighted_average import WeightedAverageAggregation
from .weighted_geometric import WeightedGeometricAggregation
from .borda_count import BordaCountAggregation
from .copeland import CopelandAggregation

# 初始化注册表
_register_builtin_methods()

__all__ = [
    "AggregationMethod",
    "AggregationRegistry",
    "WeightedAverageAggregation",
    "WeightedGeometricAggregation",
    "BordaCountAggregation",
    "CopelandAggregation",
]
