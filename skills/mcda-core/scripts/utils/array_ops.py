"""
NumPy 矩阵运算优化工具

提供高性能的矩阵运算和向量化操作
"""

import numpy as np
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .models import DecisionProblem

    MetricType = Literal['euclidean', 'manhattan', 'chebyshev']


def scores_to_numpy(problem: 'DecisionProblem') -> np.ndarray:
    """将评分字典转换为 NumPy 数组

    Args:
        problem: 决策问题对象

    Returns:
        np.ndarray: 形状为 (n_alternatives, n_criteria) 的数组

    Note:
        - 方案按字母顺序排序
        - 准则按 name 属性排序
        - 数据类型为 float64
    """
    alternatives = sorted(problem.alternatives)
    criteria = sorted(problem.criteria, key=lambda c: c.name)

    # 构建评分矩阵
    scores_matrix = []
    for alt in alternatives:
        row = [problem.scores[alt][crit.name] for crit in criteria]
        scores_matrix.append(row)

    return np.array(scores_matrix, dtype=np.float64)


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """向量标准化（L2 范数）

    Args:
        vector: 输入向量

    Returns:
        np.ndarray: 标准化后的向量（单位向量）

    Note:
        如果输入是零向量，返回原向量
    """
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector.copy()

    return vector / norm


def normalize_matrix(matrix: np.ndarray, axis: int = 0) -> np.ndarray:
    """矩阵标准化

    Args:
        matrix: 输入矩阵
        axis: 标准化轴（0=按列，1=按行）

    Returns:
        np.ndarray: 标准化后的矩阵
    """
    if axis == 0:
        # 按列标准化
        norms = np.linalg.norm(matrix, axis=0)
        norms[norms == 0] = 1  # 避免除零
        return matrix / norms
    else:
        # 按行标准化
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # 避免除零
        return matrix / norms


def compute_distance_matrix(
    matrix: np.ndarray,
    metric: 'MetricType' = 'euclidean'
) -> np.ndarray:
    """计算距离矩阵

    Args:
        matrix: 输入矩阵 (n_samples, n_features)
        metric: 距离度量类型
            - 'euclidean': 欧氏距离
            - 'manhattan': 曼哈顿距离
            - 'chebyshev': 切比雪夫距离

    Returns:
        np.ndarray: 距离矩阵 (n_samples, n_samples)

    Note:
        使用向量化计算，避免循环
    """
    if metric == 'euclidean':
        # 使用 scipy 的 cdist 更快
        try:
            from scipy.spatial.distance import cdist
            return cdist(matrix, matrix, metric='euclidean')
        except ImportError:
            # 如果 scipy 不可用，使用 NumPy 实现
            # 利用 ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a^T*b
            norm_matrix = np.sum(matrix ** 2, axis=1)
            distance_matrix = norm_matrix[:, None] + norm_matrix[None, :] - 2 * matrix @ matrix.T
            # 确保数值稳定性
            distance_matrix = np.maximum(distance_matrix, 0)
            return np.sqrt(distance_matrix)

    elif metric == 'manhattan':
        # 曼哈顿距离
        try:
            from scipy.spatial.distance import cdist
            return cdist(matrix, matrix, metric='cityblock')
        except ImportError:
            # NumPy 实现
            n = matrix.shape[0]
            distance_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    d = np.sum(np.abs(matrix[i] - matrix[j]))
                    distance_matrix[i, j] = d
                    distance_matrix[j, i] = d
            return distance_matrix

    elif metric == 'chebyshev':
        # 切比雪夫距离
        try:
            from scipy.spatial.distance import cdist
            return cdist(matrix, matrix, metric='chebyshev')
        except ImportError:
            # NumPy 实现
            n = matrix.shape[0]
            distance_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    d = np.max(np.abs(matrix[i] - matrix[j]))
                    distance_matrix[i, j] = d
                    distance_matrix[j, i] = d
            return distance_matrix

    else:
        raise ValueError(f"未知的距离度量: {metric}")


def compute_ideal_solution(
    normalized_matrix: np.ndarray,
    directions: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """计算理想解和负理想解

    Args:
        normalized_matrix: 标准化矩阵 (n_alternatives, n_criteria)
        directions: 方向数组 (n_criteria,)，1=效益型，-1=成本型

    Returns:
        tuple: (理想解, 负理想解)

    Note:
        TOPSIS 算法核心步骤
    """
    # 效益型准则：取最大值
    # 成本型准则：取最小值
    ideal = np.where(directions == 1, np.max(normalized_matrix, axis=0),
                    np.min(normalized_matrix, axis=0))

    # 负理想解
    negative_ideal = np.where(directions == 1, np.min(normalized_matrix, axis=0),
                             np.max(normalized_matrix, axis=0))

    return ideal, negative_ideal


def compute_separations(
    normalized_matrix: np.ndarray,
    ideal: np.ndarray,
    negative_ideal: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """计算到理想解和负理想解的距离

    Args:
        normalized_matrix: 标准化矩阵 (n_alternatives, n_criteria)
        ideal: 理想解 (n_criteria,)
        negative_ideal: 负理想解 (n_criteria,)

    Returns:
        tuple: (到理想解的距离, 到负理想解的距离)

    Note:
        使用欧氏距离
    """
    # 到理想解的距离
    distance_to_ideal = np.linalg.norm(normalized_matrix - ideal, axis=1)

    # 到负理想解的距离
    distance_to_negative_ideal = np.linalg.norm(normalized_matrix - negative_ideal, axis=1)

    return distance_to_ideal, distance_to_negative_ideal


def compute_closeness(
    distance_to_ideal: np.ndarray,
    distance_to_negative_ideal: np.ndarray
) -> np.ndarray:
    """计算贴近度

    Args:
        distance_to_ideal: 到理想解的距离 (n_alternatives,)
        distance_to_negative_ideal: 到负理想解的距离 (n_alternatives,)

    Returns:
        np.ndarray: 贴近度 (n_alternatives,)

    Note:
        贴近度范围 [0, 1]，越大越好
    """
    total = distance_to_ideal + distance_to_negative_ideal

    # 避免除零
    total[total == 0] = 1.0

    return distance_to_negative_ideal / total
