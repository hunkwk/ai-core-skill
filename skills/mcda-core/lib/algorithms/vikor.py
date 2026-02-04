"""
MCDA Core - VIKOR 算法实现

折衷排序法（VIseKriterijumska Optimizacija I Kompromisno Resenje）。
"""

from typing import Any, TYPE_CHECKING
import math

from .base import MCDAAlgorithm, register_algorithm

# 类型注解导入
if TYPE_CHECKING:
    from mcda_core.models import DecisionProblem, DecisionResult


@register_algorithm("vikor")
class VIKORAlgorithm(MCDAAlgorithm):
    """折衷排序法

    核心思想: 同时最大化群体效用和最小化个别遗憾

    公式:
        1. 标准化到 [0, 1]:
           f_ij = (x_j^max - x_ij) / (x_j^max - x_j^min)  (对于 lower_better)
           f_ij = (x_ij - x_j^min) / (x_j^max - x_j^min)  (对于 higher_better)

        2. 群体效用和个别遗憾:
           S_i = Σ w_j · f_ij
           R_i = max_j [w_j · f_ij]

        3. 折衷值:
           Q_i = v · (S_i - S_min) / (S_max - S_min) +
                 (1-v) · (R_i - R_min) / (R_max - R_min)

    参数:
        v: 决策策略系数（0-1），v=0.5 为折衷
           v=1: 完全重视群体效用
           v=0: 完全重视个别遗憾

    适用场景:
        - 需要折衷解的决策
        - 同时优化群体效用和个别遗憾

    特点:
        - 唯一提供折衷解的算法
        - 参数 v 可调整决策策略
        - Q 值越小越好（与 TOPSIS 相反）
    """

    def __init__(self, v: float = 0.5):
        """初始化 VIKOR 算法

        Args:
            v: 决策策略系数（0-1），默认 0.5
        """
        if not 0 <= v <= 1:
            raise ValueError(f"决策策略系数 v 必须在 [0, 1] 范围内，当前: {v}")
        self.v = v

    @property
    def name(self) -> str:
        """算法名称"""
        return "vikor"

    @property
    def description(self) -> str:
        """算法描述"""
        return "折衷排序法（VIKOR）"

    def calculate(
        self,
        problem: "DecisionProblem",
        v: float | None = None,
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 VIKOR 计算

        Args:
            problem: 决策问题
            v: 决策策略系数（可选，覆盖构造函数的值）
            **kwargs: 未使用的其他参数

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from mcda_core.models import DecisionResult, RankingItem, ResultMetadata

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
            # 获取该准则的所有评分
            values = [
                problem.scores[alt][crit.name]
                for alt in alternatives
            ]

            # 处理 lower_better（方向反转）
            if crit.direction == "lower_better":
                values = [100.0 - v for v in values]

            min_val = min(values)
            max_val = max(values)

            # 标准化到 [0, 1]
            for i, alt in enumerate(alternatives):
                if alt not in normalized:
                    normalized[alt] = {}

                if max_val == min_val:
                    # 所有值相同，标准化为 1
                    normalized[alt][crit.name] = 1.0
                else:
                    # 线性标准化
                    normalized[alt][crit.name] = (values[i] - min_val) / (max_val - min_val)

        # 2. 计算群体效用 S_i 和个别遗憾 R_i
        S = {}  # 群体效用
        R = {}  # 个别遗憾
        for alt in alternatives:
            s_i = 0.0
            r_i = 0.0
            for crit in criteria:
                f = normalized[alt][crit.name]
                weighted_f = crit.weight * f
                s_i += weighted_f
                r_i = max(r_i, weighted_f)

            S[alt] = s_i
            R[alt] = r_i

        # 3. 计算 Q_i
        S_min = min(S.values())
        S_max = max(S.values())
        R_min = min(R.values())
        R_max = max(R.values())

        Q = {}
        for alt in alternatives:
            # 处理分母为零的情况
            if S_max == S_min and R_max == R_min:
                q = 0.0
            elif S_max == S_min:
                q = (1 - v) * (R[alt] - R_min) / (R_max - R_min)
            elif R_max == R_min:
                q = v * (S[alt] - S_min) / (S_max - S_min)
            else:
                q = v * (S[alt] - S_min) / (S_max - S_min) + \
                    (1 - v) * (R[alt] - R_min) / (R_max - R_min)

            Q[alt] = q

        # 排序（Q 值越小越好）
        sorted_alts = sorted(Q.items(), key=lambda x: x[1])

        # 构建排名
        rankings = [
            RankingItem(
                rank=i,
                alternative=alt,
                score=round(score, 4)
            )
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        # 构建元数据（包含 metrics）
        metadata = ResultMetadata(
            algorithm_name=self.name,
            problem_size=(len(alternatives), len(criteria)),
            metrics={
                "Q": Q,
                "S": S,  # 群体效用
                "R": R,  # 个别遗憾
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
