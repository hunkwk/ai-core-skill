"""
变异系数法赋权

基于数据离散程度的客观权重计算。
"""

import numpy as np
from numpy.typing import NDArray


class CVWeightingError(Exception):
    """变异系数法赋权错误"""
    pass


def cv_weighting(matrix: NDArray | list) -> NDArray:
    """
    变异系数法赋权

    数学模型:
    1. 计算均值: μ_j = Σ(x_ij) / m
    2. 计算标准差: σ_j = sqrt(Σ(x_ij - μ_j)² / (m-1))
    3. 计算变异系数: CV_j = σ_j / |μ_j|
    4. 归一化权重: w_j = CV_j / Σ(CV_j)

    Args:
        matrix: 决策矩阵 (m 方案 × n 准则)

    Returns:
        权重向量 (n 维)

    Raises:
        CVWeightingError: 如果数据无效
    """
    # 输入验证
    matrix = _validate_input(matrix)

    m, n = matrix.shape  # m 方案, n 准则

    # 特殊情况: 单准则
    if n == 1:
        return np.array([1.0])

    # 特殊情况: 单方案 (返回均匀权重)
    if m == 1:
        return np.ones(n) / n

    # 1. 计算均值
    means = np.mean(matrix, axis=0)

    # 2. 计算标准差
    stds = np.std(matrix, axis=0, ddof=1)

    # 3. 计算变异系数
    # CV_j = σ_j / |μ_j|
    # 避免除零: 使用绝对均值
    abs_means = np.abs(means)
    abs_means[abs_means < 1e-10] = 1.0  # 避免除零

    cvs = stds / abs_means

    # 4. 检查所有 CV 是否为零
    if np.all(cvs < 1e-10):
        # 所有准则变异相同，返回均匀权重
        return np.ones(n) / n

    # 5. 归一化权重
    weights = cvs / np.sum(cvs)

    return weights


def _validate_input(matrix: NDArray | list) -> NDArray:
    """验证并转换输入"""
    if matrix is None:
        raise CVWeightingError("决策矩阵不能为 None")

    # 转换为 numpy array
    if not isinstance(matrix, np.ndarray):
        try:
            matrix = np.array(matrix, dtype=float)
        except (ValueError, TypeError) as e:
            raise CVWeightingError(f"无法转换数据类型: {type(matrix)}") from e

    # 检查维度
    if matrix.ndim != 2:
        raise CVWeightingError(f"决策矩阵必须是 2D, 当前维度: {matrix.ndim}")

    if matrix.shape[0] < 1 or matrix.shape[1] < 1:
        raise CVWeightingError(
            f"决策矩阵形状无效: {matrix.shape}, 至少需要 1×1"
        )

    # 检查 NaN
    if np.any(np.isnan(matrix)):
        raise CVWeightingError("决策矩阵包含 NaN")

    # 检查 Inf
    if np.any(np.isinf(matrix)):
        raise CVWeightingError("决策矩阵包含无穷值")

    return matrix
