"""
ELECTRE-I 区间版本算法实现

基于级别优于关系 (Outranking Relation) 的多准则决策排序算法的区间数版本。
支持不确定性和模糊性。
"""

from typing import Any, TYPE_CHECKING
import numpy as np
from numpy.typing import NDArray

from .base import MCDAAlgorithm, register_algorithm

# 类型注解导入
if TYPE_CHECKING:
    from ..models import DecisionProblem, DecisionResult, Criterion
    from ..interval import Interval


@register_algorithm("electre1_interval")
class ELECTRE1IntervalAlgorithm(MCDAAlgorithm):
    """ELECTRE-I 算法（区间版本）

    核心思想: 基于级别优于关系进行排序（支持区间数）

    数学模型:
        1. 区间和谐指数:
           C(A_i, A_j) = [C^L, C^U]
           基于区间比较的和谐度计算

        2. 区间不和谐指数:
           D(A_i, A_j) = [D^L, D^U]
           基于区间差异的不和谐度计算

        3. 可信度: σ(A_i, A_j) = 1  如果 C^U ≥ α 且 D^L ≤ β
                   σ(A_i, A_j) = 0  否则

        4. 核提取: 找出非被优方案集合 (Kernel)

    参数:
        alpha: 和谐度阈值 (0 < α ≤ 1, 推荐 0.5-0.7)
        beta: 不和谐度阈值 (0 ≤ β ≤ 1, 推荐 0.2-0.4)

    适用场景:
        - 需要级别优于关系的决策（带不确定性）
        - 评分是区间数
        - 不需要完全排序，只需要核（最优方案集合）

    特点:
        - 基于级别优于关系
        - 支持区间数输入
        - 提供核（非被优方案集合）
        - 参数 alpha 和 beta 控制严格程度
    """

    def __init__(self, alpha: float = 0.6, beta: float = 0.3):
        """初始化 ELECTRE-I 区间版本算法

        Args:
            alpha: 和谐度阈值 (0 < α ≤ 1)，默认 0.6
            beta: 不和谐度阈值 (0 ≤ β ≤ 1)，默认 0.3
        """
        if not 0 < alpha <= 1:
            raise ValueError(f"alpha 必须在 (0, 1] 范围内，当前: {alpha}")

        if not 0 <= beta <= 1:
            raise ValueError(f"beta 必须在 [0, 1] 范围内，当前: {beta}")

        self.alpha = alpha
        self.beta = beta

    @property
    def name(self) -> str:
        """算法名称"""
        return "electre1_interval"

    @property
    def description(self) -> str:
        """算法描述"""
        return "ELECTRE-I 级别优于关系法 - 区间版本"

    def calculate(
        self,
        problem: "DecisionProblem",
        alpha: float | None = None,
        beta: float | None = None,
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 ELECTRE-I 区间版本计算

        Args:
            problem: 决策问题（评分可以是区间数）
            alpha: 和谐度阈值（可选，覆盖构造函数的值）
            beta: 不和谐度阈值（可选，覆盖构造函数的值）
            **kwargs: 未使用的其他参数

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from ..models import DecisionResult, RankingItem, ResultMetadata
        from ..interval import Interval

        # 验证输入
        self.validate(problem)

        # 使用参数或默认值
        if alpha is None:
            alpha = self.alpha
        elif not 0 < alpha <= 1:
            raise ValueError(f"alpha 必须在 (0, 1] 范围内，当前: {alpha}")

        if beta is None:
            beta = self.beta
        elif not 0 <= beta <= 1:
            raise ValueError(f"beta 必须在 [0, 1] 范围内，当前: {beta}")

        # 获取备选方案和准则
        alternatives = problem.alternatives
        criteria = problem.criteria

        n_alt = len(alternatives)
        n_crit = len(criteria)

        if n_alt < 2:
            raise ValueError("至少需要 2 个备选方案")

        if n_crit < 1:
            raise ValueError("至少需要 1 个准则")

        # 1. 提取权重
        weights = np.array([c.weight for c in criteria])
        total_weight = weights.sum()

        if total_weight <= 0:
            raise ValueError("准则权重总和必须 > 0")

        # 2. 构建得分矩阵（处理区间数）
        scores_matrix = np.zeros((n_alt, n_crit), dtype=object)
        for i, alt in enumerate(alternatives):
            for k, crit in enumerate(criteria):
                scores_matrix[i, k] = problem.scores[alt][crit.name]

        # 3. 计算和谐矩阵（基于可能度）
        concordance = self._compute_concordance_matrix(
            scores_matrix,
            weights,
            criteria,
            total_weight
        )

        # 4. 计算不和谐矩阵（基于区间差）
        discordance = self._compute_discordance_matrix(
            scores_matrix,
            criteria
        )

        # 5. 计算可信度矩阵
        credibility = self._compute_credibility_matrix(
            concordance,
            discordance,
            alpha,
            beta
        )

        # 6. 提取核
        kernel = self._extract_kernel(credibility, alternatives)

        # 7. 构建排名（核内方案排名靠前）
        rankings = self._build_rankings(kernel, alternatives, credibility)

        # 8. 构建元数据
        metadata = ResultMetadata(
            algorithm_name="electre1_interval",
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

        # 9. 构建原始得分（使用可信度总和）
        raw_scores = {}
        for i, alt in enumerate(alternatives):
            raw_scores[alt] = float(np.sum(credibility[i, :]))

        return DecisionResult(
            rankings=rankings,
            raw_scores=raw_scores,
            metadata=metadata
        )

    def _compute_concordance_matrix(
        self,
        scores_matrix: NDArray,
        weights: NDArray,
        criteria: tuple["Criterion", ...],
        total_weight: float
    ) -> NDArray:
        """计算和谐矩阵

        对于区间数版本，使用区间中点进行比较，并结合区间重叠信息。

        Args:
            scores_matrix: 得分矩阵 (n_alt, n_crit)，元素可能是区间数
            weights: 权重向量 (n_crit,)
            criteria: 准则元组
            total_weight: 权重总和

        Returns:
            和谐矩阵 (n_alt, n_alt)
        """
        from ..interval import Interval

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

                    # 获取中点用于比较
                    if isinstance(score_i, Interval):
                        midpoint_i = score_i.midpoint
                    else:
                        midpoint_i = float(score_i)

                    if isinstance(score_j, Interval):
                        midpoint_j = score_j.midpoint
                    else:
                        midpoint_j = float(score_j)

                    # 指示函数: 检查 A_i 是否不劣于 A_j 在准则 k 上
                    if criteria[k].direction == "higher_better":
                        # 效益型: A_i ≥ A_j
                        if midpoint_i >= midpoint_j:
                            concordant_weight += weights[k]
                    else:
                        # 成本型: A_i ≤ A_j
                        if midpoint_i <= midpoint_j:
                            concordant_weight += weights[k]

                # 归一化和谐指数
                concordance[i, j] = concordant_weight / total_weight

        return concordance

    def _compute_discordance_matrix(
        self,
        scores_matrix: NDArray,
        criteria: tuple["Criterion", ...]
    ) -> NDArray:
        """计算不和谐矩阵

        对于区间数版本，使用区间上界和下界计算最大不和谐度。

        Args:
            scores_matrix: 得分矩阵 (n_alt, n_crit)，元素可能是区间数
            criteria: 准则元组

        Returns:
            不和谐矩阵 (n_alt, n_alt)
        """
        from ..interval import Interval

        n_alt, n_crit = scores_matrix.shape

        # 初始化不和谐矩阵
        discordance = np.zeros((n_alt, n_alt))

        # 计算每个准则的范围（基于区间端点）
        criterion_ranges = []
        for k in range(n_crit):
            min_val = float('inf')
            max_val = float('-inf')

            for i in range(n_alt):
                val = scores_matrix[i, k]
                if isinstance(val, Interval):
                    min_val = min(min_val, val.lower)
                    max_val = max(max_val, val.upper)
                else:
                    min_val = min(min_val, float(val))
                    max_val = max(max_val, float(val))

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

                    # 获取比较值（对于区间，使用最不利情况）
                    if isinstance(score_i, Interval):
                        val_i_lower = score_i.lower
                        val_i_upper = score_i.upper
                    else:
                        val_i_lower = float(score_i)
                        val_i_upper = float(score_i)

                    if isinstance(score_j, Interval):
                        val_j_lower = score_j.lower
                        val_j_upper = score_j.upper
                    else:
                        val_j_lower = float(score_j)
                        val_j_upper = float(score_j)

                    # 根据准则方向调整
                    if criteria[k].direction == "higher_better":
                        # 效益型: 最坏情况是 i 的下界 < j 的上界
                        if val_i_lower < val_j_upper:
                            diff = val_j_upper - val_i_lower
                            discordance_k = diff / criterion_ranges[k]
                            max_discordance = max(max_discordance, discordance_k)
                    else:
                        # 成本型: 最坏情况是 i 的上界 > j 的下界
                        if val_i_upper > val_j_lower:
                            diff = val_i_upper - val_j_lower
                            discordance_k = diff / criterion_ranges[k]
                            max_discordance = max(max_discordance, discordance_k)

                discordance[i, j] = max_discordance

        return discordance

    def _compute_credibility_matrix(
        self,
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
        self,
        credibility: NDArray,
        alternatives: tuple
    ) -> list:
        """提取核 (Kernel)

        核 = 非被优方案集合 = {A_i | 不存在 j 使得 σ(A_j, A_i) = 1}

        Args:
            credibility: 可信度矩阵 (n_alt, n_alt)
            alternatives: 备选方案元组

        Returns:
            核中的方案名称列表
        """
        n_alt = len(alternatives)

        # 核：不被任何其他方案优的方案
        kernel = []

        for i in range(n_alt):
            is_dominated = False

            # 检查是否有方案 j 优于方案 i
            for j in range(n_alt):
                if i != j and credibility[j, i] == 1.0:
                    is_dominated = True
                    break

            if not is_dominated:
                kernel.append(alternatives[i])

        return kernel

    def _build_rankings(
        self,
        kernel: list,
        alternatives: tuple,
        credibility: NDArray
    ) -> list["RankingItem"]:
        """构建排名

        核内方案排名靠前，按可信度总和排序

        Args:
            kernel: 核中的方案列表
            alternatives: 所有备选方案
            credibility: 可信度矩阵

        Returns:
            排名列表
        """
        from ..models import RankingItem

        # 计算每个方案的优势度（可信度总和）
        dominance_score = {}
        for i, alt in enumerate(alternatives):
            dominance_score[alt] = np.sum(credibility[i, :])

        # 排序：核内方案优先，然后按优势度降序
        sorted_alts = sorted(
            alternatives,
            key=lambda alt: (
                0 if alt in kernel else 1,  # 核内优先
                -dominance_score[alt]  # 优势度降序
            )
        )

        # 构建 RankingItem 列表
        rankings = []
        for rank, alt in enumerate(sorted_alts, start=1):
            rankings.append(
                RankingItem(
                    alternative=alt,
                    rank=rank,
                    score=float(dominance_score[alt])
                )
            )

        return rankings
