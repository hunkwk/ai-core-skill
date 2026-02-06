"""
MCDA Core 验证服务

功能:
- 权重归一化验证
- 评分范围验证（0-100）
- 最小方案数检查
- 最小准则数检查
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .models import Criterion, DecisionProblem

if TYPE_CHECKING:
    from collections.abc import Sequence

# ============================================================================
# 模块常量
# ============================================================================

WEIGHT_TOLERANCE = 1e-6
"""权重总和容差（浮点数比较）"""


# ============================================================================
# ValidationResult
# ============================================================================

@dataclass
class ValidationResult:
    """验证结果"""

    is_valid: bool
    """是否通过验证"""

    errors: list[str] = field(default_factory=list)
    """错误列表"""

    warnings: list[str] = field(default_factory=list)
    """警告列表"""

    total_weight: float | None = None
    """权重总和"""


# ============================================================================
# ValidationService
# ============================================================================

class ValidationService:
    """验证服务"""

    def validate(
        self,
        problem: DecisionProblem,
        *,
        normalize_weights: bool = True,
        min_alternatives: int = 2,
        min_criteria: int = 1,
    ) -> ValidationResult:
        """
        完整验证

        Args:
            problem: 决策问题
            normalize_weights: 是否自动归一化权重
            min_alternatives: 最小备选方案数
            min_criteria: 最小准则数

        Returns:
            ValidationResult: 验证结果
        """
        errors = []
        warnings = []

        # 1. 验证最小数量
        try:
            self.validate_minimum_alternatives(problem, min_alternatives)
        except Exception as e:
            errors.append(str(e))

        try:
            self.validate_minimum_criteria(problem.criteria, min_criteria)
        except Exception as e:
            errors.append(str(e))

        # 2. 验证权重
        try:
            weight_result = self.validate_weights(
                problem.criteria,
                normalize=normalize_weights,
            )
            if not weight_result.is_valid:
                errors.extend(weight_result.errors)
            if weight_result.warnings:
                warnings.extend(weight_result.warnings)
        except Exception as e:
            errors.append(str(e))

        # 3. 验证评分
        try:
            score_result = self.validate_scores(problem)
            if not score_result.is_valid:
                errors.extend(score_result.errors)
        except Exception as e:
            errors.append(str(e))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_weights(
        self,
        criteria: "Sequence[Criterion]",
        *,
        normalize: bool = True,
    ) -> ValidationResult:
        """
        验证权重归一化

        Args:
            criteria: 评价准则列表
            normalize: 是否自动归一化权重

        Returns:
            ValidationResult: 验证结果

        Raises:
            WeightValidationError: 权重未归一化且 normalize=False
        """
        from .exceptions import WeightValidationError

        total_weight = sum(c.weight for c in criteria)
        warnings = []

        # 权重总和应该接近 1.0（允许浮点误差）
        if abs(total_weight - 1.0) > WEIGHT_TOLERANCE:
            if normalize:
                # 自动归一化
                warnings = [f"权重总和为 {total_weight:.6f}，已自动归一化"]
            else:
                raise WeightValidationError(
                    f"权重总和为 {total_weight:.6f}，应该为 1.0",
                    details={"total_weight": total_weight},
                )

        return ValidationResult(
            is_valid=True,
            warnings=warnings,
            total_weight=total_weight,
        )

    def normalize_weights(
        self,
        criteria: "Sequence[Criterion]",
    ) -> tuple[Criterion, ...]:
        """
        归一化权重

        Args:
            criteria: 评价准则列表

        Returns:
            tuple[Criterion, ...]: 归一化后的准则
        """
        total_weight = sum(c.weight for c in criteria)

        if total_weight == 0:
            raise ValueError("权重总和不能为 0")

        normalized = []
        for criterion in criteria:
            # 创建新的准则对象（归一化权重）
            normalized_criterion = Criterion(
                name=criterion.name,
                weight=criterion.weight / total_weight,
                direction=criterion.direction,
            )
            normalized.append(normalized_criterion)

        return tuple(normalized)

    def validate_scores(
        self,
        problem: DecisionProblem,
    ) -> ValidationResult:
        """
        验证评分范围

        Args:
            problem: 决策问题

        Returns:
            ValidationResult: 验证结果

        Raises:
            ScoreValidationError: 评分超出范围
        """
        from .exceptions import ScoreValidationError
        from .models import MIN_SCORE, MAX_SCORE

        errors = []

        for alt in problem.alternatives:
            for crit in problem.criteria:
                score = problem.scores[alt][crit.name]

                # 检查评分范围（使用模型常量）
                if score < MIN_SCORE or score > MAX_SCORE:
                    raise ScoreValidationError(
                        f"方案 '{alt}' 在准则 '{crit.name}' 的评分为 {score}，"
                        f"超出范围 [{MIN_SCORE}, {MAX_SCORE}]",
                        details={
                            "alternative": alt,
                            "criterion": crit.name,
                            "score": score,
                        },
                    )

        return ValidationResult(is_valid=True, errors=errors)

    def validate_minimum_alternatives(
        self,
        problem: DecisionProblem,
        min_count: int = 2,
    ) -> None:
        """
        验证最小备选方案数

        Args:
            problem: 决策问题
            min_count: 最小备选方案数

        Raises:
            CriteriaValidationError: 备选方案数不足
        """
        from .exceptions import CriteriaValidationError

        if len(problem.alternatives) < min_count:
            raise CriteriaValidationError(
                f"备选方案数为 {len(problem.alternatives)}，至少需要 {min_count} 个备选方案",
                details={
                    "actual_count": len(problem.alternatives),
                    "min_count": min_count,
                },
            )

    def validate_minimum_criteria(
        self,
        criteria: "Sequence[Criterion]",
        min_count: int = 1,
    ) -> None:
        """
        验证最小准则数

        Args:
            criteria: 评价准则列表
            min_count: 最小准则数

        Raises:
            CriteriaValidationError: 准则数不足
        """
        from .exceptions import CriteriaValidationError

        if len(criteria) < min_count:
            raise CriteriaValidationError(
                f"准则数为 {len(criteria)}，至少需要 {min_count} 个准则",
                details={
                    "actual_count": len(criteria),
                    "min_count": min_count,
                },
            )


# 模块公开接口
__all__ = [
    "ValidationResult",
    "ValidationService",
    "WEIGHT_TOLERANCE",
]
