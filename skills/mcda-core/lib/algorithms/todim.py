"""
TODIM 算法实现

基于前景理论的多准则决策排序算法。
"""

from typing import Union
import numpy as np
from numpy.typing import NDArray
from ..models import DecisionProblem, Criterion, RankingItem, DecisionResult, ResultMetadata


class TODIMError(Exception):
    """TODIM 算法错误"""
    pass


def todim(
    problem: DecisionProblem,
    theta: float = 1.0
) -> DecisionResult:
    """TODIM 算法实现

    数学模型:
    1. 相对测度: φ_ij^k = √(w_k * (x_ik - x_jk) / Σw)  当 x_ik > x_jk
                     φ_ij^k = -√(Σw/w_k * (x_jk - x_ik) / (θ * Σw))  当 x_ik < x_jk

    2. 优势度: δ(A_i, A_j) = Σ φ_ij^k

    3. 全局优势度: ξ(A_i) = Σ δ(A_i, A_j) - Σ δ(A_j, A_i)

    4. 排序: 按全局优势度降序

    Args:
        problem: 决策问题
        theta: 衰减系数 (推荐 1.0-2.5)

    Returns:
        决策结果

    Raises:
        TODIMError: 如果参数无效
    """
    # 参数验证
    if theta <= 0:
        raise TODIMError(f"theta 必须 > 0, 当前值: {theta}")

    alternatives = problem.alternatives
    criteria = problem.criteria
    scores = problem.scores

    n_alt = len(alternatives)
    n_crit = len(criteria)

    if n_alt < 2:
        raise TODIMError("至少需要 2 个备选方案")

    if n_crit < 1:
        raise TODIMError("至少需要 1 个准则")

    # 1. 提取权重
    weights = np.array([c.weight for c in criteria])
    total_weight = weights.sum()

    if total_weight <= 0:
        raise TODIMError("准则权重总和必须 > 0")

    # 2. 构建得分矩阵
    scores_matrix = np.zeros((n_alt, n_crit))
    for i, alt in enumerate(alternatives):
        for k, crit in enumerate(criteria):
            scores_matrix[i, k] = scores[alt][crit.name]

    # 3. 计算相对测度矩阵 φ
    phi = _compute_phi_matrix(
        scores_matrix,
        weights,
        criteria,
        theta,
        total_weight
    )

    # 4. 计算优势度矩阵
    dominance = np.sum(phi, axis=2)  # (n_alt, n_alt)

    # 5. 计算全局优势度
    global_dominance = np.zeros(n_alt)
    for i in range(n_alt):
        global_dominance[i] = dominance[i, :].sum() - dominance[:, i].sum()

    # 6. 排序 (降序)
    sorted_indices = np.argsort(-global_dominance)

    # 构建排名 (使用密集排名 dense ranking，确保排名连续 1, 2, 3, ...)
    rankings = []
    current_rank = 1  # 当前排名

    for i, idx in enumerate(sorted_indices):
        # 检查是否与前一个元素并列（分数相同）
        if i > 0:
            prev_idx = sorted_indices[i - 1]
            # 使用近似比较处理浮点数精度
            if not np.isclose(global_dominance[idx], global_dominance[prev_idx]):
                # 分数不同，排名递增 1
                current_rank += 1
            # 如果分数相同，保持 current_rank 不变（并列）

        rankings.append(RankingItem(
            rank=current_rank,
            alternative=alternatives[idx],
            score=float(global_dominance[idx])
        ))

    # 构建元数据
    metadata = ResultMetadata(
        algorithm_name="todim",
        problem_size=(n_alt, n_crit),
        metrics={
            "theta": theta,
            "global_dominance": global_dominance.tolist(),
            "phi_matrix_shape": phi.shape,
        }
    )

    # 构建原始得分
    raw_scores = {alt: float(global_dominance[i]) for i, alt in enumerate(alternatives)}

    return DecisionResult(
        rankings=rankings,
        raw_scores=raw_scores,
        metadata=metadata
    )


def _compute_phi_matrix(
    scores_matrix: NDArray,
    weights: NDArray,
    criteria: tuple,
    theta: float,
    total_weight: float
) -> NDArray:
    """计算相对测度矩阵 φ

    Args:
        scores_matrix: 得分矩阵 (n_alt, n_crit)
        weights: 权重向量 (n_crit,)
        criteria: 准则元组
        theta: 衰减系数
        total_weight: 权重总和

    Returns:
        相对测度矩阵 (n_alt, n_alt, n_crit)
    """
    n_alt, n_crit = scores_matrix.shape

    # 初始化相对测度矩阵
    phi = np.zeros((n_alt, n_alt, n_crit))

    # 计算相对测度
    for k in range(n_crit):
        # 跳过零权重准则
        if weights[k] <= 0:
            continue

        for i in range(n_alt):
            for j in range(n_alt):
                if i == j:
                    continue

                score_i = scores_matrix[i, k]
                score_j = scores_matrix[j, k]

                # 根据准则方向调整
                if criteria[k].direction == "lower_better":
                    # 成本型: 反转比较
                    diff = score_j - score_i
                else:
                    # 效益型: 正常比较
                    diff = score_i - score_j

                # 计算相对测度
                if diff > 0:
                    # 收益: 使用权重增益
                    phi[i, j, k] = np.sqrt(
                        weights[k] * abs(diff) / total_weight
                    )
                elif diff < 0:
                    # 损失: 使用衰减系数 (前景理论)
                    phi[i, j, k] = -np.sqrt(
                        total_weight / weights[k] * abs(diff) / (theta * total_weight)
                    )
                else:
                    # 差异为零
                    phi[i, j, k] = 0.0

    return phi
