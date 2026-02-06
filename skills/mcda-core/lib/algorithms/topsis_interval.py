"""
TOPSIS 区间版本算法实现

逼近理想解排序法（TOPSIS）的区间数版本，支持不确定性和模糊性。
"""

from typing import Any, TYPE_CHECKING
import math

import numpy as np

from .base import MCDAAlgorithm, register_algorithm

# 类型注解导入
if TYPE_CHECKING:
    from mcda_core.models import DecisionProblem, DecisionResult, Criterion
    from mcda_core.interval import Interval


@register_algorithm("topsis_interval")
class IntervalTOPSISAlgorithm(MCDAAlgorithm):
    """逼近理想解排序法（区间版本）

    核心思想: 距离正理想解最近，同时距离负理想解最远（支持区间数）

    公式:
        1. Vector 标准化: r_ij = x_ij / sqrt(Σ x_ik²)
           其中 x_ij 是区间数 [x^L, x^U]

        2. 加权标准化: v_ij = w_j · r_ij

        3. 区间理想解和负理想解:
           v_j⁺ = max_i(v_ij)  (对于效益型)
           v_j⁻ = min_i(v_ij)  (对于效益型)

        4. 区间距离计算:
           D_i⁺ = sqrt(Σ (v_ij.midpoint - v_j⁺.midpoint)²)
           D_i⁻ = sqrt(Σ (v_ij.midpoint - v_j⁻.midpoint)²)

        5. 相对接近度: C_i = D_i⁻ / (D_i⁺ + D_i⁻)

        6. 排序: 根据 C_i 降序排列

    适用场景:
        - 需要距离概念的决策（带不确定性）
        - TOPSIS 是最热门的距离算法
        - 评分是区间数

    特点:
        - 基于 Vector 标准化
        - 同时考虑正负理想解
        - 相对接近度在 [0, 1] 范围内
        - 支持区间数输入
    """

    def __init__(self):
        """初始化 TOPSIS 区间版本算法"""
        pass

    @property
    def name(self) -> str:
        """算法名称"""
        return "topsis_interval"

    @property
    def description(self) -> str:
        """算法描述"""
        return "逼近理想解排序法（TOPSIS）- 区间版本"

    def calculate(
        self,
        problem: "DecisionProblem",
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 TOPSIS 区间版本计算

        Args:
            problem: 决策问题（评分可以是区间数）
            **kwargs: 未使用的其他参数

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from ..models import DecisionResult, RankingItem, ResultMetadata
        from ..interval import Interval

        # 验证输入
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

        # 3. Vector 标准化
        normalized = self._vector_normalize(scores_matrix, criteria)

        # 4. 加权标准化
        weighted = self._apply_weights(normalized, weights)

        # 5. 确定理想解和负理想解
        ideal, negative_ideal = self._find_ideal_solutions(weighted, criteria)

        # 6. 计算距离
        distance_to_ideal, distance_to_negative_ideal = self._calculate_distances(
            weighted, ideal, negative_ideal, alternatives
        )

        # 7. 计算相对接近度
        closeness = self._calculate_closeness(
            distance_to_ideal, distance_to_negative_ideal, alternatives
        )

        # 8. 构建排名（按相对接近度降序）
        rankings = self._build_rankings(closeness, alternatives)

        # 9. 构建元数据
        metadata = ResultMetadata(
            algorithm_name="topsis_interval",
            problem_size=(n_alt, n_crit),
            metrics={
                "normalized": normalized.tolist(),
                "weighted": weighted.tolist(),
                "ideal": ideal,
                "negative_ideal": negative_ideal,
                "distance_to_ideal": distance_to_ideal,
                "distance_to_negative_ideal": distance_to_negative_ideal,
            }
        )

        # 10. 构建原始得分（使用相对接近度）
        raw_scores = closeness.copy()

        return DecisionResult(
            rankings=rankings,
            raw_scores=raw_scores,
            metadata=metadata
        )

    def _vector_normalize(
        self,
        scores_matrix,
        criteria: tuple
    ):
        """Vector 标准化

        r_ij = x_ij / sqrt(Σ x_ik²)

        Args:
            scores_matrix: 得分矩阵 (n_alt, n_crit)
            criteria: 准则元组

        Returns:
            标准化后的矩阵
        """
        import numpy as np
        from ..interval import Interval

        n_alt, n_crit = scores_matrix.shape

        # 初始化标准化矩阵
        normalized = np.zeros((n_alt, n_crit), dtype=object)

        # 对每个准则进行标准化
        for k in range(n_crit):
            # 计算该准则的平方和
            sum_squares = 0.0
            for i in range(n_alt):
                val = scores_matrix[i, k]
                if isinstance(val, Interval):
                    # 使用区间中点计算范数
                    sum_squares += val.midpoint ** 2
                else:
                    sum_squares += float(val) ** 2

            norm = math.sqrt(sum_squares)

            if norm < 1e-10:
                norm = 1.0  # 避免除零

            # 标准化
            for i in range(n_alt):
                val = scores_matrix[i, k]
                if isinstance(val, Interval):
                    # 区间标准化
                    normalized[i, k] = Interval(
                        val.lower / norm,
                        val.upper / norm
                    )
                else:
                    # 标量标准化
                    normalized[i, k] = float(val) / norm

        return normalized

    def _apply_weights(self, normalized, weights):
        """应用权重

        v_ij = w_j · r_ij

        Args:
            normalized: 标准化后的矩阵
            weights: 权重向量 (n_crit,)

        Returns:
            加权标准化后的矩阵
        """
        import numpy as np
        from ..interval import Interval

        n_alt, n_crit = normalized.shape

        # 初始化加权矩阵
        weighted = np.zeros((n_alt, n_crit), dtype=object)

        for i in range(n_alt):
            for k in range(n_crit):
                val = normalized[i, k]
                if isinstance(val, Interval):
                    weighted[i, k] = val * weights[k]
                else:
                    weighted[i, k] = val * weights[k]

        return weighted

    def _find_ideal_solutions(self, weighted, criteria):
        """确定理想解和负理想解

        对于效益型准则：
        - 理想解：最大值
        - 负理想解：最小值

        对于成本型准则：
        - 理想解：最小值
        - 负理想解：最大值

        Args:
            weighted: 加权标准化后的矩阵
            criteria: 准则元组

        Returns:
            (理想解列表, 负理想解列表)
        """
        import numpy as np
        from ..interval import Interval

        n_alt, n_crit = weighted.shape

        ideal = []
        negative_ideal = []

        for k in range(n_crit):
            # 提取该准则的所有值
            values = []
            for i in range(n_alt):
                val = weighted[i, k]
                if isinstance(val, Interval):
                    values.append(val.midpoint)
                else:
                    values.append(float(val))

            # 根据准则方向确定理想解和负理想解
            if criteria[k].direction == "higher_better":
                # 效益型：最大值为理想解
                max_val = max(values)
                min_val = min(values)
            else:
                # 成本型：最小值为理想解
                max_val = min(values)
                min_val = max(values)

            ideal.append(max_val)
            negative_ideal.append(min_val)

        return ideal, negative_ideal

    def _calculate_distances(self, weighted, ideal, negative_ideal, alternatives):
        """计算到理想解和负理想解的距离

        D_i⁺ = sqrt(Σ (v_ij - v_j⁺)²)
        D_i⁻ = sqrt(Σ (v_ij - v_j⁻)²)

        Args:
            weighted: 加权标准化后的矩阵
            ideal: 理想解列表
            negative_ideal: 负理想解列表
            alternatives: 备选方案元组

        Returns:
            (到理想解的距离字典, 到负理想解的距离字典)
        """
        import numpy as np
        from ..interval import Interval

        n_alt, n_crit = weighted.shape

        distance_to_ideal = {}
        distance_to_negative_ideal = {}

        for i, alt in enumerate(alternatives):
            # 计算到理想解的距离
            sum_squared_ideal = 0.0
            sum_squared_negative = 0.0

            for k in range(n_crit):
                val = weighted[i, k]
                if isinstance(val, Interval):
                    midpoint = val.midpoint
                else:
                    midpoint = float(val)

                # 到理想解的距离平方
                diff_ideal = midpoint - ideal[k]
                sum_squared_ideal += diff_ideal ** 2

                # 到负理想解的距离平方
                diff_negative = midpoint - negative_ideal[k]
                sum_squared_negative += diff_negative ** 2

            # 计算欧氏距离
            distance_to_ideal[alt] = math.sqrt(sum_squared_ideal)
            distance_to_negative_ideal[alt] = math.sqrt(sum_squared_negative)

        return distance_to_ideal, distance_to_negative_ideal

    def _calculate_closeness(self, distance_to_ideal, distance_to_negative_ideal, alternatives):
        """计算相对接近度

        C_i = D_i⁻ / (D_i⁺ + D_i⁻)

        Args:
            distance_to_ideal: 到理想解的距离字典
            distance_to_negative_ideal: 到负理想解的距离字典
            alternatives: 备选方案元组

        Returns:
            相对接近度字典
        """
        closeness = {}

        for alt in alternatives:
            d_plus = distance_to_ideal[alt]
            d_minus = distance_to_negative_ideal[alt]

            # 避免除零
            total = d_plus + d_minus
            if total < 1e-10:
                closeness[alt] = 0.0
            else:
                closeness[alt] = d_minus / total

        return closeness

    def _build_rankings(self, closeness, alternatives):
        """构建排名

        按相对接近度降序排列。

        Args:
            closeness: 相对接近度字典
            alternatives: 所有备选方案

        Returns:
            排名列表
        """
        from ..models import RankingItem

        # 按相对接近度降序排序
        sorted_alts = sorted(
            alternatives,
            key=lambda alt: closeness[alt],
            reverse=True
        )

        # 构建 RankingItem 列表
        rankings = []
        for rank, alt in enumerate(sorted_alts, start=1):
            rankings.append(
                RankingItem(
                    alternative=alt,
                    rank=rank,
                    score=float(closeness[alt])
                )
            )

        return rankings
