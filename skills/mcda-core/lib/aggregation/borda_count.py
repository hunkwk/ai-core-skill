"""
MCDA Core - Borda 计数法聚合方法

基于排序的群决策聚合方法。
"""

from typing import Any

from .base import AggregationMethod


# =============================================================================
# Borda 计数法聚合方法
# =============================================================================

class BordaCountAggregation(AggregationMethod):
    """Borda 计数法聚合方法

    基于排序的聚合方法，将评分转换为排名分数后再聚合。

    Borda 分数计算：
        Borda_score = n - rank
        其中 n 为决策者数量，rank 为排名（1-based）

    对于相同评分的决策者，使用平均排名。

    Example:
        ```python
        aggregation = BordaCountAggregation()
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        ```
    """

    @classmethod
    def get_name(cls) -> str:
        """获取方法名称"""
        return "borda_count"

    def _compute_borda_scores(
        self,
        scores: dict[str, float]
    ) -> dict[str, float]:
        """计算 Borda 分数

        将原始评分转换为排名分数。

        Args:
            scores: 决策者评分 {decision_maker_id: score}

        Returns:
            Borda 分数 {decision_maker_id: borda_score}
        """
        # 按评分降序排序
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        n = len(sorted_items)
        borda_scores: dict[str, float] = {}

        # 处理相同评分的情况（使用平均排名）
        i = 0
        while i < n:
            j = i
            # 找到所有相同评分的决策者
            while j < n and abs(sorted_items[j][1] - sorted_items[i][1]) < 1e-9:
                j += 1

            # 计算这组相同评分的平均 Borda 分数
            # 排名从 1 开始，Borda 分数 = n - rank
            ranks = list(range(i + 1, j + 1))
            avg_rank = sum(ranks) / len(ranks)
            avg_borda = n - avg_rank

            # 分配相同的 Borda 分数
            for k in range(i, j):
                borda_scores[sorted_items[k][0]] = avg_borda

            i = j

        return borda_scores

    def aggregate(
        self,
        scores: dict[str, float],
        weights: dict[str, float] | None = None
    ) -> float:
        """使用 Borda 计数法聚合多个评分

        Args:
            scores: 决策者评分 {decision_maker_id: score}
            weights: 决策者权重（可选，默认等权重）

        Returns:
            聚合后的评分（使用 Borda 分数加权平均）

        Raises:
            ValueError: 评分为空或权重无效
        """
        if not scores:
            raise ValueError("评分不能为空")

        # 计算 Borda 分数
        borda_scores = self._compute_borda_scores(scores)

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

        # 使用 Borda 分数进行加权平均
        weighted_sum = sum(
            weights[dm_id] * borda_scores[dm_id]
            for dm_id in scores
        )
        return weighted_sum / total_weight

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
