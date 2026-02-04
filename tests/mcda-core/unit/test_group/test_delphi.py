"""
MCDA Core - 德尔菲法单元测试

测试群决策德尔菲法功能。
"""

import pytest

from mcda_core.group.delphi import (
    DelphiRound,
    DelphiProcess,
)
from mcda_core.group.models import (
    DecisionMaker,
    GroupDecisionProblem,
)
from mcda_core.models import Criterion


# =============================================================================
# DelphiRound 数据模型测试 (2 个)
# =============================================================================

class TestDelphiRound:
    """测试德尔菲法轮次记录"""

    def test_create_valid_round(self):
        """测试创建有效的轮次记录"""
        scores = {
            "DM1": {"AWS": {"成本": 80.0, "质量": 90.0}},
            "DM2": {"AWS": {"成本": 85.0, "质量": 85.0}},
        }
        statistics = {
            "AWS": {
                "成本": {"mean": 82.5, "median": 82.5, "std": 2.5, "q1": 81.25, "q3": 83.75},
                "质量": {"mean": 87.5, "median": 87.5, "std": 2.5, "q1": 86.25, "q3": 88.75},
            }
        }

        round_record = DelphiRound(
            round_number=1,
            scores=scores,
            statistics=statistics,
            convergence_score=0.95
        )

        assert round_record.round_number == 1
        assert round_record.scores == scores
        assert round_record.statistics == statistics
        assert round_record.convergence_score == 0.95

    def test_round_immutability(self):
        """测试轮次记录不可变性"""
        scores = {
            "DM1": {"AWS": {"成本": 80.0}},
            "DM2": {"AWS": {"成本": 85.0}},
        }
        statistics = {
            "AWS": {"成本": {"mean": 82.5, "median": 82.5, "std": 2.5, "q1": 81.25, "q3": 83.75}}
        }

        round_record = DelphiRound(
            round_number=1,
            scores=scores,
            statistics=statistics,
            convergence_score=0.95
        )

        # 尝试修改属性应该抛出异常
        with pytest.raises(Exception):  # FrozenInstanceError
            round_record.round_number = 2

        with pytest.raises(Exception):
            round_record.convergence_score = 1.0


# =============================================================================
# DelphiProcess 管理器测试 (3 个)
# =============================================================================

class TestDelphiProcess:
    """测试德尔菲法过程管理器"""

    @pytest.fixture
    def sample_problem(self):
        """创建示例群决策问题"""
        criteria = (
            Criterion(name="成本", weight=0.5, direction="lower_better"),
            Criterion(name="质量", weight=0.5, direction="higher_better"),
        )
        decision_makers = (
            DecisionMaker(id="DM1", name="张三"),
            DecisionMaker(id="DM2", name="李四"),
        )
        individual_scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 85.0},
                "Azure": {"成本": 75.0, "质量": 90.0},
            },
        }

        return GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=individual_scores
        )

    def test_create_delphi_process(self, sample_problem):
        """测试创建德尔菲法过程"""
        process = DelphiProcess(
            initial_problem=sample_problem,
            max_rounds=3,
            convergence_threshold=0.05
        )

        assert process.initial_problem == sample_problem
        assert process.max_rounds == 3
        assert process.convergence_threshold == 0.05
        assert process.rounds == ()

    def test_add_round(self, sample_problem):
        """测试添加新轮次"""
        process = DelphiProcess(
            initial_problem=sample_problem,
            max_rounds=3,
            convergence_threshold=0.05
        )

        new_scores = {
            "DM1": {
                "AWS": {"成本": 82.0, "质量": 88.0},
                "Azure": {"成本": 72.0, "质量": 87.0},
            },
            "DM2": {
                "AWS": {"成本": 83.0, "质量": 86.0},
                "Azure": {"成本": 73.0, "质量": 88.0},
            },
        }

        round_record = process.add_round(new_scores)

        assert isinstance(round_record, DelphiRound)
        assert round_record.round_number == 1
        assert len(process.rounds) == 1
        assert process.rounds[0] == round_record

    def test_get_rounds_returns_immutable_tuple(self, sample_problem):
        """测试获取轮次列表返回不可变元组"""
        process = DelphiProcess(
            initial_problem=sample_problem,
            max_rounds=3,
            convergence_threshold=0.05
        )

        new_scores = {
            "DM1": {"AWS": {"成本": 80.0, "质量": 90.0}},
            "DM2": {"AWS": {"成本": 85.0, "质量": 85.0}},
        }

        process.add_round(new_scores)
        rounds = process.rounds

        # 返回的应该是元组（不可变）
        assert isinstance(rounds, tuple)
        assert len(rounds) == 1


# =============================================================================
# 统计摘要测试 (2 个)
# =============================================================================

class TestStatisticsSummary:
    """测试统计摘要生成"""

    @pytest.fixture
    def sample_process(self):
        """创建示例德尔菲法过程"""
        criteria = (
            Criterion(name="成本", weight=0.5, direction="lower_better"),
            Criterion(name="质量", weight=0.5, direction="higher_better"),
        )
        decision_makers = (
            DecisionMaker(id="DM1", name="张三"),
            DecisionMaker(id="DM2", name="李四"),
            DecisionMaker(id="DM3", name="王五"),
        )
        individual_scores = {
            "DM1": {
                "AWS": {"成本": 80.0, "质量": 90.0},
                "Azure": {"成本": 70.0, "质量": 85.0},
            },
            "DM2": {
                "AWS": {"成本": 85.0, "质量": 85.0},
                "Azure": {"成本": 75.0, "质量": 90.0},
            },
            "DM3": {
                "AWS": {"成本": 75.0, "质量": 95.0},
                "Azure": {"成本": 65.0, "质量": 80.0},
            },
        }

        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=individual_scores
        )

        return DelphiProcess(initial_problem=problem)

    def test_compute_statistics_summary(self, sample_process):
        """测试计算统计摘要（均值、中位数、标准差、四分位数）"""
        scores = {
            "DM1": {"AWS": {"成本": 80.0, "质量": 90.0}},
            "DM2": {"AWS": {"成本": 85.0, "质量": 85.0}},
            "DM3": {"AWS": {"成本": 75.0, "质量": 95.0}},
        }

        stats = sample_process.compute_statistics(scores)

        # 成本: [75, 80, 85] -> mean=80, median=80, std=5.0 (样本标准差)
        assert "AWS" in stats
        assert "成本" in stats["AWS"]
        cost_stats = stats["AWS"]["成本"]
        assert cost_stats["mean"] == pytest.approx(80.0)
        assert cost_stats["median"] == 80.0
        assert cost_stats["std"] == pytest.approx(5.0)  # 样本标准差: sqrt(50/2) = 5
        assert "q1" in cost_stats
        assert "q3" in cost_stats

        # 质量: [85, 90, 95] -> mean=90, median=90, std=5.0
        quality_stats = stats["AWS"]["质量"]
        assert quality_stats["mean"] == pytest.approx(90.0)
        assert quality_stats["median"] == 90.0

    def test_compute_statistics_empty_data(self, sample_process):
        """测试处理空数据"""
        stats = sample_process.compute_statistics({})

        assert stats == {}


# =============================================================================
# 收敛检查测试 (1 个)
# =============================================================================

class TestConvergenceCheck:
    """测试收敛检查"""

    @pytest.fixture
    def sample_process(self):
        """创建示例德尔菲法过程"""
        criteria = (
            Criterion(name="成本", weight=1.0, direction="lower_better"),
        )
        decision_makers = (
            DecisionMaker(id="DM1", name="张三"),
            DecisionMaker(id="DM2", name="李四"),
        )
        individual_scores = {
            "DM1": {"AWS": {"成本": 80.0}, "Azure": {"成本": 70.0}},
            "DM2": {"AWS": {"成本": 85.0}, "Azure": {"成本": 75.0}},
        }

        problem = GroupDecisionProblem(
            alternatives=("AWS", "Azure"),
            criteria=criteria,
            decision_makers=decision_makers,
            individual_scores=individual_scores
        )

        return DelphiProcess(initial_problem=problem, convergence_threshold=0.05)

    def test_check_convergence_below_threshold(self, sample_process):
        """测试评分变化小于阈值时判定为收敛"""
        # 第一轮评分
        scores1 = {
            "DM1": {"AWS": {"成本": 80.0}, "Azure": {"成本": 70.0}},
            "DM2": {"AWS": {"成本": 85.0}, "Azure": {"成本": 75.0}},
        }
        round1 = sample_process.add_round(scores1)

        # 第二轮评分变化很小（小于阈值 0.05）
        scores2 = {
            "DM1": {"AWS": {"成本": 80.02}, "Azure": {"成本": 70.02}},  # 变化 0.02
            "DM2": {"AWS": {"成本": 85.02}, "Azure": {"成本": 75.02}},  # 变化 0.02
        }

        convergence_score = sample_process._compute_convergence_score(scores2)
        assert convergence_score < 0.05  # 应该收敛

    def test_check_convergence_above_threshold(self, sample_process):
        """测试评分变化大于阈值时未收敛"""
        # 第一轮评分
        scores1 = {
            "DM1": {"AWS": {"成本": 80.0}, "Azure": {"成本": 70.0}},
            "DM2": {"AWS": {"成本": 85.0}, "Azure": {"成本": 75.0}},
        }
        sample_process.add_round(scores1)

        # 第二轮评分变化较大
        scores2 = {
            "DM1": {"AWS": {"成本": 70.0}, "Azure": {"成本": 60.0}},  # 变化 10
            "DM2": {"AWS": {"成本": 75.0}, "Azure": {"成本": 65.0}},  # 变化 10
        }

        convergence_score = sample_process._compute_convergence_score(scores2)
        assert convergence_score > 0.05  # 不应该收敛

    def test_check_convergence_no_previous_round(self, sample_process):
        """测试没有上一轮数据时收敛分数为 1.0（完全未收敛）"""
        scores = {
            "DM1": {"AWS": {"成本": 80.0}, "Azure": {"成本": 70.0}},
            "DM2": {"AWS": {"成本": 85.0}, "Azure": {"成本": 75.0}},
        }

        # 没有上一轮，应该返回 1.0（表示完全未收敛）
        convergence_score = sample_process._compute_convergence_score(scores)
        assert convergence_score == 1.0
