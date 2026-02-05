"""
ConstraintService 服务层测试

测试一票否决机制的服务层功能：
- filter_problem(): 过滤决策问题
- apply_penalties(): 应用惩罚分数
- get_constraint_metadata(): 获取元数据
"""

import pytest

from mcda_core.services.constraint_service import ConstraintService
from mcda_core.constraints.models import (
    VetoCondition,
    VetoConfig,
    VetoTier,
)
from mcda_core.models import Criterion, DecisionProblem


class MockCriterion:
    """模拟 Criterion 类（带 veto 支持）"""
    def __init__(self, name, weight=1.0, direction='higher_better', veto=None):
        self.name = name
        self.weight = weight
        self.direction = direction
        self.veto = veto


class TestConstraintService:
    """测试 ConstraintService 服务层"""

    def test_filter_problem_no_veto_rules(self):
        """测试过滤：无否决规则，原样返回"""
        criteria = [
            MockCriterion(name="成本", weight=0.5, direction='lower_better'),
            MockCriterion(name="质量", weight=0.5, direction='higher_better'),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002", "A003"),
            criteria=criteria,
            scores={
                "A001": {"成本": 50, "质量": 80},
                "A002": {"成本": 60, "质量": 90},
                "A003": {"成本": 40, "质量": 85},
            }
        )

        service = ConstraintService()
        filtered_problem, veto_results = service.filter_problem(problem)

        # 无否决规则，应该原样返回
        assert len(filtered_problem.alternatives) == 3
        assert len(veto_results) == 3
        assert all(not result.rejected for result in veto_results.values())

    def test_filter_problem_with_hard_veto(self):
        """测试过滤：过滤掉被硬否决的方案"""
        criteria = [
            MockCriterion(
                name="资质评分",
                weight=1.0,
                direction='higher_better',
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=60, action="reject")
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002", "A003"),
            criteria=criteria,
            scores={
                "A001": {"资质评分": 80},
                "A002": {"资质评分": 40},  # 低于 60，应该被拒绝
                "A003": {"资质评分": 70},
            }
        )

        service = ConstraintService()
        filtered_problem, veto_results = service.filter_problem(problem)

        # 应该过滤掉 A002
        assert len(filtered_problem.alternatives) == 2
        assert "A001" in filtered_problem.alternatives
        assert "A003" in filtered_problem.alternatives
        assert "A002" not in filtered_problem.alternatives

        # A002 应该被标记为拒绝
        assert veto_results["A002"].rejected is True

    def test_filter_problem_all_rejected(self):
        """测试过滤：所有方案被拒绝，返回原问题"""
        criteria = [
            MockCriterion(
                name="资质评分",
                weight=1.0,
                direction='higher_better',
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=90, action="reject")
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002"),
            criteria=criteria,
            scores={
                "A001": {"资质评分": 50},
                "A002": {"资质评分": 60},
            }
        )

        service = ConstraintService()
        filtered_problem, veto_results = service.filter_problem(problem)

        # 所有方案被拒绝，返回原问题
        assert len(filtered_problem.alternatives) == 2
        assert all(result.rejected for result in veto_results.values())

    def test_filter_problem_partial_rejected(self):
        """测试过滤：部分方案被拒绝"""
        criteria = [
            MockCriterion(
                name="财务风险",
                weight=1.0,
                direction='lower_better',
                veto=VetoConfig(
                    type="tiered",
                    tiers=(
                        VetoTier(min=0, max=60, action="accept"),
                        VetoTier(min=60, max=100, action="reject"),
                    )
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002", "A003", "A004"),
            criteria=criteria,
            scores={
                "A001": {"财务风险": 50},  # 接受
                "A002": {"财务风险": 70},  # 拒绝
                "A003": {"财务风险": 55},  # 接受
                "A004": {"财务风险": 80},  # 拒绝
            }
        )

        service = ConstraintService()
        filtered_problem, veto_results = service.filter_problem(problem)

        # 应该只保留 A001 和 A003
        assert len(filtered_problem.alternatives) == 2
        assert "A001" in filtered_problem.alternatives
        assert "A003" in filtered_problem.alternatives
        assert "A002" not in filtered_problem.alternatives
        assert "A004" not in filtered_problem.alternatives

    def test_apply_penalties_to_scores(self):
        """测试应用惩罚分数"""
        criteria = [
            MockCriterion(
                name="财务风险",
                weight=1.0,
                direction='lower_better',
                veto=VetoConfig(
                    type="soft",
                    condition=VetoCondition(operator=">", value=60, action="warning"),
                    penalty_score=-30
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002"),
            criteria=criteria,
            scores={
                "A001": {"财务风险": 50},  # 不触发惩罚
                "A002": {"财务风险": 70},  # 触发惩罚 -30
            }
        )

        service = ConstraintService()
        adjusted_problem = service.apply_penalties(problem)

        # A002 应该被扣分
        # 注意：这里假设 apply_penalties 会添加一个 "penalty" 准则来记录惩罚
        assert "penalty" in adjusted_problem.scores["A002"]
        assert adjusted_problem.scores["A002"]["penalty"] == -30

    def test_apply_penalties_with_soft_veto(self):
        """测试应用软否决惩罚"""
        criteria = [
            MockCriterion(
                name="财务风险",
                weight=0.5,
                direction='lower_better',
                veto=VetoConfig(
                    type="soft",
                    condition=VetoCondition(operator=">", value=60, action="warning"),
                    penalty_score=-30
                )
            ),
            MockCriterion(
                name="技术风险",
                weight=0.5,
                direction='lower_better',
                veto=VetoConfig(
                    type="soft",
                    condition=VetoCondition(operator=">", value=50, action="warning"),
                    penalty_score=-20
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002"),
            criteria=criteria,
            scores={
                "A001": {"财务风险": 70, "技术风险": 60},  # 两个都触发: -30 + -20 = -50
                "A002": {"财务风险": 50, "技术风险": 40},  # 都不触发
            }
        )

        service = ConstraintService()
        adjusted_problem = service.apply_penalties(problem)

        # A001 累计惩罚 -50
        assert adjusted_problem.scores["A001"]["penalty"] == -50

        # A002 无惩罚
        assert "penalty" not in adjusted_problem.scores["A002"] or \
               adjusted_problem.scores["A002"].get("penalty", 0) == 0

    def test_get_constraint_metadata(self):
        """测试获取元数据"""
        criteria = [
            MockCriterion(
                name="资质评分",
                weight=1.0,
                direction='higher_better',
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=60, action="reject")
                )
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002", "A003", "A004", "A005"),
            criteria=criteria,
            scores={
                "A001": {"资质评分": 80},  # 接受
                "A002": {"资质评分": 40},  # 拒绝
                "A003": {"资质评分": 70},  # 接受
                "A004": {"资质评分": 50},  # 拒绝
                "A005": {"资质评分": 90},  # 接受
            }
        )

        service = ConstraintService()
        filtered_problem, veto_results = service.filter_problem(problem)
        metadata = service.get_constraint_metadata(problem, veto_results)

        # 验证元数据统计
        assert metadata.total_alternatives == 5
        assert metadata.rejected_count == 2
        assert metadata.accept_count == 3
        assert metadata.rejection_rate == 0.4  # 2/5

    def test_service_integration_with_algorithm(self):
        """测试服务与算法集成"""
        criteria = [
            MockCriterion(
                name="资质评分",
                weight=0.6,
                direction='higher_better',
                veto=VetoConfig(
                    type="hard",
                    condition=VetoCondition(operator=">=", value=60, action="reject")
                )
            ),
            MockCriterion(
                name="价格",
                weight=0.4,
                direction='lower_better',
                veto=None
            ),
        ]

        problem = DecisionProblem(
            alternatives=("A001", "A002", "A003"),
            criteria=criteria,
            scores={
                "A001": {"资质评分": 80, "价格": 50},
                "A002": {"资质评分": 40, "价格": 40},  # 被拒绝
                "A003": {"资质评分": 70, "价格": 60},
            }
        )

        service = ConstraintService()
        filtered_problem, veto_results = service.filter_problem(problem)

        # 过滤后只剩 2 个方案
        assert len(filtered_problem.alternatives) == 2

        # 过滤后的问题应该可以用于算法计算
        # 这里我们只验证数据结构正确，不实际调用算法
        assert "A002" not in filtered_problem.scores
        assert "A001" in filtered_problem.scores
        assert "A003" in filtered_problem.scores
