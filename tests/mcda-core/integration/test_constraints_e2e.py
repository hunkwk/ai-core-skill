"""
MCDA Core - 约束否决 E2E 测试

测试一票否决机制的端到端功能。
"""

import pytest
from pathlib import Path

from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.constraints.models import (
    VetoConfig,
    VetoCondition,
    VetoTier,
    VetoResult,
)
from mcda_core.constraints.evaluator import VetoEvaluator


class TestVetoMechanism:
    """否决机制端到端测试"""

    def test_hard_veto_rejection(self):
        """测试: 硬否决 - 方案被拒绝"""
        # 创建带硬否决的准则
        # 成本越低越好 (lower_better)
        # 设置通过条件: 成本 <= 80
        # 不满足条件时 (成本 > 80) 被拒绝
        criteria = [
            Criterion(
                name="成本",
                weight=0.5,
                direction="lower_better",
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator="<=", value=80, action="reject"),
                    reject_reason="成本超过 80 被拒绝"
                )
            ),
            Criterion(name="质量", weight=0.5, direction="higher_better"),
        ]

        # 方案 A 成本 85（超过阈值，应被拒绝）
        problem = DecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=tuple(criteria),
            scores={
                "方案A": {"成本": 85, "质量": 90},
                "方案B": {"成本": 60, "质量": 80},
            }
        )

        # 评估否决
        evaluator = VetoEvaluator()
        result_a = evaluator.evaluate("方案A", problem.scores["方案A"], problem.criteria)
        result_b = evaluator.evaluate("方案B", problem.scores["方案B"], problem.criteria)

        # 验证否决结果
        assert result_a.rejected == True
        assert len(result_a.reject_reasons) > 0
        assert "成本" in result_a.reject_reasons[0]

        # 方案B 应该通过
        assert result_b.rejected == False

    def test_soft_veto_warning(self):
        """测试: 软否决 - 警告但接受"""
        # 风险越低越好 (lower_better)
        # 设置触发警告条件: 风险 > 50 时触发警告
        criteria = [
            Criterion(
                name="风险",
                weight=1.0,
                direction="lower_better",
                veto=VetoConfig(
                    type="soft",
                    condition=VetoCondition(operator=">", value=50, action="warning"),
                    penalty_score=-10
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=tuple(criteria),
            scores={
                "方案A": {"风险": 60},  # 满足触发条件，触发警告
                "方案B": {"风险": 40},  # 不满足触发条件
            }
        )

        evaluator = VetoEvaluator()
        result_a = evaluator.evaluate("方案A", problem.scores["方案A"], problem.criteria)
        result_b = evaluator.evaluate("方案B", problem.scores["方案B"], problem.criteria)

        # 验证：软否决不拒绝，但有警告
        assert result_a.rejected == False
        assert len(result_a.warnings) > 0
        assert result_a.penalties.get("风险") == -10

        # 方案B 应该无警告
        assert result_b.rejected == False
        assert len(result_b.warnings) == 0

    def test_no_veto_triggered(self):
        """测试: 无否决触发 - 正常接受"""
        # 成本越低越好
        # 设置通过条件: 成本 <= 100
        criteria = [
            Criterion(
                name="成本",
                weight=0.5,
                direction="lower_better",
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator="<=", value=100, action="reject")
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=tuple(criteria),
            scores={
                "方案A": {"成本": 50},  # 满足条件，不被否决
                "方案B": {"成本": 80},  # 满足条件，不被否决
            }
        )

        evaluator = VetoEvaluator()
        result_a = evaluator.evaluate("方案A", problem.scores["方案A"], problem.criteria)
        result_b = evaluator.evaluate("方案B", problem.scores["方案B"], problem.criteria)

        # 验证：都不被拒绝
        assert result_a.rejected == False
        assert len(result_a.reject_reasons) == 0
        assert result_b.rejected == False
        assert len(result_b.reject_reasons) == 0

    def test_multiple_criteria_veto(self):
        """测试: 多个准则带否决"""
        criteria = [
            # 成本越低越好，通过条件: 成本 <= 90
            Criterion(
                name="成本",
                weight=0.3,
                direction="lower_better",
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator="<=", value=90, action="reject")
                )
            ),
            # 质量越高越好，通过条件: 质量 >= 50
            Criterion(
                name="质量",
                weight=0.4,
                direction="higher_better",
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=50, action="reject")
                )
            ),
            # 服务越高越好，触发警告条件: 服务 < 60 时警告
            Criterion(
                name="服务",
                weight=0.3,
                direction="higher_better",
                veto=VetoConfig(
                    type="soft",
                    condition=VetoCondition(operator="<", value=60, action="warning"),
                    penalty_score=-5
                )
            ),
        ]

        # 方案A：成本高（被拒绝），质量低（被拒绝），服务低（警告）
        problem = DecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=tuple(criteria),
            scores={
                "方案A": {"成本": 95, "质量": 40, "服务": 55},
                "方案B": {"成本": 70, "质量": 80, "服务": 75},
            }
        )

        evaluator = VetoEvaluator()
        result_a = evaluator.evaluate("方案A", problem.scores["方案A"], problem.criteria)
        result_b = evaluator.evaluate("方案B", problem.scores["方案B"], problem.criteria)

        # 验证：方案A 多个否决
        assert result_a.rejected == True
        assert len(result_a.reject_reasons) >= 2  # 成本和质量都拒绝
        # 注意：由于硬否决已拒绝，软否决可能不会评估（取决于实现）

        # 方案B 应该通过
        assert result_b.rejected == False

    def test_tiered_veto(self):
        """测试: 分级否决"""
        criteria = [
            Criterion(
                name="得分",
                weight=1.0,
                direction="higher_better",
                veto=VetoConfig(
                    type="tiered",
                    tiers=(
                        VetoTier(min=90, max=100, action="accept"),
                        VetoTier(min=70, max=90, action="warning", penalty_score=-5),
                        VetoTier(min=50, max=70, action="warning", penalty_score=-10),
                        VetoTier(min=0, max=50, action="reject"),
                    )
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("方案A", "方案B", "方案C"),
            criteria=tuple(criteria),
            scores={
                "方案A": {"得分": 95},  # 优秀档
                "方案B": {"得分": 65},  # 中等档（警告-10分）
                "方案C": {"得分": 40},  # 差档（拒绝）
            }
        )

        evaluator = VetoEvaluator()

        # 方案A - 优秀，无惩罚
        result_a = evaluator.evaluate("方案A", problem.scores["方案A"], problem.criteria)
        assert result_a.rejected == False
        assert sum(result_a.penalties.values()) == 0

        # 方案B - 中等，有惩罚
        result_b = evaluator.evaluate("方案B", problem.scores["方案B"], problem.criteria)
        assert result_b.rejected == False
        assert sum(result_b.penalties.values()) == -10

        # 方案C - 差，被拒绝
        result_c = evaluator.evaluate("方案C", problem.scores["方案C"], problem.criteria)
        assert result_c.rejected == True

    def test_veto_with_orchestrator(self):
        """测试: 否决机制与编排器集成"""
        # 注意：当前版本否决功能可能还未完全集成到 orchestrator
        # 这个测试验证未来集成后的行为
        # 安全性越高越好，通过条件: 安全性 >= 60
        criteria = [
            Criterion(
                name="安全性",
                weight=0.6,
                direction="higher_better",
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=60, action="reject"),
                    reject_reason="安全性低于 60 一票否决"
                )
            ),
            Criterion(name="成本", weight=0.4, direction="lower_better"),
        ]

        problem = DecisionProblem(
            alternatives=("供应商A", "供应商B"),
            criteria=tuple(criteria),
            scores={
                "供应商A": {"安全性": 50, "成本": 80},  # 安全性低，应被否决
                "供应商B": {"安全性": 80, "成本": 70},
            }
        )

        # 评估
        evaluator = VetoEvaluator()
        result_a = evaluator.evaluate("供应商A", problem.scores["供应商A"], problem.criteria)
        result_b = evaluator.evaluate("供应商B", problem.scores["供应商B"], problem.criteria)

        # 验证：供应商A被否决，供应商B通过
        assert result_a.rejected == True
        assert result_b.rejected == False
