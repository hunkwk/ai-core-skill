"""
一票否决机制数据模型测试

测试 VetoCondition, VetoConfig, VetoTier, VetoResult, ConstraintMetadata
"""

import pytest
from dataclasses import FrozenInstanceError

from mcda_core.constraints.models import (
    VetoCondition,
    VetoConfig,
    VetoTier,
    VetoResult,
    ConstraintMetadata,
)
from mcda_core.interval import Interval


class TestVetoCondition:
    """测试 VetoCondition 数据模型"""

    def test_veto_condition_equals_operator(self):
        """测试等于操作符 (==)"""
        condition = VetoCondition(operator="==", value=60, action="reject")

        assert condition.operator == "=="
        assert condition.value == 60
        assert condition.action == "reject"
        assert condition.penalty_score == 0.0
        assert condition.label == ""

    def test_veto_condition_greater_than_operator(self):
        """测试大于操作符 (>)"""
        condition = VetoCondition(operator=">", value=50, action="warning")

        assert condition.operator == ">"
        assert condition.value == 50
        assert condition.action == "warning"

    def test_veto_condition_less_than_operator(self):
        """测试小于操作符 (<)"""
        condition = VetoCondition(operator="<", value=0.8, action="accept", penalty_score=-10)

        assert condition.operator == "<"
        assert condition.value == 0.8
        assert condition.penalty_score == -10

    def test_veto_condition_in_operator(self):
        """测试包含操作符 (in)"""
        condition = VetoCondition(
            operator="in",
            value=["A", "B", "C"],
            action="reject",
            label="资质等级不满足"
        )

        assert condition.operator == "in"
        assert condition.value == ["A", "B", "C"]
        assert condition.label == "资质等级不满足"

    def test_veto_condition_invalid_operator_raises_error(self):
        """测试无效操作符抛出错误"""
        with pytest.raises(ValueError, match="无效的操作符"):
            VetoCondition(operator="invalid", value=10)

    def test_veto_condition_with_interval_value(self):
        """测试区间数值评估"""
        interval = Interval(lower=50, upper=70)
        condition = VetoCondition(operator=">", value=interval, action="reject")

        assert isinstance(condition.value, Interval)
        assert condition.value.lower == 50
        assert condition.value.upper == 70


class TestVetoConfig:
    """测试 VetoConfig 配置模型"""

    def test_veto_config_hard_type(self):
        """测试硬否决配置"""
        condition = VetoCondition(operator=">=", value=60, action="reject")
        config = VetoConfig(type="hard", condition=condition)

        assert config.type == "hard"
        assert config.condition is not None
        assert config.condition.operator == ">="

    def test_veto_config_soft_type(self):
        """测试软否决配置"""
        condition = VetoCondition(operator=">", value=60, action="warning", penalty_score=-30)
        config = VetoConfig(type="soft", condition=condition, penalty_score=-30)

        assert config.type == "soft"
        assert config.penalty_score == -30
        assert config.reject_reason == "未满足否决条件"

    def test_veto_config_tiered_type(self):
        """测试分级否决配置"""
        tiers = (
            VetoTier(min=0, max=30, action="accept"),
            VetoTier(min=30, max=60, action="warning", penalty_score=-15),
            VetoTier(min=60, max=100, action="reject"),
        )
        config = VetoConfig(type="tiered", tiers=tiers)

        assert config.type == "tiered"
        assert len(config.tiers) == 3
        assert config.tiers[0].action == "accept"

    def test_veto_config_composite_type(self):
        """测试组合否决配置"""
        conditions = (
            VetoCondition(operator="==", value="expired", action="reject"),
            VetoCondition(operator="in", value=["revoked", "suspended"], action="reject"),
        )
        config = VetoConfig(type="composite", conditions=conditions, logic="or")

        assert config.type == "composite"
        assert len(config.conditions) == 2
        assert config.logic == "or"

    def test_veto_config_validation(self):
        """测试配置验证逻辑"""
        # hard 类型必须有 condition
        with pytest.raises(ValueError, match="hard 类型必须提供 condition"):
            VetoConfig(type="hard")

        # tiered 类型必须有 tiers
        with pytest.raises(ValueError, match="tiered 类型必须提供 tiers"):
            VetoConfig(type="tiered")

        # composite 类型必须有 conditions 和 logic
        with pytest.raises(ValueError, match="composite 类型必须提供 conditions"):
            VetoConfig(type="composite", logic="or")

    def test_veto_config_invalid_type_raises_error(self):
        """测试无效类型抛出错误"""
        with pytest.raises(ValueError, match="无效的否决类型"):
            VetoConfig(type="invalid")


class TestVetoTier:
    """测试 VetoTier 档位模型"""

    def test_veto_tier_creation(self):
        """测试档位创建"""
        tier = VetoTier(min=0, max=30, action="accept")

        assert tier.min == 0
        assert tier.max == 30
        assert tier.action == "accept"
        assert tier.penalty_score == 0.0
        assert tier.label == ""

    def test_veto_tier_with_penalty(self):
        """测试带惩罚分的档位"""
        tier = VetoTier(
            min=30,
            max=60,
            action="warning",
            penalty_score=-15,
            label="中等风险"
        )

        assert tier.action == "warning"
        assert tier.penalty_score == -15
        assert tier.label == "中等风险"

    def test_veto_tier_immutability(self):
        """测试档位不可变性"""
        tier = VetoTier(min=0, max=30, action="accept")

        with pytest.raises(FrozenInstanceError):
            tier.min = 10


class TestVetoResult:
    """测试 VetoResult 结果模型"""

    def test_veto_result_creation(self):
        """测试结果创建"""
        result = VetoResult(
            alternative_id="A001",
            rejected=False,
            warnings=[],
            penalties={}
        )

        assert result.alternative_id == "A001"
        assert result.rejected is False
        assert result.warnings == []
        assert result.penalties == {}

    def test_veto_result_rejected(self):
        """测试被拒绝方案"""
        result = VetoResult(
            alternative_id="A002",
            rejected=True,
            reject_reasons=["资质评分不足: 40 < 60"],
            warnings=[],
            penalties={}
        )

        assert result.rejected is True
        assert len(result.reject_reasons) == 1
        assert "资质评分不足" in result.reject_reasons[0]

    def test_veto_result_warning(self):
        """测试有警告方案"""
        result = VetoResult(
            alternative_id="A003",
            rejected=False,
            warnings=["财务风险偏高"],
            penalties={"财务风险": -30}
        )

        assert result.rejected is False
        assert len(result.warnings) == 1
        assert result.penalties["财务风险"] == -30

    def test_veto_result_with_details(self):
        """测试详细信息"""
        result = VetoResult(
            alternative_id="A004",
            rejected=False,
            warnings=["警告1", "警告2"],
            penalties={"准则1": -10, "准则2": -20},
            reject_reasons=[]
        )

        assert len(result.warnings) == 2
        assert len(result.penalties) == 2
        assert result.total_penalty == -30


class TestConstraintMetadata:
    """测试 ConstraintMetadata 元数据模型"""

    def test_constraint_metadata_creation(self):
        """测试元数据创建"""
        metadata = ConstraintMetadata(
            total_alternatives=5,
            rejected_count=2,
            warning_count=1,
            accept_count=2
        )

        assert metadata.total_alternatives == 5
        assert metadata.rejected_count == 2
        assert metadata.warning_count == 1
        assert metadata.accept_count == 2

    def test_constraint_metadata_rejection_rate(self):
        """测试拒绝率计算"""
        metadata = ConstraintMetadata(
            total_alternatives=10,
            rejected_count=3,
            warning_count=2,
            accept_count=5
        )

        assert metadata.rejection_rate == 0.3
        assert metadata.warning_rate == 0.2
