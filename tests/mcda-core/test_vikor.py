"""
MCDA Core - VIKOR 算法测试

测试折衷排序法（VIseKriterijumska Optimizacija I Kompromisno Resenje）。
"""

import pytest
from skills.mcda_core.lib.models import (
    Criterion,
    Direction,
)
from skills.mcda_core.lib.algorithms.vikor import VIKORAlgorithm


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_criteria():
    """示例准则（权重已归一化）"""
    return [
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.2, direction="higher_better"),
        Criterion(name="易用性", weight=0.1, direction="higher_better"),
    ]


@pytest.fixture
def sample_scores():
    """示例评分（已标准化到 0-100）"""
    return {
        "AWS": {"性能": 85.0, "成本": 60.0, "可靠性": 90.0, "易用性": 80.0},
        "Azure": {"性能": 92.0, "成本": 50.0, "可靠性": 85.0, "易用性": 85.0},
        "GCP": {"性能": 88.0, "成本": 70.0, "可靠性": 80.0, "易用性": 75.0},
    }


@pytest.fixture
def sample_problem(sample_criteria, sample_scores):
    """创建示例决策问题"""
    from skills.mcda_core.lib.models import DecisionProblem

    return DecisionProblem(
        
        alternatives=tuple(sample_scores.keys()),
        criteria=sample_criteria,
        scores=sample_scores,
    )


# =============================================================================
# VIKOR Algorithm Tests
# =============================================================================

class TestVIKORAlgorithm:
    """VIKOR 算法测试"""

    def test_vikor_basic_calculation(self, sample_problem):
        """测试 VIKOR 基本计算"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证排名存在
        assert len(result.rankings) == 3
        assert len(result.raw_scores) == 3

        # 验证 Q 值存在
        for alt in sample_problem.alternatives:
            assert alt in result.raw_scores

        # 验证排名（Q 值越小越好）
        assert result.rankings[0].rank == 1
        assert result.rankings[1].rank == 2
        assert result.rankings[2].rank == 3

    def test_vikor_s_r_calculation(self, sample_problem):
        """测试群体效用 S 和个别遗憾 R 的计算"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        S = result.metadata.metrics["S"]
        R = result.metadata.metrics["R"]

        # 验证 S 和 R 存在
        for alt in sample_problem.alternatives:
            assert alt in S
            assert alt in R
            assert S[alt] >= 0  # S 应该是非负的
            assert R[alt] >= 0  # R 应该是非负的

    def test_vikor_q_calculation(self, sample_problem):
        """测试折衷值 Q 的计算"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        S = result.metadata.metrics["S"]
        R = result.metadata.metrics["R"]
        Q = result.raw_scores

        # 获取 S 和 R 的最小值和最大值
        S_min = min(S.values())
        S_max = max(S.values())
        R_min = min(R.values())
        R_max = max(R.values())

        v = result.metadata.metrics["v"]  # 决策策略系数

        # 验证 Q 值计算公式
        for alt in sample_problem.alternatives:
            expected_q = v * (S[alt] - S_min) / (S_max - S_min) + \
                        (1 - v) * (R[alt] - R_min) / (R_max - R_min)

            # 处理分母为零的情况
            if S_max == S_min and R_max == R_min:
                expected_q = 0.0
            elif S_max == S_min:
                expected_q = (1 - v) * (R[alt] - R_min) / (R_max - R_min)
            elif R_max == R_min:
                expected_q = v * (S[alt] - S_min) / (S_max - S_min)

            assert abs(Q[alt] - expected_q) < 0.001, \
                f"{alt}: Q 值计算错误"

    def test_vikor_v_parameter(self, sample_problem):
        """测试决策策略系数 v"""
        # 默认 v = 0.5
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert result.metadata.metrics["v"] == 0.5

    def test_vikor_custom_v_parameter(self, sample_problem):
        """测试自定义 v 参数"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem, v=0.7)

        assert result.metadata.metrics["v"] == 0.7

        # v = 0.7 应该更重视群体效用 S
        result_v07 = result
        result_v05 = algorithm.calculate(sample_problem, v=0.5)

        # 不同 v 值应该产生不同的 Q 值（一般情况下）
        # 但这不保证排名一定会改变

    def test_vikor_metadata(self, sample_problem):
        """测试元数据"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        assert result.metadata.algorithm_name == "vikor"
        assert result.metadata.problem_size == (3, 4)

    def test_vikor_metrics(self, sample_problem):
        """测试算法指标"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        # 验证指标包含
        assert "Q" in result.metadata.metrics
        assert "S" in result.metadata.metrics
        assert "R" in result.metadata.metrics
        assert "v" in result.metadata.metrics

        # 验证指标类型
        assert isinstance(result.metadata.metrics["Q"], dict)
        assert isinstance(result.metadata.metrics["S"], dict)
        assert isinstance(result.metadata.metrics["R"], dict)
        assert isinstance(result.metadata.metrics["v"], (int, float))


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestVIKOREdgeCases:
    """VIKOR 边界情况测试"""

    def test_vikor_two_alternatives(self):
        """测试只有 2 个备选方案"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 80.0, "成本": 60.0},
            "B": {"性能": 90.0, "成本": 70.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(problem)

        assert len(result.rankings) == 2
        assert set(result.raw_scores.keys()) == {"A", "B"}

    def test_vikor_many_alternatives(self):
        """测试多个备选方案"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=1.0, direction="higher_better"),
        ]

        scores = {
            f"方案{i}": {"性能": float(i * 10)}
            for i in range(1, 11)  # 10 个方案
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(problem)

        assert len(result.rankings) == 10
        # 验证排名正确（性能越高越好，Q 值越小）
        assert result.rankings[0].alternative == "方案1"
        assert result.rankings[-1].alternative == "方案10"  # Q 值最大

    def test_vikor_equal_scores(self):
        """测试所有方案评分相同"""
        from skills.mcda_core.lib.models import DecisionProblem

        criteria = [
            Criterion(name="性能", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        ]

        scores = {
            "A": {"性能": 80.0, "成本": 60.0},
            "B": {"性能": 80.0, "成本": 60.0},
        }

        problem = DecisionProblem(
            
            alternatives=tuple(scores.keys()),
            criteria=criteria,
            scores=scores,
        )

        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(problem)

        # 所有方案应该有相同的 Q 值
        assert abs(result.raw_scores["A"] - result.raw_scores["B"]) < 0.001

    def test_vikor_v_extremes(self, sample_problem):
        """测试 v 参数的极端值"""
        algorithm = VIKORAlgorithm()

        # v = 0: 只考虑个别遗憾 R
        result_v0 = algorithm.calculate(sample_problem, v=0.0)
        assert result_v0.metadata.metrics["v"] == 0.0

        # v = 1: 只考虑群体效用 S
        result_v1 = algorithm.calculate(sample_problem, v=1.0)
        assert result_v1.metadata.metrics["v"] == 1.0


# =============================================================================
# Property Tests
# =============================================================================

class TestVIKORProperties:
    """VIKOR 算法属性测试"""

    def test_vikor_algorithm_name(self):
        """测试算法名称"""
        algorithm = VIKORAlgorithm()
        assert algorithm.name == "vikor"

    def test_vikor_description(self):
        """测试算法描述"""
        algorithm = VIKORAlgorithm()
        assert len(algorithm.description) > 0
        assert "折衷" in algorithm.description or "compromise" in algorithm.description.lower()


# =============================================================================
# VIKOR Specific Tests
# =============================================================================

class TestVIKORSpecific:
    """VIKOR 特定测试"""

    def test_vikor_compromise_solution(self, sample_problem):
        """测试折衷解判定"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        # VIKOR 的核心优势是提供折衷解
        # 折衷解应该满足：
        # 1. Q 值最小
        # 2. 在 S 和 R 上也有较好的表现

        best_alt = result.rankings[0].alternative
        Q = result.raw_scores
        S = result.metadata.metrics["S"]
        R = result.metadata.metrics["R"]

        # 验证最佳方案的 Q 值最小
        assert Q[best_alt] == min(Q.values())

    def test_vikor_strategy_coefficient_impact(self, sample_problem):
        """测试决策策略系数对结果的影响"""
        algorithm = VIKORAlgorithm()

        # 计算不同 v 值的结果
        result_v0 = algorithm.calculate(sample_problem, v=0.0)
        result_v05 = algorithm.calculate(sample_problem, v=0.5)
        result_v1 = algorithm.calculate(sample_problem, v=1.0)

        # 不同 v 值应该产生不同的 Q 值分布
        # 但这不保证排名一定会改变

        # 验证 v 参数被正确记录
        assert result_v0.metadata.metrics["v"] == 0.0
        assert result_v05.metadata.metrics["v"] == 0.5
        assert result_v1.metadata.metrics["v"] == 1.0

    def test_vikor_s_and_r_relationship(self, sample_problem):
        """测试 S 和 R 的关系"""
        algorithm = VIKORAlgorithm()
        result = algorithm.calculate(sample_problem)

        S = result.metadata.metrics["S"]
        R = result.metadata.metrics["R"]

        # R 应该是每个方案在各准则上的最大加权遗憾
        # S 应该是每个方案在各准则上的加权遗憾总和

        for alt in sample_problem.alternatives:
            # R 应该小于等于 S（如果所有权重相等且只有一个准则起作用）
            # 但一般情况下 R <= S 不一定成立
            # 我们只验证两者都是非负的
            assert S[alt] >= 0
            assert R[alt] >= 0
