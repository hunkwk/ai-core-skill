"""
MCDA Core - WSM 算法实现

加权算术平均模型（Weighted Sum Model）。
"""

from typing import Any, TYPE_CHECKING

from skills.mcda_core.lib.algorithms.base import MCDAAlgorithm, register_algorithm

# 类型注解导入
if TYPE_CHECKING:
    from skills.mcda_core.lib.models import DecisionProblem, DecisionResult


@register_algorithm("wsm")
class WSMAlgorithm(MCDAAlgorithm):
    """加权算术平均模型

    公式: S_i = Σ w_j · r_ij

    适用场景:
        - 准则间相互独立
        - 最通用、最直观的决策场景
        - 快速决策

    特点:
        - 线性聚合
        - 简单易懂
        - 计算效率高
    """

    @property
    def name(self) -> str:
        """算法名称"""
        return "wsm"

    @property
    def description(self) -> str:
        """算法描述"""
        return "加权算术平均模型（Weighted Sum Model）"

    def calculate(
        self,
        problem: "DecisionProblem",
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 WSM 计算

        Args:
            problem: 决策问题
            **kwargs: 未使用（保持接口一致性）

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from skills.mcda_core.lib.models import DecisionResult, RankingItem, ResultMetadata

        # 验证输入
        self.validate(problem)

        # 计算每个方案的加权得分
        weighted_sums = {}
        for alt in problem.alternatives:
            weighted_sum = 0.0
            for crit in problem.criteria:
                value = problem.scores[alt][crit.name]

                # 处理 lower_better（方向反转）
                if crit.direction == "lower_better":
                    # 假设评分在 0-100 范围内
                    value = 100.0 - value

                weighted_sum += crit.weight * value

            weighted_sums[alt] = weighted_sum

        # 排序（得分从高到低）
        sorted_alts = sorted(
            weighted_sums.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 构建排名
        rankings = [
            RankingItem(
                rank=i,
                alternative=alt,
                score=round(score, 4)
            )
            for i, (alt, score) in enumerate(sorted_alts, 1)
        ]

        # 构建元数据（包含 metrics）
        metadata = ResultMetadata(
            algorithm_name=self.name,
            problem_size=(len(problem.alternatives), len(problem.criteria)),
            metrics={"weighted_sums": weighted_sums},
        )

        # 构建结果
        result = DecisionResult(
            rankings=rankings,
            raw_scores=weighted_sums,
            metadata=metadata,
        )

        return result
