"""
MCDA Core - 加权几何平均聚合方法

使用对数域计算避免数值溢出问题。
"""

import math
from typing import Any

from .base import AggregationMethod


# =============================================================================
# 加权几何平均聚合方法
# =============================================================================

class WeightedGeometricAggregation(AggregationMethod):
    """加权几何平均聚合方法

    使用几何平均将多个决策者的评分聚合为群决策结果。

    使用对数域计算避免数值溢出问题：
        log_score = sum(w_k * log(x_k)) / sum(w_k)
        score = exp(log_score)

    几何平均的特点：
    - 对极端值不敏感（比算术平均更稳健）
    - 适用于比例型数据
    - 不能处理零值或负值

    Example:
        ```python
        aggregation = WeightedGeometricAggregation()
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        ```
    """

    @classmethod
    def get_name(cls) -> str:
        """获取方法名称"""
        return "weighted_geometric"

    def aggregate(
        self,
        scores: dict[str, float],
        weights: dict[str, float] | None = None
    ) -> float:
        """聚合多个评分（使用几何平均）

        Args:
            scores: 决策者评分 {decision_maker_id: score}
            weights: 决策者权重（可选，默认等权重）

        Returns:
            聚合后的评分

        Raises:
            ValueError: 评分为空、包含零值/负值、或权重无效
        """
        if not scores:
            raise ValueError("评分不能为空")

        # 验证所有评分必须为正数
        for dm_id, score in scores.items():
            if score <= 0:
                raise ValueError(
                    f"几何平均不能处理零值或负值: 决策者 '{dm_id}' 的评分为 {score}"
                )

        # 如果没有提供权重，使用等权重
        if weights is None:
            weights = {dm_id: 1.0 for dm_id in scores}

        # 验证权重和评分的决策者 ID 一致
        score_ids = set(scores.keys())
        weight_ids = set(weights.keys())

        if score_ids != weight_ids:
            extra = weight_ids - score_ids
            missing = score_ids - weight_ids
            if extra:
                raise ValueError(f"权重中存在未评分的决策者: {extra}")
            if missing:
                raise ValueError(f"缺少决策者的权重: {missing}")

        # 计算总权重
        total_weight = sum(weights.values())
        if total_weight == 0:
            raise ValueError("权重总和不能为 0")

        # 使用对数域计算避免溢出
        # log(score) = sum(w_k * log(x_k)) / sum(w_k)
        log_weighted_sum = 0.0
        for dm_id in scores:
            log_weighted_sum += weights[dm_id] * math.log(scores[dm_id])

        log_score = log_weighted_sum / total_weight
        return math.exp(log_score)

    def aggregate_matrix(
        self,
        score_matrix: dict[str, dict[str, dict[str, float]]],
        weights: dict[str, float] | None = None
    ) -> dict[str, dict[str, float]]:
        """聚合评分矩阵

        Args:
            score_matrix: 评分矩阵
                {alternative: {criterion: {decision_maker_id: score}}}
            weights: 决策者权重（可选）

        Returns:
            聚合后的评分矩阵 {alternative: {criterion: aggregated_score}}
        """
        result: dict[str, dict[str, float]] = {}

        for alternative, criteria_scores in score_matrix.items():
            result[alternative] = {}
            for criterion, dm_scores in criteria_scores.items():
                result[alternative][criterion] = self.aggregate(dm_scores, weights)

        return result
