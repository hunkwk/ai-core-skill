"""
MCDA Core - WPM 算法实现

加权几何平均模型（Weighted Product Model）。
"""

from typing import Any, TYPE_CHECKING

from .base import MCDAAlgorithm, register_algorithm
from ..models import MAX_SCORE

# 类型注解导入
if TYPE_CHECKING:
    from mcda_core.models import DecisionProblem, DecisionResult


@register_algorithm("wpm")
class WPMAlgorithm(MCDAAlgorithm):
    """加权几何平均模型

    公式: P_i = Π r_ij^w_j

    适用场景:
        - 准则间有乘积效应
        - 需要强调"短板效应"
        - 非线性聚合

    特点:
        - 几何平均，低分拖累
        - 考虑准则间相互作用
        - 对零值敏感（需要特殊处理）
    """

    # 避免零值的小常数
    EPSILON = 1e-10

    @property
    def name(self) -> str:
        """算法名称"""
        return "wpm"

    @property
    def description(self) -> str:
        """算法描述"""
        return "加权几何平均模型（Weighted Product Model）"

    def calculate(
        self,
        problem: "DecisionProblem",
        **kwargs: Any
    ) -> "DecisionResult":
        """执行 WPM 计算

        Args:
            problem: 决策问题
            **kwargs: 未使用（保持接口一致性）

        Returns:
            决策结果
        """
        # 运行时导入（避免循环导入）
        from mcda_core.models import DecisionResult, RankingItem, ResultMetadata

        # 验证输入
        self.validate(problem)

        # 计算每个方案的加权乘积
        products = {}
        for alt in problem.alternatives:
            product = 1.0
            for crit in problem.criteria:
                value = problem.scores[alt][crit.name]

                # 处理 lower_better（方向反转）
                if crit.direction == "lower_better":
                    # 假设评分在 0-100 范围内
                    value = MAX_SCORE - value

                # 避免零值（加小常数）
                value = max(value, self.EPSILON)

                # 加权乘积：value^weight
                product *= value ** crit.weight

            products[alt] = product

        # 排序（得分从高到低）
        sorted_alts = sorted(
            products.items(),
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
            metrics={"products": products},
        )

        # 构建结果
        result = DecisionResult(
            rankings=rankings,
            raw_scores=products,
            metadata=metadata,
        )

        return result
