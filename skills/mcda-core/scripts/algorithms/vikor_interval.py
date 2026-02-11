"""
MCDA Core - VIKOR 区间版本算法实现

折衷排序法的区间数版本，支持不确定性和模糊性。
"""

from typing import Any, TYPE_CHECKING
import math

from .base import MCDAAlgorithm, register_algorithm

# 类型注解导入
if TYPE_CHECKING:
    from ..models import DecisionProblem, DecisionResult
    from ..interval import Interval


@register_algorithm("vikor_interval")
class IntervalVIKORAlgorithm(MCDAAlgorithm):
    """折衷排序法（区间版本）

    核心思想: 同时最大化群体效用和最小化个别遗憾（支持区间数）

    公式:
        1. 标准化到 [0, 1]:
           f_ij = (x_j^max - x_ij) / (x_j^max - x_j^min)  (对于 lower_better)
           f_ij = (x_ij - x_j^min) / (x_j^max - x_j^min)  (对于 higher_better)

           其中 x_ij 是区间数 [x^L, x^U]

        2. 区间群体效用和个别遗憾:
           S_i = [S_i^L, S_i^U] = Σ w_j · f_ij
           R_i = [R_i^L, R_i^U] = max_j [w_j · f_ij]

        3. 区间折衷值:
           Q_i = [Q_i^L, Q_i^U]
               = v · (S_i - S_min) / (S_max - S_min)
               + (1-v) · (R_i - R_min) / (R_max - R_min)

        4. 排序: 使用可能度排序对 Q_i 排序（Q 值越小越好）

    参数:
        v: 决策策略系数（0-1），v=0.5 为折衷
           v=1: 完全重视群体效用
           v=0: 完全重视个别遗憾

    适用场景:
        - 需要折衷解的决策（带不确定性）
        - 同时优化群体效用和个别遗憾
        - 评分是区间数

    特点:
        - 唯一提供折衷解的算法
        - 参数 v 可调整决策策略
        - 支持区间数输入
        - Q 值越小越好（与 TOPSIS 相反）
    """

    def __init__(self, v: float = 0.5):
        """初始化区间 VIKOR 算法

        Args:
            v: 决策策略系数（0-1），默认 0.5
        """
        if not 0 <= v <= 1:
            raise ValueError(f"决策策略系数 v 必须在 [0, 1] 范围内，当前: {v}")
        self.v = v

    @property
    def name(self) -> str:
        """算法名称"""
        return "vikor_interval"

    @property
    def description(self) -> str:
        """算法描述"""
        return "折衷排序法（VIKOR）- 区间版本"

    def calculate(
        self,
        problem: "DecisionProblem",
        v: float | None = None,
        **kwargs: Any
    ) -> "DecisionResult":
        """执行区间 VIKOR 计算

        Args:
            problem: 决策问题（评分可以是区间数）
            v: 决策策略系数（可选，覆盖构造函数的值）
            **kwargs: 未使用的其他参数

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from ..models import DecisionResult, RankingItem, ResultMetadata
        from ..interval import Interval
        from ..ranking import PossibilityDegree

        # 验证输入
        self.validate(problem)

        # 使用参数或默认值
        if v is None:
            v = self.v
        elif not 0 <= v <= 1:
            raise ValueError(f"决策策略系数 v 必须在 [0, 1] 范围内，当前: {v}")

        # 获取备选方案和准则
        alternatives = problem.alternatives
        criteria = problem.criteria

        # 1. 标准化到 [0, 1]
        normalized = {}
        for crit in criteria:
            # 获取该准则的所有评分（可能是区间数）
            values = [
                problem.scores[alt][crit.name]
                for alt in alternatives
            ]

            # 处理 lower_better（方向反转）
            if crit.direction == "lower_better":
                # 区间数反转: [a, b] → [100-b, 100-a]
                values = [
                    Interval(100.0 - v.upper, 100.0 - v.lower) if isinstance(v, Interval)
                    else 100.0 - v
                    for v in values
                ]

            # 计算最小值和最大值（基于中点比较）
            def get_value(x):
                """获取用于比较的值（中点）"""
                if isinstance(x, Interval):
                    return x.midpoint
                return float(x)

            min_val = min(get_value(v) for v in values)
            max_val = max(get_value(v) for v in values)

            # 标准化到 [0, 1]
            for i, alt in enumerate(alternatives):
                if alt not in normalized:
                    normalized[alt] = {}

                if max_val == min_val:
                    # 所有值相同，标准化为 1（或退化区间）
                    val = values[i]
                    if isinstance(val, Interval):
                        normalized[alt][crit.name] = Interval(1.0, 1.0)
                    else:
                        normalized[alt][crit.name] = 1.0
                else:
                    # 线性标准化
                    val = values[i]
                    if isinstance(val, Interval):
                        # 区间标准化: (x - min) / (max - min)
                        normalized[alt][crit.name] = Interval(
                            (val.lower - min_val) / (max_val - min_val),
                            (val.upper - min_val) / (max_val - min_val)
                        )
                    else:
                        # 精确数标准化
                        normalized[alt][crit.name] = (val - min_val) / (max_val - min_val)

        # 2. 计算区间群体效用 S_i 和个别遗憾 R_i
        S = {}  # 区间群体效用
        R = {}  # 区间个别遗憾
        for alt in alternatives:
            s_i = None  # 累加区间和
            r_i = None  # 最大区间值

            for crit in criteria:
                f = normalized[alt][crit.name]
                weighted_f = f * crit.weight

                # 累加群体效用
                if s_i is None:
                    s_i = weighted_f
                else:
                    s_i = s_i + weighted_f if isinstance(s_i, Interval) else s_i + weighted_f

                # 更新个别遗憾（最大值）
                if r_i is None:
                    r_i = weighted_f
                else:
                    # 比较区间或标量，取最大值
                    if isinstance(weighted_f, Interval) and isinstance(r_i, Interval):
                        # 使用中点比较
                        r_i = weighted_f if weighted_f.midpoint > r_i.midpoint else r_i
                    elif isinstance(weighted_f, Interval):
                        r_i = weighted_f if weighted_f.midpoint > r_i else r_i
                    elif isinstance(r_i, Interval):
                        r_i = weighted_f if weighted_f > r_i.midpoint else r_i
                    else:
                        r_i = max(weighted_f, r_i)

            S[alt] = s_i if s_i is not None else 0.0
            R[alt] = r_i if r_i is not None else 0.0

        # 3. 计算 Q_i（区间折衷值）
        # 使用中点法比较区间
        def get_midpoint(x):
            """获取中点（区间或标量）"""
            if isinstance(x, Interval):
                return x.midpoint
            return float(x)

        S_min_alt = min(S.items(), key=lambda x: get_midpoint(x[1]))[0]
        S_max_alt = max(S.items(), key=lambda x: get_midpoint(x[1]))[0]
        R_min_alt = min(R.items(), key=lambda x: get_midpoint(x[1]))[0]
        R_max_alt = max(R.items(), key=lambda x: get_midpoint(x[1]))[0]

        S_min = S[S_min_alt]
        S_max = S[S_max_alt]
        R_min = R[R_min_alt]
        R_max = R[R_max_alt]

        # 计算范围（使用中点，确保是标量）
        s_range_val = get_midpoint(S_max) - get_midpoint(S_min)
        r_range_val = get_midpoint(R_max) - get_midpoint(R_min)

        Q = {}
        for alt in alternatives:
            # 计算 (S_i - S_min) / (S_max - S_min)
            s_val = S[alt]
            s_diff = s_val - S_min if isinstance(s_val, Interval) else s_val - get_midpoint(S_min)

            # 计算 (R_i - R_min) / (R_max - R_min)
            r_val = R[alt]
            r_diff = r_val - R_min if isinstance(r_val, Interval) else r_val - get_midpoint(R_min)

            # 处理分母为零
            if s_range_val == 0:
                s_normalized = 0.0
            else:
                # 使用标量除法（除数是标量）
                if isinstance(s_diff, Interval):
                    s_normalized = Interval(s_diff.lower / s_range_val, s_diff.upper / s_range_val)
                else:
                    s_normalized = s_diff / s_range_val

            if r_range_val == 0:
                r_normalized = 0.0
            else:
                # 使用标量除法（除数是标量）
                if isinstance(r_diff, Interval):
                    r_normalized = Interval(r_diff.lower / r_range_val, r_diff.upper / r_range_val)
                else:
                    r_normalized = r_diff / r_range_val

            # Q_i = v · s_normalized + (1-v) · r_normalized
            if isinstance(s_normalized, Interval) or isinstance(r_normalized, Interval):
                # 至少一个是区间，结果是区间
                s_val_norm = s_normalized if isinstance(s_normalized, Interval) else Interval(s_normalized, s_normalized)
                r_val_norm = r_normalized if isinstance(r_normalized, Interval) else Interval(r_normalized, r_normalized)

                q = (s_val_norm * v) + (r_val_norm * (1 - v))
                Q[alt] = q
            else:
                # 都是标量
                q = v * s_normalized + (1 - v) * r_normalized
                Q[alt] = q

        # 4. 排序（Q 值越小越好）
        # 检查是否有区间 Q 值
        has_intervals = any(isinstance(q, Interval) for q in Q.values())

        if has_intervals:
            # 使用可能度排序
            ranker = PossibilityDegree()

            # 计算综合得分（越小越好）
            # 使用负可能度：score = -Σ P(Q_i ≥ Q_j)
            scores = {}
            for alt_i in Q.keys():
                score = 0.0
                for alt_j in Q.keys():
                    if alt_i != alt_j:
                        q_i = Q[alt_i]
                        q_j = Q[alt_j]

                        if isinstance(q_i, Interval) and isinstance(q_j, Interval):
                            # P(Q_i ≥ Q_j)
                            prob = ranker.calculate(q_i, q_j)
                            # Q 值越小越好，所以取负
                            score -= prob
                        elif isinstance(q_i, Interval):
                            # q_i 是区间，q_j 是标量
                            # 比较中点
                            if q_i.midpoint < q_j:
                                score -= 1.0
                            elif q_i.midpoint > q_j:
                                score -= 0.0
                            else:
                                score -= 0.5
                        elif isinstance(q_j, Interval):
                            # q_i 是标量，q_j 是区间
                            if q_i < q_j.midpoint:
                                score -= 1.0
                            elif q_i > q_j.midpoint:
                                score -= 0.0
                            else:
                                score -= 0.5
                        else:
                            # 都是标量
                            if q_i < q_j:
                                score -= 1.0
                            elif q_i > q_j:
                                score -= 0.0
                            else:
                                score -= 0.5

                scores[alt_i] = score

            # 按得分降序排列（越负越好）
            sorted_alts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        else:
            # 所有 Q 都是标量，直接排序
            sorted_alts = sorted(Q.items(), key=lambda x: get_midpoint(x[1]))

        # 构建排名
        rankings = [
            RankingItem(
                rank=i,
                alternative=alt,
                score=round(get_midpoint(score), 4)
            )
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        # 构建元数据（包含 metrics）
        metadata = ResultMetadata(
            algorithm_name=self.name,
            problem_size=(len(alternatives), len(criteria)),
            metrics={
                "Q": Q,
                "S": S,  # 区间群体效用
                "R": R,  # 区间个别遗憾
                "v": v,  # 决策策略系数
            },
        )

        # 构建结果
        result = DecisionResult(
            rankings=rankings,
            raw_scores=Q,
            metadata=metadata,
        )

        return result
