"""
ConstraintService: 一票否决约束服务

提供决策问题的约束过滤和惩罚应用功能
"""

from typing import Any

from mcda_core.constraints.evaluator import VetoEvaluator
from mcda_core.constraints.models import ConstraintMetadata, VetoResult
from ..models import DecisionProblem


class ConstraintService:
    """
    一票否决约束服务

    提供决策问题的约束过滤和惩罚应用功能

    Examples:
        >>> service = ConstraintService()
        >>> filtered_problem, veto_results = service.filter_problem(problem)
        >>> adjusted_problem = service.apply_penalties(problem)
        >>> metadata = service.get_constraint_metadata(problem, veto_results)
    """

    def __init__(self):
        """初始化服务，创建 VetoEvaluator"""
        self.evaluator = VetoEvaluator()

    def filter_problem(
        self,
        problem: DecisionProblem
    ) -> tuple[DecisionProblem, dict[str, VetoResult]]:
        """
        过滤决策问题，移除被拒绝的方案

        Args:
            problem: 原始决策问题

        Returns:
            tuple[DecisionProblem, dict[str, VetoResult]]:
                - 过滤后的决策问题
                - 所有方案的否决结果 {alternative_id: VetoResult}
        """
        # 评估所有方案
        veto_results = {}
        for alt_id in problem.alternatives:
            # 获取该方案的评分
            scores = problem.scores.get(alt_id, {})
            if not scores:
                continue

            # 评估该方案
            result = self.evaluator.evaluate(alt_id, scores, problem.criteria)
            veto_results[alt_id] = result

        # 过滤掉被拒绝的方案
        accepted_alternatives = [
            alt_id for alt_id, result in veto_results.items()
            if not result.rejected
        ]

        # 如果所有方案都被拒绝，返回原问题
        if not accepted_alternatives:
            return problem, veto_results

        # 创建过滤后的问题
        filtered_problem = self._create_filtered_problem(
            problem,
            accepted_alternatives
        )

        return filtered_problem, veto_results

    def apply_penalties(self, problem: DecisionProblem) -> DecisionProblem:
        """
        应用惩罚分数到评分

        为每个方案添加 "penalty" 准则，记录软否决的惩罚分数

        Args:
            problem: 决策问题

        Returns:
            DecisionProblem: 应用惩罚后的问题
        """
        # 创建新的评分矩阵
        new_scores = {}
        for alt_id in problem.alternatives:
            scores = problem.scores.get(alt_id, {}).copy()
            if not scores:
                new_scores[alt_id] = scores
                continue

            # 评估该方案
            result = self.evaluator.evaluate(alt_id, scores, problem.criteria)

            # 如果有惩罚，添加到评分中
            if result.total_penalty != 0:
                scores["penalty"] = result.total_penalty

            new_scores[alt_id] = scores

        # 创建新的决策问题对象（由于 frozen，需要创建新实例）
        # 这里我们简化处理，直接修改 scores
        # 实际项目中可能需要创建新的 DecisionProblem 实例
        adjusted_problem = DecisionProblem(
            alternatives=problem.alternatives,
            criteria=problem.criteria,
            scores=new_scores,
            algorithm=problem.algorithm if hasattr(problem, 'algorithm') else None,
            data_source=problem.data_source if hasattr(problem, 'data_source') else None,
            raw_data=problem.raw_data if hasattr(problem, 'raw_data') else None,
            score_range=problem.score_range if hasattr(problem, 'score_range') else (0.0, 100.0),
        )

        return adjusted_problem

    def get_constraint_metadata(
        self,
        problem: DecisionProblem,
        veto_results: dict[str, VetoResult]
    ) -> ConstraintMetadata:
        """
        获取约束元数据

        统计被拒绝、警告、接受的方案数量

        Args:
            problem: 决策问题
            veto_results: 否决结果字典

        Returns:
            ConstraintMetadata: 约束元数据
        """
        total = len(problem.alternatives)
        rejected = sum(1 for result in veto_results.values() if result.rejected)
        warning = sum(1 for result in veto_results.values() if not result.rejected and result.warnings)
        accepted = total - rejected - warning

        return ConstraintMetadata(
            total_alternatives=total,
            rejected_count=rejected,
            warning_count=warning,
            accept_count=accepted
        )

    def _create_filtered_problem(
        self,
        problem: DecisionProblem,
        accepted_alternatives: list[str]
    ) -> DecisionProblem:
        """
        创建过滤后的决策问题（私有方法）

        Args:
            problem: 原始决策问题
            accepted_alternatives: 被接受的方案列表

        Returns:
            DecisionProblem: 过滤后的决策问题
        """
        # 过滤评分矩阵
        filtered_scores = {
            alt_id: problem.scores[alt_id]
            for alt_id in accepted_alternatives
            if alt_id in problem.scores
        }

        # 创建新的决策问题
        filtered_problem = DecisionProblem(
            alternatives=tuple(accepted_alternatives),
            criteria=problem.criteria,
            scores=filtered_scores,
            algorithm=problem.algorithm if hasattr(problem, 'algorithm') else None,
            data_source=problem.data_source if hasattr(problem, 'data_source') else None,
            raw_data=problem.raw_data if hasattr(problem, 'raw_data') else None,
            score_range=problem.score_range if hasattr(problem, 'score_range') else (0.0, 100.0),
        )

        return filtered_problem
