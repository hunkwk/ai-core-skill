"""
CRITIC 赋权方法

基于对比强度和冲突性的权重计算。
"""

from typing import Union
import numpy as np
from numpy.typing import NDArray


class CRITICWeightingError(Exception):
    """CRITIC 赋权错误"""
    pass


def critic_weighting(matrix: Union[NDArray, list]) -> NDArray:
    """
    CRITIC 赋权方法

    数学模型:
    1. 标准化决策矩阵 (Z-score)
    2. 计算标准差 (对比强度): σ_j = sqrt(Σ(x'_ij - μ'_j)² / (m-1))
    3. 计算相关系数 (冲突性): r_jk = correlation(j, k)
    4. 计算信息量: C_j = σ_j * Σ(1 - r_jk)
    5. 归一化权重: w_j = C_j / Σ(C_j)

    Args:
        matrix: 决策矩阵 (m 方案 × n 准则)

    Returns:
        权重向量 (n 维)

    Raises:
        CRITICWeightingError: 如果数据无效
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

    # 1. 标准化 (Z-score)
    matrix_std = _zscore(matrix, axis=0, ddof=1)

    # 处理 NaN (单值列)
    matrix_std = np.nan_to_num(matrix_std, nan=0.0)

    # 2. 计算标准差 (对比强度)
    std_dev = np.std(matrix_std, axis=0, ddof=1)

    # 处理零标准差
    if np.any(std_dev < 1e-10):
        # 所有准则标准差都接近 0,返回均匀权重
        if np.all(std_dev < 1e-10):
            return np.ones(n) / n
        # 零标准差准则设为最小非零值
        min_std = std_dev[std_dev > 1e-10].min()
        std_dev[std_dev < 1e-10] = min_std

    # 3. 计算相关系数矩阵 (冲突性)
    try:
        corr_matrix = np.corrcoef(matrix_std.T)
    except Exception:
        # 如果相关系数计算失败,使用单位矩阵
        corr_matrix = np.eye(n)

    # 处理 NaN (单值列导致的相关系数)
    corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)

    # 确保对角线为 1
    np.fill_diagonal(corr_matrix, 1.0)

    # 4. 计算信息量
    # C_j = σ_j * Σ(1 - r_jk)
    conflict = np.sum(1 - corr_matrix, axis=1)
    information = std_dev * conflict

    # 处理零信息量
    if np.all(np.isclose(information, 0)):
        return np.ones(n) / n

    # 5. 归一化权重
    weights = information / np.sum(information)

    return weights


def _zscore(a: NDArray, axis: int = 0, ddof: int = 0) -> NDArray:
    """
    计算 Z-score 标准化

    Args:
        a: 输入数组
        axis: 计算轴
        ddof: 自由度调整

    Returns:
        标准化后的数组
    """
    mean = np.mean(a, axis=axis)
    std = np.std(a, axis=axis, ddof=ddof)

    # 避免除零
    std[std < 1e-10] = 1.0

    # 广播计算
    if axis == 0:
        return (a - mean) / std
    else:
        return (a - mean[:, np.newaxis]) / std[:, np.newaxis]


def _validate_input(matrix: Union[NDArray, list]) -> NDArray:
    """验证并转换输入"""
    if matrix is None:
        raise CRITICWeightingError("决策矩阵不能为 None")

    # 转换为 numpy array
    if not isinstance(matrix, np.ndarray):
        try:
            matrix = np.array(matrix, dtype=float)
        except (ValueError, TypeError) as e:
            raise CRITICWeightingError(f"无法转换数据类型: {type(matrix)}") from e

    # 检查维度
    if matrix.ndim != 2:
        raise CRITICWeightingError(f"决策矩阵必须是 2D, 当前维度: {matrix.ndim}")

    if matrix.shape[0] < 1 or matrix.shape[1] < 1:
        raise CRITICWeightingError(
            f"决策矩阵形状无效: {matrix.shape}, 至少需要 1×1"
        )

    # 检查 NaN
    if np.any(np.isnan(matrix)):
        raise CRITICWeightingError("决策矩阵包含 NaN")

    # 检查 Inf
    if np.any(np.isinf(matrix)):
        raise CRITICWeightingError("决策矩阵包含无穷值")

    return matrix
