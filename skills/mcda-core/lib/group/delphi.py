"""
MCDA Core - 德尔菲法（简化版）

提供群决策德尔菲法的实现，用于通过多轮专家咨询达成共识。
"""

from dataclasses import dataclass, field
from typing import Any
import statistics as stats


# =============================================================================
# 德尔菲法轮次记录（不可变）
# =============================================================================

@dataclass(frozen=True)
class DelphiRound:
    """德尔菲法轮次（不可变记录）

    记录德尔菲法过程中某一轮的完整状态。

    Attributes:
        round_number: 轮次编号（从 1 开始）
        scores: 该轮的评分
            {dm_id: {alternative: {criterion: score}}}
        statistics: 统计摘要
            {alternative: {criterion: {stat_name: value}}}
            stat_name 包括: mean, median, std, q1, q3
        convergence_score: 收敛分数（0-1，越小表示越收敛）

    Example:
        ```python
        round_record = DelphiRound(
            round_number=1,
            scores={"DM1": {"AWS": {"成本": 80.0}}},
            statistics={"AWS": {"成本": {"mean": 80.0, "median": 80.0, ...}}},
            convergence_score=0.1
        )
        ```
    """

    round_number: int
    scores: dict[str, dict[str, dict[str, float]]]
    statistics: dict[str, dict[str, dict[str, float]]]
    convergence_score: float

    def __post_init__(self):
        """验证数据有效性"""
        if self.round_number < 1:
            raise ValueError(
                f"DelphiRound: round_number ({self.round_number}) 必须大于 0"
            )

        if not self.scores:
            raise ValueError("DelphiRound: scores 不能为空")

        if not (0 <= self.convergence_score <= 1):
            raise ValueError(
                f"DelphiRound: convergence_score ({self.convergence_score}) "
                f"必须在 0-1 范围内"
            )


# =============================================================================
# 德尔菲法过程管理器（可变状态）
# =============================================================================

class DelphiProcess:
    """德尔菲法过程管理器

    管理德尔菲法的完整流程，包括多轮评分、统计分析和收敛检查。

    Attributes:
        initial_problem: 初始群决策问题
        max_rounds: 最大轮次数（默认 3）
        convergence_threshold: 收敛阈值（默认 0.05）

    Example:
        ```python
        process = DelphiProcess(
            initial_problem=problem,
            max_rounds=3,
            convergence_threshold=0.05
        )

        # 添加第一轮评分
        round1 = process.add_round(scores1)

        # 添加第二轮评分
        round2 = process.add_round(scores2)

        # 检查所有轮次
        for round in process.rounds:
            print(f"Round {round.round_number}: {round.convergence_score}")
        ```
    """

    def __init__(
        self,
        initial_problem: Any,  # GroupDecisionProblem
        max_rounds: int = 3,
        convergence_threshold: float = 0.05
    ):
        """初始化德尔菲法过程

        Args:
            initial_problem: 初始群决策问题
            max_rounds: 最大轮次数（必须 >= 1）
            convergence_threshold: 收敛阈值（必须 > 0）
        """
        self.initial_problem = initial_problem
        self.max_rounds = max_rounds
        self.convergence_threshold = convergence_threshold
        self._rounds: list[DelphiRound] = []

        # 验证参数
        if self.max_rounds < 1:
            raise ValueError(
                f"DelphiProcess: max_rounds ({self.max_rounds}) 必须大于 0"
            )

        if self.convergence_threshold <= 0:
            raise ValueError(
                f"DelphiProcess: convergence_threshold ({self.convergence_threshold}) "
                f"必须大于 0"
            )

    @property
    def rounds(self) -> tuple[DelphiRound, ...]:
        """获取所有轮次（返回不可变副本）

        Returns:
            包含所有轮次的元组
        """
        return tuple(self._rounds)

    def add_round(
        self,
        scores: dict[str, dict[str, dict[str, float]]]
    ) -> DelphiRound:
        """添加新轮次，返回不可变记录

        Args:
            scores: 新一轮的评分
                {dm_id: {alternative: {criterion: score}}}

        Returns:
            新创建的 DelphiRound 记录

        Raises:
            ValueError: 如果超过最大轮次数
        """
        # 检查轮次限制
        if len(self._rounds) >= self.max_rounds:
            raise ValueError(
                f"DelphiProcess: 已达到最大轮次数 ({self.max_rounds})"
            )

        # 计算统计摘要
        statistics = self.compute_statistics(scores)

        # 计算收敛分数
        convergence_score = self._compute_convergence_score(scores)

        # 创建轮次记录
        round_number = len(self._rounds) + 1
        round_record = DelphiRound(
            round_number=round_number,
            scores=scores,
            statistics=statistics,
            convergence_score=convergence_score
        )

        # 添加到内部列表
        self._rounds.append(round_record)

        return round_record

    def compute_statistics(
        self,
        scores: dict[str, dict[str, dict[str, float]]]
    ) -> dict[str, dict[str, dict[str, float]]]:
        """计算统计摘要

        对每个方案的每个准则计算：
        - 均值 (mean)
        - 中位数 (median)
        - 标准差 (std)
        - 第一四分位数 (q1)
        - 第三四分位数 (q3)

        Args:
            scores: 评分数据
                {dm_id: {alternative: {criterion: score}}}

        Returns:
            统计摘要
            {alternative: {criterion: {stat_name: value}}}
        """
        statistics: dict[str, dict[str, dict[str, float]]] = {}

        if not scores:
            return statistics

        # 收集所有决策者对每个方案-准则的评分
        alternative_criterion_scores: dict[str, dict[str, list[float]]] = {}

        for dm_scores in scores.values():
            for alt, alt_scores in dm_scores.items():
                if alt not in alternative_criterion_scores:
                    alternative_criterion_scores[alt] = {}

                for crit, score in alt_scores.items():
                    if crit not in alternative_criterion_scores[alt]:
                        alternative_criterion_scores[alt][crit] = []
                    alternative_criterion_scores[alt][crit].append(score)

        # 计算每个方案-准则的统计量
        for alt, crit_scores_dict in alternative_criterion_scores.items():
            statistics[alt] = {}

            for crit, values in crit_scores_dict.items():
                # 排序以便计算四分位数
                sorted_values = sorted(values)

                stat_values: dict[str, float] = {
                    "mean": stats.mean(sorted_values),
                    "median": stats.median(sorted_values),
                    "std": stats.stdev(sorted_values) if len(sorted_values) > 1 else 0.0,
                }

                # 计算四分位数
                n = len(sorted_values)
                if n >= 4:
                    # Q1 = 25th percentile, Q3 = 75th percentile
                    q1_idx = int(n * 0.25)
                    q3_idx = int(n * 0.75)
                    stat_values["q1"] = sorted_values[q1_idx]
                    stat_values["q3"] = sorted_values[q3_idx]
                elif n == 3:
                    stat_values["q1"] = sorted_values[0]
                    stat_values["q3"] = sorted_values[2]
                elif n == 2:
                    stat_values["q1"] = sorted_values[0]
                    stat_values["q3"] = sorted_values[1]
                else:  # n == 1
                    stat_values["q1"] = sorted_values[0]
                    stat_values["q3"] = sorted_values[0]

                statistics[alt][crit] = stat_values

        return statistics

    def _compute_convergence_score(
        self,
        scores: dict[str, dict[str, dict[str, float]]]
    ) -> float:
        """计算收敛分数

        收敛分数定义为当前轮与上一轮评分的平均变化量。
        变化量越小，收敛分数越小（表示越收敛）。

        Args:
            scores: 当前轮次的评分

        Returns:
            收敛分数（0-1，1 表示完全未收敛，0 表示完全收敛）
        """
        # 如果没有上一轮，返回 1.0（完全未收敛）
        if not self._rounds:
            return 1.0

        previous_scores = self._rounds[-1].scores

        # 计算评分变化
        total_change = 0.0
        count = 0

        for dm_id, alt_scores in scores.items():
            if dm_id not in previous_scores:
                continue

            for alt, crit_scores in alt_scores.items():
                if alt not in previous_scores[dm_id]:
                    continue

                for crit, score in crit_scores.items():
                    if crit in previous_scores[dm_id][alt]:
                        prev_score = previous_scores[dm_id][alt][crit]
                        change = abs(score - prev_score)
                        total_change += change
                        count += 1

        if count == 0:
            return 1.0

        # 平均变化量，归一化到 0-1
        # 假设最大合理变化为 50 分
        avg_change = total_change / count
        convergence_score = min(avg_change / 50.0, 1.0)

        return convergence_score

    def has_converged(self) -> bool:
        """检查是否已收敛

        Returns:
            如果最新轮次的收敛分数小于阈值，返回 True
        """
        if not self._rounds:
            return False

        latest_convergence = self._rounds[-1].convergence_score
        return latest_convergence < self.convergence_threshold

    def can_add_round(self) -> bool:
        """检查是否可以添加新轮次

        Returns:
            如果未达到最大轮次数，返回 True
        """
        return len(self._rounds) < self.max_rounds
