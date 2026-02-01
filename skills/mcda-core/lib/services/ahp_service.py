"""
AHP (层次分析法) 权重计算服务

实现 AHP 算法的核心功能：
- 成对比较矩阵验证
- 权重计算（特征向量法）
- 一致性检验

References:
- Saaty, T. L. (1980). The Analytic Hierarchy Process.
"""

import numpy as np
from typing import Literal


class AHPValidationError(Exception):
    """AHP 验证错误

    当成对比较矩阵不满足要求时抛出。
    """
    pass


class AHPService:
    """AHP (层次分析法) 服务

    提供基于成对比较矩阵的权重计算和一致性检验功能。

    Example:
        ```python
        service = AHPService()

        # 成对比较矩阵
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        # 计算权重
        weights = service.calculate_weights(matrix)

        # 计算一致性比率
        cr = service.calculate_consistency_ratio(matrix)

        # 完整工作流
        result = service.calculate_weights_with_consistency(
            matrix,
            criteria=["成本", "质量", "功能"]
        )
        ```
    """

    # 随机一致性指标 (Random Index)
    # 来源: Saaty (1980)
    _RANDOM_INDICES = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }

    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-6):
        """初始化 AHP 服务

        Args:
            max_iterations: 幂法最大迭代次数
            tolerance: 收敛容忍度
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    # =========================================================================
    # 矩阵验证
    # =========================================================================

    def _validate_matrix(self, matrix: np.ndarray) -> None:
        """验证成对比较矩阵

        Args:
            matrix: 成对比较矩阵 (n x n)

        Raises:
            AHPValidationError: 矩阵不满足要求
        """
        if not isinstance(matrix, np.ndarray):
            raise AHPValidationError(
                f"矩阵必须是 numpy 数组，当前类型: {type(matrix)}"
            )

        if matrix.size == 0:
            raise AHPValidationError("矩阵不能为空")

        if matrix.ndim != 2:
            raise AHPValidationError(
                f"矩阵必须是二维数组，当前维度: {matrix.ndim}"
            )

        n, m = matrix.shape

        if n != m:
            raise AHPValidationError(
                f"成对比较矩阵必须是方阵，当前形状: {matrix.shape}"
            )

        # 检查对角线是否为 1
        for i in range(n):
            if not np.isclose(matrix[i, i], 1.0):
                raise AHPValidationError(
                    f"对角线元素必须为 1，a[{i},{i}] = {matrix[i, i]}"
                )

        # 检查所有元素是否为正数
        if np.any(matrix <= 0):
            raise AHPValidationError("矩阵元素必须全部为正数")

        # 检查互反性: a_ij = 1 / a_ji
        for i in range(n):
            for j in range(i + 1, n):
                if not np.isclose(matrix[i, j], 1.0 / matrix[j, i], rtol=1e-5):
                    raise AHPValidationError(
                        f"矩阵不满足互反性: "
                        f"a[{i},{j}] = {matrix[i, j]}, "
                        f"a[{j},{i}] = {matrix[j, i]}, "
                        f"期望 a[{j},{i}] = {1.0 / matrix[i, j]}"
                    )

    # =========================================================================
    # 权重计算（特征向量法 - 幂法）
    # =========================================================================

    def calculate_weights(self, matrix: np.ndarray) -> np.ndarray:
        """计算权重向量（特征向量法）

        使用幂法迭代计算最大特征值对应的特征向量，
        并归一化得到权重。

        Args:
            matrix: 成对比较矩阵 (n x n)

        Returns:
            归一化权重向量 (n,)

        Raises:
            AHPValidationError: 矩阵验证失败
        """
        # 验证矩阵
        self._validate_matrix(matrix)

        n = matrix.shape[0]

        # 特殊情况：1x1 矩阵
        if n == 1:
            return np.array([1.0])

        # 初始化权重向量（均匀分布）
        weights = np.ones(n) / n

        # 幂法迭代
        for _ in range(self.max_iterations):
            # 计算新权重: w_new = A * w
            new_weights = np.dot(matrix, weights)

            # 归一化
            new_weights = new_weights / np.sum(new_weights)

            # 检查收敛
            if np.allclose(new_weights, weights, atol=self.tolerance):
                break

            weights = new_weights

        return weights

    # =========================================================================
    # 一致性检验
    # =========================================================================

    def calculate_consistency_ratio(
        self, matrix: np.ndarray
    ) -> float:
        """计算一致性比率

        CR = CI / RI
        其中:
        - CI = (λ_max - n) / (n - 1) (一致性指标)
        - RI = 随机一致性指标

        Args:
            matrix: 成对比较矩阵

        Returns:
            一致性比率 CR

        Note:
            - CR < 0.1: 可接受的一致性
            - CR >= 0.1: 需要重新评估成对比较
        """
        self._validate_matrix(matrix)

        n = matrix.shape[0]

        # 特殊情况：n <= 2，总是完全一致的
        if n <= 2:
            return 0.0

        # 计算权重
        weights = self.calculate_weights(matrix)

        # 计算最大特征值
        lambda_max = self._calculate_lambda_max(matrix, weights)

        # 计算一致性指标
        ci = self._calculate_consistency_index(lambda_max, n)

        # 获取随机一致性指标
        ri = self._get_random_index(n)

        # 计算一致性比率
        cr = ci / ri if ri > 0 else 0.0

        return cr

    def _calculate_lambda_max(
        self, matrix: np.ndarray, weights: np.ndarray
    ) -> float:
        """计算最大特征值

        λ_max = (1/n) * Σ(A * w)_i / w_i

        Args:
            matrix: 成对比较矩阵
            weights: 权重向量

        Returns:
            最大特征值
        """
        n = matrix.shape[0]

        # 计算 A * w
        aw = np.dot(matrix, weights)

        # λ_max = (1/n) * Σ(aw_i / w_i)
        lambda_max = np.mean(aw / weights)

        return float(lambda_max)

    def _calculate_consistency_index(
        self, lambda_max: float, n: int
    ) -> float:
        """计算一致性指标

        CI = (λ_max - n) / (n - 1)

        Args:
            lambda_max: 最大特征值
            n: 矩阵大小

        Returns:
            一致性指标
        """
        if n <= 1:
            return 0.0

        ci = (lambda_max - n) / (n - 1)
        return float(ci)

    def _get_random_index(self, n: int) -> float:
        """获取随机一致性指标

        对于 n > 10，使用线性插值。

        Args:
            n: 矩阵大小

        Returns:
            随机一致性指标 RI
        """
        if n in self._RANDOM_INDICES:
            return self._RANDOM_INDICES[n]

        # 对于 n > 10，使用线性插值
        # RI(n) ≈ 1.49 + (n - 10) * 0.1
        if n > 10:
            ri_10 = self._RANDOM_INDICES[10]
            # 简单线性外推
            return ri_10 + (n - 10) * 0.1

        # 不应该到达这里
        raise ValueError(f"无法获取 n={n} 的随机一致性指标")

    # =========================================================================
    # 完整工作流
    # =========================================================================

    def calculate_weights_with_consistency(
        self,
        matrix: np.ndarray,
        criteria: list[str] | None = None
    ) -> dict[str, any]:
        """计算权重及一致性检验（完整工作流）

        Args:
            matrix: 成对比较矩阵 (n x n)
            criteria: 准则名称列表（可选）

        Returns:
            包含以下键的字典:
            - weights: np.ndarray - 权重向量
            - consistency_ratio: float - 一致性比率
            - criteria: list[str] - 准则名称
            - lambda_max: float - 最大特征值
            - acceptable: bool - 一致性是否可接受 (CR < 0.1)

        Example:
            ```python
            service = AHPService()
            matrix = np.array([
                [1, 3, 5],
                [1/3, 1, 2],
                [1/5, 1/2, 1]
            ])

            result = service.calculate_weights_with_consistency(
                matrix,
                criteria=["成本", "质量", "功能"]
            )

            print(f"权重: {result['weights']}")
            print(f"一致性比率: {result['consistency_ratio']:.3f}")
            print(f"可接受: {result['acceptable']}")
            ```
        """
        self._validate_matrix(matrix)

        n = matrix.shape[0]

        # 计算权重
        weights = self.calculate_weights(matrix)

        # 计算一致性比率
        cr = self.calculate_consistency_ratio(matrix)

        # 计算最大特征值
        lambda_max = self._calculate_lambda_max(matrix, weights)

        # 判断一致性是否可接受
        acceptable = cr < 0.1

        # 准则名称
        if criteria is None:
            criteria = [f"C{i+1}" for i in range(n)]

        return {
            "weights": weights,
            "consistency_ratio": cr,
            "criteria": criteria,
            "lambda_max": lambda_max,
            "acceptable": acceptable,
        }
