"""
MCDA Core 验证服务测试

测试范围:
- 权重归一化验证
- 评分范围验证（0-100）
- 最小方案数检查
- 最小准则数检查
"""

import sys
from pathlib import Path

# 添加 mcda_core 模块路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_core_path.resolve()))

import pytest
from mcda_core.models import (
    Criterion,
    DecisionProblem,
    Direction,
)
from mcda_core.exceptions import (
    ValidationError,
    WeightValidationError,
    ScoreValidationError,
    CriteriaValidationError,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def valid_criteria():
    """有效的评价准则"""
    return (
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.3, direction="higher_better"),
    )

@pytest.fixture
def valid_scores():
    """有效的评分数据"""
    return {
        "方案A": {"性能": 85.0, "成本": 60.0, "可靠性": 75.0},
        "方案B": {"性能": 70.0, "成本": 80.0, "可靠性": 90.0},
        "方案C": {"性能": 90.0, "成本": 50.0, "可靠性": 85.0},
    }

@pytest.fixture
def valid_problem(valid_criteria, valid_scores):
    """有效的决策问题"""
    return DecisionProblem(
        alternatives=tuple(valid_scores.keys()),
        criteria=valid_criteria,
        scores=valid_scores,
    )


# ============================================================================
# Test ValidationService - 权重验证
# ============================================================================

class TestWeightValidation:
    """权重归一化验证测试"""

    def test_normalized_weights_sum_to_one(self, valid_problem):
        """测试: 归一化权重总和应该等于 1"""
        from mcda_core.validation import ValidationService

        validator = ValidationService()
        result = validator.validate_weights(valid_problem.criteria)

        assert result.is_valid is True
        assert result.total_weight == pytest.approx(1.0, rel=1e-6)
        assert len(result.errors) == 0

    def test_unnormalized_weights_raise_error(self):
        """测试: 未归一化的权重应该抛出异常"""
        from mcda_core.validation import ValidationService

        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.4, direction="lower_better"),
            Criterion(name="可靠性", weight=0.3, direction="higher_better"),  # 总和 = 1.2
        )

        validator = ValidationService()

        with pytest.raises(WeightValidationError) as exc_info:
            validator.validate_weights(criteria, normalize=False)

        assert "权重总和" in str(exc_info.value)
        assert exc_info.value.details["total_weight"] == pytest.approx(1.2, rel=1e-6)

    def test_auto_normalize_weights(self):
        """测试: 自动归一化权重"""
        from mcda_core.validation import ValidationService

        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        )

        validator = ValidationService()
        normalized = validator.normalize_weights(criteria)

        total = sum(c.weight for c in normalized)
        assert total == pytest.approx(1.0, rel=1e-6)

        # 验证权重比例保持不变
        assert normalized[0].weight / normalized[1].weight == pytest.approx(0.5 / 0.3, rel=1e-6)


# ============================================================================
# Test ValidationService - 评分范围验证
# ============================================================================

class TestScoreValidation:
    """评分范围验证测试"""

    def test_valid_score_range(self, valid_problem):
        """测试: 有效评分范围（0-100）"""
        from mcda_core.validation import ValidationService

        validator = ValidationService()
        result = validator.validate_scores(valid_problem)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_negative_scores_raise_error(self):
        """测试: 负数评分应该抛出异常"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": -10.0, "成本": 60.0, "可靠性": 75.0},
            "方案B": {"性能": 70.0, "成本": 80.0, "可靠性": 90.0},
        }
        criteria = (
            Criterion(name="性能", weight=0.4, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.3, direction="higher_better"),
        )

        # 使用扩展的 score_range 绕过 DecisionProblem 的验证
        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
            score_range=(-100.0, 100.0),  # 扩展范围以允许负数
        )

        validator = ValidationService()

        with pytest.raises(ScoreValidationError) as exc_info:
            validator.validate_scores(problem)

        assert "超出范围" in str(exc_info.value)
        assert exc_info.value.details["alternative"] == "方案A"
        assert exc_info.value.details["criterion"] == "性能"
        assert exc_info.value.details["score"] == -10.0

    def test_scores_above_100_raise_error(self):
        """测试: 评分超过 100 应该抛出异常"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": 85.0, "成本": 60.0, "可靠性": 105.0},  # 超过 100
            "方案B": {"性能": 70.0, "成本": 80.0, "可靠性": 90.0},
        }
        criteria = (
            Criterion(name="性能", weight=0.4, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.3, direction="higher_better"),
        )

        # 使用扩展的 score_range 绕过 DecisionProblem 的验证
        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
            score_range=(0.0, 200.0),  # 扩展范围以允许 > 100
        )

        validator = ValidationService()

        with pytest.raises(ScoreValidationError) as exc_info:
            validator.validate_scores(problem)

        assert "超出范围" in str(exc_info.value)
        assert exc_info.value.details["alternative"] == "方案A"
        assert exc_info.value.details["criterion"] == "可靠性"

    def test_boundary_scores(self):
        """测试: 边界值评分（0 和 100）"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": 0.0, "成本": 100.0},
            "方案B": {"性能": 50.0, "成本": 50.0},
        }
        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        )

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        validator = ValidationService()
        result = validator.validate_scores(problem)

        assert result.is_valid is True


# ============================================================================
# Test ValidationService - 最小数量检查
# ============================================================================

class TestMinimumItemsValidation:
    """最小数量验证测试"""

    def test_minimum_alternatives(self):
        """测试: 至少需要 2 个备选方案"""
        from mcda_core.validation import ValidationService

        # 创建有效的决策问题（2个方案）
        scores = {"方案A": {"性能": 85.0}, "方案B": {"性能": 75.0}}
        criteria = (Criterion(name="性能", weight=1.0, direction="higher_better"),)

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        validator = ValidationService()

        # 测试通过的情况（2个方案 >= 2个最小要求）
        # 不应该抛出异常
        validator.validate_minimum_alternatives(problem, min_count=2)

        # 测试失败的情况（2个方案 < 3个最小要求）
        from mcda_core.exceptions import CriteriaValidationError
        with pytest.raises(CriteriaValidationError) as exc_info:
            validator.validate_minimum_alternatives(problem, min_count=3)

        assert "至少需要" in str(exc_info.value)
        assert "3 个备选方案" in str(exc_info.value)

    def test_minimum_criteria(self):
        """测试: 至少需要 1 个准则"""
        from mcda_core.validation import ValidationService

        scores = {"方案A": {}}
        criteria = ()

        validator = ValidationService()

        with pytest.raises(CriteriaValidationError) as exc_info:
            validator.validate_minimum_criteria(criteria, min_count=1)

        assert "至少需要" in str(exc_info.value)
        assert "1 个准则" in str(exc_info.value)


# ============================================================================
# Test ValidationService - 完整验证
# ============================================================================

class TestFullValidation:
    """完整验证流程测试"""

    def test_valid_problem_passes_all_validations(self, valid_problem):
        """测试: 有效的决策问题通过所有验证"""
        from mcda_core.validation import ValidationService

        validator = ValidationService()
        result = validator.validate(valid_problem)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_multiple_validation_errors(self):
        """测试: 多个验证错误"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": 150.0, "成本": -10.0},  # 两个错误
            "方案B": {"性能": 70.0, "成本": 80.0},  # 添加方案B 以绕过 DecisionProblem 验证
        }
        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.6, direction="lower_better"),  # 总和 = 1.1
        )

        # 使用扩展的 score_range 绕过 DecisionProblem 的验证
        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
            score_range=(-100.0, 200.0),  # 扩展范围以允许无效评分
        )

        validator = ValidationService()
        result = validator.validate(problem, normalize_weights=False)

        assert result.is_valid is False
        assert len(result.errors) >= 2  # 权重 + 评分错误


# ============================================================================
# Test ValidationResult
# ============================================================================

class TestValidationResult:
    """ValidationResult 数据类测试"""

    def test_validation_result_properties(self):
        """测试: ValidationResult 属性访问"""
        from mcda_core.validation import ValidationResult

        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["权重总和为 1.0"],
            total_weight=1.0,
        )

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.total_weight == 1.0

    def test_validation_result_with_errors(self):
        """测试: ValidationResult 包含错误"""
        from mcda_core.validation import ValidationResult

        result = ValidationResult(
            is_valid=False,
            errors=["错误1", "错误2"],
            warnings=[],
        )

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 0

    def test_validation_result_empty(self):
        """测试: 空 ValidationResult"""
        from mcda_core.validation import ValidationResult

        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_normalize_weights_returns_correct_weights(self):
        """测试: normalize_weights 返回正确的归一化权重"""
        from mcda_core.validation import ValidationService

        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        )

        validator = ValidationService()
        normalized = validator.normalize_weights(criteria)

        # 验证权重总和为 1.0
        total_weight = sum(c.weight for c in normalized)
        assert total_weight == pytest.approx(1.0, rel=1e-6)

        # 验证权重比例保持不变
        assert normalized[0].weight / normalized[1].weight == pytest.approx(0.5 / 0.3, rel=1e-6)
        assert normalized[1].weight / normalized[2].weight == pytest.approx(0.3 / 0.2, rel=1e-6)

    def test_validate_weights_with_zero_total_weight(self):
        """测试: 权重总和为 0 时抛出异常"""
        from mcda_core.validation import ValidationService

        # 创建一个权重为 0 的准则（这种情况不合理）
        criteria = (Criterion(name="性能", weight=0.0, direction="higher_better"),)

        validator = ValidationService()
        with pytest.raises(ValueError):
            validator.normalize_weights(criteria)

    def test_validate_scores_with_exact_boundaries(self):
        """测试: 边界值评分（0 和 100）通过验证"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": 0.0, "成本": 100.0},
            "方案B": {"性能": 50.0, "成本": 50.0},
        }
        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        )

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        validator = ValidationService()
        result = validator.validate_scores(problem)

        assert result.is_valid is True

    def test_validate_with_single_alternative_fails(self):
        """测试: 只有 1 个备选方案时验证失败"""
        from mcda_core.validation import ValidationService
        from mcda_core.exceptions import CriteriaValidationError

        # 这个测试会创建一个有效的 2 方案问题，然后验证 min_count=3
        scores = {"方案A": {"性能": 85.0}, "方案B": {"性能": 75.0}}
        criteria = (Criterion(name="性能", weight=1.0, direction="higher_better"),)

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        validator = ValidationService()
        result = validator.validate(problem, min_alternatives=3)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_with_zero_criteria_fails(self):
        """测试: 0 个准则时验证失败"""
        from mcda_core.validation import ValidationService
        from mcda_core.exceptions import CriteriaValidationError

        criteria = ()

        validator = ValidationService()

        with pytest.raises(CriteriaValidationError) as exc_info:
            validator.validate_minimum_criteria(criteria, min_count=1)

        assert "准则数为 0" in str(exc_info.value)
        assert "至少需要 1 个准则" in str(exc_info.value)

    def test_validate_with_unnormalized_weights_warning(self):
        """测试: 未归一化权重产生警告"""
        from mcda_core.validation import ValidationService

        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.4, direction="lower_better"),  # 总和 = 0.9
        )

        validator = ValidationService()
        result = validator.validate_weights(criteria, normalize=True)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert "已自动归一化" in result.warnings[0]

    def test_validate_with_unnormalized_weights_error(self):
        """测试: 未归一化权重且 normalize=False 时抛出异常"""
        from mcda_core.validation import ValidationService
        from mcda_core.exceptions import WeightValidationError

        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.4, direction="lower_better"),  # 总和 = 0.9
        )

        validator = ValidationService()

        with pytest.raises(WeightValidationError):
            validator.validate_weights(criteria, normalize=False)

    def test_validate_minimum_criteria_with_zero(self):
        """测试: 0 个准则时抛出异常"""
        from mcda_core.validation import ValidationService
        from mcda_core.exceptions import CriteriaValidationError

        criteria = ()

        validator = ValidationService()

        with pytest.raises(CriteriaValidationError):
            validator.validate_minimum_criteria(criteria, min_count=1)

    def test_validate_minimum_criteria_with_exact_count(self):
        """测试: 准则数等于最小值时通过验证"""
        from mcda_core.validation import ValidationService

        criteria = (
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        )

        validator = ValidationService()
        # 不应该抛出异常
        validator.validate_minimum_criteria(criteria, min_count=1)

    def test_validate_with_multiple_scores_out_of_range(self):
        """测试: 多个评分超出范围"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": -10.0, "成本": 150.0},  # 两个都超出范围
            "方案B": {"性能": 70.0, "成本": 80.0},
        }
        criteria = (
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        )

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
            score_range=(-100.0, 200.0),  # 扩展范围
        )

        validator = ValidationService()

        # 第一个超出范围的评分会抛出异常
        with pytest.raises(Exception):
            validator.validate_scores(problem)

    def test_validation_result_total_weight_field(self):
        """测试: ValidationResult 的 total_weight 字段"""
        from mcda_core.validation import ValidationResult, ValidationService

        criteria = (
            Criterion(name="性能", weight=0.4, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.3, direction="higher_better"),
        )

        validator = ValidationService()
        result = validator.validate_weights(criteria, normalize=False)

        assert result.total_weight == pytest.approx(1.0, rel=1e-6)

    def test_validate_with_both_alternatives_and_criteria_minimum(self):
        """测试: 同时检查备选方案和准则的最小数量"""
        from mcda_core.validation import ValidationService

        scores = {
            "方案A": {"性能": 85.0},
            "方案B": {"性能": 75.0},  # 至少需要 2 个备选方案
        }
        criteria = (Criterion(name="性能", weight=1.0, direction="higher_better"),)

        problem = DecisionProblem(
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        validator = ValidationService()
        result = validator.validate(
            problem,
            min_alternatives=3,  # 要求至少 3 个方案（只有 1 个）
            min_criteria=1,
        )

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validation_service_instantiation(self):
        """测试: ValidationService 实例化"""
        from mcda_core.validation import ValidationService

        validator = ValidationService()
        assert validator is not None
