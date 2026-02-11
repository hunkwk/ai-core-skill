"""
MCDA Core - Copeland 方法聚合

基于两两比较的群决策聚合方法。
"""

from typing import Any

from .base import AggregationMethod


# =============================================================================
# Copeland 方法聚合
# =============================================================================

class CopelandAggregation(AggregationMethod):
    """Copeland 方法聚合

    基于两两比较的聚合方法。
    对于多个决策者的评分，通过加权平均得到聚合结果。

    在多方案场景中，Copeland 方法通过两两比较计算每个方案的"胜场"，
    但在单一评分聚合场景中，退化为加权平均。

    Example:
        ```python
        aggregation = CopelandAggregation()
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        ```
    """

    @classmethod
    def get_name(cls) -> str:
        """获取方法名称"""
        return "copeland"

    def aggregate(
        self,
        scores: dict[str, float],
        weights: dict[str, float] | None = None
    ) -> float:
        """使用 Copeland 方法聚合多个评分

        对于单一准则的评分聚合，使用加权平均。

        Args:
            scores: 决策者评分 {decision_maker_id: score}
            weights: 决策者权重（可选，默认等权重）

        Returns:
            聚合后的评分

        Raises:
            ValueError: 评分为空或权重无效
        """
        if not scores:
            raise ValueError("评分不能为空")

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

        # 计算加权平均
        weighted_sum = sum(weights[dm_id] * scores[dm_id] for dm_id in scores)
        return weighted_sum / total_weight

    def aggregate_matrix(
        self,
        score_matrix: dict[str, dict[str, dict[str, float]]],
        weights: dict[str, float] | None = None
    ) -> dict[str, dict[str, float]]:
        """聚合评分矩阵

        对于评分矩阵，使用 Copeland 方法的两两比较逻辑。
        每个方案的最终得分基于与其他方案的比较结果。

        Args:
            score_matrix: 评分矩阵
                {alternative: {criterion: {decision_maker_id: score}}}
            weights: 决策者权重（可选）

        Returns:
            聚合后的评分矩阵 {alternative: {criterion: aggregated_score}}
        """
        result: dict[str, dict[str, float]] = {}

        # 如果没有方案，返回空字典
        if not score_matrix:
            return result

        # 获取所有方案和准则
        alternatives = list(score_matrix.keys())

        # 获取准则集合（假设所有方案有相同的准则）
        criteria = set()
        for alt_scores in score_matrix.values():
            criteria.update(alt_scores.keys())

        # 为每个方案和准则计算聚合评分
        for alternative in alternatives:
            result[alternative] = {}
            for criterion in criteria:
                if criterion not in score_matrix[alternative]:
                    continue

                dm_scores = score_matrix[alternative][criterion]
                result[alternative][criterion] = self.aggregate(dm_scores, weights)

        return result

    def compute_copeland_scores(
        self,
        score_matrix: dict[str, dict[str, float]],
        criterion_weights: dict[str, float] | None = None
    ) -> dict[str, float]:
        """计算 Copeland 分数（基于两两比较）

        对于每个方案对 (A, B)，比较它们在所有准则上的得分，
        统计胜场数，最终归一化得到 Copeland 分数。

        Args:
            score_matrix: 评分矩阵 {alternative: {criterion: score}}
            criterion_weights: 准则权重（可选）

        Returns:
            Copeland 分数 {alternative: copeland_score}
        """
        if not score_matrix:
            return {}

        alternatives = list(score_matrix.keys())
        n = len(alternatives)
        if n == 0:
            return {}

        # 获取准则集合
        criteria = set()
        for alt_scores in score_matrix.values():
            criteria.update(alt_scores.keys())

        if not criterion_weights:
            criterion_weights = {c: 1.0 for c in criteria}

        # 初始化胜场计数
        wins: dict[str, float] = {alt: 0.0 for alt in alternatives}

        # 两两比较
        for i, alt_a in enumerate(alternatives):
            for alt_b in alternatives:
                if alt_a == alt_b:
                    continue

                # 比较两个方案在所有准则上的表现
                comparison_score = 0.0
                total_weight = 0.0

                for criterion in criteria:
                    if criterion not in score_matrix[alt_a]:
                        continue
                    if criterion not in score_matrix[alt_b]:
                        continue

                    score_a = score_matrix[alt_a][criterion]
                    score_b = score_matrix[alt_b][criterion]
                    weight = criterion_weights.get(criterion, 1.0)

                    # 使用 sign 函数确定胜负
                    if score_a > score_b:
                        comparison_score += weight
                    elif score_a < score_b:
                        comparison_score -= weight
                    # 平局不加分

                    total_weight += weight

                # 累加胜场（归一化）
                if total_weight > 0:
                    wins[alt_a] += comparison_score / total_weight

        # 归一化到 [0, 1] 范围
        max_wins = max(wins.values()) if wins.values() else 1.0
        min_wins = min(wins.values()) if wins.values() else 0.0

        if max_wins == min_wins:
            return {alt: 0.5 for alt in alternatives}

        copeland_scores: dict[str, float] = {}
        for alt in alternatives:
            copeland_scores[alt] = (wins[alt] - min_wins) / (max_wins - min_wins)

        return copeland_scores
