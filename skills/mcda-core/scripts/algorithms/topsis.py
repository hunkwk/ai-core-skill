"""
MCDA Core - TOPSIS 算法实现

逼近理想解排序法（Technique for Order Preference by Similarity to Ideal Solution）。
"""

from typing import Any, TYPE_CHECKING
import math

from .base import MCDAAlgorithm, register_algorithm
from ..models import MAX_SCORE

# 类型注解导入
if TYPE_CHECKING:
    from ..models import DecisionProblem, DecisionResult


@register_algorithm("topsis")
class TOPSISAlgorithm(MCDAAlgorithm):
    """逼近理想解排序法

    核心思想: 距离正理想解最近，同时距离负理想解最远

    公式:
        1. Vector 标准化: r_ij = x_ij / sqrt(Σ x_ij²)
        2. 加权标准化: v_ij = w_j · r_ij
        3. 距离计算:
           D_i⁺ = sqrt(Σ (v_ij - v_j⁺)²)
           D_i⁻ = sqrt(Σ (v_ij - v_j⁻)²)
        4. 相对接近度: C_i = D_i⁻ / (D_i⁺ + D_i⁻)

    适用场景:
        - 需要距离概念的决策
        - TOPSIS 是最热门的距离算法

    特点:
        - 基于 Vector 标准化
        - 同时考虑正负理想解
        - 相对接近度在 [0, 1] 范围内
    """

    @property
    def name(self) -> str:
        """算法名称"""
        return "topsis"

    @property
    def description(self) -> str:
        """算法描述"""
        return "逼近理想解排序法（TOPSIS）"

    def calculate(
        self,
        problem: "DecisionProblem",
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 TOPSIS 计算

        Args:
            problem: 决策问题
            **kwargs: 未使用（保持接口一致性）

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from ..models import DecisionResult, RankingItem, ResultMetadata

        # 验证输入
        self.validate(problem)

        # 获取备选方案和准则列表
        alternatives = problem.alternatives
        criteria = problem.criteria
        n_alts = len(alternatives)
        n_crits = len(criteria)

        # 构建决策矩阵（行为备选方案，列为准则）
        import numpy as np

        X = np.zeros((n_alts, n_crits))
        for i, alt in enumerate(alternatives):
            for j, crit in enumerate(criteria):
                value = problem.scores[alt][crit.name]

                # 处理 lower_better（方向反转）
                if crit.direction == "lower_better":
                    value = MAX_SCORE - value

                X[i, j] = value

        # 1. Vector 标准化
        norms = np.sqrt(np.sum(X ** 2, axis=0))
        # 避免除以零
        norms[norms == 0] = 1.0
        R = X / norms

        # 2. 加权标准化
        weights = np.array([crit.weight for crit in criteria])
        V = R * weights

        # 3. 确定理想解和负理想解
        v_plus = np.max(V, axis=0)  # 正理想解
        v_minus = np.min(V, axis=0)  # 负理想解

        # 4. 计算距离
        D_plus = np.sqrt(np.sum((V - v_plus) ** 2, axis=1))
        D_minus = np.sqrt(np.sum((V - v_minus) ** 2, axis=1))

        # 5. 计算相对接近度
        C = D_minus / (D_plus + D_minus)

        # 处理分母为零的情况
        denominator = D_plus + D_minus
        C[denominator == 0] = 0.0

        # 构建结果字典
        closeness = {alt: float(C[i]) for i, alt in enumerate(alternatives)}
        d_plus = {alt: float(D_plus[i]) for i, alt in enumerate(alternatives)}
        d_minus = {alt: float(D_minus[i]) for i, alt in enumerate(alternatives)}

        # 排序（接近度从高到低）
        sorted_alts = sorted(
            closeness.items(),
            key=lambda x: x[1],
            reverse=True
        )

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
                "closeness": closeness,
                "d_plus": d_plus,
                "d_minus": d_minus,
            },
        )

        # 构建结果
        result = DecisionResult(
            rankings=rankings,
            raw_scores=closeness,
            metadata=metadata,
        )

        return result
