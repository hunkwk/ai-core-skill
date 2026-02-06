"""
MCDA Core - 群决策数据模型

定义群决策问题的数据结构。
"""

from dataclasses import dataclass, field
from typing import Literal


# =============================================================================
# 决策者数据模型
# =============================================================================

@dataclass(frozen=True)
class DecisionMaker:
    """决策者

    表示群决策中的单个决策者。

    Attributes:
        id: 决策者唯一标识
        name: 决策者名称
        weight: 决策者权重（默认 1.0）
        expertise: 领域专业知识权重 {criterion_name: weight}（可选）

    Example:
        ```python
        dm = DecisionMaker(
            id="DM1",
            name="张三",
            weight=1.0,
            expertise={"成本": 0.8, "质量": 0.9}
        )
        ```
    """

    id: str
    name: str
    weight: float = 1.0
    expertise: dict[str, float] | None = None

    def __post_init__(self):
        """验证参数有效性"""
        if not self.id:
            raise ValueError("DecisionMaker: id 不能为空")
        if not self.name:
            raise ValueError("DecisionMaker: name 不能为空")
        if self.weight < 0:
            raise ValueError(f"DecisionMaker: weight ({self.weight}) 不能为负数")

        # 验证专业知识权重
        if self.expertise is not None:
            for crit_name, weight in self.expertise.items():
                if not isinstance(weight, (int, float)):
                    raise ValueError(
                        f"DecisionMaker: expertise['{crit_name}'] 必须是数值类型"
                    )
                if weight < 0 or weight > 1:
                    raise ValueError(
                        f"DecisionMaker: expertise['{crit_name}'] ({weight}) "
                        f"必须在 0-1 范围内"
                    )


# =============================================================================
# 聚合配置数据模型
# =============================================================================

@dataclass(frozen=True)
class AggregationConfig:
    """聚合配置

    定义群决策评分聚合的配置参数。

    Attributes:
        score_aggregation: 评分聚合方法
        consensus_strategy: 共识策略（none/threshold/feedback）
        consensus_threshold: 共识阈值（0-1，默认 0.7）

    Example:
        ```python
        config = AggregationConfig(
            score_aggregation="weighted_average",
            consensus_strategy="threshold",
            consensus_threshold=0.7
        )
        ```
    """

    score_aggregation: Literal[
        "weighted_average",
        "weighted_geometric",
        "borda_count",
        "copeland",
    ] = "weighted_average"
    consensus_strategy: Literal[
        "none",
        "threshold",
        "feedback",
    ] = "none"
    consensus_threshold: float = 0.7

    def __post_init__(self):
        """验证配置有效性"""
        valid_aggregations = {
            "weighted_average",
            "weighted_geometric",
            "borda_count",
            "copeland",
        }
        if self.score_aggregation not in valid_aggregations:
            raise ValueError(
                f"AggregationConfig: score_aggregation ({self.score_aggregation}) "
                f"必须是 {valid_aggregations} 之一"
            )

        valid_strategies = {"none", "threshold", "feedback"}
        if self.consensus_strategy not in valid_strategies:
            raise ValueError(
                f"AggregationConfig: consensus_strategy ({self.consensus_strategy}) "
                f"必须是 {valid_strategies} 之一"
            )

        if self.consensus_threshold < 0 or self.consensus_threshold > 1:
            raise ValueError(
                f"AggregationConfig: consensus_threshold ({self.consensus_threshold}) "
                f"必须在 0-1 范围内"
            )


# =============================================================================
# 群决策问题数据模型
# =============================================================================

@dataclass(frozen=True)
class GroupDecisionProblem:
    """群决策问题

    定义一个群决策问题，包含多个决策者和各自的评分。

    Attributes:
        alternatives: 备选方案列表
        criteria: 评价准则列表
        decision_makers: 决策者列表
        individual_scores: 个人评分
            {decision_maker_id: {alternative: {criterion: score}}}
        aggregation_config: 聚合配置（可选）

    Note:
        individual_scores 的结构：
        {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0}
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 80.0},
                "Azure": {"成本": 75.0, "质量": 90.0}
            }
        }

    Example:
        ```python
        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=(Criterion(name="成本", weight=0.5, direction="lower_better"),),
            decision_makers=(
                DecisionMaker(id="DM1", name="张三"),
                DecisionMaker(id="DM2", name="李四"),
            ),
            individual_scores={
                "DM1": {
                    "AWS": {"成本": 80.0, "质量": 90.0},
                    "Azure": {"成本": 70.0, "质量": 85.0}
                },
                "DM2": {
                    "AWS": {"成本": 85.0, "质量": 80.0},
                    "Azure": {"成本": 75.0, "质量": 90.0}
                }
            }
        )
        ```
    """

    alternatives: tuple[str, ...]
    criteria: tuple  # 使用 tuple 避免循环导入，实际应为 tuple[Criterion, ...]
    decision_makers: tuple[DecisionMaker, ...]
    individual_scores: dict[str, dict[str, dict[str, float]]]
    aggregation_config: AggregationConfig | None = None

    def __post_init__(self):
        """验证数据一致性"""
        if len(self.alternatives) < 2:
            raise ValueError("GroupDecisionProblem: 至少需要 2 个备选方案")
        if len(self.criteria) < 1:
            raise ValueError("GroupDecisionProblem: 至少需要 1 个评价准则")
        if len(self.decision_makers) < 2:
            raise ValueError("GroupDecisionProblem: 至少需要 2 个决策者")

        # 验证决策者 ID 唯一性
        dm_ids = [dm.id for dm in self.decision_makers]
        if len(dm_ids) != len(set(dm_ids)):
            raise ValueError("GroupDecisionProblem: 决策者 ID 必须唯一")

        # 验证个人评分结构
        self._validate_individual_scores()

    def _validate_individual_scores(self):
        """验证个人评分的完整性和有效性"""
        dm_ids = [dm.id for dm in self.decision_makers]  # 使用列表保持顺序
        alt_names = set(self.alternatives)

        # 获取准则名称
        if self.criteria:
            crit_names = {c.name if hasattr(c, 'name') else str(c) for c in self.criteria}
        else:
            crit_names = set()

        # 验证所有决策者都有评分
        for dm_id in dm_ids:
            if dm_id not in self.individual_scores:
                raise ValueError(
                    f"GroupDecisionProblem: 缺少决策者 '{dm_id}' 的评分"
                )

        # 验证评分结构
        for dm_id, alt_scores in self.individual_scores.items():
            if dm_id not in dm_ids:
                raise ValueError(
                    f"GroupDecisionProblem: 评分中存在未定义的决策者 '{dm_id}'"
                )

            if not isinstance(alt_scores, dict):
                raise ValueError(
                    f"GroupDecisionProblem: 决策者 '{dm_id}' 的评分必须是字典"
                )

            # 验证所有备选方案都有评分
            for alt in self.alternatives:
                if alt not in alt_scores:
                    raise ValueError(
                        f"GroupDecisionProblem: 决策者 '{dm_id}' 缺少方案 '{alt}' 的评分"
                    )

                crit_scores = alt_scores[alt]
                if not isinstance(crit_scores, dict):
                    raise ValueError(
                        f"GroupDecisionProblem: 决策者 '{dm_id}' 对方案 '{alt}' 的评分必须是字典"
                    )

                # 验证评分范围
                for crit_name, score in crit_scores.items():
                    if not isinstance(score, (int, float)):
                        raise ValueError(
                            f"GroupDecisionProblem: 评分必须是数值类型 "
                            f"(DM: {dm_id}, Alt: {alt}, Crit: {crit_name})"
                        )
                    if not (0 <= score <= 100):
                        raise ValueError(
                            f"GroupDecisionProblem: 评分必须在 0-100 范围内 "
                            f"(DM: {dm_id}, Alt: {alt}, Crit: {crit_name}, Score: {score})"
                        )

    def get_decision_maker(self, dm_id: str) -> DecisionMaker | None:
        """获取指定 ID 的决策者

        Args:
            dm_id: 决策者 ID

        Returns:
            决策者对象，不存在则返回 None
        """
        for dm in self.decision_makers:
            if dm.id == dm_id:
                return dm
        return None

    def get_decision_maker_weights(self) -> dict[str, float]:
        """获取所有决策者的权重

        Returns:
            {decision_maker_id: weight}
        """
        return {dm.id: dm.weight for dm in self.decision_makers}
