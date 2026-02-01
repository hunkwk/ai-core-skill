"""
熵权法 (Entropy Weight Method) 服务

实现基于信息熵的客观权重计算功能。

References:
- Zou, Z., Yun, Y., & Sun, J. (2006). Entropy method for determination of weight of evaluating indicators in fuzzy synthetic evaluation for water quality assessment.
"""

import numpy as np
from typing import Literal


class EntropyWeightValidationError(Exception):
    """熵权法验证错误

    当输入数据不满足要求时抛出。
    """
    pass


class EntropyWeightService:
    """熵权法 (Entropy Weight Method) 服务

    基于信息熵理论计算客观权重：
    1. 数据标准化
    2. 计算信息熵
    3. 计算差异系数
    4. 确定客观权重
    5. 支持主客观权重组合

    Example:
        ```python
        service = EntropyWeightService()

        # 决策矩阵 (n_alternatives x n_criteria)
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ])

        # 计算客观权重
        weights = service.calculate_weights(decision_matrix)

        # 完整工作流（含详细信息）
        result = service.calculate_weights_with_details(
            decision_matrix,
            criteria=["Cost", "Quality", "Function"]
        )

        # 与主观权重组合
        subjective = np.array([0.5, 0.3, 0.2])
        combined = service.combine_weights(
            subjective,
            result["weights"],
            method="linear",
            alpha=0.6
        )
        ```
    """

    def __init__(self, epsilon: float = 1e-10):
        """初始化熵权法服务

        Args:
            epsilon: 小常数，避免 log(0)
        """
        self.epsilon = epsilon

    # =========================================================================
    # 数据标准化
    # =========================================================================

    def _normalize(
        self,
        scores: np.ndarray,
        direction: Literal["higher_better", "lower_better"]
    ) -> np.ndarray:
        """标准化评分

        Args:
            scores: 评分向量 (n_alternatives,)
            direction: 准则方向
                - higher_better: 越大越好
                - lower_better: 越小越好

        Returns:
            标准化后的评分 (范围 [0, 1])

        Note:
            对于越大越好: x_norm = (x - min) / (max - min)
            对于越小越好: x_norm = (max - x) / (max - min)
        """
        min_val = np.min(scores)
        max_val = np.max(scores)

        # 避免除以零（所有值相同时）
        if np.isclose(max_val, min_val):
            return np.zeros_like(scores)

        if direction == "higher_better":
            normalized = (scores - min_val) / (max_val - min_val)
        elif direction == "lower_better":
            normalized = (max_val - scores) / (max_val - min_val)
        else:
            raise ValueError(
                f"无效的方向: '{direction}'. "
                f"必须是 'higher_better' 或 'lower_better'"
            )

        return normalized

    def _normalize_with_shift(
        self,
        scores: np.ndarray,
        direction: Literal["higher_better", "lower_better"]
    ) -> np.ndarray:
        """标准化并平移（避免零值，用于后续 log 计算）

        Args:
            scores: 评分向量
            direction: 准则方向

        Returns:
            标准化并平移后的评分（确保 > 0）
        """
        normalized = self._normalize(scores, direction)

        # 平移避免零值：x' = x + epsilon
        shifted = normalized + self.epsilon

        return shifted

    # =========================================================================
    # 信息熵计算
    # =========================================================================

    def _calculate_entropy(self, p: np.ndarray) -> float:
        """计算信息熵

        E = - (1 / ln(n)) * Σ(p_i * ln(p_i))

        Args:
            p: 概率分布向量 (Σ p_i = 1)

        Returns:
            归一化信息熵 (范围 [0, 1])

        Note:
            - E = 0: 完全确定（极端分布）
            - E = 1: 完全不确定（均匀分布）
        """
        n = len(p)

        # 过滤零值（避免 log(0)）
        p_valid = p[p > 0]

        # 计算熵
        entropy = -np.sum(p_valid * np.log(p_valid))

        # 归一化
        if n > 1:
            normalized_entropy = entropy / np.log(n)
        else:
            normalized_entropy = 0.0

        return float(normalized_entropy)

    # =========================================================================
    # 权重计算
    # =========================================================================

    def calculate_weights(
        self,
        decision_matrix: np.ndarray,
        directions: list[Literal["higher_better", "lower_better"]] | None = None
    ) -> np.ndarray:
        """计算客观权重

        Args:
            decision_matrix: 决策矩阵 (n_alternatives x n_criteria)
            directions: 准则方向列表（可选）
                - None: 默认所有准则为 "higher_better"
                - list: 每个准则的方向

        Returns:
            客观权重向量 (n_criteria,)

        Raises:
            EntropyWeightValidationError: 输入验证失败
        """
        # 验证输入
        self._validate_matrix(decision_matrix)

        n_alternatives, n_criteria = decision_matrix.shape

        # 默认方向
        if directions is None:
            directions = ["higher_better"] * n_criteria

        # 验证方向数量
        if len(directions) != n_criteria:
            raise ValueError(
                f"方向数量 ({len(directions)}) 必须等于准则数量 ({n_criteria})"
            )

        # 标准化每个准则
        normalized_matrix = np.zeros_like(decision_matrix, dtype=float)
        for j in range(n_criteria):
            normalized_matrix[:, j] = self._normalize_with_shift(
                decision_matrix[:, j],
                directions[j]
            )

        # 计算每个准则的比重矩阵
        p_matrix = np.zeros_like(normalized_matrix, dtype=float)
        for j in range(n_criteria):
            column_sum = np.sum(normalized_matrix[:, j])
            p_matrix[:, j] = normalized_matrix[:, j] / column_sum

        # 计算每个准则的信息熵
        entropies = np.zeros(n_criteria)
        for j in range(n_criteria):
            entropies[j] = self._calculate_entropy(p_matrix[:, j])

        # 计算差异系数
        divergence_coefficients = 1 - entropies

        # 计算权重（归一化差异系数）
        total_divergence = np.sum(divergence_coefficients)

        if total_divergence > 0:
            weights = divergence_coefficients / total_divergence
        else:
            # 所有准则的熵都为1（完全相同），均匀分配权重
            weights = np.ones(n_criteria) / n_criteria

        return weights

    def _validate_matrix(self, matrix: np.ndarray) -> None:
        """验证决策矩阵

        Args:
            matrix: 决策矩阵

        Raises:
            EntropyWeightValidationError: 验证失败
        """
        if not isinstance(matrix, np.ndarray):
            raise EntropyWeightValidationError(
                f"决策矩阵必须是 numpy 数组，当前类型: {type(matrix)}"
            )

        if matrix.size == 0:
            raise EntropyWeightValidationError("决策矩阵不能为空")

        if matrix.ndim != 2:
            raise EntropyWeightValidationError(
                f"决策矩阵必须是二维数组，当前维度: {matrix.ndim}"
            )

        n_alternatives, n_criteria = matrix.shape

        if n_alternatives < 2:
            raise EntropyWeightValidationError(
                f"至少需要 2 个备选方案，当前: {n_alternatives}"
            )

        if n_criteria < 1:
            raise EntropyWeightValidationError(
                f"至少需要 1 个准则，当前: {n_criteria}"
            )

        # 检查是否包含 NaN 或 Inf
        if np.any(np.isnan(matrix)):
            raise EntropyWeightValidationError("决策矩阵包含 NaN")

        if np.any(np.isinf(matrix)):
            raise EntropyWeightValidationError("决策矩阵包含无穷大值")

    # =========================================================================
    # 主客观权重组合
    # =========================================================================

    def combine_weights(
        self,
        subjective: np.ndarray,
        objective: np.ndarray,
        method: Literal["linear", "multiplicative"] = "linear",
        alpha: float = 0.5
    ) -> np.ndarray:
        """组合主客观权重

        Args:
            subjective: 主观权重向量
            objective: 客观权重向量
            method: 组合方法
                - linear: 线性加权: w = α*w_sub + (1-α)*w_obj
                - multiplicative: 乘法合成: w = (w_sub * w_obj) / Σ(w_sub * w_obj)
            alpha: 主观权重比例（仅用于 linear 方法）

        Returns:
            组合权重向量

        Raises:
            ValueError: 参数无效
        """
        # 验证输入
        if len(subjective) != len(objective):
            raise ValueError(
                f"主观权重长度 ({len(subjective)}) 必须等于 "
                f"客观权重长度 ({len(objective)})"
            )

        if method == "linear":
            if not 0 <= alpha <= 1:
                raise ValueError(f"alpha 必须在 [0, 1] 范围内，当前: {alpha}")

            combined = alpha * subjective + (1 - alpha) * objective

        elif method == "multiplicative":
            # 乘法合成后归一化
            product = subjective * objective
            combined = product / np.sum(product)

        else:
            raise ValueError(
                f"无效的组合方法: '{method}'. "
                f"必须是 'linear' 或 'multiplicative'"
            )

        return combined

    # =========================================================================
    # 完整工作流
    # =========================================================================

    def calculate_weights_with_details(
        self,
        decision_matrix: np.ndarray,
        criteria: list[str] | None = None,
        directions: list[Literal["higher_better", "lower_better"]] | None = None,
        subjective_weights: np.ndarray | None = None,
        alpha: float = 0.5
    ) -> dict[str, any]:
        """计算权重及详细信息（完整工作流）

        Args:
            decision_matrix: 决策矩阵 (n_alternatives x n_criteria)
            criteria: 准则名称列表（可选）
            directions: 准则方向列表（可选）
            subjective_weights: 主观权重（可选，用于组合）
            alpha: 主观权重比例（默认 0.5）

        Returns:
            包含以下键的字典:
            - weights: np.ndarray - 客观权重向量
            - entropies: np.ndarray - 信息熵向量
            - divergence_coefficients: np.ndarray - 差异系数向量
            - criteria: list[str] - 准则名称
            - combined_weights: np.ndarray - 组合权重（如果提供主观权重）
        """
        self._validate_matrix(decision_matrix)

        n_criteria = decision_matrix.shape[1]

        # 准则名称
        if criteria is None:
            criteria = [f"C{i+1}" for i in range(n_criteria)]

        # 计算客观权重
        weights = self.calculate_weights(decision_matrix, directions)

        # 计算熵值和差异系数
        # （重新计算以提供详细信息）
        normalized_matrix = np.zeros_like(decision_matrix, dtype=float)
        if directions is None:
            directions = ["higher_better"] * n_criteria

        for j in range(n_criteria):
            normalized_matrix[:, j] = self._normalize_with_shift(
                decision_matrix[:, j],
                directions[j]
            )

        entropies = np.zeros(n_criteria)
        p_matrix = np.zeros_like(normalized_matrix, dtype=float)

        for j in range(n_criteria):
            column_sum = np.sum(normalized_matrix[:, j])
            p_matrix[:, j] = normalized_matrix[:, j] / column_sum
            entropies[j] = self._calculate_entropy(p_matrix[:, j])

        divergence_coefficients = 1 - entropies

        # 构建结果
        result = {
            "weights": weights,
            "entropies": entropies,
            "divergence_coefficients": divergence_coefficients,
            "criteria": criteria,
        }

        # 如果提供了主观权重，计算组合权重
        if subjective_weights is not None:
            combined = self.combine_weights(
                subjective_weights,
                weights,
                method="linear",
                alpha=alpha
            )
            result["combined_weights"] = combined

        return result
