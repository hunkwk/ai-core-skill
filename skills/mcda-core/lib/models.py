"""
MCDA Core - 数据模型定义

使用 frozen dataclass 确保不可变性和类型安全。
评分范围: 0-100（百分制）
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Any

# =============================================================================
# 模块常量
# =============================================================================

MIN_ALTERNATIVES = 2
"""最少备选方案数量"""

MIN_CRITERIA = 1
"""最少评价准则数量"""

MIN_SCORE = 0.0
"""最低评分"""

MAX_SCORE = 100.0
"""最高评分"""

MIN_WEIGHT = 0.0
"""最低权重"""

MAX_WEIGHT = 1.0
"""最高权重"""

# =============================================================================
# 类型别名
# =============================================================================

Direction = Literal["higher_better", "lower_better"]
"""评价准则方向: higher_better（越高越好）或 lower_better（越低越好）"""

ScoreMatrix = dict[str, dict[str, float]]
"""评分矩阵: {alternative: {criterion: score}}"""

ScoreRange = tuple[float, float]
"""评分范围: (min, max)，默认 (0.0, 100.0)"""

# =============================================================================
# 评分规则数据模型
# =============================================================================

@dataclass(frozen=True)
class LinearScoringRule:
    """线性评分规则

    将原始值线性映射到 0-100 分。

    公式:
    - higher_better: score = 100 * (value - min) / (max - min)
    - lower_better: score = 100 * (max - value) / (max - min)

    Example:
        ```yaml
        scoring_rule:
          type: linear
          min: 0
          max: 100
          scale: 100
        ```
    """
    min: float
    max: float
    scale: float = 100.0
    type: Literal["linear"] = "linear"

    def __post_init__(self):
        """验证参数有效性"""
        if self.min >= self.max:
            raise ValueError(f"LinearScoringRule: min ({self.min}) 必须小于 max ({self.max})")
        if self.scale <= 0:
            raise ValueError(f"LinearScoringRule: scale ({self.scale}) 必须大于 0")


@dataclass(frozen=True)
class ThresholdRange:
    """阈值范围

    定义单个阈值区间的评分规则。

    Example:
        ```python
        ThresholdRange(max=100, score=100)  # value < 100 → score = 100
        ThresholdRange(min=100, max=500, score=80)  # 100 <= value < 500 → score = 80
        ```
    """
    min: float | None = None
    max: float | None = None
    score: float = 100.0

    def __post_init__(self):
        """验证参数有效性"""
        if self.min is not None and self.max is not None and self.min >= self.max:
            raise ValueError(f"ThresholdRange: min ({self.min}) 必须小于 max ({self.max})")
        if self.score < 0 or self.score > 100:
            raise ValueError(f"ThresholdRange: score ({self.score}) 必须在 0-100 范围内")


@dataclass(frozen=True)
class ThresholdScoringRule:
    """阈值分段评分规则

    根据原始值落在哪个区间来决定评分。

    Example:
        ```yaml
        scoring_rule:
          type: threshold
          ranges:
            - {max: 100, score: 100}
            - {min: 100, max: 500, score: 80}
            - {min: 500, max: 1000, score: 60}
            - {min: 1000, score: 40}
          default_score: 0
        ```
    """
    ranges: tuple[ThresholdRange, ...]
    default_score: float = 0.0
    type: Literal["threshold"] = "threshold"

    def __post_init__(self):
        """验证参数有效性"""
        if not self.ranges:
            raise ValueError("ThresholdScoringRule: ranges 不能为空")
        if self.default_score < 0 or self.default_score > 100:
            raise ValueError(f"ThresholdScoringRule: default_score ({self.default_score}) 必须在 0-100 范围内")


# 评分规则联合类型
ScoringRule = LinearScoringRule | ThresholdScoringRule

# =============================================================================
# 数据源数据模型
# =============================================================================

@dataclass(frozen=True)
class DataSource:
    """数据源配置

    支持的数据源类型:
    - yaml: YAML 配置文件
    - csv: CSV 文件（使用标准库 csv）
    - excel: Excel 文件（需要 openpyxl）

    Example:
        ```yaml
        data_source:
          type: excel
          file: data/vendor_data.xlsx
          sheet: 决策数据
          encoding: utf-8
        ```
    """
    type: Literal["yaml", "csv", "excel"]
    file: str
    sheet: str | None = None
    encoding: str = "utf-8"

    def __post_init__(self):
        """验证参数有效性"""
        valid_types = {"yaml", "csv", "excel"}
        if self.type not in valid_types:
            raise ValueError(f"DataSource: type ({self.type}) 必须是 {valid_types} 之一")
        if self.type == "excel" and not self.sheet:
            raise ValueError("DataSource: Excel 数据源必须指定 sheet 名称")


# =============================================================================
# 核心数据模型
# =============================================================================

@dataclass(frozen=True)
class Criterion:
    """评价准则

    定义单个评价准则的属性。

    Attributes:
        name: 准则名称（唯一标识）
        weight: 权重（0-1 之间，所有准则权重总和应为 1.0）
        direction: 方向性（higher_better 或 lower_better）
        description: 准则描述（可选）
        scoring_rule: 评分规则（可选，用于自动计算评分）
        column: 数据源列名（可选，用于导入外部数据）

    Example:
        ```python
        criterion = Criterion(
            name="成本",
            weight=0.35,
            direction="lower_better",
            description="月度成本（万元）"
        )
        ```
    """
    name: str
    weight: float
    direction: Direction
    description: str = ""
    scoring_rule: ScoringRule | None = None
    column: str | None = None

    def __post_init__(self):
        """验证参数有效性"""
        if not self.name:
            raise ValueError("Criterion: name 不能为空")
        if self.weight < 0 or self.weight > 1:
            raise ValueError(f"Criterion: weight ({self.weight}) 必须在 0-1 范围内")
        if self.direction not in ("higher_better", "lower_better"):
            raise ValueError(f"Criterion: direction ({self.direction}) 必须是 'higher_better' 或 'lower_better'")


@dataclass(frozen=True)
class AlgorithmConfig:
    """算法配置

    定义 MCDA 算法的配置参数。

    Attributes:
        name: 算法名称（如 wsm, wpm, topsis, vikor）
        params: 算法特定参数（可选）

    Example:
        ```python
        config = AlgorithmConfig(name="wsm", params={})
        config = AlgorithmConfig(name="vikor", params={"v": 0.5})
        ```
    """
    name: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """验证参数有效性"""
        if not self.name:
            raise ValueError("AlgorithmConfig: name 不能为空")


@dataclass(frozen=True)
class DecisionProblem:
    """决策问题（不可变）

    完整定义一个多准则决策问题。

    Attributes:
        alternatives: 备选方案列表（至少 2 个）
        criteria: 评价准则列表（至少 2 个）
        scores: 评分矩阵（{alternative: {criterion: score}}）
        algorithm: 算法配置
        data_source: 数据源配置（可选）
        raw_data: 原始数据（可选，用于评分计算）
        score_range: 评分范围，默认 (0.0, 100.0)

    Example:
        ```python
        problem = DecisionProblem(
            alternatives=("AWS", "Azure", "GCP"),
            criteria=(
                Criterion(name="成本", weight=0.35, direction="lower_better"),
                Criterion(name="功能完整性", weight=0.30, direction="higher_better"),
            ),
            scores={
                "AWS": {"成本": 3.0, "功能完整性": 5.0},
                "Azure": {"成本": 4.0, "功能完整性": 4.0},
                "GCP": {"成本": 5.0, "功能完整性": 4.0},
            },
            algorithm=AlgorithmConfig(name="wsm")
        )
        ```
    """
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    scores: ScoreMatrix | None = None
    algorithm: AlgorithmConfig | None = None
    data_source: DataSource | None = None
    raw_data: dict | None = None
    score_range: ScoreRange = (0.0, 100.0)

    def __post_init__(self):
        """验证数据一致性"""
        if len(self.alternatives) < 2:
            raise ValueError("DecisionProblem: 至少需要 2 个备选方案")
        if len(self.criteria) < 1:
            raise ValueError("DecisionProblem: 至少需要 1 个评价准则")

        # 验证评分范围
        min_score, max_score = self.score_range
        if min_score >= max_score:
            raise ValueError(f"DecisionProblem: score_range 无效 ({min_score}, {max_score})")

        # 验证评分矩阵（如果提供）
        if self.scores:
            self._validate_score_matrix()

    def _validate_score_matrix(self):
        """验证评分矩阵的完整性和有效性"""
        min_score, max_score = self.score_range

        for alt in self.alternatives:
            if alt not in self.scores:
                raise ValueError(f"DecisionProblem: 缺少方案 '{alt}' 的评分")
            if not isinstance(self.scores[alt], dict):
                raise ValueError(f"DecisionProblem: 方案 '{alt}' 的评分必须是字典")

            for crit in self.criteria:
                if crit.name not in self.scores[alt]:
                    raise ValueError(f"DecisionProblem: 缺少方案 '{alt}' 在准则 '{crit.name}' 的评分")

                score = self.scores[alt][crit.name]
                if not isinstance(score, (int, float)):
                    raise ValueError(f"DecisionProblem: 评分必须是数值类型")

                if not (min_score <= score <= max_score):
                    raise ValueError(
                        f"DecisionProblem: 方案 '{alt}' 在准则 '{crit.name}' 的评分 {score} "
                        f"超出范围 [{min_score}, {max_score}]"
                    )


@dataclass(frozen=True)
class RankingItem:
    """排名项

    表示单个备选方案的排名结果。

    Attributes:
        rank: 排名（1 表示最优）
        alternative: 备选方案名称
        score: 综合得分
        details: 详细得分（可选，如各准则的加权得分）
    """
    rank: int
    alternative: str
    score: float
    details: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """验证参数有效性"""
        if self.rank < 1:
            raise ValueError(f"RankingItem: rank ({self.rank}) 必须大于 0")
        if not self.alternative:
            raise ValueError("RankingItem: alternative 不能为空")


@dataclass(frozen=True)
class ResultMetadata:
    """结果元数据

    记录决策计算的元信息。

    Attributes:
        algorithm_name: 算法名称
        algorithm_version: 算法版本
        calculated_at: 计算时间（ISO 8601 格式）
        problem_size: 问题规模 (备选方案数, 准则数)
        metrics: 算法特定指标（可选）
    """
    algorithm_name: str
    algorithm_version: str = "1.0.0"
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    problem_size: tuple[int, int] = (0, 0)
    metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """验证参数有效性"""
        if not self.algorithm_name:
            raise ValueError("ResultMetadata: algorithm_name 不能为空")
        if self.problem_size[0] < 0 or self.problem_size[1] < 0:
            raise ValueError(f"ResultMetadata: problem_size {self.problem_size} 无效")


@dataclass(frozen=True)
class PerturbationResult:
    """单次扰动结果

    记录权重扰动后的排名变化。

    Attributes:
        criterion_name: 扰动的准则名称
        original_weight: 原始权重
        perturbed_weight: 扰动后权重
        delta: 扰动幅度（如 0.1 表示 +10%）
        rank_changes: 排名变化 {alternative: (old_rank, new_rank)}
    """
    criterion_name: str
    original_weight: float
    perturbed_weight: float
    delta: float
    rank_changes: dict[str, tuple[int, int]] = field(default_factory=dict)

    def __post_init__(self):
        """验证参数有效性"""
        if not self.criterion_name:
            raise ValueError("PerturbationResult: criterion_name 不能为空")
        if self.original_weight < 0 or self.original_weight > 1:
            raise ValueError(f"PerturbationResult: original_weight ({self.original_weight}) 必须在 0-1 范围内")
        if self.perturbed_weight < 0 or self.perturbed_weight > 1:
            raise ValueError(f"PerturbationResult: perturbed_weight ({self.perturbed_weight}) 必须在 0-1 范围内")


@dataclass
class SensitivityResult:
    """敏感性分析结果

    记录敏感性分析的完整结果。

    Attributes:
        perturbations: 所有的扰动结果列表
        critical_criteria: 关键准则列表（对排名影响最大的准则）
        robustness_score: 稳健性得分（0-1，越接近 1 表示越稳健）
    """
    perturbations: list[PerturbationResult]
    critical_criteria: list[str]
    robustness_score: float

    def __post_init__(self):
        """验证参数有效性"""
        if self.robustness_score < 0 or self.robustness_score > 1:
            raise ValueError(f"SensitivityResult: robustness_score ({self.robustness_score}) 必须在 0-1 范围内")

    @property
    def criterion_name(self) -> str | None:
        """获取扰动的准则名称（便捷属性）"""
        if self.perturbations:
            return self.perturbations[0].criterion_name
        return None

    @property
    def original_weight(self) -> float | None:
        """获取原始权重（便捷属性）"""
        if self.perturbations:
            return self.perturbations[0].original_weight
        return None


@dataclass(frozen=True)
class CriticalCriterion:
    """关键准则

    记录对排名影响最大的准则。

    Attributes:
        criterion_name: 准则名称
        weight: 权重
        rank_changes: 排名变化数
    """
    criterion_name: str
    weight: float
    rank_changes: int

    def __post_init__(self):
        """验证参数有效性"""
        if not self.criterion_name:
            raise ValueError("CriticalCriterion: criterion_name 不能为空")
        if self.weight < 0 or self.weight > 1:
            raise ValueError(f"CriticalCriterion: weight ({self.weight}) 必须在 0-1 范围内")
        if self.rank_changes < 0:
            raise ValueError(f"CriticalCriterion: rank_changes ({self.rank_changes}) 不能为负数")


@dataclass(frozen=True)
class SensitivityAnalysisResult:
    """综合敏感性分析结果

    记录完整的敏感性分析结果。

    Attributes:
        critical_criteria: 关键准则列表
        perturbation_results: 所有准则的扰动结果列表
    """
    critical_criteria: tuple[CriticalCriterion, ...]
    perturbation_results: tuple["SensitivityResult", ...]


@dataclass
class DecisionResult:
    """决策结果

    完整的决策分析结果。

    Attributes:
        rankings: 排名列表（按得分降序）
        raw_scores: 原始得分 {alternative: score}
        metadata: 结果元数据
        sensitivity: 敏感性分析结果（可选）

    Note:
        使用普通 dataclass（非 frozen），因为敏感性分析可能在事后计算
    """
    rankings: list[RankingItem]
    raw_scores: dict[str, float]
    metadata: ResultMetadata
    sensitivity: SensitivityResult | None = None

    def __post_init__(self):
        """验证数据一致性"""
        if not self.rankings:
            raise ValueError("DecisionResult: rankings 不能为空")
        if not self.raw_scores:
            raise ValueError("DecisionResult: raw_scores 不能为空")
        if len(self.rankings) != len(self.raw_scores):
            raise ValueError("DecisionResult: rankings 和 raw_scores 长度不一致")

        # 验证排名连续性
        ranks = sorted(item.rank for item in self.rankings)
        if ranks != list(range(1, len(ranks) + 1)):
            raise ValueError("DecisionResult: rankings 必须是连续的 1, 2, 3, ...")


# =============================================================================
# 标准化数据模型
# =============================================================================

NormalizationType = Literal["minmax", "vector"]
"""标准化方法类型"""


@dataclass(frozen=True)
class NormalizationConfig:
    """标准化配置

    Attributes:
        type: 标准化方法类型（minmax, vector 或其他自定义方法）
        direction: 方向（higher_better 越高越好, lower_better 越低越好）
    """
    type: str  # 改为 str 以支持任意方法名
    direction: Direction = "higher_better"

    def __post_init__(self):
        """验证配置有效性"""
        if self.direction not in ("higher_better", "lower_better"):
            raise ValueError(f"NormalizationConfig: 不支持的方向 '{self.direction}'")


# =============================================================================
# 导出公共 API
# =============================================================================

__all__ = [
    # 类型别名
    "Direction",
    "ScoreMatrix",
    "ScoreRange",
    "NormalizationType",
    # 评分规则
    "LinearScoringRule",
    "ThresholdRange",
    "ThresholdScoringRule",
    "ScoringRule",
    # 数据源
    "DataSource",
    # 核心模型
    "Criterion",
    "AlgorithmConfig",
    "DecisionProblem",
    "RankingItem",
    "ResultMetadata",
    "PerturbationResult",
    "SensitivityResult",
    "CriticalCriterion",
    "SensitivityAnalysisResult",
    "DecisionResult",
    # 标准化
    "NormalizationConfig",
]
