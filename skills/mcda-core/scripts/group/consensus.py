"""
MCDA Core - 共识度测量

提供群决策中共识度的计算方法。
"""

from dataclasses import dataclass
from typing import Any
import math


# =============================================================================
# 共识度测量结果
# =============================================================================

@dataclass(frozen=True)
class ConsensusResult:
    """共识度测量结果

    记录群决策的共识度分析结果。

    Attributes:
        overall_consensus: 整体共识度（0-1，1 表示完全共识）
        criterion_consensus: 各准则的共识度 {criterion: consensus}
        decision_maker_distances: 决策者距离矩阵
            {dm_id: {dm_id: distance}}
       达到了共识阈值
    """
    overall_consensus: float
    criterion_consensus: dict[str, float]
    decision_maker_distances: dict[str, dict[str, float]]
    threshold_reached: bool

    def __post_init__(self):
        """验证数据有效性"""
        if not (0 <= self.overall_consensus <= 1):
            raise ValueError(
                f"ConsensusResult: overall_consensus ({self.overall_consensus}) "
                f"必须在 0-1 范围内"
            )

        for crit, consensus in self.criterion_consensus.items():
            if not (0 <= consensus <= 1):
                raise ValueError(
                    f"ConsensusResult: criterion_consensus['{crit}'] ({consensus}) "
                    f"必须在 0-1 范围内"
                )


# =============================================================================
# 共识度测量方法
# =============================================================================

class ConsensusMeasure:
    """共识度测量

    计算群决策中决策者之间的共识度。

    支持的共识度计算方法：
    - standard_deviation: 标准差法（越小共识度越高）
    - coefficient_of_variation: 变异系数法
    - average_distance: 平均距离法
    - agreement_rate: 同意率法（评分差异小于阈值的比例）
    """

    @staticmethod
    def compute_standard_deviation(
        scores: dict[str, float]
    ) -> tuple[float, float]:
        """计算评分的标准差和均值

        Args:
            scores: 评分字典 {decision_maker_id: score}

        Returns:
            (均值, 标准差)
        """
        if not scores:
            return 0.0, 0.0

        values = list(scores.values())
        n = len(values)
        mean = sum(values) / n

        if n == 1:
            return mean, 0.0

        variance = sum((x - mean) ** 2 for x in values) / n
        std = math.sqrt(variance)

        return mean, std

    @staticmethod
    def compute_coefficient_of_variation(scores: dict[str, float]) -> float:
        """计算变异系数

        变异系数 = 标准差 / 均值

        Args:
            scores: 评分字典 {decision_maker_id: score}

        Returns:
            变异系数（0-1，通过归一化）
        """
        if not scores:
            return 0.0

        mean, std = ConsensusMeasure.compute_standard_deviation(scores)

        if mean == 0:
            return 0.0 if std == 0 else 1.0

        cv = std / abs(mean)
        # 归一化到 0-1，假设 cv > 1 表示低共识
        return min(cv, 1.0)

    @staticmethod
    def compute_euclidean_distance(
        scores1: dict[str, float],
        scores2: dict[str, float]
    ) -> float:
        """计算两个评分向量的欧氏距离

        Args:
            scores1: 第一个评分向量
            scores2: 第二个评分向量

        Returns:
            欧氏距离
        """
        # 确保两个评分向量有相同的键
        keys = set(scores1.keys()) | set(scores2.keys())

        sum_squares = 0.0
        for key in keys:
            v1 = scores1.get(key, 0)
            v2 = scores2.get(key, 0)
            sum_squares += (v1 - v2) ** 2

        return math.sqrt(sum_squares)

    @staticmethod
    def compute_agreement_rate(
        scores: dict[str, float],
        tolerance: float = 10.0
    ) -> float:
        """计算同意率

        同意率 = 与均值差异小于容差的评分比例

        Args:
            scores: 评分字典 {decision_maker_id: score}
            tolerance: 容差值（默认 10）

        Returns:
            同意率（0-1）
        """
        if not scores:
            return 0.0

        if len(scores) == 1:
            return 1.0

        mean, _ = ConsensusMeasure.compute_standard_deviation(scores)

        agreed = sum(1 for score in scores.values() if abs(score - mean) <= tolerance)
        return agreed / len(scores)

    @classmethod
    def compute_criterion_consensus(
        cls,
        scores: dict[str, float],
        method: str = "standard_deviation"
    ) -> float:
        """计算单个准则的共识度

        Args:
            scores: 决策者对该准则的评分 {dm_id: score}
            method: 计算方法
                - "standard_deviation": 标准差法（转换为共识度）
                - "coefficient_of_variation": 变异系数法
                - "agreement_rate": 同意率法

        Returns:
            共识度（0-1，1 表示完全共识）
        """
        if not scores:
            return 0.0

        if len(scores) == 1:
            return 1.0

        if method == "standard_deviation":
            _, std = cls.compute_standard_deviation(scores)
            # 将标准差转换为共识度：std=0 -> consensus=1, std>=50 -> consensus=0
            consensus = max(0, 1 - std / 50)
            return consensus

        elif method == "coefficient_of_variation":
            cv = cls.compute_coefficient_of_variation(scores)
            return 1 - cv

        elif method == "agreement_rate":
            return cls.compute_agreement_rate(scores)

        else:
            raise ValueError(f"未知的共识度计算方法: {method}")

    @classmethod
    def compute_consensus(
        cls,
        individual_scores: dict[str, dict[str, dict[str, float]]],
        alternatives: tuple[str, ...],
        criteria: tuple,
        threshold: float = 0.7,
        method: str = "standard_deviation"
    ) -> ConsensusResult:
        """计算群决策的整体共识度

        Args:
            individual_scores: 个人评分
                {dm_id: {alternative: {criterion: score}}}
            alternatives: 备选方案列表
            criteria: 评价准则列表
            threshold: 共识阈值
            method: 共识度计算方法

        Returns:
            共识度测量结果
        """
        criterion_consensus: dict[str, float] = {}
        decision_maker_distances: dict[str, dict[str, float]] = {}

        # 获取准则名称
        if criteria:
            crit_names = [c.name if hasattr(c, 'name') else str(c) for c in criteria]
        else:
            crit_names = []

        # 计算各准则的共识度（对所有备选方案取平均）
        if crit_names:
            for crit in crit_names:
                crit_scores: dict[str, float] = {}

                # 收集所有决策者对该准则的评分（跨所有备选方案）
                for dm_id, alt_scores in individual_scores.items():
                    dm_crit_scores = []
                    for alt in alternatives:
                        if alt in alt_scores and crit in alt_scores[alt]:
                            dm_crit_scores.append(alt_scores[alt][crit])

                    # 使用该决策者的平均评分
                    if dm_crit_scores:
                        crit_scores[dm_id] = sum(dm_crit_scores) / len(dm_crit_scores)

                # 计算该准则的共识度
                criterion_consensus[crit] = cls.compute_criterion_consensus(
                    crit_scores, method
                )

        # 计算决策者之间的距离
        dm_ids = list(individual_scores.keys())
        for dm_id1 in dm_ids:
            decision_maker_distances[dm_id1] = {}
            for dm_id2 in dm_ids:
                if dm_id1 == dm_id2:
                    decision_maker_distances[dm_id1][dm_id2] = 0.0
                else:
                    # 计算两个决策者评分的欧氏距离
                    scores1: dict[str, float] = {}
                    scores2: dict[str, float] = {}

                    for alt in alternatives:
                        for crit in crit_names:
                            key = f"{alt}_{crit}"
                            scores1[key] = individual_scores[dm_id1].get(alt, {}).get(crit, 0)
                            scores2[key] = individual_scores[dm_id2].get(alt, {}).get(crit, 0)

                    distance = cls.compute_euclidean_distance(scores1, scores2)
                    decision_maker_distances[dm_id1][dm_id2] = distance

        # 计算整体共识度（各准则共识度的平均）
        if criterion_consensus:
            overall_consensus = sum(criterion_consensus.values()) / len(criterion_consensus)
        else:
            overall_consensus = 1.0

        # 判断是否达到共识阈值
        threshold_reached = overall_consensus >= threshold

        return ConsensusResult(
            overall_consensus=overall_consensus,
            criterion_consensus=criterion_consensus,
            decision_maker_distances=decision_maker_distances,
            threshold_reached=threshold_reached
        )
