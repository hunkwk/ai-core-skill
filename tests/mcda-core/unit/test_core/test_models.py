"""
MCDA Core - 数据模型单元测试

测试所有数据模型的创建、验证和不可变性。
"""

import pytest
from datetime import datetime

# 导入数据模型
from mcda_core.models import (
    # 类型别名
    Direction,
    ScoreMatrix,
    ScoreRange,
    # 评分规则
    LinearScoringRule,
    ThresholdRange,
    ThresholdScoringRule,
    ScoringRule,
    # 数据源
    DataSource,
    # 核心模型
    Criterion,
    AlgorithmConfig,
    DecisionProblem,
    RankingItem,
    ResultMetadata,
    PerturbationResult,
    SensitivityResult,
    DecisionResult,
)


# =============================================================================
# Criterion 测试
# =============================================================================

class TestCriterion:
    """测试 Criterion 数据模型"""

    def test_create_valid_criterion(self):
        """测试创建有效的准则"""
        criterion = Criterion(
            name="成本",
            weight=0.35,
            direction="lower_better",
            description="月度成本（万元）"
        )

        assert criterion.name == "成本"
        assert criterion.weight == 0.35
        assert criterion.direction == "lower_better"
        assert criterion.description == "月度成本（万元）"

    def test_criterion_with_scoring_rule(self):
        """测试带评分规则的准则"""
        rule = LinearScoringRule(min=0, max=100, scale=100)
        criterion = Criterion(
            name="响应时间",
            weight=0.25,
            direction="lower_better",
            scoring_rule=rule,
            column="响应时间ms"
        )

        assert criterion.scoring_rule == rule
        assert criterion.column == "响应时间ms"

    def test_criterion_empty_name_raises_error(self):
        """测试空名称抛出异常"""
        with pytest.raises(ValueError, match="name 不能为空"):
            Criterion(name="", weight=0.5, direction="higher_better")

    def test_criterion_invalid_weight_raises_error(self):
        """测试无效权重抛出异常"""
        with pytest.raises(ValueError, match="weight.*必须在 0-1 范围内"):
            Criterion(name="成本", weight=1.5, direction="higher_better")

        with pytest.raises(ValueError, match="weight.*必须在 0-1 范围内"):
            Criterion(name="成本", weight=-0.1, direction="higher_better")

    def test_criterion_invalid_direction_raises_error(self):
        """测试无效方向抛出异常"""
        with pytest.raises(ValueError, match="direction.*必须是 'higher_better' 或 'lower_better'"):
            Criterion(name="成本", weight=0.5, direction="invalid")

    def test_criterion_immutability(self):
        """测试准则不可变性"""
        criterion = Criterion(name="成本", weight=0.35, direction="lower_better")

        with pytest.raises(Exception):  # FrozenInstanceError
            criterion.name = "新名称"


# =============================================================================
# AlgorithmConfig 测试
# =============================================================================

class TestAlgorithmConfig:
    """测试 AlgorithmConfig 数据模型"""

    def test_create_valid_config(self):
        """测试创建有效的算法配置"""
        config = AlgorithmConfig(name="wsm")
        assert config.name == "wsm"
        assert config.params == {}

    def test_create_config_with_params(self):
        """测试带参数的算法配置"""
        config = AlgorithmConfig(
            name="vikor",
            params={"v": 0.5, "strategy": "compromise"}
        )
        assert config.name == "vikor"
        assert config.params == {"v": 0.5, "strategy": "compromise"}

    def test_config_empty_name_raises_error(self):
        """测试空名称抛出异常"""
        with pytest.raises(ValueError, match="name 不能为空"):
            AlgorithmConfig(name="")

    def test_config_immutability(self):
        """测试配置不可变性"""
        config = AlgorithmConfig(name="wsm")

        with pytest.raises(Exception):  # FrozenInstanceError
            config.name = "wpm"


# =============================================================================
# LinearScoringRule 测试
# =============================================================================

class TestLinearScoringRule:
    """测试 LinearScoringRule 数据模型"""

    def test_create_valid_rule(self):
        """测试创建有效的线性评分规则"""
        rule = LinearScoringRule(min=0, max=100, scale=100)
        assert rule.type == "linear"
        assert rule.min == 0
        assert rule.max == 100
        assert rule.scale == 100

    def test_rule_default_scale(self):
        """测试默认 scale 为 100"""
        rule = LinearScoringRule(min=0, max=100)
        assert rule.scale == 100.0

    def test_rule_min_equals_max_raises_error(self):
        """测试 min == max 抛出异常"""
        with pytest.raises(ValueError, match="min.*必须小于 max"):
            LinearScoringRule(min=100, max=100)

    def test_rule_min_greater_than_max_raises_error(self):
        """测试 min > max 抛出异常"""
        with pytest.raises(ValueError, match="min.*必须小于 max"):
            LinearScoringRule(min=100, max=50)

    def test_rule_invalid_scale_raises_error(self):
        """测试无效 scale 抛出异常"""
        with pytest.raises(ValueError, match="scale.*必须大于 0"):
            LinearScoringRule(min=0, max=100, scale=0)

        with pytest.raises(ValueError, match="scale.*必须大于 0"):
            LinearScoringRule(min=0, max=100, scale=-10)


# =============================================================================
# ThresholdRange 测试
# =============================================================================

class TestThresholdRange:
    """测试 ThresholdRange 数据模型"""

    def test_create_valid_range_with_max_only(self):
        """测试创建只有 max 的有效范围"""
        range_ = ThresholdRange(max=100, score=100)
        assert range_.min is None
        assert range_.max == 100
        assert range_.score == 100

    def test_create_valid_range_with_min_and_max(self):
        """测试创建有 min 和 max 的有效范围"""
        range_ = ThresholdRange(min=100, max=500, score=80)
        assert range_.min == 100
        assert range_.max == 500
        assert range_.score == 80

    def test_create_valid_range_with_min_only(self):
        """测试创建只有 min 的有效范围"""
        range_ = ThresholdRange(min=1000, score=40)
        assert range_.min == 1000
        assert range_.max is None
        assert range_.score == 40

    def test_range_default_score(self):
        """测试默认 score 为 100"""
        range_ = ThresholdRange(max=100)
        assert range_.score == 100.0

    def test_range_min_greater_than_max_raises_error(self):
        """测试 min >= max 抛出异常"""
        with pytest.raises(ValueError, match="min.*必须小于 max"):
            ThresholdRange(min=500, max=100, score=80)

    def test_range_invalid_score_raises_error(self):
        """测试无效 score 抛出异常"""
        with pytest.raises(ValueError, match="score.*必须在 0-100 范围内"):
            ThresholdRange(max=100, score=-10)

        with pytest.raises(ValueError, match="score.*必须在 0-100 范围内"):
            ThresholdRange(max=100, score=150)


# =============================================================================
# ThresholdScoringRule 测试
# =============================================================================

class TestThresholdScoringRule:
    """测试 ThresholdScoringRule 数据模型"""

    def test_create_valid_rule(self):
        """测试创建有效的阈值评分规则"""
        ranges = (
            ThresholdRange(max=100, score=100),
            ThresholdRange(min=100, max=500, score=80),
            ThresholdRange(min=500, max=1000, score=60),
            ThresholdRange(min=1000, score=40),
        )
        rule = ThresholdScoringRule(ranges=ranges, default_score=0)
        assert rule.type == "threshold"
        assert len(rule.ranges) == 4
        assert rule.default_score == 0

    def test_rule_default_default_score(self):
        """测试默认 default_score 为 0"""
        ranges = (ThresholdRange(max=100, score=100),)
        rule = ThresholdScoringRule(ranges=ranges)
        assert rule.default_score == 0.0

    def test_rule_empty_ranges_raises_error(self):
        """测试空 ranges 抛出异常"""
        with pytest.raises(ValueError, match="ranges 不能为空"):
            ThresholdScoringRule(ranges=())

    def test_rule_invalid_default_score_raises_error(self):
        """测试无效 default_score 抛出异常"""
        ranges = (ThresholdRange(max=100, score=100),)
        with pytest.raises(ValueError, match="default_score.*必须在 0-100 范围内"):
            ThresholdScoringRule(ranges=ranges, default_score=-10)

        with pytest.raises(ValueError, match="default_score.*必须在 0-100 范围内"):
            ThresholdScoringRule(ranges=ranges, default_score=150)


# =============================================================================
# DataSource 测试
# =============================================================================

class TestDataSource:
    """测试 DataSource 数据模型"""

    def test_create_yaml_source(self):
        """测试创建 YAML 数据源"""
        source = DataSource(type="yaml", file="config.yaml")
        assert source.type == "yaml"
        assert source.file == "config.yaml"
        assert source.sheet is None
        assert source.encoding == "utf-8"

    def test_create_csv_source(self):
        """测试创建 CSV 数据源"""
        source = DataSource(type="csv", file="data.csv", encoding="gbk")
        assert source.type == "csv"
        assert source.file == "data.csv"
        assert source.encoding == "gbk"

    def test_create_excel_source(self):
        """测试创建 Excel 数据源"""
        source = DataSource(
            type="excel",
            file="data.xlsx",
            sheet="决策数据",
            encoding="utf-8"
        )
        assert source.type == "excel"
        assert source.file == "data.xlsx"
        assert source.sheet == "决策数据"

    def test_excel_source_without_sheet_raises_error(self):
        """测试 Excel 数据源缺少 sheet 抛出异常"""
        with pytest.raises(ValueError, match="Excel 数据源必须指定 sheet 名称"):
            DataSource(type="excel", file="data.xlsx")

    def test_source_invalid_type_raises_error(self):
        """测试无效类型抛出异常"""
        with pytest.raises(ValueError, match="type.*必须是"):
            DataSource(type="json", file="data.json")

    def test_source_default_encoding(self):
        """测试默认编码为 utf-8"""
        source = DataSource(type="yaml", file="config.yaml")
        assert source.encoding == "utf-8"


# =============================================================================
# DecisionProblem 测试
# =============================================================================

class TestDecisionProblem:
    """测试 DecisionProblem 数据模型"""

    @pytest.fixture
    def sample_criteria(self):
        """创建示例准则"""
        return (
            Criterion(name="成本", weight=0.35, direction="lower_better"),
            Criterion(name="功能完整性", weight=0.30, direction="higher_better"),
            Criterion(name="稳定性", weight=0.25, direction="higher_better"),
            Criterion(name="技术支持", weight=0.10, direction="higher_better"),
        )

    @pytest.fixture
    def sample_scores(self):
        """创建示例评分"""
        return {
            "AWS": {"成本": 3.0, "功能完整性": 5.0, "稳定性": 5.0, "技术支持": 4.0},
            "Azure": {"成本": 4.0, "功能完整性": 4.0, "稳定性": 4.0, "技术支持": 5.0},
            "GCP": {"成本": 5.0, "功能完整性": 4.0, "稳定性": 4.0, "技术支持": 3.0},
        }

    def test_create_valid_problem(self, sample_criteria, sample_scores):
        """测试创建有效的决策问题"""
        problem = DecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=sample_criteria,
            scores=sample_scores,
            algorithm=AlgorithmConfig(name="wsm")
        )

        assert len(problem.alternatives) == 3
        assert len(problem.criteria) == 4
        assert problem.scores == sample_scores
        assert problem.algorithm.name == "wsm"

    def test_problem_default_score_range(self, sample_criteria, sample_scores):
        """测试默认评分范围为 (0.0, 100.0)"""
        problem = DecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            scores={
                "AWS": {"成本": 50.0, "功能完整性": 80.0},
                "Azure": {"成本": 60.0, "功能完整性": 70.0},
            },
        )
        assert problem.score_range == (0.0, 100.0)

    def test_problem_less_than_2_alternatives_raises_error(self, sample_criteria):
        """测试少于 2 个备选方案抛出异常"""
        with pytest.raises(ValueError, match="至少需要 2 个备选方案"):
            DecisionProblem(
                alternatives=("AWS",),
                criteria=sample_criteria
            )

    def test_problem_less_than_2_criteria_raises_error(self):
        """测试少于 1 个准则抛出异常"""
        with pytest.raises(ValueError, match="至少需要 1 个评价准则"):
            DecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=()  # 空准则列表
            )

    def test_problem_invalid_score_range_raises_error(self, sample_criteria):
        """测试无效评分范围抛出异常"""
        with pytest.raises(ValueError, match="score_range 无效"):
            DecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria[:2],
                score_range=(100.0, 0.0)
            )

    def test_problem_missing_alternative_scores_raises_error(self, sample_criteria):
        """测试缺少方案评分抛出异常"""
        scores = {
            "AWS": {"成本": 3.0, "功能完整性": 5.0},
            # 缺少 Azure
        }
        with pytest.raises(ValueError, match="缺少方案 'Azure' 的评分"):
            DecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria[:2],
                scores=scores
            )

    def test_problem_missing_criterion_scores_raises_error(self, sample_criteria):
        """测试缺少准则评分抛出异常"""
        scores = {
            "AWS": {"成本": 3.0, "功能完整性": 5.0},
            "Azure": {"成本": 4.0}  # 缺少 "功能完整性"
        }
        with pytest.raises(ValueError, match="缺少方案 'Azure' 在准则 '功能完整性' 的评分"):
            DecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria[:2],
                scores=scores
            )

    def test_problem_invalid_score_type_raises_error(self, sample_criteria):
        """测试无效评分类型抛出异常"""
        scores = {
            "AWS": {"成本": "高", "功能完整性": 5.0},  # 字符串而非数值
            "Azure": {"成本": 4.0, "功能完整性": 4.0},
        }
        with pytest.raises(ValueError, match="评分必须是数值类型"):
            DecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria[:2],
                scores=scores
            )

    def test_problem_score_out_of_range_raises_error(self, sample_criteria):
        """测试评分超出范围抛出异常"""
        scores = {
            "AWS": {"成本": 3.0, "功能完整性": 150.0},  # 超出 0-100
            "Azure": {"成本": 4.0, "功能完整性": 4.0},
        }
        with pytest.raises(ValueError, match="超出范围"):
            DecisionProblem(
                alternatives=("AWS", "Azure"),
                criteria=sample_criteria[:2],
                scores=scores
            )

    def test_problem_with_data_source(self, sample_criteria):
        """测试带数据源的决策问题"""
        source = DataSource(type="excel", file="data.xlsx", sheet="决策数据")
        problem = DecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            data_source=source
        )
        assert problem.data_source == source

    def test_problem_immutability(self, sample_criteria, sample_scores):
        """测试决策问题不可变性"""
        problem = DecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=sample_criteria[:2],
            scores={
                "AWS": {"成本": 50.0, "功能完整性": 80.0},
                "Azure": {"成本": 60.0, "功能完整性": 70.0},
            },
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            problem.alternatives = ("AWS", "Azure", "GCP")


# =============================================================================
# RankingItem 测试
# =============================================================================

class TestRankingItem:
    """测试 RankingItem 数据模型"""

    def test_create_valid_ranking(self):
        """测试创建有效的排名项"""
        ranking = RankingItem(rank=1, alternative="AWS", score=4.05)
        assert ranking.rank == 1
        assert ranking.alternative == "AWS"
        assert ranking.score == 4.05
        assert ranking.details == {}

    def test_ranking_with_details(self):
        """测试带详细信息的排名"""
        details = {"加权成本": 1.05, "加权功能": 1.50, "加权稳定性": 1.25, "加权支持": 0.25}
        ranking = RankingItem(
            rank=1,
            alternative="AWS",
            score=4.05,
            details=details
        )
        assert ranking.details == details

    def test_ranking_invalid_rank_raises_error(self):
        """测试无效排名抛出异常"""
        with pytest.raises(ValueError, match="rank.*必须大于 0"):
            RankingItem(rank=0, alternative="AWS", score=4.05)

        with pytest.raises(ValueError, match="rank.*必须大于 0"):
            RankingItem(rank=-1, alternative="AWS", score=4.05)

    def test_ranking_empty_alternative_raises_error(self):
        """测试空方案名称抛出异常"""
        with pytest.raises(ValueError, match="alternative 不能为空"):
            RankingItem(rank=1, alternative="", score=4.05)

    def test_ranking_immutability(self):
        """测试排名项不可变性"""
        ranking = RankingItem(rank=1, alternative="AWS", score=4.05)

        with pytest.raises(Exception):  # FrozenInstanceError
            ranking.score = 5.0


# =============================================================================
# ResultMetadata 测试
# =============================================================================

class TestResultMetadata:
    """测试 ResultMetadata 数据模型"""

    def test_create_valid_metadata(self):
        """测试创建有效的元数据"""
        metadata = ResultMetadata(
            algorithm_name="wsm",
            algorithm_version="1.0.0",
            problem_size=(3, 4)
        )
        assert metadata.algorithm_name == "wsm"
        assert metadata.algorithm_version == "1.0.0"
        assert metadata.problem_size == (3, 4)

    def test_metadata_default_values(self):
        """测试默认值"""
        metadata = ResultMetadata(algorithm_name="wsm")
        assert metadata.algorithm_version == "1.0.0"
        assert metadata.calculated_at  # 应该有默认时间戳
        assert metadata.problem_size == (0, 0)

    def test_metadata_calculated_at_format(self):
        """测试计算时间格式（ISO 8601）"""
        metadata = ResultMetadata(algorithm_name="wsm")
        # ISO 8601 格式示例: 2026-01-31T12:34:56.789012
        assert "T" in metadata.calculated_at

    def test_metadata_empty_algorithm_name_raises_error(self):
        """测试空算法名称抛出异常"""
        with pytest.raises(ValueError, match="algorithm_name 不能为空"):
            ResultMetadata(algorithm_name="")

    def test_metadata_invalid_problem_size_raises_error(self):
        """测试无效问题规模抛出异常"""
        with pytest.raises(ValueError, match="problem_size.*无效"):
            ResultMetadata(algorithm_name="wsm", problem_size=(-1, 4))

        with pytest.raises(ValueError, match="problem_size.*无效"):
            ResultMetadata(algorithm_name="wsm", problem_size=(3, -2))


# =============================================================================
# PerturbationResult 测试
# =============================================================================

class TestPerturbationResult:
    """测试 PerturbationResult 数据模型"""

    def test_create_valid_perturbation(self):
        """测试创建有效的扰动结果"""
        perturbation = PerturbationResult(
            criterion_name="成本",
            original_weight=0.35,
            perturbed_weight=0.38,
            delta=0.1,
            rank_changes={"AWS": (1, 2), "Azure": (2, 1)}
        )
        assert perturbation.criterion_name == "成本"
        assert perturbation.original_weight == 0.35
        assert perturbation.perturbed_weight == 0.38
        assert perturbation.delta == 0.1
        assert perturbation.rank_changes == {"AWS": (1, 2), "Azure": (2, 1)}

    def test_perturbation_empty_rank_changes(self):
        """测试空排名变化"""
        perturbation = PerturbationResult(
            criterion_name="成本",
            original_weight=0.35,
            perturbed_weight=0.38,
            delta=0.1
        )
        assert perturbation.rank_changes == {}

    def test_perturbation_empty_criterion_name_raises_error(self):
        """测试空准则名称抛出异常"""
        with pytest.raises(ValueError, match="criterion_name 不能为空"):
            PerturbationResult(
                criterion_name="",
                original_weight=0.35,
                perturbed_weight=0.38,
                delta=0.1
            )

    def test_perturbation_invalid_original_weight_raises_error(self):
        """测试无效原始权重抛出异常"""
        with pytest.raises(ValueError, match="original_weight.*必须在 0-1 范围内"):
            PerturbationResult(
                criterion_name="成本",
                original_weight=1.5,
                perturbed_weight=0.38,
                delta=0.1
            )

    def test_perturbation_invalid_perturbed_weight_raises_error(self):
        """测试无效扰动权重抛出异常"""
        with pytest.raises(ValueError, match="perturbed_weight.*必须在 0-1 范围内"):
            PerturbationResult(
                criterion_name="成本",
                original_weight=0.35,
                perturbed_weight=1.2,
                delta=0.1
            )


# =============================================================================
# SensitivityResult 测试
# =============================================================================

class TestSensitivityResult:
    """测试 SensitivityResult 数据模型"""

    def test_create_valid_sensitivity_result(self):
        """测试创建有效的敏感性分析结果"""
        perturbations = [
            PerturbationResult(
                criterion_name="成本",
                original_weight=0.35,
                perturbed_weight=0.38,
                delta=0.1
            ),
            PerturbationResult(
                criterion_name="功能完整性",
                original_weight=0.30,
                perturbed_weight=0.33,
                delta=0.1
            ),
        ]
        result = SensitivityResult(
            perturbations=perturbations,
            critical_criteria=["成本"],
            robustness_score=0.85
        )
        assert len(result.perturbations) == 2
        assert result.critical_criteria == ["成本"]
        assert result.robustness_score == 0.85

    def test_sensitivity_empty_perturbations(self):
        """测试空扰动列表"""
        result = SensitivityResult(
            perturbations=[],
            critical_criteria=[],
            robustness_score=1.0
        )
        assert result.perturbations == []
        assert result.critical_criteria == []

    def test_sensitivity_invalid_robustness_score_raises_error(self):
        """测试无效稳健性得分抛出异常"""
        with pytest.raises(ValueError, match="robustness_score.*必须在 0-1 范围内"):
            SensitivityResult(
                perturbations=[],
                critical_criteria=[],
                robustness_score=1.5
            )

        with pytest.raises(ValueError, match="robustness_score.*必须在 0-1 范围内"):
            SensitivityResult(
                perturbations=[],
                critical_criteria=[],
                robustness_score=-0.1
            )


# =============================================================================
# DecisionResult 测试
# =============================================================================

class TestDecisionResult:
    """测试 DecisionResult 数据模型"""

    @pytest.fixture
    def sample_rankings(self):
        """创建示例排名"""
        return [
            RankingItem(rank=1, alternative="AWS", score=4.05),
            RankingItem(rank=2, alternative="Azure", score=3.85),
            RankingItem(rank=3, alternative="GCP", score=3.60),
        ]

    @pytest.fixture
    def sample_raw_scores(self):
        """创建示例原始得分"""
        return {"AWS": 4.05, "Azure": 3.85, "GCP": 3.60}

    @pytest.fixture
    def sample_metadata(self):
        """创建示例元数据"""
        return ResultMetadata(
            algorithm_name="wsm",
            problem_size=(3, 4)
        )

    def test_create_valid_result(self, sample_rankings, sample_raw_scores, sample_metadata):
        """测试创建有效的决策结果"""
        result = DecisionResult(
            rankings=sample_rankings,
            raw_scores=sample_raw_scores,
            metadata=sample_metadata
        )
        assert len(result.rankings) == 3
        assert result.raw_scores == sample_raw_scores
        assert result.metadata.algorithm_name == "wsm"
        assert result.sensitivity is None

    def test_result_with_sensitivity(self, sample_rankings, sample_raw_scores, sample_metadata):
        """测试带敏感性分析的决策结果"""
        sensitivity = SensitivityResult(
            perturbations=[],
            critical_criteria=["成本"],
            robustness_score=0.85
        )
        result = DecisionResult(
            rankings=sample_rankings,
            raw_scores=sample_raw_scores,
            metadata=sample_metadata,
            sensitivity=sensitivity
        )
        assert result.sensitivity == sensitivity

    def test_result_empty_rankings_raises_error(self, sample_raw_scores, sample_metadata):
        """测试空排名抛出异常"""
        with pytest.raises(ValueError, match="rankings 不能为空"):
            DecisionResult(
                rankings=[],
                raw_scores=sample_raw_scores,
                metadata=sample_metadata
            )

    def test_result_empty_raw_scores_raises_error(self, sample_rankings, sample_metadata):
        """测试空原始得分抛出异常"""
        with pytest.raises(ValueError, match="raw_scores 不能为空"):
            DecisionResult(
                rankings=sample_rankings,
                raw_scores={},
                metadata=sample_metadata
            )

    def test_result_mismatched_lengths_raises_error(self, sample_rankings, sample_metadata):
        """测试排名和原始得分长度不一致抛出异常"""
        with pytest.raises(ValueError, match="rankings 和 raw_scores 长度不一致"):
            DecisionResult(
                rankings=sample_rankings,
                raw_scores={"AWS": 4.05, "Azure": 3.85},  # 只有 2 个
                metadata=sample_metadata
            )

    def test_result_non_consecutive_ranks_raises_error(self, sample_raw_scores, sample_metadata):
        """测试非连续排名抛出异常"""
        rankings = [
            RankingItem(rank=1, alternative="AWS", score=4.05),
            RankingItem(rank=3, alternative="Azure", score=3.85),  # 跳过 rank 2
        ]
        # 使用与 rankings 长度匹配的 raw_scores
        raw_scores = {"AWS": 4.05, "Azure": 3.85}
        with pytest.raises(ValueError, match="rankings 必须是连续的"):
            DecisionResult(
                rankings=rankings,
                raw_scores=raw_scores,
                metadata=sample_metadata
            )

    def test_result_mutability(self, sample_rankings, sample_raw_scores, sample_metadata):
        """测试决策结果可变性（非 frozen）"""
        result = DecisionResult(
            rankings=sample_rankings,
            raw_scores=sample_raw_scores,
            metadata=sample_metadata
        )
        # 应该可以修改敏感性分析（事后计算）
        sensitivity = SensitivityResult(
            perturbations=[],
            critical_criteria=[],
            robustness_score=1.0
        )
        result.sensitivity = sensitivity
        assert result.sensitivity == sensitivity
