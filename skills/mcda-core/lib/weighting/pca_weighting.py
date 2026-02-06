"""
主成分分析赋权 (PCA Weighting)

基于主成分分析的客观权重计算。

核心思想:
通过特征值分解协方差矩阵，提取主成分的方差贡献率作为权重。
高方差准则代表更多信息量，应获得更高权重。

数学模型:
1. 标准化决策矩阵: z_ij = (x_ij - μ_j) / σ_j
2. 计算协方差矩阵: C = Z^T · Z / (n-1)
3. 特征值分解: C · v_k = λ_k · v_k
4. 提取主成分权重: w_j = Σ λ_k · v_kj² / Σ λ_k

References:
    - Jolliffe, I.T. (2002). Principal Component Analysis
"""

import numpy as np
from numpy.typing import NDArray


class PCAWeightingError(Exception):
    """PCA 赋权错误

    当输入数据不满足要求或计算过程出现错误时抛出。
    """
    pass


# PCA 准则数量限制
MAX_CRITERIA = 50


def pca_weighting(matrix: NDArray | list) -> NDArray:
    """
    主成分分析赋权

    通过特征值分解提取主成分的方差贡献率作为权重。

    数学模型:
    1. 标准化决策矩阵 (Z-score)
    2. 计算协方差矩阵（含正则化）
    3. 特征值分解 (使用 np.linalg.eigh)
    4. 提取主成分权重

    Args:
        matrix: 决策矩阵 (m 方案 × n 准则)

    Returns:
        权重向量 (n 维)

    Raises:
        PCAWeightingError: 如果数据无效或准则超过限制

    Example:
        ```python
        import numpy as np
        from mcda_core.weighting.pca_weighting import pca_weighting

        matrix = np.array([
            [10, 50, 100],
            [12, 60, 90],
            [8, 40, 110],
        ])

        weights = pca_weighting(matrix)
        # array([0.3, 0.3, 0.4])  # 示例输出
        ```
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

    # 1. 标准化决策矩阵
    standardized = _standardize(matrix)

    # 2. 计算协方差矩阵（含正则化）
    covariance = _compute_covariance(standardized)

    # 3. 特征值分解
    eigenvalues, eigenvectors = _eigen_decomposition(covariance)

    # 4. 提取主成分权重
    weights = _extract_weights(eigenvalues, eigenvectors)

    return weights


def _validate_input(matrix: NDArray | list) -> NDArray:
    """验证并转换输入

    Args:
        matrix: 输入决策矩阵

    Returns:
        验证后的 numpy 数组

    Raises:
        PCAWeightingError: 如果数据无效
    """
    if matrix is None:
        raise PCAWeightingError("决策矩阵不能为 None")

    # 转换为 numpy array
    if not isinstance(matrix, np.ndarray):
        try:
            matrix = np.array(matrix, dtype=float)
        except (ValueError, TypeError) as e:
            raise PCAWeightingError(f"无法转换数据类型: {type(matrix)}") from e

    # 检查维度
    if matrix.ndim != 2:
        raise PCAWeightingError(f"决策矩阵必须是 2D, 当前维度: {matrix.ndim}")

    if matrix.shape[0] < 1 or matrix.shape[1] < 1:
        raise PCAWeightingError(
            f"决策矩阵形状无效: {matrix.shape}, 至少需要 1×1"
        )

    # 检查准则数量限制
    n_criteria = matrix.shape[1]
    if n_criteria > MAX_CRITERIA:
        raise PCAWeightingError(
            f"PCA 不支持超过 {MAX_CRITERIA} 个准则, 当前: {n_criteria}"
        )

    # 检查 NaN
    if np.any(np.isnan(matrix)):
        raise PCAWeightingError("决策矩阵包含 NaN")

    # 检查 Inf
    if np.any(np.isinf(matrix)):
        raise PCAWeightingError("决策矩阵包含无穷值")

    return matrix


def _standardize(matrix: NDArray) -> NDArray:
    """标准化决策矩阵 (Z-score)

    z_ij = (x_ij - μ_j) / σ_j

    Args:
        matrix: 原始决策矩阵

    Returns:
        标准化后的矩阵
    """
    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0, ddof=1)

    # 避免除零
    stds[stds < 1e-10] = 1.0

    standardized = (matrix - means) / stds
    return standardized


def _compute_covariance(standardized: NDArray) -> NDArray:
    """计算协方差矩阵（含正则化）

    C = X^T · X / (n-1)

    添加正则化避免数值不稳定:
    C += ε · I

    Args:
        standardized: 标准化后的决策矩阵

    Returns:
        协方差矩阵
    """
    m, n = standardized.shape

    # 计算协方差矩阵
    covariance = np.dot(standardized.T, standardized) / (m - 1)

    # 添加正则化避免数值不稳定
    epsilon = 1e-10
    covariance += np.eye(n) * epsilon

    return covariance


def _eigen_decomposition(covariance: NDArray) -> tuple[NDArray, NDArray]:
    """特征值分解

    使用 np.linalg.eigh 进行对称矩阵特征值分解（更稳定）

    Args:
        covariance: 协方差矩阵

    Returns:
        (特征值, 特征向量) 元组
    """
    # 使用 eigh 处理对称矩阵（数值更稳定）
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)

    # 确保特征值非负（数值误差可能产生微小负值）
    eigenvalues = np.maximum(eigenvalues, 0)

    # 按特征值降序排序
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    return eigenvalues, eigenvectors


def _extract_weights(
    eigenvalues: NDArray,
    eigenvectors: NDArray
) -> NDArray:
    """提取主成分权重

    w_j = Σ λ_k · v_kj² / Σ λ_k

    使用向量化操作提高效率。

    Args:
        eigenvalues: 特征值向量
        eigenvectors: 特征向量矩阵

    Returns:
        权重向量
    """
    n = len(eigenvalues)
    total_variance = np.sum(eigenvalues)

    # 处理零方差情况
    if total_variance < 1e-10:
        # 所有特征值接近 0，返回均匀权重
        return np.ones(n) / n

    # 向量化计算权重
    # w_j = Σ λ_k · v_kj² / Σ λ_k
    # 使用 (eigenvectors ** 2) 计算每个元素平方
    # 然后 @ eigenvalues 进行加权求和
    squared_loadings = eigenvectors ** 2
    weights = squared_loadings @ eigenvalues / total_variance

    return weights
