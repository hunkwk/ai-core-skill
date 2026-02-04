"""
MCDA Core - TODIM 区间版本算法实现

TODIM（Tomada de Escolha por Interação e Tradeoff Off）的区间数版本。
基于前景理论和国际 TODIM 算法。
"""

from typing import Any, TYPE_CHECKING
import math

from .base import MCDAAlgorithm, register_algorithm

# 类型注解导入
if TYPE_CHECKING:
    from mcda_core.models import DecisionProblem, DecisionResult
    from mcda_core.interval import Interval


@register_algorithm("todim_interval")
class IntervalTODIMAlgorithm(MCDAAlgorithm):
    """TODIM 区间版本算法

    核心思想: 基于前景理论，考虑决策者的风险态度

    前景理论价值函数:
        v(d) = {
            d^α,                   if d ≥ 0  (收益)
            -θ · (-d)^β,           if d < 0  (损失)
        }

    参数:
        alpha: 风险态度参数（收益），默认 0.88
        beta: 风险态度参数（损失），默认 0.88
        theta: 损失厌恶系数，默认 2.25

    适用场景:
        - 考虑决策者心理行为的决策
        - 风险规避/风险偏好建模
        - 区间数不确定下的决策

    特点:
        - 基于前景理论（卡尼曼和特沃斯基）
        - 考虑损失厌恶
        - 支持区间数输入
        - δ 值越大越好
    """

    def __init__(self, alpha: float = 0.88, beta: float = 0.88, theta: float = 2.25):
        """初始化区间 TODIM 算法

        Args:
            alpha: 风险态度参数（收益），默认 0.88
            beta: 风险态度参数（损失），默认 0.88
            theta: 损失厌恶系数，默认 2.25
        """
        if not 0 < alpha <= 1:
            raise ValueError(f"alpha 必须在 (0, 1] 范围内，当前: {alpha}")
        if not 0 < beta <= 1:
            raise ValueError(f"beta 必须在 (0, 1] 范围内，当前: {beta}")
        if not theta > 1:
            raise ValueError(f"theta 必须大于 1，当前: {theta}")

        self.alpha = alpha
        self.beta = beta
        self.theta = theta

    @property
    def name(self) -> str:
        """算法名称"""
        return "todim_interval"

    @property
    def description(self) -> str:
        """算法描述"""
        return "TODIM（区间版本）- 基于前景理论的多准则决策"

    def calculate(
        self,
        problem: "DecisionProblem",
        alpha: float | None = None,
        beta: float | None = None,
        theta: float | None = None,
        **kwargs: Any
    ) -> "DecisionResult":
        """执行区间 TODIM 计算

        Args:
            problem: 决策问题（评分可以是区间数）
            alpha: 风险态度参数（可选）
            beta: 风险态度参数（可选）
            theta: 损失厌恶系数（可选）
            **kwargs: 未使用的其他参数

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from mcda_core.models import DecisionResult, RankingItem, ResultMetadata
        from mcda_core.interval import Interval
        from mcda_core.ranking import PossibilityDegree

        # 验证输入
        self.validate(problem)

        # 使用参数或默认值
        a = alpha if alpha is not None else self.alpha
        b = beta if beta is not None else self.beta
        t = theta if theta is not None else self.theta

        # 获取备选方案和准则
        alternatives = problem.alternatives
        criteria = problem.criteria

        # 确定参考点（每个准则的最小值）
        reference_points = {}
        for crit in criteria:
            values = [
                problem.scores[alt][crit.name]
                for alt in alternatives
            ]

            # 获取中点用于比较
            def get_midpoint(x):
                if isinstance(x, Interval):
                    return x.midpoint
                return float(x)

            if crit.direction == "higher_better":
                # 收益准则：参考点是最小值
                reference_points[crit.name] = min(get_midpoint(v) for v in values)
            else:
                # 成本准则：参考点是最大值（需要反转）
                max_val = max(get_midpoint(v) for v in values)
                reference_points[crit.name] = 100.0 - max_val

        # 计算最大权重（用于标准化）
        max_weight = max(crit.weight for crit in criteria)

        # 计算全局优势度
        global_dominance = {}
        for alt_i in alternatives:
            phi_sum = 0.0

            for crit in criteria:
                # 计算差距 d_ij
                value_ij = problem.scores[alt_i][crit.name]
                ref_point = reference_points[crit.name]

                # 处理 lower_better（方向反转）
                if crit.direction == "lower_better":
                    # 反转值：[a, b] → [100-b, 100-a]
                    if isinstance(value_ij, Interval):
                        value_ij = Interval(100.0 - value_ij.upper, 100.0 - value_ij.lower)

                # 计算差距（区间减法或标量减法）
                if isinstance(value_ij, Interval) and isinstance(ref_point, (int, float)):
                    d_ij = Interval(value_ij.lower - ref_point, value_ij.upper - ref_point)
                elif isinstance(value_ij, Interval):
                    # 两者都是区间（这种情况很少，因为 ref_point 是标量）
                    pass
                else:
                    # value_ij 是标量
                    d_ij = value_ij - ref_point

                # 计算前景价值
                if isinstance(d_ij, Interval):
                    # 区间版本
                    if d_ij.lower >= 0:
                        # 收益区间
                        v_ij = Interval(d_ij.lower ** a, d_ij.upper ** a)
                    elif d_ij.upper <= 0:
                        # 损失区间
                        v_ij = Interval(
                            -t * ((-d_ij.lower) ** b),
                            -t * ((-d_ij.upper) ** b)
                        )
                    else:
                        # 混合区间（跨越 0）
                        # 简化处理：使用中点
                        mid = d_ij.midpoint
                        if mid >= 0:
                            v_ij = mid ** a
                        else:
                            v_ij = -t * ((-mid) ** b)
                else:
                    # 标量版本
                    if d_ij >= 0:
                        v_ij = d_ij ** a
                    else:
                        v_ij = -t * ((-d_ij) ** b)

                # 计算优势度
                normalized_weight = crit.weight / max_weight
                if isinstance(v_ij, Interval):
                    phi_ij = v_ij * normalized_weight
                    # 使用中点求和
                    phi_sum += phi_ij.midpoint
                else:
                    phi_sum += v_ij * normalized_weight

            global_dominance[alt_i] = phi_sum

        # 排序（δ 值越大越好）
        # 检查是否有区间值
        has_intervals = any(isinstance(v, Interval) for v in global_dominance.values())

        if has_intervals:
            # 使用可能度排序
            ranker = PossibilityDegree()

            # 将全局优势度转换为区间（如果有）
            intervals = {
                alt: (val if isinstance(val, Interval) else Interval(val, val))
                for alt, val in global_dominance.items()
            }

            # 使用可能度排序（δ 值越大越好）
            sorted_alts = ranker.rank(intervals)
        else:
            # 所有值都是标量，直接排序
            sorted_alts = sorted(
                global_dominance.items(),
                key=lambda x: x[1],
                reverse=True
            )

        # 构建排名
        rankings = [
            RankingItem(
                rank=i,
                alternative=alt,
                score=round(score, 4) if isinstance(score, (int, float)) else round(
                    score.midpoint if isinstance(score, Interval) else score, 4
                )
            )
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        # 构建元数据
        metadata = ResultMetadata(
            algorithm_name=self.name,
            problem_size=(len(alternatives), len(criteria)),
            metrics={
                "global_dominance": global_dominance,
                "alpha": a,
                "beta": b,
                "theta": t,
            },
        )

        # 构建结果
        result = DecisionResult(
            rankings=rankings,
            raw_scores=global_dominance,
            metadata=metadata,
        )

        return result
