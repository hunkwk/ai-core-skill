"""
PROMETHEE II 区间版本算法实现

基于净流量 (Net Flow) 的多准则决策排序算法的区间数版本。
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


@register_algorithm("promethee2_interval")
class PROMETHEE2IntervalAlgorithm(MCDAAlgorithm):
    """PROMETHEE II 算法（区间版本）

    核心思想: 基于净流量进行排序（支持区间数）

    数学模型:
        1. 区间偏好指数:
           P(a, b) = Σ w_j · p_j(a, b)
           其中 p_j(a, b) 是基于区间差的偏好函数值

        2. 正流量: Φ^+(a) = Σ P(a, b)
        3. 负流量: Φ^-(a) = Σ P(b, a)
        4. 净流量: Φ(a) = Φ^+(a) - Φ^-(a)

        5. 排序: 根据 Φ(a) 降序排列

    参数:
        preference_function: 偏好函数类型
            - "usual": 通常型（阶跃函数）
            - "u_shape": U 型（阶跃函数，有阈值）
            - "v_shape": V 型（线性函数，有阈值）
            - "level": 水平型（线性函数，有 indifference 阈值）
            - "linear": 线性型（分段线性函数）
        threshold: 阈值参数（用于 U 型和 V 型偏好函数）

    适用场景:
        - 需要完全排序的决策（带不确定性）
        - 评分是区间数
        - 需要考虑偏好函数

    特点:
        - 基于净流量排序
        - 支持区间数输入
        - 提供完全排序
        - 支持多种偏好函数
    """

    def __init__(
        self,
        preference_function: str = "usual",
        threshold: float = 0.0
    ):
        """初始化 PROMETHEE II 区间版本算法

        Args:
            preference_function: 偏好函数类型，默认 "usual"
            threshold: 阈值参数，默认 0.0
        """
        valid_functions = ["usual", "u_shape", "v_shape", "level", "linear"]

        if preference_function not in valid_functions:
            raise ValueError(
                f"preference_function 必须是 {valid_functions} 之一，"
                f"当前: {preference_function}"
            )

        if threshold < 0:
            raise ValueError(f"threshold 必须非负，当前: {threshold}")

        self.preference_function = preference_function
        self.threshold = threshold

    @property
    def name(self) -> str:
        """算法名称"""
        return "promethee2_interval"

    @property
    def description(self) -> str:
        """算法描述"""
        return "PROMETHEE II 净流量法 - 区间版本"

    def calculate(
        self,
        problem: "DecisionProblem",
        preference_function: str | None = None,
        threshold: float | None = None,
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 PROMETHEE II 区间版本计算

        Args:
            problem: 决策问题（评分可以是区间数）
            preference_function: 偏好函数类型（可选，覆盖构造函数的值）
            threshold: 阈值参数（可选，覆盖构造函数的值）
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
        if preference_function is None:
            preference_function = self.preference_function
        elif preference_function not in ["usual", "u_shape", "v_shape", "level", "linear"]:
            raise ValueError(f"无效的 preference_function: {preference_function}")

        if threshold is None:
            threshold = self.threshold
        elif threshold < 0:
            raise ValueError(f"threshold 必须非负，当前: {threshold}")

        # 使用基类的验证方法
        self.validate(problem)

        # 获取备选方案和准则
        alternatives = problem.alternatives
        criteria = problem.criteria

        n_alt = len(alternatives)
        n_crit = len(criteria)

        # 1. 提取权重
        weights = np.array([c.weight for c in criteria])

        # 2. 构建得分矩阵（处理区间数）
        scores_matrix = np.zeros((n_alt, n_crit), dtype=object)
        for i, alt in enumerate(alternatives):
            for k, crit in enumerate(criteria):
                scores_matrix[i, k] = problem.scores[alt][crit.name]

        # 3. 计算偏好矩阵
        preference_matrix = self._compute_preference_matrix(
            scores_matrix,
            criteria,
            preference_function,
            threshold
        )

        # 4. 计算正流量、负流量和净流量
        positive_flow, negative_flow, net_flow = self._compute_flows(
            preference_matrix,
            weights,
            alternatives
        )

        # 5. 构建排名（按净流量降序）
        rankings = self._build_rankings(net_flow, alternatives)

        # 6. 构建元数据
        metadata = ResultMetadata(
            algorithm_name="promethee2_interval",
            problem_size=(n_alt, n_crit),
            metrics={
                "preference_function": preference_function,
                "threshold": threshold,
                "positive_flow": positive_flow,
                "negative_flow": negative_flow,
                "net_flow": net_flow,
            }
        )

        # 7. 构建原始得分（使用净流量）
        raw_scores = net_flow.copy()

        return DecisionResult(
            rankings=rankings,
            raw_scores=raw_scores,
            metadata=metadata
        )

    def _compute_preference_matrix(
        self,
        scores_matrix: NDArray,
        criteria: tuple["Criterion", ...],
        preference_function: str,
        threshold: float
    ) -> NDArray:
        """计算偏好矩阵

        对于每对方案 (a, b)，计算在每个准则上的偏好度。

        Args:
            scores_matrix: 得分矩阵 (n_alt, n_crit)，元素可能是区间数
            criteria: 准则元组
            preference_function: 偏好函数类型
            threshold: 阈值参数

        Returns:
            偏好矩阵 (n_alt, n_alt, n_crit)
        """
        from ..interval import Interval

        n_alt, n_crit = scores_matrix.shape

        # 初始化偏好矩阵
        preference = np.zeros((n_alt, n_alt, n_crit))

        # 计算每对方案在每个准则上的偏好度
        for i in range(n_alt):
            for j in range(n_alt):
                if i == j:
                    continue

                for k in range(n_crit):
                    score_i = scores_matrix[i, k]
                    score_j = scores_matrix[j, k]

                    # 获取中点用于比较
                    if isinstance(score_i, Interval):
                        val_i = score_i.midpoint
                    else:
                        val_i = float(score_i)

                    if isinstance(score_j, Interval):
                        val_j = score_j.midpoint
                    else:
                        val_j = float(score_j)

                    # 根据准则方向调整差值
                    if criteria[k].direction == "higher_better":
                        diff = val_i - val_j
                    else:
                        diff = val_j - val_i  # 成本型反转

                    # 计算偏好度
                    preference[i, j, k] = self._apply_preference_function(
                        diff, preference_function, threshold
                    )

        return preference

    def _apply_preference_function(
        self,
        diff: float,
        preference_function: str,
        threshold: float
    ) -> float:
        """应用偏好函数

        Args:
            diff: 差值
            preference_function: 偏好函数类型
            threshold: 阈值参数

        Returns:
            偏好度（0-1 之间）
        """
        if preference_function == "usual":
            # 通常型：P(d) = 1 if d > 0, else 0
            return 1.0 if diff > 0 else 0.0

        elif preference_function == "u_shape":
            # U 型：P(d) = 0 if d <= q, else 1
            if threshold <= 0:
                threshold = 1e-6
            return 0.0 if diff <= threshold else 1.0

        elif preference_function == "v_shape":
            # V 型：P(d) = 0 if d <= 0, else d/p if 0 < d < p, else 1
            if threshold <= 0:
                threshold = 1.0
            if diff <= 0:
                return 0.0
            elif diff >= threshold:
                return 1.0
            else:
                return diff / threshold

        elif preference_function == "level":
            # 水平型：P(d) = 0 if d <= q, else 0.5 if q < d < p, else 1
            q = threshold
            p = threshold * 2 if threshold > 0 else 1.0
            if diff <= q:
                return 0.0
            elif diff >= p:
                return 1.0
            else:
                return 0.5

        elif preference_function == "linear":
            # 线性型：P(d) = 0 if d <= q, else (d-q)/(p-q) if q < d < p, else 1
            q = threshold
            p = threshold * 2 if threshold > 0 else 1.0
            if diff <= q:
                return 0.0
            elif diff >= p:
                return 1.0
            else:
                return (diff - q) / (p - q)

        else:
            # 默认使用通常型
            return 1.0 if diff > 0 else 0.0

    def _compute_flows(
        self,
        preference_matrix: NDArray,
        weights: NDArray,
        alternatives: tuple
    ) -> tuple[dict, dict, dict]:
        """计算正流量、负流量和净流量

        Args:
            preference_matrix: 偏好矩阵 (n_alt, n_alt, n_crit)
            weights: 权重向量 (n_crit,)
            alternatives: 备选方案元组

        Returns:
            (正流量字典, 负流量字典, 净流量字典)
        """
        n_alt = len(alternatives)
        n_crit = len(weights)

        # 初始化流量字典
        positive_flow = {}
        negative_flow = {}
        net_flow = {}

        for i, alt in enumerate(alternatives):
            # 计算正流量：方案 i 优于其他方案的程度
            phi_plus = 0.0
            for j in range(n_alt):
                if i == j:
                    continue
                for k in range(n_crit):
                    phi_plus += weights[k] * preference_matrix[i, j, k]

            # 计算负流量：其他方案优于方案 i 的程度
            phi_minus = 0.0
            for j in range(n_alt):
                if i == j:
                    continue
                for k in range(n_crit):
                    phi_minus += weights[k] * preference_matrix[j, i, k]

            # 归一化（除以方案数 - 1）
            if n_alt > 1:
                phi_plus /= (n_alt - 1)
                phi_minus /= (n_alt - 1)

            # 计算净流量
            phi = phi_plus - phi_minus

            positive_flow[alt] = float(phi_plus)
            negative_flow[alt] = float(phi_minus)
            net_flow[alt] = float(phi)

        return positive_flow, negative_flow, net_flow

    def _build_rankings(
        self,
        net_flow: dict,
        alternatives: tuple
    ) -> list["RankingItem"]:
        """构建排名

        按净流量降序排序。

        Args:
            net_flow: 净流量字典
            alternatives: 所有备选方案

        Returns:
            排名列表
        """
        from ..models import RankingItem

        # 按净流量降序排序
        sorted_alts = sorted(
            alternatives,
            key=lambda alt: net_flow[alt],
            reverse=True
        )

        # 构建 RankingItem 列表
        rankings = []
        for rank, alt in enumerate(sorted_alts, start=1):
            rankings.append(
                RankingItem(
                    alternative=alt,
                    rank=rank,
                    score=float(net_flow[alt])
                )
            )

        return rankings
