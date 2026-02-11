"""
MCDA Core - 聚合方法抽象基类

定义评分聚合方法的接口规范。
"""

from abc import ABC, abstractmethod
from typing import Protocol


# =============================================================================
# 聚合方法抽象基类
# =============================================================================

class AggregationMethod(ABC):
    """评分聚合方法抽象基类

    定义将多个决策者的评分聚合为群决策结果的接口。

    Example:
        ```python
        class MyAggregation(AggregationMethod):
            def aggregate(self, scores: dict[str, float], weights: dict[str, float]) -> float:
                # 实现聚合逻辑
                return aggregated_score
        ```
    """

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """获取聚合方法名称

        Returns:
            方法名称（用于注册和查找）
        """
        ...

    @abstractmethod
    def aggregate(
        self,
        scores: dict[str, float],
        weights: dict[str, float] | None = None
    ) -> float:
        """聚合多个评分

        Args:
            scores: 决策者评分 {decision_maker_id: score}
            weights: 决策者权重（可选，默认等权重）

        Returns:
            聚合后的评分

        Raises:
            ValueError: 评分数据无效
        """
        ...

    @abstractmethod
    def aggregate_matrix(
        self,
        score_matrix: dict[str, dict[str, dict[str, float]]],
        weights: dict[str, float] | None = None
    ) -> dict[str, dict[str, float]]:
        """聚合评分矩阵

        Args:
            score_matrix: 评分矩阵
                {alternative: {criterion: {decision_maker_id: score}}}
            weights: 决策者权重（可选）

        Returns:
            聚合后的评分矩阵 {alternative: {criterion: aggregated_score}}
        """
        ...


# =============================================================================
# 聚合方法注册表
# =============================================================================

class AggregationRegistry:
    """聚合方法注册表

    管理所有可用的聚合方法。
    """

    _methods: dict[str, type[AggregationMethod]] = {}

    @classmethod
    def register(cls, method_class: type[AggregationMethod]) -> None:
        """注册聚合方法

        Args:
            method_class: 聚合方法类

        Raises:
            ValueError: 方法名称已存在
        """
        name = method_class.get_name()
        if name in cls._methods:
            raise ValueError(f"聚合方法 '{name}' 已存在")
        cls._methods[name] = method_class

    @classmethod
    def get(cls, name: str) -> type[AggregationMethod]:
        """获取聚合方法类

        Args:
            name: 方法名称

        Returns:
            聚合方法类

        Raises:
            KeyError: 方法不存在
        """
        if name not in cls._methods:
            raise KeyError(f"未知的聚合方法: '{name}'")
        return cls._methods[name]

    @classmethod
    def create(cls, name: str) -> AggregationMethod:
        """创建聚合方法实例

        Args:
            name: 方法名称

        Returns:
            聚合方法实例
        """
        return cls.get(name)()

    @classmethod
    def list_methods(cls) -> list[str]:
        """列出所有已注册的方法

        Returns:
            方法名称列表
        """
        return sorted(cls._methods.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """检查方法是否已注册

        Args:
            name: 方法名称

        Returns:
            是否已注册
        """
        return name in cls._methods


# 自动注册内置聚合方法
def _register_builtin_methods() -> None:
    """注册内置聚合方法"""
    from .weighted_average import WeightedAverageAggregation
    from .weighted_geometric import WeightedGeometricAggregation
    from .borda_count import BordaCountAggregation
    from .copeland import CopelandAggregation

    AggregationRegistry.register(WeightedAverageAggregation)
    AggregationRegistry.register(WeightedGeometricAggregation)
    AggregationRegistry.register(BordaCountAggregation)
    AggregationRegistry.register(CopelandAggregation)
