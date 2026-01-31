"""
MCDA Core 敏感性分析服务

功能:
- 权重扰动测试
- 排名变化检测
- 关键准则识别
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcda_core.models import Criterion, DecisionProblem, DecisionResult, MCDAAlgorithm


# ============================================================================
# SensitivityService
# ============================================================================

class SensitivityService:
    """敏感性分析服务"""

    def perturb_weights(
        self,
        problem: "DecisionProblem",
        algorithm: "MCDAAlgorithm",
        *,
        criterion_name: str,
        perturbation: float,
    ) -> "SensitivityResult":
        """
        扰动单个准则的权重

        Args:
            problem: 决策问题
            algorithm: MCDA 算法
            criterion_name: 准则名称
            perturbation: 扰动幅度（0-1）

        Returns:
            SensitivityResult: 敏感性分析结果（使用现有模型）

        Raises:
            SensitivityAnalysisError: 扰动值无效或准则不存在
        """
        from mcda_core.exceptions import SensitivityAnalysisError
        from mcda_core.models import PerturbationResult, SensitivityResult

        # 验证扰动值
        if perturbation < 0.0 or perturbation > 1.0:
            raise SensitivityAnalysisError(
                f"扰动幅度必须在 [0, 1] 范围内，当前值为 {perturbation}",
            )

        # 查找准则（使用更 Pythonic 的方式）
        target_criterion = next(
            (c for c in problem.criteria if c.name == criterion_name),
            None
        )

        if target_criterion is None:
            raise SensitivityAnalysisError(
                f"准则 '{criterion_name}' 不存在",
            )

        original_weight = target_criterion.weight
        perturbations = []

        # 计算原始排名
        original_result = algorithm.calculate(problem)
        original_ranks = {r.alternative: r.rank for r in original_result.rankings}

        # 扰动 +perturbation 和 -perturbation
        for delta in [perturbation, -perturbation]:
            # 计算新权重
            new_weight = original_weight * (1 + delta)

            # 归一化权重（重新分配其他准则的权重）
            new_criteria = []
            for crit in problem.criteria:
                if crit.name == criterion_name:
                    # 使用扰动后的权重
                    new_criteria.append(
                        type(crit)(
                            name=crit.name,
                            weight=new_weight,
                            direction=crit.direction,
                        )
                    )
                else:
                    # 按比例调整其他准则的权重
                    scale_factor = (1 - new_weight) / (1 - original_weight)
                    new_criteria.append(
                        type(crit)(
                            name=crit.name,
                            weight=crit.weight * scale_factor,
                            direction=crit.direction,
                        )
                    )

            # 创建新的决策问题
            from mcda_core.models import DecisionProblem
            new_problem = DecisionProblem(
                alternatives=problem.alternatives,
                criteria=tuple(new_criteria),
                scores=problem.scores,
            )

            # 计算新排名
            new_result = algorithm.calculate(new_problem)

            # 构建排名变化字典 {alternative: (old_rank, new_rank)}
            rank_changes = {}
            for r in new_result.rankings:
                old_rank = original_ranks.get(r.alternative, r.rank)
                rank_changes[r.alternative] = (old_rank, r.rank)

            # 创建 PerturbationResult（匹配现有模型）
            perturbations.append(
                PerturbationResult(
                    criterion_name=criterion_name,
                    original_weight=original_weight,
                    perturbed_weight=new_weight,
                    delta=delta,
                    rank_changes=rank_changes,
                )
            )

        return SensitivityResult(
            perturbations=perturbations,
            critical_criteria=[],
            robustness_score=1.0,
        )

    def detect_ranking_changes(
        self,
        original: "DecisionResult",
        new: "DecisionResult",
    ) -> list[dict[str, Any]]:
        """
        检测排名变化

        Args:
            original: 原始排名结果
            new: 新排名结果

        Returns:
            list[dict]: 排名变化列表
        """
        changes = []

        # 构建原始排名映射
        original_ranks = {r.alternative: r.rank for r in original.rankings}

        # 检测变化
        for ranking in new.rankings:
            old_rank = original_ranks.get(ranking.alternative, ranking.rank)
            rank_change = old_rank - ranking.rank

            if rank_change != 0:
                changes.append({
                    "alternative": ranking.alternative,
                    "old_rank": old_rank,
                    "new_rank": ranking.rank,
                    "rank_change": rank_change,
                })

        return changes

    def identify_critical_criteria(
        self,
        problem: "DecisionProblem",
        algorithm: "MCDAAlgorithm",
        *,
        perturbation: float = 0.1,
        threshold: int = 1,
    ) -> list["CriticalCriterion"]:
        """
        识别关键准则

        Args:
            problem: 决策问题
            algorithm: MCDA 算法
            perturbation: 扰动幅度
            threshold: 排名变化阈值

        Returns:
            list[CriticalCriterion]: 关键准则列表（按影响程度降序）
        """
        from mcda_core.models import CriticalCriterion

        critical_criteria = []

        for crit in problem.criteria:
            # 扰动该准则的权重
            result = self.perturb_weights(
                problem=problem,
                algorithm=algorithm,
                criterion_name=crit.name,
                perturbation=perturbation,
            )

            # 计算最大排名变化
            max_rank_changes = 0
            for p in result.perturbations:
                # 统计有变化的方案数
                changes = sum(
                    1 for old, new in p.rank_changes.values() if old != new
                )
                max_rank_changes = max(max_rank_changes, changes)

            # 如果超过阈值，则认为是关键准则
            if max_rank_changes >= threshold:
                critical_criteria.append(
                    CriticalCriterion(
                        criterion_name=crit.name,
                        weight=crit.weight,
                        rank_changes=max_rank_changes,
                    )
                )

        # 按影响程度降序排列
        critical_criteria.sort(key=lambda x: x.rank_changes, reverse=True)

        return critical_criteria

    def analyze(
        self,
        problem: "DecisionProblem",
        algorithm: "MCDAAlgorithm",
        *,
        perturbation: float = 0.1,
    ) -> "SensitivityAnalysisResult":
        """
        综合敏感性分析

        Args:
            problem: 决策问题
            algorithm: MCDA 算法
            perturbation: 扰动幅度

        Returns:
            SensitivityAnalysisResult: 敏感性分析结果
        """
        from mcda_core.models import SensitivityResult, SensitivityAnalysisResult

        # 识别关键准则
        critical_criteria = self.identify_critical_criteria(
            problem=problem,
            algorithm=algorithm,
            perturbation=perturbation,
            threshold=1,  # 至少1个排名变化
        )

        # 扰动所有准则
        perturbation_results = []
        for crit in problem.criteria:
            result = self.perturb_weights(
                problem=problem,
                algorithm=algorithm,
                criterion_name=crit.name,
                perturbation=perturbation,
            )
            perturbation_results.append(result)

        return SensitivityAnalysisResult(
            critical_criteria=tuple(critical_criteria),
            perturbation_results=tuple(perturbation_results),
        )

    def _count_ranking_changes(
        self,
        original: "DecisionResult",
        new: "DecisionResult",
    ) -> int:
        """
        计算排名变化总数

        Args:
            original: 原始排名结果
            new: 新排名结果

        Returns:
            int: 排名变化总数
        """
        changes = self.detect_ranking_changes(original, new)
        return len(changes)


# ============================================================================
# 辅助数据类（已存在于 models.py，这里仅用于类型提示）
# ============================================================================

if TYPE_CHECKING:
    from mcda_core.models import CriticalCriterion, SensitivityAnalysisResult
