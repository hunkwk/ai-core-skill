"""
PROMETHEE-II 算法实现

基于偏好函数的排序方法。

References:
- Brans, J. P., & Vincke, P. (1985). A preference ranking organisation method.
- Behzadian, M., et al. (2010). A comprehensive literature review on PROMETHEE.
"""

import numpy as np
from typing import Literal


class PROMETHEEValidationError(Exception):
    """PROMETHEE 验证错误

    当输入数据不满足要求时抛出。
    """
    pass


class PROMETHEEService:
    """PROMETHEE-II 排序服务

    基于偏好函数的排序方法：
    1. 定义偏好函数
    2. 计算偏好指数
    3. 计算流量（leaving, entering, net）
    4. 完整排序

    Example:
        ```python
        service = PROMETHEEService()

        # 决策矩阵 (n_alternatives x n_criteria)
        decision_matrix = np.array([
            [80, 5, 100],   # 方案 A
            [90, 3, 120],   # 方案 B
            [70, 7, 90],    # 方案 C
        ])

        # 准则权重
        weights = np.array([0.4, 0.3, 0.3])

        # 偏好函数配置
        preference_functions = [
            {"type": "v_shape_indifference", "q": 5.0, "p": 15.0},
            {"type": "level", "q": 1.0, "p": 3.0},
            {"type": "gaussian", "s": 10.0}
        ]

        # 计算排序
        result = service.rank(
            decision_matrix,
            weights,
            preference_functions,
            alternatives=["A", "B", "C"]
        )

        # 结果
        rankings = result["rankings"]  # 排序后的方案
        net_flows = result["net_flows"]  # 净流量
        ```
    """

    def __init__(self):
        """初始化 PROMETHEE-II 服务"""
        pass

    # =========================================================================
    # 偏好函数
    # =========================================================================

    def _usual_criterion(self, d: float) -> float:
        """通常准则

        P(d) = 0  if d ≤ 0
        P(d) = 1  if d > 0

        Args:
            d: 差异值

        Returns:
            偏好度
        """
        return 1.0 if d > 0 else 0.0

    def _u_shape_criterion(self, d: float, q: float) -> float:
        """U型准则

        P(d) = 0       if |d| ≤ q
        P(d) = 1       if |d| > q

        Args:
            d: 差异值
            q: 无差异阈值

        Returns:
            偏好度
        """
        return 0.0 if abs(d) <= q else 1.0

    def _v_shape_criterion(self, d: float, p: float) -> float:
        """V型准则

        P(d) = 0       if d ≤ 0
        P(d) = d/p     if 0 < d ≤ p
        P(d) = 1       if d > p

        Args:
            d: 差异值
            p: 严格偏好阈值

        Returns:
            偏好度
        """
        if d <= 0:
            return 0.0
        elif d <= p:
            return d / p
        else:
            return 1.0

    def _level_criterion(self, d: float, q: float, p: float) -> float:
        """水平准则

        P(d) = 0            if |d| ≤ q
        P(d) = 0.5          if q < |d| ≤ p
        P(d) = 1            if |d| > p

        Args:
            d: 差异值
            q: 无差异阈值
            p: 严格偏好阈值

        Returns:
            偏好度
        """
        abs_d = abs(d)
        if abs_d <= q:
            return 0.0
        elif abs_d <= p:
            return 0.5
        else:
            return 1.0

    def _v_shape_indifference(self, d: float, q: float, p: float) -> float:
        """V型无差异准则

        P(d) = 0              if |d| ≤ q
        P(d) = (|d|-q)/(p-q)  if q < |d| ≤ p
        P(d) = 1              if |d| > p

        Args:
            d: 差异值
            q: 无差异阈值
            p: 严格偏好阈值

        Returns:
            偏好度
        """
        abs_d = abs(d)
        if abs_d <= q:
            return 0.0
        elif abs_d <= p:
            return (abs_d - q) / (p - q)
        else:
            return 1.0

    def _gaussian_criterion(self, d: float, s: float) -> float:
        """高斯准则

        P(d) = 1 - exp(-d²/2σ²)

        Args:
            d: 差异值
            s: 标准差参数 σ

        Returns:
            偏好度
        """
        return 1.0 - np.exp(-(d ** 2) / (2 * s ** 2))

    def _get_preference_function(self, func_type: str):
        """获取偏好函数

        Args:
            func_type: 函数类型

        Returns:
            偏好函数

        Raises:
            ValueError: 无效的函数类型
        """
        functions = {
            "usual": self._usual_criterion,
            "u_shape": self._u_shape_criterion,
            "v_shape": self._v_shape_criterion,
            "level": self._level_criterion,
            "v_shape_indifference": self._v_shape_indifference,
            "gaussian": self._gaussian_criterion,
        }

        if func_type not in functions:
            raise ValueError(
                f"无效的偏好函数类型: '{func_type}'. "
                f"必须是以下之一: {list(functions.keys())}"
            )

        return functions[func_type]

    # =========================================================================
    # 偏好指数计算
    # =========================================================================

    def _calculate_preference_index(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        preference_functions: list[dict]
    ) -> np.ndarray:
        """计算偏好指数矩阵

        Args:
            decision_matrix: 决策矩阵 (n_alternatives x n_criteria)
            weights: 准则权重 (n_criteria,)
            preference_functions: 偏好函数配置列表

        Returns:
            偏好指数矩阵 (n_alternatives x n_alternatives)
        """
        n_alternatives, n_criteria = decision_matrix.shape

        # 初始化偏好指数矩阵
        preference_index = np.zeros((n_alternatives, n_alternatives))

        # 计算每对方案的偏好度
        for a in range(n_alternatives):
            for b in range(n_alternatives):
                if a == b:
                    preference_index[a, b] = 0.0
                    continue

                # 对每个准则计算偏好度
                for j in range(n_criteria):
                    func_config = preference_functions[j]
                    func_type = func_config["type"]
                    func = self._get_preference_function(func_type)

                    # 计算差异 d = a_j - b_j
                    d = decision_matrix[a, j] - decision_matrix[b, j]

                    # 根据函数类型调用
                    if func_type == "usual":
                        p_j = func(d)
                    elif func_type == "u_shape":
                        p_j = func(d, func_config["q"])
                    elif func_type == "v_shape":
                        p_j = func(d, func_config["p"])
                    elif func_type == "level":
                        p_j = func(d, func_config["q"], func_config["p"])
                    elif func_type == "v_shape_indifference":
                        p_j = func(d, func_config["q"], func_config["p"])
                    elif func_type == "gaussian":
                        p_j = func(d, func_config["s"])
                    else:
                        p_j = 0.0

                    # 加权累加
                    preference_index[a, b] += weights[j] * p_j

        return preference_index

    # =========================================================================
    # 流量计算
    # =========================================================================

    def _calculate_leaving_flow(self, preference_matrix: np.ndarray) -> np.ndarray:
        """计算离开流

        Φ⁺(a) = (1/n) * Σ_b P(a, b)

        Args:
            preference_matrix: 偏好指数矩阵

        Returns:
            离开流向量
        """
        n = preference_matrix.shape[0]
        return np.sum(preference_matrix, axis=1) / n

    def _calculate_entering_flow(self, preference_matrix: np.ndarray) -> np.ndarray:
        """计算进入流

        Φ⁻(a) = (1/n) * Σ_b P(b, a)

        Args:
            preference_matrix: 偏好指数矩阵

        Returns:
            进入流向量
        """
        n = preference_matrix.shape[0]
        return np.sum(preference_matrix, axis=0) / n

    def _calculate_net_flow(
        self,
        leaving_flow: np.ndarray,
        entering_flow: np.ndarray
    ) -> np.ndarray:
        """计算净流量

        Φ(a) = Φ⁺(a) - Φ⁻(a)

        Args:
            leaving_flow: 离开流向量
            entering_flow: 进入流向量

        Returns:
            净流量向量
        """
        return leaving_flow - entering_flow

    # =========================================================================
    # 验证
    # =========================================================================

    def _validate_inputs(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        preference_functions: list[dict]
    ) -> None:
        """验证输入

        Args:
            decision_matrix: 决策矩阵
            weights: 准则权重
            preference_functions: 偏好函数配置

        Raises:
            PROMETHEEValidationError: 验证失败
        """
        # 验证决策矩阵
        if not isinstance(decision_matrix, np.ndarray):
            raise PROMETHEEValidationError(
                f"决策矩阵必须是 numpy 数组，当前类型: {type(decision_matrix)}"
            )

        if decision_matrix.ndim != 2:
            raise PROMETHEEValidationError(
                f"决策矩阵必须是二维数组，当前维度: {decision_matrix.ndim}"
            )

        n_alternatives, n_criteria = decision_matrix.shape

        if n_alternatives < 2:
            raise PROMETHEEValidationError(
                f"至少需要 2 个备选方案，当前: {n_alternatives}"
            )

        if n_criteria < 1:
            raise PROMETHEEValidationError(
                f"至少需要 1 个准则，当前: {n_criteria}"
            )

        # 检查 NaN 或 Inf
        if np.any(np.isnan(decision_matrix)):
            raise PROMETHEEValidationError("决策矩阵包含 NaN")

        if np.any(np.isinf(decision_matrix)):
            raise PROMETHEEValidationError("决策矩阵包含无穷大值")

        # 验证权重
        if len(weights) != n_criteria:
            raise ValueError(
                f"权重数量 ({len(weights)}) 必须等于准则数量 ({n_criteria})"
            )

        if np.any(weights < 0):
            raise PROMETHEEValidationError("权重不能为负数")

        weights_sum = np.sum(weights)
        if not np.isclose(weights_sum, 1.0, atol=0.01):
            raise PROMETHEEValidationError(
                f"权重之和必须为 1，当前: {weights_sum}"
            )

        # 验证偏好函数
        if len(preference_functions) != n_criteria:
            raise ValueError(
                f"偏好函数数量 ({len(preference_functions)}) 必须等于 "
                f"准则数量 ({n_criteria})"
            )

    # =========================================================================
    # 完整工作流
    # =========================================================================

    def rank(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        preference_functions: list[dict],
        alternatives: list[str] | None = None
    ) -> dict[str, any]:
        """计算 PROMETHEE-II 排序

        Args:
            decision_matrix: 决策矩阵 (n_alternatives x n_criteria)
            weights: 准则权重 (n_criteria,)
            preference_functions: 偏好函数配置列表
            alternatives: 方案名称列表（可选）

        Returns:
            包含以下键的字典:
            - rankings: list[dict] - 排序后的方案
            - net_flows: np.ndarray - 净流量向量
            - leaving_flows: np.ndarray - 离开流向量
            - entering_flows: np.ndarray - 进入流向量
            - preference_matrix: np.ndarray - 偏好指数矩阵
        """
        # 验证输入
        self._validate_inputs(decision_matrix, weights, preference_functions)

        n_alternatives = decision_matrix.shape[0]

        # 方案名称
        if alternatives is None:
            alternatives = [f"A{i}" for i in range(n_alternatives)]

        # 计算偏好指数矩阵
        preference_matrix = self._calculate_preference_index(
            decision_matrix,
            weights,
            preference_functions
        )

        # 计算流量
        leaving_flows = self._calculate_leaving_flow(preference_matrix)
        entering_flows = self._calculate_entering_flow(preference_matrix)
        net_flows = self._calculate_net_flow(leaving_flows, entering_flows)

        # 排序（按净流量降序）
        sorted_indices = np.argsort(-net_flows)

        rankings = [
            {
                "rank": idx + 1,
                "alternative": alternatives[i],
                "net_flow": net_flows[i],
                "leaving_flow": leaving_flows[i],
                "entering_flow": entering_flows[i],
            }
            for idx, i in enumerate(sorted_indices)
        ]

        return {
            "rankings": rankings,
            "net_flows": net_flows,
            "leaving_flows": leaving_flows,
            "entering_flows": entering_flows,
            "preference_matrix": preference_matrix,
        }
