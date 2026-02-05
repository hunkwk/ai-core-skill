"""
VetoEvaluator 核心功能测试

简化版测试，验证评估器核心逻辑
"""

import pytest

from mcda_core.constraints.evaluator import VetoEvaluator
from mcda_core.constraints.models import (
    VetoCondition,
    VetoConfig,
    VetoTier,
)


class MockCriterion:
    """模拟 Criterion 类"""
    def __init__(self, name, direction='higher_better', veto=None):
        self.name = name
        self.direction = direction
        self.veto = veto


class TestVetoEvaluatorCore:
    """测试 VetoEvaluator 核心功能"""

    def test_evaluate_hard_veto_accept(self):
        """测试硬否决：通过"""
        criterion = MockCriterion(
            name="资质评分",
            direction='higher_better',
            veto=VetoConfig(
                type="hard",
                condition=VetoCondition(operator=">=", value=60, action="reject")
            )
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A001",
            scores={"资质评分": 80},
            criteria=[criterion]
        )

        assert result.rejected is False
        assert result.alternative_id == "A001"

    def test_evaluate_hard_veto_reject(self):
        """测试硬否决：拒绝"""
        criterion = MockCriterion(
            name="资质评分",
            direction='higher_better',
            veto=VetoConfig(
                type="hard",
                condition=VetoCondition(operator=">=", value=60, action="reject")
            )
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A002",
            scores={"资质评分": 40},
            criteria=[criterion]
        )

        assert result.rejected is True
        assert len(result.reject_reasons) == 1

    def test_evaluate_soft_veto_no_penalty(self):
        """测试软否决：不触发惩罚"""
        criterion = MockCriterion(
            name="财务风险",
            direction='lower_better',
            veto=VetoConfig(
                type="soft",
                condition=VetoCondition(operator=">", value=60, action="warning"),
                penalty_score=-30
            )
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A003",
            scores={"财务风险": 50},
            criteria=[criterion]
        )

        assert result.rejected is False
        assert len(result.warnings) == 0
        assert result.total_penalty == 0

    def test_evaluate_soft_veto_with_penalty(self):
        """测试软否决：触发惩罚"""
        criterion = MockCriterion(
            name="财务风险",
            direction='lower_better',
            veto=VetoConfig(
                type="soft",
                condition=VetoCondition(operator=">", value=60, action="warning"),
                penalty_score=-30
            )
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A004",
            scores={"财务风险": 70},
            criteria=[criterion]
        )

        assert result.rejected is False
        assert len(result.warnings) == 1
        assert result.total_penalty == -30

    def test_evaluate_tiered_veto_accept(self):
        """测试分级否决：接受"""
        tiers = (
            VetoTier(min=0, max=30, action="accept"),
            VetoTier(min=30, max=60, action="warning", penalty_score=-15),
            VetoTier(min=60, max=100, action="reject"),
        )

        criterion = MockCriterion(
            name="技术风险",
            direction='lower_better',
            veto=VetoConfig(type="tiered", tiers=tiers)
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A005",
            scores={"技术风险": 25},
            criteria=[criterion]
        )

        assert result.rejected is False
        assert len(result.warnings) == 0

    def test_evaluate_tiered_veto_warning(self):
        """测试分级否决：警告"""
        tiers = (
            VetoTier(min=0, max=30, action="accept"),
            VetoTier(min=30, max=60, action="warning", penalty_score=-15),
            VetoTier(min=60, max=100, action="reject"),
        )

        criterion = MockCriterion(
            name="技术风险",
            direction='lower_better',
            veto=VetoConfig(type="tiered", tiers=tiers)
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A006",
            scores={"技术风险": 45},
            criteria=[criterion]
        )

        assert result.rejected is False
        assert len(result.warnings) == 1
        assert result.total_penalty == -15

    def test_evaluate_tiered_veto_reject(self):
        """测试分级否决：拒绝"""
        tiers = (
            VetoTier(min=0, max=30, action="accept"),
            VetoTier(min=30, max=60, action="warning", penalty_score=-15),
            VetoTier(min=60, max=100, action="reject"),
        )

        criterion = MockCriterion(
            name="技术风险",
            direction='lower_better',
            veto=VetoConfig(type="tiered", tiers=tiers)
        )

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A007",
            scores={"技术风险": 70},
            criteria=[criterion]
        )

        assert result.rejected is True

    def test_evaluate_composite_or_logic(self):
        """测试组合否决：OR 逻辑"""
        conditions = (
            VetoCondition(operator="==", value="expired", action="reject"),
            VetoCondition(operator="in", value=["revoked", "suspended"], action="reject"),
        )

        criterion = MockCriterion(
            name="许可证状态",
            direction='higher_better',
            veto=VetoConfig(
                type="composite",
                conditions=conditions,
                logic="or"
            )
        )

        evaluator = VetoEvaluator()

        # 测试第一个条件满足
        result = evaluator.evaluate(
            alternative_id="A008",
            scores={"许可证状态": "expired"},
            criteria=[criterion]
        )
        assert result.rejected is True

        # 测试第二个条件满足
        result = evaluator.evaluate(
            alternative_id="A009",
            scores={"许可证状态": "revoked"},
            criteria=[criterion]
        )
        assert result.rejected is True

    def test_evaluate_composite_and_logic(self):
        """测试组合否决：AND 逻辑"""
        conditions = (
            VetoCondition(operator=">", value=50, action="warning"),
            VetoCondition(operator="<", value=80, action="warning"),
        )

        criterion = MockCriterion(
            name="风险指数",
            direction='lower_better',
            veto=VetoConfig(
                type="composite",
                conditions=conditions,
                logic="and"
            )
        )

        evaluator = VetoEvaluator()

        # 测试两个条件都满足
        result = evaluator.evaluate(
            alternative_id="A010",
            scores={"风险指数": 60},
            criteria=[criterion]
        )
        assert len(result.warnings) == 1

        # 测试只有一个条件满足
        result = evaluator.evaluate(
            alternative_id="A011",
            scores={"风险指数": 90},
            criteria=[criterion]
        )
        assert len(result.warnings) == 0

    def test_evaluate_multiple_criteria(self):
        """测试多准则评估"""
        criteria = [
            MockCriterion(
                name="资质评分",
                direction='higher_better',
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=60, action="reject")
                )
            ),
            MockCriterion(
                name="财务风险",
                direction='lower_better',
                veto=VetoConfig(
                    type="soft",
                    condition=VetoCondition(operator=">", value=60, action="warning"),
                    penalty_score=-30
                )
            ),
        ]

        evaluator = VetoEvaluator()
        result = evaluator.evaluate(
            alternative_id="A012",
            scores={"资质评分": 70, "财务风险": 70},
            criteria=criteria
        )

        # 硬否决通过，软否决触发警告
        assert result.rejected is False
        assert len(result.warnings) == 1
        assert result.total_penalty == -30
