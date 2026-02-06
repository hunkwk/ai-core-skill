"""
一票否决机制数据模型

定义一票否决机制的核心数据结构：
- VetoCondition: 否决条件
- VetoConfig: 否决配置
- VetoTier: 分级档位
- VetoResult: 评估结果
- ConstraintMetadata: 约束元数据
"""

from dataclasses import dataclass, field
from typing import Any, Literal

from mcda_core.interval import Interval


@dataclass(frozen=True)
class VetoCondition:
    """
    否决条件

    定义单个否决条件的评估规则

    Attributes:
        operator: 比较操作符（==, !=, >, >=, <, <=, in, not_in）
        value: 比较值（可以是数字、字符串、列表、区间等）
        action: 触发动作（accept, warning, reject）
        penalty_score: 惩罚分数（默认 0.0）
        label: 条件标签（用于显示）

    Examples:
        >>> condition = VetoCondition(operator=">=", value=60, action="reject")
        >>> condition = VetoCondition(operator="in", value=["A", "B"], action="warning")
    """

    operator: Literal["==", "!=", ">", ">=", "<", "<=", "in", "not_in"]
    value: Any
    action: Literal["accept", "warning", "reject"] = "warning"
    penalty_score: float = 0.0
    label: str = ""

    def __post_init__(self):
        """验证操作符有效性"""
        valid_operators = {"==", "!=", ">", ">=", "<", "<=", "in", "not_in"}
        if self.operator not in valid_operators:
            raise ValueError(f"无效的操作符: {self.operator}，必须是 {valid_operators} 之一")


@dataclass(frozen=True)
class VetoTier:
    """
    分级否决档位

    定义分级否决的单个档位

    Attributes:
        min: 最小值（包含）
        max: 最大值（不包含）
        action: 触发动作（accept, warning, reject）
        penalty_score: 惩罚分数（默认 0.0）
        label: 档位标签（用于显示）

    Examples:
        >>> tier = VetoTier(min=0, max=30, action="accept")
        >>> tier = VetoTier(min=30, max=60, action="warning", penalty_score=-15)
    """

    min: float
    max: float
    action: Literal["accept", "warning", "reject"] = "accept"
    penalty_score: float = 0.0
    label: str = ""


@dataclass(frozen=True)
class VetoConfig:
    """
    否决配置

    定义准则的否决规则配置

    Attributes:
        type: 否决类型（hard, soft, tiered, composite）
        condition: 单个条件（hard/soft 类型使用）
        tiers: 分级档位（tiered 类型使用）
        conditions: 多个条件（composite 类型使用）
        logic: 组合逻辑（and/or，composite 类型使用）
        penalty_score: 默认惩罚分数（soft 类型使用）
        reject_reason: 拒绝原因描述

    Examples:
        >>> # 硬否决
        >>> condition = VetoCondition(operator=">=", value=60, action="reject")
        >>> config = VetoConfig(type="hard", condition=condition)

        >>> # 分级否决
        >>> tiers = (
        ...     VetoTier(min=0, max=30, action="accept"),
        ...     VetoTier(min=30, max=60, action="warning"),
        ... )
        >>> config = VetoConfig(type="tiered", tiers=tiers)
    """

    type: Literal["hard", "soft", "tiered", "composite"]
    condition: VetoCondition | None = None
    tiers: tuple[VetoTier, ...] = ()
    conditions: tuple[VetoCondition, ...] = ()
    logic: Literal["and", "or"] = "or"
    penalty_score: float = -20.0
    reject_reason: str = "未满足否决条件"

    def __post_init__(self):
        """验证配置有效性"""
        if self.type == "hard":
            if self.condition is None:
                raise ValueError("hard 类型必须提供 condition 参数")
        elif self.type == "soft":
            if self.condition is None:
                raise ValueError("soft 类型必须提供 condition 参数")
        elif self.type == "tiered":
            if not self.tiers:
                raise ValueError("tiered 类型必须提供 tiers 参数")
        elif self.type == "composite":
            if not self.conditions:
                raise ValueError("composite 类型必须提供 conditions 参数")
        else:
            raise ValueError(f"无效的否决类型: {self.type}")


@dataclass(frozen=True)
class VetoResult:
    """
    否决评估结果

    记录单个方案的否决评估结果

    Attributes:
        alternative_id: 方案 ID
        rejected: 是否被拒绝
        reject_reasons: 拒绝原因列表
        warnings: 警告信息列表
        penalties: 惩罚分数字典 {准则名称: 惩罚分数}
        total_penalty: 总惩罚分数

    Examples:
        >>> result = VetoResult(
        ...     alternative_id="A001",
        ...     rejected=False,
        ...     warnings=["财务风险偏高"],
        ...     penalties={"财务风险": -30}
        ... )
    """

    alternative_id: str
    rejected: bool
    reject_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    penalties: dict[str, float] = field(default_factory=dict)
    total_penalty: float = 0.0

    def __post_init__(self):
        """计算总惩罚分数"""
        if not self.total_penalty and self.penalties:
            # 使用 object.__setattr__ 因为 frozen=True
            object.__setattr__(
                self,
                "total_penalty",
                sum(self.penalties.values())
            )


@dataclass(frozen=True)
class ConstraintMetadata:
    """
    约束元数据

    统计约束评估的元数据信息

    Attributes:
        total_alternatives: 总方案数
        rejected_count: 被拒绝方案数
        warning_count: 有警告方案数
        accept_count: 接受方案数
        rejection_rate: 拒绝率
        warning_rate: 警告率

    Examples:
        >>> metadata = ConstraintMetadata(
        ...     total_alternatives=10,
        ...     rejected_count=2,
        ...     warning_count=3,
        ...     accept_count=5
        ... )
        >>> assert metadata.rejection_rate == 0.2
    """

    total_alternatives: int
    rejected_count: int
    warning_count: int
    accept_count: int

    @property
    def rejection_rate(self) -> float:
        """计算拒绝率"""
        if self.total_alternatives == 0:
            return 0.0
        return self.rejected_count / self.total_alternatives

    @property
    def warning_rate(self) -> float:
        """计算警告率"""
        if self.total_alternatives == 0:
            return 0.0
        return self.warning_count / self.total_alternatives
