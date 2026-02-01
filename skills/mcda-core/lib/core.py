"""
MCDA Core - 核心编排器模块

提供决策问题的完整工作流程：加载、验证、分析、报告生成。
"""

from pathlib import Path
from datetime import datetime
from typing import Any

from mcda_core.models import (
    DecisionProblem,
    DecisionResult,
    Criterion,
    Direction,
)
from mcda_core.utils import load_yaml, normalize_weights
from mcda_core.algorithms import get_algorithm
from mcda_core.validation import ValidationService, ValidationResult
from mcda_core.reporter import ReportService
from mcda_core.sensitivity import SensitivityService
from mcda_core.exceptions import (
    MCDAError,
    YAMLParseError,
    ValidationError as MCDAValidationError,
)


# =============================================================================
# MCDAOrchestrator - 核心编排器
# =============================================================================

class MCDAOrchestrator:
    """MCDA 核心编排器

    协调各个服务模块，提供完整的决策分析工作流程：
    1. 加载配置（YAML）
    2. 验证数据
    3. 执行算法分析
    4. 生成报告
    5. 敏感性分析
    """

    def __init__(self):
        """初始化编排器"""
        self.validation_service = ValidationService()
        self.reporter_service = ReportService()
        self.sensitivity_service = SensitivityService()

    # -------------------------------------------------------------------------
    # 加载决策问题
    # -------------------------------------------------------------------------

    def load_from_yaml(
        self,
        file_path: Path | str,
        auto_normalize_weights: bool = True
    ) -> DecisionProblem:
        """从 YAML 文件加载决策问题

        Args:
            file_path: YAML 配置文件路径
            auto_normalize_weights: 是否自动归一化权重（默认 True）

        Returns:
            决策问题对象

        Raises:
            YAMLParseError: YAML 文件格式错误
            MCDAValidationError: 数据验证失败
        """
        # 1. 加载 YAML
        data = load_yaml(file_path)

        # 2. 解析备选方案
        alternatives = self._parse_alternatives(data)

        # 3. 解析准则
        criteria = self._parse_criteria(data, auto_normalize_weights)

        # 4. 解析评分矩阵
        scores = self._parse_scores(data, alternatives, criteria)

        # 5. 解析算法配置
        algorithm_config = self._parse_algorithm_config(data)

        # 6. 创建决策问题
        try:
            problem = DecisionProblem(
                alternatives=tuple(alternatives),
                criteria=tuple(criteria),
                scores=scores,
                algorithm=algorithm_config
            )
        except Exception as e:
            raise MCDAValidationError(
                f"创建决策问题失败: {str(e)}",
                details={"error": str(e)}
            ) from e

        return problem

    def _parse_alternatives(self, data: dict[str, Any]) -> list[str]:
        """解析备选方案列表"""
        if "alternatives" not in data:
            raise MCDAValidationError(
                "YAML 配置缺少 'alternatives' 字段",
                field="alternatives"
            )

        alternatives = data["alternatives"]

        if not isinstance(alternatives, list):
            raise MCDAValidationError(
                f"'alternatives' 必须是列表，实际类型: {type(alternatives).__name__}",
                field="alternatives"
            )

        if len(alternatives) < 2:
            raise MCDAValidationError(
                f"至少需要 2 个备选方案，当前: {len(alternatives)}",
                field="alternatives",
                count=len(alternatives)
            )

        return [str(alt) for alt in alternatives]

    def _parse_criteria(
        self,
        data: dict[str, Any],
        auto_normalize_weights: bool
    ) -> list[Criterion]:
        """解析准则列表"""
        if "criteria" not in data:
            raise MCDAValidationError(
                "YAML 配置缺少 'criteria' 字段",
                field="criteria"
            )

        criteria_data = data["criteria"]

        if not isinstance(criteria_data, list):
            raise MCDAValidationError(
                f"'criteria' 必须是列表，实际类型: {type(criteria_data).__name__}",
                field="criteria"
            )

        if len(criteria_data) < 1:
            raise MCDAValidationError(
                f"至少需要 1 个准则，当前: {len(criteria_data)}",
                field="criteria",
                count=len(criteria_data)
            )

        # 提取权重
        weights = {}
        criterion_list = []

        for i, crit_data in enumerate(criteria_data):
            if not isinstance(crit_data, dict):
                raise MCDAValidationError(
                    f"准则 {i} 必须是字典，实际类型: {type(crit_data).__name__}",
                    field="criteria"
                )

            if "name" not in crit_data:
                raise MCDAValidationError(
                    f"准则 {i} 缺少 'name' 字段",
                    field="criteria"
                )

            name = str(crit_data["name"])

            if "weight" not in crit_data:
                raise MCDAValidationError(
                    f"准则 '{name}' 缺少 'weight' 字段",
                    field="criteria",
                    criterion=name
                )

            weight = float(crit_data["weight"])

            if "direction" not in crit_data:
                raise MCDAValidationError(
                    f"准则 '{name}' 缺少 'direction' 字段",
                    field="criteria",
                    criterion=name
                )

            direction = crit_data["direction"]

            if direction not in ["higher_better", "lower_better"]:
                raise MCDAValidationError(
                    f"准则 '{name}' 的 'direction' 值无效: '{direction}'，"
                    f"必须是 'higher_better' 或 'lower_better'",
                    field="criteria",
                    criterion=name
                )

            weights[name] = weight

            criterion_list.append(
                Criterion(
                    name=name,
                    weight=weight,  # 临时值，稍后归一化
                    direction=direction,
                    description=crit_data.get("description", "")
                )
            )

        # 归一化权重
        if auto_normalize_weights:
            normalized_weights = normalize_weights(weights)

            # 更新准则权重
            criterion_list = [
                Criterion(
                    name=c.name,
                    weight=normalized_weights[c.name],
                    direction=c.direction,
                    description=c.description
                )
                for c in criterion_list
            ]

        return criterion_list

    def _parse_scores(
        self,
        data: dict[str, Any],
        alternatives: list[str],
        criteria: list[Criterion]
    ) -> dict[str, dict[str, float]]:
        """解析评分矩阵"""
        if "scores" not in data:
            raise MCDAValidationError(
                "YAML 配置缺少 'scores' 字段",
                field="scores"
            )

        scores_data = data["scores"]

        if not isinstance(scores_data, dict):
            raise MCDAValidationError(
                f"'scores' 必须是字典，实际类型: {type(scores_data).__name__}",
                field="scores"
            )

        # 验证所有备选方案都有评分
        scores = {}
        criterion_names = {c.name for c in criteria}

        for alt in alternatives:
            if alt not in scores_data:
                raise MCDAValidationError(
                    f"备选方案 '{alt}' 缺少评分数据",
                    field="scores",
                    alternative=alt
                )

            alt_scores = scores_data[alt]

            if not isinstance(alt_scores, dict):
                raise MCDAValidationError(
                    f"备选方案 '{alt}' 的评分必须是字典，"
                    f"实际类型: {type(alt_scores).__name__}",
                    field="scores",
                    alternative=alt
                )

            # 验证所有准则都有评分
            for crit_name in criterion_names:
                if crit_name not in alt_scores:
                    raise MCDAValidationError(
                        f"备选方案 '{alt}' 在准则 '{crit_name}' 缺少评分",
                        field="scores",
                        alternative=alt,
                        criterion=crit_name
                    )

                score = float(alt_scores[crit_name])

            # 转换评分
            scores[alt] = {crit: float(alt_scores[crit]) for crit in criterion_names}

        return scores

    def _parse_algorithm_config(self, data: dict[str, Any]) -> dict[str, Any]:
        """解析算法配置"""
        if "algorithm" not in data:
            raise MCDAValidationError(
                "YAML 配置缺少 'algorithm' 字段",
                field="algorithm"
            )

        algo_config = data["algorithm"]

        if not isinstance(algo_config, dict):
            # 如果是字符串，转换为字典
            if isinstance(algo_config, str):
                return {"name": algo_config}
            else:
                raise MCDAValidationError(
                    f"'algorithm' 必须是字典或字符串，"
                    f"实际类型: {type(algo_config).__name__}",
                    field="algorithm"
                )

        if "name" not in algo_config:
            raise MCDAValidationError(
                "算法配置缺少 'name' 字段",
                field="algorithm"
            )

        return algo_config

    # -------------------------------------------------------------------------
    # 验证决策问题
    # -------------------------------------------------------------------------

    def validate(self, problem: DecisionProblem) -> ValidationResult:
        """验证决策问题

        Args:
            problem: 决策问题

        Returns:
            验证结果
        """
        return self.validation_service.validate(problem)

    # -------------------------------------------------------------------------
    # 分析决策问题
    # -------------------------------------------------------------------------

    def analyze(
        self,
        problem: DecisionProblem,
        algorithm_name: str | None = None,
        run_sensitivity: bool = False,
        **algorithm_params
    ) -> DecisionResult:
        """分析决策问题

        Args:
            problem: 决策问题
            algorithm_name: 算法名称（默认使用问题配置的算法）
            run_sensitivity: 是否运行敏感性分析
            **algorithm_params: 算法参数

        Returns:
            决策结果
        """
        # 1. 确定使用的算法
        if algorithm_name is None:
            algorithm_name = problem.algorithm.get("name", "wsm")

        # 2. 获取算法实例
        algorithm = get_algorithm(algorithm_name)

        # 3. 执行分析
        result = algorithm.calculate(problem, **algorithm_params)

        # 4. 运行敏感性分析（可选）
        if run_sensitivity:
            sensitivity_result = self.sensitivity_service.analyze(
                problem=problem,
                algorithm=algorithm,
                perturbation=0.1
            )
            # 更新结果的敏感性分析数据
            # 这里取决于 DecisionResult 的具体实现

        return result

    # -------------------------------------------------------------------------
    # 报告生成
    # -------------------------------------------------------------------------

    def generate_report(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        format: str = "markdown",
        **kwargs
    ) -> str:
        """生成分析报告

        Args:
            problem: 决策问题
            result: 决策结果
            format: 报告格式（"markdown" 或 "json"）
            **kwargs: 额外参数

        Returns:
            报告内容
        """
        if format == "markdown":
            return self.reporter_service.generate_markdown(
                problem=problem,
                result=result,
                **kwargs
            )
        elif format == "json":
            return self.reporter_service.generate_json(
                problem=problem,
                result=result
            )
        else:
            raise ValueError(f"不支持的报告格式: {format}")

    def save_report(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        file_path: Path | str,
        format: str = "markdown",
        **kwargs
    ) -> None:
        """保存报告到文件

        Args:
            problem: 决策问题
            result: 决策结果
            file_path: 输出文件路径
            format: 报告格式（"markdown" 或 "json"）
            **kwargs: 额外参数
        """
        file_path = Path(file_path)

        # 生成报告
        report = self.generate_report(problem, result, format, **kwargs)

        # 保存文件
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report)

    # -------------------------------------------------------------------------
    # 完整工作流程
    # -------------------------------------------------------------------------

    def run_workflow(
        self,
        file_path: Path | str,
        output_path: Path | str | None = None,
        algorithm_name: str | None = None,
        run_sensitivity: bool = False,
        **kwargs
    ) -> DecisionResult:
        """运行完整的决策分析工作流程

        Args:
            file_path: YAML 配置文件路径
            output_path: 输出报告文件路径（可选）
            algorithm_name: 算法名称（可选）
            run_sensitivity: 是否运行敏感性分析
            **kwargs: 额外参数

        Returns:
            决策结果
        """
        # 1. 加载问题
        problem = self.load_from_yaml(file_path)

        # 2. 验证问题
        validation_result = self.validate(problem)

        if not validation_result.is_valid:
            errors = ", ".join(validation_result.errors)
            raise MCDAError(
                f"决策问题验证失败: {errors}",
                details={"errors": validation_result.errors}
            )

        # 3. 分析问题
        result = self.analyze(
            problem,
            algorithm_name=algorithm_name,
            run_sensitivity=run_sensitivity
        )

        # 4. 生成和保存报告（可选）
        if output_path is not None:
            self.save_report(problem, result, output_path, **kwargs)

        return result
