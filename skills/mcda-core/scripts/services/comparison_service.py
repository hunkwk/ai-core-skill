"""
算法对比服务

提供多算法结果对比功能。
"""

import numpy as np
from typing import Literal

from ..algorithms import get_algorithm, list_algorithms


class ComparisonValidationError(Exception):
    """对比验证错误"""
    pass


class ComparisonService:
    """算法对比服务

    对比多个 MCDA 算法的排序结果。

    Example:
        ```python
        service = ComparisonService()

        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        # 对比多个算法
        result = service.compare_algorithms(
            decision_matrix,
            weights,
            algorithms=["wsm", "topsis", "vikor"]
        )

        # 查看排名
        for algo_result in result["rankings"]:
            print(f"{algo_result['algorithm']}: {algo_result['ranking']}")

        # 查看相关性
        print(result["correlations"])

        # 查看差异
        print(result["differences"])
        ```
    """

    def __init__(self):
        """初始化对比服务

        自动从算法注册表获取所有已注册的算法。
        无需手动维护算法列表，支持动态扩展。
        """
        # 从算法注册表动态获取所有已注册算法
        self.supported_algorithms = list_algorithms()

    # ========================================================================
    # 算法对比
    # ========================================================================

    def compare_algorithms(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        algorithms: list[str],
        criteria_directions: list[Literal["higher_better", "lower_better"]] | None = None,
        alternatives: list[str] | None = None
    ) -> dict[str, any]:
        """对比多个算法的排序结果

        Args:
            decision_matrix: 决策矩阵 (n_alternatives x n_criteria)
            weights: 准则权重
            algorithms: 算法名称列表
            criteria_directions: 准则方向列表
            alternatives: 方案名称列表

        Returns:
            对比结果字典，包含：
            - rankings: 各算法的排名
            - correlations: 算法间的相关性矩阵
            - differences: 排名差异列表
            - summary: 对比摘要
        """
        # 验证输入
        self._validate_input(decision_matrix, weights, algorithms)

        n_alternatives = decision_matrix.shape[0]

        # 方案名称
        if alternatives is None:
            alternatives = [f"A{i}" for i in range(n_alternatives)]

        # 准则方向
        if criteria_directions is None:
            criteria_directions = ["higher_better"] * len(weights)

        # 运行所有算法
        rankings = {}

        # 转换决策矩阵为 scores 字典格式
        # decision_matrix: np.ndarray (n_alternatives x n_criteria)
        # scores: {alternative: {criterion: score}}
        scores = {}
        for i, alt_name in enumerate(alternatives):
            scores[alt_name] = {}
            for j in range(len(weights)):
                criterion_name = f"C{j}"
                scores[alt_name][criterion_name] = float(decision_matrix[i, j])

        # 创建准则列表
        from ..models import Criterion, AlgorithmConfig
        criteria = []
        for j, direction in enumerate(criteria_directions):
            criterion_name = f"C{j}"
            criteria.append(
                Criterion(
                    name=criterion_name,
                    weight=float(weights[j]),
                    direction=direction
                )
            )

        for algo_name in algorithms:
            algo = get_algorithm(algo_name)

            # 创建 DecisionProblem（使用正确的 API）
            # 注意：禁用评分范围验证，因为决策矩阵可能包含任意数值
            from ..models import DecisionProblem
            problem = DecisionProblem(
                alternatives=tuple(alternatives),
                criteria=tuple(criteria),
                scores=scores,
                algorithm=AlgorithmConfig(name=algo_name),
                score_range=(-float('inf'), float('inf'))  # 允许任意范围
            )

            result = algo.calculate(problem)

            # 提取排名（DecisionResult 是 dataclass，访问 rankings 属性）
            ranking = [0] * n_alternatives
            for rank_item in result.rankings:
                # rank_item.alternative 是方案名称（如 "A0"）
                # rank_item.rank 是排名（从 1 开始）
                alt_name = rank_item.alternative
                rank_value = rank_item.rank

                # 从方案名称中提取索引
                if isinstance(alt_name, str) and alt_name.startswith("A"):
                    idx = int(alt_name.replace("A", ""))
                else:
                    # 如果不是标准格式，从 alternatives 列表中查找
                    idx = alternatives.index(alt_name)

                ranking[idx] = rank_value - 1  # 转换为 0-based

            rankings[algo_name] = ranking

        # 计算相关性
        correlations = self._calculate_correlation_matrix(rankings)

        # 识别差异
        differences = self.identify_ranking_differences(rankings)

        # 生成摘要
        summary = self._generate_summary(rankings, correlations, differences)

        return {
            "rankings": [
                {
                    "algorithm": algo,
                    "ranking": rankings[algo],
                }
                for algo in algorithms
            ],
            "correlations": correlations,
            "differences": differences,
            "summary": summary,
        }

    def calculate_ranking_correlation(
        self,
        ranking1: list[int],
        ranking2: list[int]
    ) -> float:
        """计算两个排名的 Spearman 相关系数

        Args:
            ranking1: 第一个排名
            ranking2: 第二个排名

        Returns:
            Spearman 相关系数 (范围 [-1, 1])

        Raises:
            ValueError: 排名长度不一致
        """
        if len(ranking1) != len(ranking2):
            raise ValueError(
                f"排名长度不一致: {len(ranking1)} vs {len(ranking2)}"
            )

        n = len(ranking1)

        if n <= 1:
            return 1.0  # 只有一个元素时，完全相关

        # 计算排名差值平方和
        # ρ = 1 - (6 * Σd²) / (n * (n² - 1))
        sum_squared_diff = sum((r1 - r2) ** 2 for r1, r2 in zip(ranking1, ranking2))

        denominator = n * (n ** 2 - 1)

        if denominator == 0:
            return 1.0

        correlation = 1 - (6 * sum_squared_diff) / denominator

        return float(correlation)

    def identify_ranking_differences(
        self,
        rankings: dict[str, list[int]]
    ) -> list[dict]:
        """识别排名差异

        Args:
            rankings: 各算法的排名字典

        Returns:
            差异列表，每个差异包含：
            - alternative: 方案索引
            - algorithms: 涉及的算法
            - ranks: 各算法中的排名
            - variance: 排名方差
        """
        n_alternatives = len(next(iter(rankings.values())))
        algorithm_names = list(rankings.keys())

        differences = []

        for alt_idx in range(n_alternatives):
            # 收集该方案在各算法中的排名
            ranks = [
                rankings[algo][alt_idx]
                for algo in algorithm_names
            ]

            # 计算排名方差
            rank_variance = np.var(ranks)

            # 如果有差异（方差 > 0）
            if rank_variance > 0:
                differences.append({
                    "alternative": alt_idx,
                    "algorithms": algorithm_names,
                    "ranks": ranks,
                    "variance": float(rank_variance),
                    "min_rank": int(min(ranks)),
                    "max_rank": int(max(ranks)),
                })

        # 按方差降序排序
        differences.sort(key=lambda x: x["variance"], reverse=True)

        return differences

    def generate_comparison_report(
        self,
        comparison_result: dict[str, any]
    ) -> str:
        """生成对比报告（文本格式）

        Args:
            comparison_result: compare_algorithms() 的返回结果

        Returns:
            文本报告
        """
        lines = []
        lines.append("=" * 60)
        lines.append("算法对比报告")
        lines.append("=" * 60)
        lines.append("")

        # 排名部分
        lines.append("排名结果:")
        lines.append("-" * 40)
        for algo_result in comparison_result["rankings"]:
            algo_name = algo_result["algorithm"].upper()
            ranking = algo_result["ranking"]
            lines.append(f"{algo_name}: {ranking}")
        lines.append("")

        # 相关性部分
        if comparison_result["correlations"]:
            lines.append("算法相关性 (Spearman):")
            lines.append("-" * 40)
            corr = comparison_result["correlations"]
            for pair, value in corr.items():
                lines.append(f"{pair}: {value:.3f}")
            lines.append("")

        # 差异部分
        if comparison_result["differences"]:
            lines.append("排名差异:")
            lines.append("-" * 40)
            for diff in comparison_result["differences"][:5]:  # 只显示前5个
                alt = diff["alternative"]
                var = diff["variance"]
                min_r = diff["min_rank"]
                max_r = diff["max_rank"]
                lines.append(f"方案 {alt}: 方差={var:.2f}, 排名范围=[{min_r}, {max_r}]")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    # ========================================================================
    # 内部方法
    # ========================================================================

    def _validate_input(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        algorithms: list[str]
    ) -> None:
        """验证输入

        Args:
            decision_matrix: 决策矩阵
            weights: 权重
            algorithms: 算法列表

        Raises:
            ComparisonValidationError: 验证失败
        """
        # 验证决策矩阵
        if not isinstance(decision_matrix, np.ndarray):
            raise ComparisonValidationError(
                f"决策矩阵必须是 numpy 数组，当前类型: {type(decision_matrix)}"
            )

        if decision_matrix.ndim != 2:
            raise ComparisonValidationError(
                f"决策矩阵必须是二维数组，当前维度: {decision_matrix.ndim}"
            )

        n_alternatives, n_criteria = decision_matrix.shape

        if n_alternatives < 1:
            raise ComparisonValidationError("至少需要 1 个备选方案")

        if n_criteria < 1:
            raise ComparisonValidationError("至少需要 1 个准则")

        # 验证权重
        if len(weights) != n_criteria:
            raise ValueError(
                f"权重数量 ({len(weights)}) 必须等于准则数量 ({n_criteria})"
            )

        # 验证算法列表
        if not algorithms:
            raise ComparisonValidationError("算法列表不能为空")

        for algo in algorithms:
            if algo not in self.supported_algorithms:
                raise ComparisonValidationError(
                    f"不支持的算法: '{algo}'. "
                    f"支持的算法: {self.supported_algorithms}"
                )

    def _calculate_correlation_matrix(
        self,
        rankings: dict[str, list[int]]
    ) -> dict[str, float]:
        """计算算法间的相关性矩阵

        Args:
            rankings: 各算法的排名

        Returns:
            相关性字典 {pair: correlation}
        """
        algorithm_names = list(rankings.keys())
        correlations = {}

        for i, algo1 in enumerate(algorithm_names):
            for algo2 in algorithm_names[i + 1:]:
                corr = self.calculate_ranking_correlation(
                    rankings[algo1],
                    rankings[algo2]
                )
                pair_name = f"{algo1.upper()} vs {algo2.upper()}"
                correlations[pair_name] = corr

        return correlations

    def _generate_summary(
        self,
        rankings: dict[str, list[int]],
        correlations: dict[str, float],
        differences: list[dict]
    ) -> dict[str, any]:
        """生成对比摘要

        Args:
            rankings: 各算法的排名
            correlations: 相关性矩阵
            differences: 排名差异

        Returns:
            摘要字典
        """
        n_algorithms = len(rankings)
        n_alternatives = len(next(iter(rankings.values())))

        # 平均相关性
        if correlations:
            avg_correlation = np.mean(list(correlations.values()))
        else:
            avg_correlation = 0.0

        # 最大差异
        if differences:
            max_variance = max(d["variance"] for d in differences)
        else:
            max_variance = 0.0

        return {
            "n_algorithms": n_algorithms,
            "n_alternatives": n_alternatives,
            "avg_correlation": float(avg_correlation),
            "max_variance": float(max_variance),
            "has_differences": len(differences) > 0,
        }
