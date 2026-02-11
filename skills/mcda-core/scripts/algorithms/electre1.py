"""
ELECTRE-I 算法实现

基于级别优于关系 (Outranking Relation) 的多准则决策排序算法。
"""

import numpy as np
from numpy.typing import NDArray
from ..models import DecisionProblem, Criterion, RankingItem, DecisionResult, ResultMetadata


class ELECTRE1Error(Exception):
    """ELECTRE-I 算法错误"""
    pass


def electre1(
    problem: DecisionProblem,
    alpha: float = 0.6,
    beta: float = 0.3
) -> DecisionResult:
    """ELECTRE-I 算法实现

    数学模型:
    1. 和谐指数: c(A_i, A_j) = Σ w_k * I_k(A_i, A_j) / Σ w_k
       其中 I_k(A_i, A_j) 是指示函数 (1 或 0)

    2. 不和谐指数: d_k(A_i, A_j) = max(0, x_jk - x_ik) / (max_k - min_k)
       全局不和谐: d(A_i, A_j) = max_k d_k(A_i, A_j)

    3. 可信度: σ(A_i, A_j) = 1  如果 c(A_i, A_j) ≥ α 且 d(A_i, A_j) ≤ β
                 σ(A_i, A_j) = 0  否则

    4. 核提取: 找出非被优方案集合 (Kernel)

    Args:
        problem: 决策问题
        alpha: 和谐度阈值 (0 < α ≤ 1, 推荐 0.5-0.7)
        beta: 不和谐度阈值 (0 ≤ β ≤ 1, 推荐 0.2-0.4)

    Returns:
        决策结果

    Raises:
        ELECTRE1Error: 如果参数无效
    """
    # 参数验证
    if alpha <= 0 or alpha > 1:
        raise ELECTRE1Error(f"alpha 必须在 (0, 1] 范围内, 当前值: {alpha}")

    if beta < 0 or beta > 1:
        raise ELECTRE1Error(f"beta 必须在 [0, 1] 范围内, 当前值: {beta}")

    alternatives = problem.alternatives
    criteria = problem.criteria
    scores = problem.scores

    n_alt = len(alternatives)
    n_crit = len(criteria)

    if n_alt < 2:
        raise ELECTRE1Error("至少需要 2 个备选方案")

    if n_crit < 1:
        raise ELECTRE1Error("至少需要 1 个准则")

    # 1. 提取权重
    weights = np.array([c.weight for c in criteria])
    total_weight = weights.sum()

    if total_weight <= 0:
        raise ELECTRE1Error("准则权重总和必须 > 0")

    # 2. 构建得分矩阵
    scores_matrix = np.zeros((n_alt, n_crit))
    for i, alt in enumerate(alternatives):
        for k, crit in enumerate(criteria):
            scores_matrix[i, k] = scores[alt][crit.name]

    # 3. 计算和谐矩阵
    concordance = _compute_concordance_matrix(
        scores_matrix,
        weights,
        criteria,
        total_weight
    )

    # 4. 计算不和谐矩阵
    discordance = _compute_discordance_matrix(
        scores_matrix,
        criteria
    )

    # 5. 计算可信度矩阵
    credibility = _compute_credibility_matrix(
        concordance,
        discordance,
        alpha,
        beta
    )

    # 6. 构建级别优于关系并提取核
    kernel = _extract_kernel(credibility, alternatives)

    # 7. 构建排名 (核内方案排名靠前,按原始得分排序)
    rankings = _build_rankings(kernel, alternatives, credibility, scores_matrix)

    # 8. 构建元数据
    metadata = ResultMetadata(
        algorithm_name="electre1",
        problem_size=(n_alt, n_crit),
        metrics={
            "alpha": alpha,
            "beta": beta,
            "concordance_matrix": concordance.tolist(),
            "discordance_matrix": discordance.tolist(),
            "credibility_matrix": credibility.tolist(),
            "kernel": kernel,
        }
    )

    # 9. 构建原始得分
    # ELECTRE-I 没有明确的得分，使用可信度总和作为得分
    raw_scores = {}
    for i, alt in enumerate(alternatives):
        # 可信度总和作为优势度
        raw_scores[alt] = float(np.sum(credibility[i, :]))

    return DecisionResult(
        rankings=rankings,
        raw_scores=raw_scores,
        metadata=metadata
    )


def _compute_concordance_matrix(
    scores_matrix: NDArray,
    weights: NDArray,
    criteria: tuple,
    total_weight: float
) -> NDArray:
    """计算和谐矩阵

    Args:
        scores_matrix: 得分矩阵 (n_alt, n_crit)
        weights: 权重向量 (n_crit,)
        criteria: 准则元组
        total_weight: 权重总和

    Returns:
        和谐矩阵 (n_alt, n_alt)
    """
    n_alt, n_crit = scores_matrix.shape

    # 初始化和谐矩阵
    concordance = np.zeros((n_alt, n_alt))

    # 计算每对方案的和谐指数
    for i in range(n_alt):
        for j in range(n_alt):
            if i == j:
                continue

            concordant_weight = 0.0

            for k in range(n_crit):
                score_i = scores_matrix[i, k]
                score_j = scores_matrix[j, k]

                # 指示函数: 检查 A_i 是否不劣于 A_j 在准则 k 上
                if criteria[k].direction == "higher_better":
                    # 效益型: A_i ≥ A_j
                    if score_i >= score_j:
                        concordant_weight += weights[k]
                else:
                    # 成本型: A_i ≤ A_j
                    if score_i <= score_j:
                        concordant_weight += weights[k]

            # 归一化和谐指数
            concordance[i, j] = concordant_weight / total_weight

    return concordance


def _compute_discordance_matrix(
    scores_matrix: NDArray,
    criteria: tuple
) -> NDArray:
    """计算不和谐矩阵

    Args:
        scores_matrix: 得分矩阵 (n_alt, n_crit)
        criteria: 准则元组

    Returns:
        不和谐矩阵 (n_alt, n_alt)
    """
    n_alt, n_crit = scores_matrix.shape

    # 初始化不和谐矩阵
    discordance = np.zeros((n_alt, n_alt))

    # 计算每个准则的范围
    criterion_ranges = []
    for k in range(n_crit):
        col = scores_matrix[:, k]
        min_val = np.min(col)
        max_val = np.max(col)
        range_val = max_val - min_val

        if range_val < 1e-10:
            range_val = 1.0  # 避免除零

        criterion_ranges.append(range_val)

    # 计算每对方案的全局不和谐指数
    for i in range(n_alt):
        for j in range(n_alt):
            if i == j:
                continue

            max_discordance = 0.0

            for k in range(n_crit):
                score_i = scores_matrix[i, k]
                score_j = scores_matrix[j, k]

                # 根据准则方向调整
                if criteria[k].direction == "higher_better":
                    # 效益型: A_i < A_j 时才有不和谐
                    if score_i < score_j:
                        diff = score_j - score_i
                        discordance_k = diff / criterion_ranges[k]
                        max_discordance = max(max_discordance, discordance_k)
                else:
                    # 成本型: A_i > A_j 时才有不和谐
                    if score_i > score_j:
                        diff = score_i - score_j
                        discordance_k = diff / criterion_ranges[k]
                        max_discordance = max(max_discordance, discordance_k)

            discordance[i, j] = max_discordance

    return discordance


def _compute_credibility_matrix(
    concordance: NDArray,
    discordance: NDArray,
    alpha: float,
    beta: float
) -> NDArray:
    """计算可信度矩阵

    可信度条件:
    - c(A_i, A_j) ≥ α (和谐度足够高)
    - d(A_i, A_j) ≤ β (不和谐度足够低)

    Args:
        concordance: 和谐矩阵 (n_alt, n_alt)
        discordance: 不和谐矩阵 (n_alt, n_alt)
        alpha: 和谐度阈值
        beta: 不和谐度阈值

    Returns:
        可信度矩阵 (n_alt, n_alt)
    """
    n_alt = concordance.shape[0]

    # 初始化可信度矩阵
    credibility = np.zeros((n_alt, n_alt))

    # 计算可信度
    for i in range(n_alt):
        for j in range(n_alt):
            if i == j:
                credibility[i, j] = 0.0
            else:
                # 检查和谐度和不和谐度条件
                if concordance[i, j] >= alpha and discordance[i, j] <= beta:
                    credibility[i, j] = 1.0
                else:
                    credibility[i, j] = 0.0

    return credibility


def _extract_kernel(
    credibility: NDArray,
    alternatives: tuple
) -> list:
    """提取核 (Kernel)

    核 = 非被优方案集合 = {A_i | 不存在 j 使得 σ(A_j, A_i) = 1}

    Args:
        credibility: 可信度矩阵 (n_alt, n_alt)
        alternatives: 方案元组

    Returns:
        核中的方案列表
    """
    n_alt = credibility.shape[0]

    # 找出非被优方案
    kernel = []
    for i in range(n_alt):
        is_dominated = False

        for j in range(n_alt):
            if credibility[j, i] == 1.0:
                # 存在 A_j 优于 A_i
                is_dominated = True
                break

        if not is_dominated:
            kernel.append(alternatives[i])

    return kernel


def _build_rankings(
    kernel: list,
    alternatives: tuple,
    credibility: NDArray,
    scores_matrix: NDArray
) -> list:
    """构建排名

    核内的方案排名靠前，核外的方案排在后面
    同组内按原始得分总和降序排列

    Args:
        kernel: 核中的方案列表
        alternatives: 所有方案元组
        credibility: 可信度矩阵
        scores_matrix: 得分矩阵

    Returns:
        RankingItem 列表
    """
    rankings = []

    # 计算所有方案的原始得分总和
    all_scores = []
    for i, alt in enumerate(alternatives):
        # 使用原始得分总和,不是可信度总和
        raw_score = np.sum(scores_matrix[i, :])
        in_kernel = alt in kernel
        all_scores.append((alt, raw_score, in_kernel))

    # 排序: 先按是否在核中 (核内优先),再按原始得分降序
    # (not in_kernel, -raw_score) 的排序结果是: 核内在前,得分高在前
    all_scores.sort(key=lambda x: (not x[2], -x[1]), reverse=False)

    # 分配连续排名 - 每个方案都有唯一排名
    current_rank = 1
    for i, (alt, raw_score, in_kernel) in enumerate(all_scores):
        # score字段存储原始得分总和
        rankings.append(RankingItem(
            rank=current_rank,
            alternative=alt,
            score=float(raw_score)
        ))
        # 每个元素排名递增 (不管得分是否相同)
        current_rank += 1

    return rankings
