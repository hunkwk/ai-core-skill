"""
MCDA Core - 群决策服务

提供群决策分析的核心服务功能。
"""

from .models import DecisionMaker, GroupDecisionProblem, AggregationConfig
from .consensus import ConsensusMeasure, ConsensusResult
from ..aggregation import AggregationRegistry
from ..models import DecisionProblem, Criterion


class GroupDecisionService:
    """群决策服务

    提供群决策分析的完整功能：
    1. 评分聚合
    2. 共识度测量
    3. 转换为单决策者问题
    """

    def __init__(self):
        """初始化服务"""
        self.consensus_measure = ConsensusMeasure()

    def aggregate_scores(
        self,
        problem: GroupDecisionProblem,
        method: str | None = None
    ) -> dict[str, dict[str, float]]:
        """聚合个人评分为群决策评分

        Args:
            problem: 群决策问题
            method: 聚合方法名称（默认使用配置中的方法）

        Returns:
            聚合后的评分矩阵 {alternative: {criterion: score}}
        """
        # 确定使用的聚合方法
        if method is None:
            config = problem.aggregation_config
            if config is not None:
                method = config.score_aggregation
            else:
                method = "weighted_average"

        # 获取聚合方法实例
        aggregation_method = AggregationRegistry.create(method)

        # 获取决策者权重
        dm_weights = problem.get_decision_maker_weights()

        # 转换评分格式
        score_matrix: dict[str, dict[str, dict[str, float]]] = {}
        for alt in problem.alternatives:
            score_matrix[alt] = {}
            crit_names = [c.name if hasattr(c, 'name') else str(c) for c in problem.criteria]
            for crit in crit_names:
                score_matrix[alt][crit] = {}
                for dm in problem.decision_makers:
                    score = problem.individual_scores.get(dm.id, {}).get(alt, {}).get(crit, 0)
                    score_matrix[alt][crit][dm.id] = score

        # 执行聚合
        return aggregation_method.aggregate_matrix(score_matrix, dm_weights)

    def compute_consensus(
        self,
        problem: GroupDecisionProblem,
        threshold: float | None = None,
        method: str = "standard_deviation"
    ) -> ConsensusResult:
        """计算群决策共识度

        Args:
            problem: 群决策问题
            threshold: 共识阈值（默认使用配置中的阈值）
            method: 共识度计算方法

        Returns:
            共识度测量结果
        """
        # 确定使用的阈值
        if threshold is None:
            config = problem.aggregation_config
            if config is not None:
                threshold = config.consensus_threshold
            else:
                threshold = 0.7

        return self.consensus_measure.compute_consensus(
            individual_scores=problem.individual_scores,
            alternatives=problem.alternatives,
            criteria=problem.criteria,
            threshold=threshold,
            method=method
        )

    def to_decision_problem(
        self,
        problem: GroupDecisionProblem,
        aggregation_method: str | None = None
    ) -> DecisionProblem:
        """将群决策问题转换为单决策者问题

        Args:
            problem: 群决策问题
            aggregation_method: 聚合方法名称

        Returns:
            单决策者问题对象
        """
        # 聚合评分
        aggregated_scores = self.aggregate_scores(problem, aggregation_method)

        # 创建决策问题
        return DecisionProblem(
            alternatives=problem.alternatives,
            criteria=problem.criteria,  # type: ignore
            scores=aggregated_scores
        )

    def analyze(
        self,
        problem: GroupDecisionProblem,
        check_consensus: bool = True,
        aggregation_method: str | None = None
    ) -> tuple[dict[str, dict[str, float]], ConsensusResult | None]:
        """分析群决策问题

        Args:
            problem: 群决策问题
            check_consensus: 是否检查共识度
            aggregation_method: 聚合方法名称

        Returns:
            (聚合评分, 共识度结果)
        """
        # 聚合评分
        aggregated_scores = self.aggregate_scores(problem, aggregation_method)

        # 计算共识度
        consensus_result = None
        if check_consensus:
            consensus_result = self.compute_consensus(problem)

        return aggregated_scores, consensus_result
