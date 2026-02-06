"""
MCDA Core 敏感性分析服务测试

测试范围:
- 权重扰动测试
- 排名变化检测
- 关键准则识别
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
    DecisionResult,
    RankingItem,
    ResultMetadata,
    SensitivityResult,
    PerturbationResult,
    Direction,
)
from mcda_core.exceptions import SensitivityAnalysisError


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_criteria():
    """示例准则"""
    return (
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.3, direction="higher_better"),
    )

@pytest.fixture
def sample_scores():
    """示例评分"""
    return {
        "方案A": {"性能": 85.0, "成本": 60.0, "可靠性": 75.0},
        "方案B": {"性能": 70.0, "成本": 80.0, "可靠性": 90.0},
        "方案C": {"性能": 90.0, "成本": 50.0, "可靠性": 85.0},
    }

@pytest.fixture
def sample_problem(sample_criteria, sample_scores):
    """示例决策问题"""
    return DecisionProblem(
        alternatives=tuple(sample_scores.keys()),
        criteria=sample_criteria,
        scores=sample_scores,
    )

@pytest.fixture
def sample_result():
    """示例决策结果"""
    rankings = (
        RankingItem(alternative="方案C", rank=1, score=0.85),
        RankingItem(alternative="方案A", rank=2, score=0.75),
        RankingItem(alternative="方案B", rank=3, score=0.65),
    )

    metadata = ResultMetadata(
        algorithm_name="WSM",
        problem_size=(3, 3),
        metrics={"weighted_sums": {"方案C": 85.0, "方案A": 75.0, "方案B": 65.0}},
    )

    return DecisionResult(
        rankings=rankings,
        raw_scores={"方案C": 85.0, "方案A": 75.0, "方案B": 65.0},
        metadata=metadata,
    )


# ============================================================================
# Test SensitivityService - 权重扰动测试
# ============================================================================

class TestWeightPerturbation:
    """权重扰动测试"""

    def test_perturb_single_criterion(self, sample_problem, sample_result):
        """测试: 扰动单个准则的权重"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        # 扰动"性能"准则的权重 ±10%
        result = sensitivity.perturb_weights(
            problem=sample_problem,
            algorithm=algorithm,
            criterion_name="性能",
            perturbation=0.1,
        )

        assert result is not None
        assert result.criterion_name == "性能"
        assert result.original_weight == pytest.approx(0.4, rel=1e-6)
        assert len(result.perturbations) == 2  # +10% 和 -10%

    def test_perturb_weights_with_custom_perturbation(self, sample_problem, sample_result):
        """测试: 自定义扰动幅度"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        result = sensitivity.perturb_weights(
            problem=sample_problem,
            algorithm=algorithm,
            criterion_name="成本",
            perturbation=0.2,  # ±20%
        )

        assert result.perturbations[0].perturbed_weight == pytest.approx(0.36, rel=1e-6)  # 0.3 * 1.2
        assert result.perturbations[1].perturbed_weight == pytest.approx(0.24, rel=1e-6)  # 0.3 * 0.8

    def test_perturb_weights_invalid_criterion(self, sample_problem, sample_result):
        """测试: 扰动不存在的准则"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        with pytest.raises(SensitivityAnalysisError) as exc_info:
            sensitivity.perturb_weights(
                problem=sample_problem,
                algorithm=algorithm,
                criterion_name="不存在的准则",
                perturbation=0.1,
            )

        assert "准则" in str(exc_info.value)
        assert "不存在" in str(exc_info.value)

    def test_perturb_weights_extreme_values(self, sample_problem, sample_result):
        """测试: 极端扰动幅度"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        # 50% 扰动
        result = sensitivity.perturb_weights(
            problem=sample_problem,
            algorithm=algorithm,
            criterion_name="可靠性",
            perturbation=0.5,
        )

        assert result.perturbations[0].perturbed_weight == pytest.approx(0.45, rel=1e-6)  # 0.3 * 1.5
        assert result.perturbations[1].perturbed_weight == pytest.approx(0.15, rel=1e-6)  # 0.3 * 0.5


# ============================================================================
# Test SensitivityService - 排名变化检测
# ============================================================================

class TestRankingChangeDetection:
    """排名变化检测测试"""

    def test_detect_ranking_changes(self, sample_problem, sample_result):
        """测试: 检测排名变化"""
        from mcda_core.sensitivity import SensitivityService

        sensitivity = SensitivityService()

        # 创建不同的排名
        new_rankings = (
            RankingItem(alternative="方案A", rank=1, score=0.80),
            RankingItem(alternative="方案C", rank=2, score=0.75),
            RankingItem(alternative="方案B", rank=3, score=0.65),
        )

        new_result = DecisionResult(
            rankings=new_rankings,
            raw_scores={"方案A": 80.0, "方案C": 75.0, "方案B": 65.0},
            metadata=sample_result.metadata,
        )

        changes = sensitivity.detect_ranking_changes(sample_result, new_result)

        assert changes is not None
        assert len(changes) > 0
        # 方案C 从第1名降到第2名
        # 方案A 从第2名升到第1名

    def test_no_ranking_changes(self, sample_problem, sample_result):
        """测试: 无排名变化"""
        from mcda_core.sensitivity import SensitivityService

        sensitivity = SensitivityService()
        changes = sensitivity.detect_ranking_changes(sample_result, sample_result)

        assert len(changes) == 0

    def test_ranking_change_details(self, sample_problem, sample_result):
        """测试: 排名变化详情"""
        from mcda_core.sensitivity import SensitivityService

        sensitivity = SensitivityService()

        # 创建排名交换的情况
        new_rankings = (
            RankingItem(alternative="方案A", rank=1, score=0.85),
            RankingItem(alternative="方案C", rank=2, score=0.80),
            RankingItem(alternative="方案B", rank=3, score=0.65),
        )

        new_result = DecisionResult(
            rankings=new_rankings,
            raw_scores={"方案A": 85.0, "方案C": 80.0, "方案B": 65.0},
            metadata=sample_result.metadata,
        )

        changes = sensitivity.detect_ranking_changes(sample_result, new_result)

        # 验证变化记录包含必要信息
        for change in changes:
            assert "alternative" in change
            assert "old_rank" in change
            assert "new_rank" in change
            assert "rank_change" in change


# ============================================================================
# Test SensitivityService - 关键准则识别
# ============================================================================

class TestCriticalCriteriaIdentification:
    """关键准则识别测试"""

    def test_identify_critical_criteria(self, sample_problem, sample_result):
        """测试: 识别关键准则"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        # 使用更大的扰动幅度以确保能检测到排名变化
        critical = sensitivity.identify_critical_criteria(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.5,  # 50% 扰动
        )

        assert critical is not None
        assert len(critical) <= len(sample_problem.criteria)
        # 如果有关键准则，验证其属性
        for item in critical:
            assert hasattr(item, "criterion_name")
            assert hasattr(item, "weight")
            assert hasattr(item, "rank_changes")

    def test_critical_criteria_threshold(self, sample_problem, sample_result):
        """测试: 关键准则阈值"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        # 只识别导致排名变化的准则
        critical = sensitivity.identify_critical_criteria(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.1,
            threshold=1,  # 至少1个排名变化
        )

        # 验证返回的准则都满足阈值条件
        for item in critical:
            assert item.rank_changes >= 1

    def test_critical_criteria_sorted_by_impact(self, sample_problem, sample_result):
        """测试: 关键准则按影响程度排序"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        critical = sensitivity.identify_critical_criteria(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.1,
        )

        # 验证按影响程度降序排列
        if len(critical) > 1:
            for i in range(len(critical) - 1):
                assert critical[i].rank_changes >= critical[i + 1].rank_changes


# ============================================================================
# Test SensitivityService - 完整敏感性分析
# ============================================================================

class TestFullSensitivityAnalysis:
    """完整敏感性分析测试"""

    def test_comprehensive_sensitivity_analysis(self, sample_problem, sample_result):
        """测试: 综合敏感性分析"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        result = sensitivity.analyze(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.1,
        )

        assert result is not None
        assert hasattr(result, "critical_criteria")
        assert hasattr(result, "perturbation_results")

    def test_sensitivity_analysis_with_different_algorithms(self, sample_problem):
        """测试: 使用不同算法进行敏感性分析"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()

        for algo_name in ["wsm", "wpm"]:
            algorithm = get_algorithm(algo_name)
            result = algorithm.calculate(sample_problem)

            sensitivity_result = sensitivity.analyze(
                problem=sample_problem,
                algorithm=algorithm,
                perturbation=0.1,
            )

            assert sensitivity_result is not None


# ============================================================================
# Test SensitivityResult
# ============================================================================

class TestSensitivityResult:
    """SensitivityResult 数据类测试"""

    def test_sensitivity_result_properties(self):
        """测试: SensitivityResult 属性"""
        from mcda_core.models import PerturbationResult

        perturbations = [
            PerturbationResult(
                criterion_name="性能",
                original_weight=0.4,
                perturbed_weight=0.44,
                delta=0.1,
                rank_changes={"方案A": (1, 2), "方案C": (2, 1)},
            )
        ]

        result = SensitivityResult(
            perturbations=perturbations,
            critical_criteria=[],
            robustness_score=0.8,
        )

        # 使用便捷属性
        assert result.criterion_name == "性能"
        assert result.original_weight == 0.4
        assert len(result.perturbations) == 1


# ============================================================================
# Test SensitivityService Error Handling
# ============================================================================

class TestSensitivityServiceErrors:
    """敏感性分析错误处理测试"""

    def test_invalid_perturbation_value(self, sample_problem):
        """测试: 无效的扰动值"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        with pytest.raises(SensitivityAnalysisError):
            sensitivity.perturb_weights(
                problem=sample_problem,
                algorithm=algorithm,
                criterion_name="性能",
                perturbation=-0.1,  # 负值
            )

        with pytest.raises(SensitivityAnalysisError):
            sensitivity.perturb_weights(
                problem=sample_problem,
                algorithm=algorithm,
                criterion_name="性能",
                perturbation=1.5,  # 超过100%
            )

    def test_empty_rankings_comparison(self):
        """测试: 空排名比较会在创建 DecisionResult 时抛出异常"""
        from mcda_core.sensitivity import SensitivityService

        sensitivity = SensitivityService()

        # DecisionResult 在创建时会验证 rankings 不能为空
        with pytest.raises(ValueError) as exc_info:
            empty_result1 = DecisionResult(
                rankings=(),
                raw_scores={},
                metadata=ResultMetadata(algorithm_name="WSM", problem_size=(0, 0)),
            )

        assert "rankings 不能为空" in str(exc_info.value)


# ============================================================================
# Test SensitivityService Properties
# ============================================================================

class TestSensitivityServiceProperties:
    """SensitivityService 属性测试"""

    def test_service_instantiation(self):
        """测试: SensitivityService 实例化"""
        from mcda_core.sensitivity import SensitivityService

        sensitivity = SensitivityService()
        assert sensitivity is not None

    def test_perturb_weights_with_large_perturbation(self, sample_problem, sample_result):
        """测试: 大幅度权重扰动（50%）"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        result = sensitivity.perturb_weights(
            problem=sample_problem,
            algorithm=algorithm,
            criterion_name="性能",
            perturbation=0.5,  # 50% 扰动
        )

        assert result is not None
        assert len(result.perturbations) == 2
        # 验证权重被正确扰动
        assert result.perturbations[0].delta == 0.5
        assert result.perturbations[1].delta == -0.5

    def test_perturb_weights_with_small_perturbation(self, sample_problem, sample_result):
        """测试: 小幅度权重扰动（1%）"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        result = sensitivity.perturb_weights(
            problem=sample_problem,
            algorithm=algorithm,
            criterion_name="性能",
            perturbation=0.01,  # 1% 扰动
        )

        assert result is not None
        assert len(result.perturbations) == 2

    def test_detect_ranking_changes_with_no_changes(self, sample_result):
        """测试: 无排名变化时返回空列表"""
        from mcda_core.sensitivity import SensitivityService

        sensitivity = SensitivityService()
        changes = sensitivity.detect_ranking_changes(sample_result, sample_result)

        assert changes == []
        assert len(changes) == 0

    def test_detect_ranking_changes_with_complete_reversal(self, sample_problem, sample_result):
        """测试: 完全排名逆转"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.models import RankingItem

        sensitivity = SensitivityService()

        # 创建完全相反的排名（需要重新分配 rank 值）
        # 原始: 方案C=1, 方案A=2, 方案B=3
        # 逆转: 方案B=1, 方案C=2, 方案A=3（所有方案的 rank 都改变了）
        reversed_rankings = (
            RankingItem(alternative="方案B", rank=1, score=sample_result.raw_scores["方案B"]),
            RankingItem(alternative="方案C", rank=2, score=sample_result.raw_scores["方案C"]),
            RankingItem(alternative="方案A", rank=3, score=sample_result.raw_scores["方案A"]),
        )
        new_result = DecisionResult(
            rankings=list(reversed_rankings),
            raw_scores=sample_result.raw_scores,
            metadata=sample_result.metadata,
        )

        changes = sensitivity.detect_ranking_changes(sample_result, new_result)

        # 所有方案都改变了排名：C(1→3), A(2→3), B(3→1)
        assert len(changes) == 3

    def test_identify_critical_criteria_with_high_threshold(self, sample_problem, sample_result):
        """测试: 高阈值导致无关键准则"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        # 使用高阈值（需要至少 10 个排名变化）
        critical = sensitivity.identify_critical_criteria(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.1,
            threshold=10,  # 高阈值
        )

        # 可能没有准则满足如此高的阈值
        assert isinstance(critical, list)
        assert len(critical) <= len(sample_problem.criteria)

    def test_critical_criteria_sorted_descending(self, sample_problem, sample_result):
        """测试: 关键准则按影响程度降序排列"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        critical = sensitivity.identify_critical_criteria(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.5,  # 使用较大扰动
        )

        # 验证降序排列
        for i in range(len(critical) - 1):
            if i + 1 < len(critical):
                assert critical[i].rank_changes >= critical[i + 1].rank_changes

    def test_analyze_returns_all_data(self, sample_problem):
        """测试: 综合分析返回所有必要数据"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        result = sensitivity.analyze(
            problem=sample_problem,
            algorithm=algorithm,
            perturbation=0.1,
        )

        assert result is not None
        assert hasattr(result, "critical_criteria")
        assert hasattr(result, "perturbation_results")
        assert len(result.perturbation_results) == len(sample_problem.criteria)

    def test_perturb_nonexistent_criterion(self, sample_problem):
        """测试: 扰动不存在的准则抛出异常"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm
        from mcda_core.exceptions import SensitivityAnalysisError

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        with pytest.raises(SensitivityAnalysisError) as exc_info:
            sensitivity.perturb_weights(
                problem=sample_problem,
                algorithm=algorithm,
                criterion_name="不存在的准则",
                perturbation=0.1,
            )

        assert "不存在" in str(exc_info.value)

    def test_perturb_with_negative_delta(self, sample_problem):
        """测试: 负扰动值抛出异常"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm
        from mcda_core.exceptions import SensitivityAnalysisError

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        with pytest.raises(SensitivityAnalysisError):
            sensitivity.perturb_weights(
                problem=sample_problem,
                algorithm=algorithm,
                criterion_name="性能",
                perturbation=-0.1,  # 负值
            )

    def test_perturb_with_too_large_delta(self, sample_problem):
        """测试: 过大的扰动值抛出异常"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm
        from mcda_core.exceptions import SensitivityAnalysisError

        sensitivity = SensitivityService()
        algorithm = get_algorithm("wsm")

        with pytest.raises(SensitivityAnalysisError):
            sensitivity.perturb_weights(
                problem=sample_problem,
                algorithm=algorithm,
                criterion_name="性能",
                perturbation=1.5,  # 150% 扰动
            )

    def test_sensitivity_result_convenience_properties(self):
        """测试: SensitivityResult 便捷属性"""
        from mcda_core.models import PerturbationResult, SensitivityResult

        perturbations = [
            PerturbationResult(
                criterion_name="性能",
                original_weight=0.4,
                perturbed_weight=0.44,
                delta=0.1,
                rank_changes={"方案A": (1, 2)},
            ),
            PerturbationResult(
                criterion_name="性能",
                original_weight=0.4,
                perturbed_weight=0.36,
                delta=-0.1,
                rank_changes={"方案B": (2, 3)},
            ),
        ]

        result = SensitivityResult(
            perturbations=perturbations,
            critical_criteria=["性能"],
            robustness_score=0.9,
        )

        # 测试便捷属性
        assert result.criterion_name == "性能"
        assert result.original_weight == 0.4
        assert len(result.perturbations) == 2

    def test_comprehensive_sensitivity_with_different_algorithms(self, sample_problem):
        """测试: 使用不同算法进行敏感性分析"""
        from mcda_core.sensitivity import SensitivityService
        from mcda_core.algorithms import get_algorithm

        sensitivity = SensitivityService()

        for algo_name in ["wsm", "wpm", "topsis"]:
            algorithm = get_algorithm(algo_name)
            result = sensitivity.analyze(
                problem=sample_problem,
                algorithm=algorithm,
                perturbation=0.2,
            )

            assert result is not None
            assert len(result.perturbation_results) > 0
