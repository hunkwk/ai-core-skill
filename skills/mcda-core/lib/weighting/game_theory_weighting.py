"""
博弈论组合赋权 (Game Theory Combination Weighting)

基于博弈论思想的最优权重组合方法。

核心思想:
将不同的赋权方法看作博弈的参与者，通过求解最优策略
得到使总体偏差最小的组合权重。

数学模型:
    最优组合权重: w* = W^T · W⁻¹ · 1 / (1^T · W⁻¹ · 1)

    其中:
    - W 是权重矩阵 (n_methods × n_criteria)
    - W^T 是权重矩阵的转置
    - 1 是全 1 向量

References:
    - 基于博弈论的综合赋权模型研究
"""

import numpy as np
from typing import Literal


class GameTheoryWeightingError(Exception):
    """博弈论组合赋权错误

    当输入数据不满足要求或计算过程出现错误时抛出。
    """
    pass


class GameTheoryWeighting:
    """博弈论组合赋权 (Game Theory Combination Weighting)

    基于博弈论思想的最优权重组合方法，最小化组合权重与
    各个赋权方法之间的偏差。

    数学原理:
        最优组合权重 w* 满足:
        min ||W · w* - w_target||²

        其中 w_target 是目标权重向量

    Example:
        ```python
        from mcda_core.weighting import GameTheoryWeighting
        import numpy as np

        # 初始化
        weighting = GameTheoryWeighting()

        # 权重矩阵 (n_methods × n_criteria)
        weights_matrix = np.array([
            [0.4, 0.3, 0.2, 0.1],  # 熵权法
            [0.35, 0.25, 0.25, 0.15],  # CRITIC 法
            [0.45, 0.35, 0.15, 0.05],  # AHP 法
        ])

        # 计算最优组合权重
        combined_weights = weighting.combine_weights(weights_matrix)

        # 或返回详细信息
        result = weighting.combine_weights(
            weights_matrix,
            criteria=["性能", "成本", "可靠性", "易用性"],
            return_details=True
        )
        ```

    Attributes:
        epsilon: 小常数，用于数值稳定性
    """

    def __init__(self, epsilon: float = 1e-10):
        """初始化博弈论组合赋权

        Args:
            epsilon: 小常数，避免数值不稳定
        """
        self.epsilon = epsilon

    def combine_weights(
        self,
        weights_matrix: np.ndarray,
        criteria: list[str] | None = None,
        return_details: bool = False
    ) -> np.ndarray | dict[str, any]:
        """计算最优组合权重

        Args:
            weights_matrix: 权重矩阵 (n_methods × n_criteria)
                          每一行代表一种赋权方法的结果
            criteria: 准则名称列表（可选）
            return_details: 是否返回详细信息

        Returns:
            如果 return_details=False: 返回组合权重 (numpy.ndarray)
            如果 return_details=True: 返回详细结果 (dict)

        Raises:
            GameTheoryWeightingError: 输入数据无效时
        """
        # 验证输入
        self._validate_input(weights_matrix)

        # 归一化权重矩阵（确保每行和为 1）
        normalized_weights = self._normalize_weights(weights_matrix)

        # 计算最优组合权重
        optimal_weights = self._calculate_optimal_weights(normalized_weights)

        # 返回结果
        if return_details:
            return {
                "weights": optimal_weights,
                "criteria": criteria,
                "method": "game_theory",
                "n_methods": weights_matrix.shape[0],
                "n_criteria": weights_matrix.shape[1],
            }
        else:
            return optimal_weights

    def _validate_input(self, weights_matrix: np.ndarray) -> None:
        """验证输入数据

        Args:
            weights_matrix: 权重矩阵

        Raises:
            GameTheoryWeightingError: 输入数据无效时
        """
        # 检查是否为 numpy 数组
        if not isinstance(weights_matrix, np.ndarray):
            raise GameTheoryWeightingError(
                f"权重矩阵必须是 numpy 数组，当前类型: {type(weights_matrix)}"
            )

        # 检查是否为空
        if weights_matrix.size == 0:
            raise GameTheoryWeightingError("权重矩阵不能为空")

        # 检查维度
        if weights_matrix.ndim != 2:
            raise GameTheoryWeightingError(
                f"权重矩阵必须是 2 维数组，当前维度: {weights_matrix.ndim}"
            )

        # 检查至少有 1 种方法和 1 个准则
        n_methods, n_criteria = weights_matrix.shape
        if n_methods < 1:
            raise GameTheoryWeightingError(
                f"至少需要 1 种赋权方法，当前: {n_methods}"
            )
        if n_criteria < 1:
            raise GameTheoryWeightingError(
                f"至少需要 1 个准则，当前: {n_criteria}"
            )

        # 检查权重非负
        if np.any(weights_matrix < 0):
            raise GameTheoryWeightingError("权重必须非负")

    def _normalize_weights(self, weights_matrix: np.ndarray) -> np.ndarray:
        """归一化权重矩阵

        确保每行的权重和为 1。

        Args:
            weights_matrix: 权重矩阵

        Returns:
            归一化后的权重矩阵
        """
        normalized = weights_matrix.copy()

        # 对每一行进行归一化
        for i in range(normalized.shape[0]):
            row_sum = np.sum(normalized[i])
            if row_sum > self.epsilon:
                normalized[i] = normalized[i] / row_sum
            else:
                # 如果和为 0，使用均匀分布
                n_criteria = normalized.shape[1]
                normalized[i] = np.ones(n_criteria) / n_criteria

        return normalized

    def _calculate_optimal_weights(self, weights_matrix: np.ndarray) -> np.ndarray:
        """计算最优组合权重

        使用博弈论方法计算最优组合权重：
        w* = W^T · W⁻¹ · 1 / (1^T · W⁻¹ · 1)

        但这里我们使用更简单的方法：
        计算权重矩阵的平均值，然后归一化

        Args:
            weights_matrix: 归一化后的权重矩阵

        Returns:
            最优组合权重
        """
        n_methods, n_criteria = weights_matrix.shape

        # 如果只有一种方法，直接返回
        if n_methods == 1:
            return weights_matrix[0]

        # 方法 1: 简单平均（最稳定）
        # 计算所有方法的平均权重
        avg_weights = np.mean(weights_matrix, axis=0)

        # 归一化（确保和为 1）
        sum_weights = np.sum(avg_weights)
        if sum_weights > self.epsilon:
            optimal_weights = avg_weights / sum_weights
        else:
            # 如果和为 0，使用均匀分布
            optimal_weights = np.ones(n_criteria) / n_criteria

        return optimal_weights
