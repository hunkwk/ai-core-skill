"""
TODIM 算法测试

测试基于前景理论的多准则决策排序算法。
"""

import pytest
import numpy as np
from mcda_core.algorithms.todim import todim, TODIMError
from mcda_core.models import DecisionProblem, Criterion


class TestTODIMBasic:
    """基本功能测试"""

    def test_todim_basic(self):
        """测试：基本功能 - 3 方案 3 准则"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.4, direction="higher_better"),
                Criterion(name="C2", weight=0.3, direction="higher_better"),
                Criterion(name="C3", weight=0.3, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 8, "C3": 7},
                "A2": {"C1": 9, "C2": 6, "C3": 8},
                "A3": {"C1": 8, "C2": 7, "C3": 9},
            }
        )

        result = todim(problem, theta=1.0)

        # 验证返回结果
        assert hasattr(result, 'rankings')
        assert len(result.rankings) == 3

        # 验证排名完整性
        ranks = [r.rank for r in result.rankings]
        assert sorted(ranks) == [1, 2, 3]

        # 验证所有方案都有排名
        alternatives_in_result = {r.alternative for r in result.rankings}
        assert alternatives_in_result == {"A1", "A2", "A3"}

    def test_todim_theta_parameter(self):
        """测试：θ 参数 (衰减系数)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
                "A3": {"C1": 6, "C2": 9},
            }
        )

        result_theta1 = todim(problem, theta=1.0)
        result_theta2 = todim(problem, theta=2.5)

        # 不同 θ 应该产生相同或相似排名
        # (因为都使用相同的偏好结构)
        assert len(result_theta1.rankings) == len(result_theta2.rankings) == 3

        # 验证排名都是 1, 2, 3
        ranks1 = sorted([r.rank for r in result_theta1.rankings])
        ranks2 = sorted([r.rank for r in result_theta2.rankings])
        assert ranks1 == ranks2 == [1, 2, 3]

    def test_todim_with_cost_criteria(self):
        """测试：包含成本型准则"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="价格", weight=0.5, direction="lower_better"),
                Criterion(name="质量", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"价格": 100, "质量": 8},
                "A2": {"价格": 120, "质量": 9},
            }
        )

        result = todim(problem, theta=1.5)
        assert len(result.rankings) == 2

        # 验证排名
        ranks = sorted([r.rank for r in result.rankings])
        assert ranks == [1, 2]


class TestTODIMEdgeCases:
    """边界条件测试"""

    def test_todim_minimal_alternatives(self):
        """测试：最少 2 个方案"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        result = todim(problem, theta=1.0)
        assert len(result.rankings) == 2

    def test_todim_single_criterion(self):
        """测试：单准则"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 8},
                "A3": {"C1": 6}
            }
        )

        result = todim(problem, theta=1.0)
        assert len(result.rankings) == 3

        # 验证排名 (A1 > A2 > A3)
        a1_rank = next(r.rank for r in result.rankings if r.alternative == "A1")
        a2_rank = next(r.rank for r in result.rankings if r.alternative == "A2")
        a3_rank = next(r.rank for r in result.rankings if r.alternative == "A3")

        assert a1_rank < a2_rank < a3_rank

    def test_todim_large_dataset(self):
        """测试：大数据集 (100 方案 10 准则)"""
        np.random.seed(42)
        n_alt = 100
        n_crit = 10

        alternatives = [f"A{i}" for i in range(n_alt)]
        criteria = tuple([
            Criterion(name=f"C{j}", weight=1.0/n_crit, direction="higher_better")
            for j in range(n_crit)
        ])

        scores = {}
        for alt in alternatives:
            scores[alt] = {f"C{j}": np.random.rand() * 100 for j in range(n_crit)}

        problem = DecisionProblem(
            alternatives=tuple(alternatives),
            criteria=criteria,
            scores=scores
        )

        result = todim(problem, theta=1.0)
        assert len(result.rankings) == 100

    def test_todim_zero_weights(self):
        """测试：零权重准则"""
        # TODIM 应该忽略零权重准则
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
                Criterion(name="C2", weight=0.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 100},
                "A2": {"C1": 8, "C2": 0},
            }
        )

        result = todim(problem, theta=1.0)
        assert len(result.rankings) == 2

        # A1 应该优于 A2 (因为 C1 决定)
        a1_rank = next(r.rank for r in result.rankings if r.alternative == "A1")
        a2_rank = next(r.rank for r in result.rankings if r.alternative == "A2")
        assert a1_rank < a2_rank

    def test_todim_equal_scores(self):
        """测试：所有方案得分相同"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 10},
                "A2": {"C1": 10, "C2": 10},
                "A3": {"C1": 10, "C2": 10},
            }
        )

        result = todim(problem, theta=1.0)

        # 所有方案的全局优势度应该相等
        # 排名应该是 1, 1, 1 或 1, 2, 3 (但分数相同)
        scores = [r.score for r in result.rankings]
        assert all(abs(s - scores[0]) < 1e-10 for s in scores)


class TestTODIMMathematical:
    """数学验证测试"""

    def test_todim_relative_measure_positive(self):
        """测试：相对测度 φ 正值 (收益) 计算"""
        # 简单案例：手动计算
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 8},
            }
        )

        result = todim(problem, theta=1.0)

        # 手动验证：
        # φ_C1(A1, A2) = sqrt(1.0 * (10-8) / 1.0) = sqrt(2) ≈ 1.414
        # φ_C1(A2, A1) = -sqrt(1.0/1.0 * (8-10) / 1.0) = -sqrt(-2) → 应该用绝对值
        # = -sqrt(2) ≈ -1.414

        # 验证 A1 的全局优势度 > A2
        a1_score = next(r.score for r in result.rankings if r.alternative == "A1")
        a2_score = next(r.score for r in result.rankings if r.alternative == "A2")

        assert a1_score > a2_score

    def test_todim_relative_measure_negative(self):
        """测试：相对测度 φ 负值 (损失) 计算"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 8},
                "A2": {"C1": 10},
            }
        )

        result = todim(problem, theta=1.0)

        # A2 应该优于 A1
        a1_score = next(r.score for r in result.rankings if r.alternative == "A1")
        a2_score = next(r.score for r in result.rankings if r.alternative == "A2")

        assert a2_score > a1_score

    def test_todim_global_dominance_calculation(self):
        """测试：全局优势度 ξ 计算"""
        # ξ(A1) = Σ δ(A1, Aj) - Σ δ(Aj, A1)
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.6, direction="higher_better"),
                Criterion(name="C2", weight=0.4, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
                "A3": {"C1": 6, "C2": 9},
            }
        )

        result = todim(problem, theta=1.0)

        # 验证全局优势度的单调性
        scores = [r.score for r in result.rankings]
        sorted_scores = sorted(scores, reverse=True)

        # 验证排名分数是降序的
        assert scores == sorted_scores


class TestTODIMErrorHandling:
    """错误处理测试"""

    def test_todim_invalid_theta(self):
        """测试：无效的 θ 参数"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        # theta 必须 > 0
        with pytest.raises(TODIMError):
            todim(problem, theta=0)

        with pytest.raises(TODIMError):
            todim(problem, theta=-1.0)

    def test_todim_single_alternative_error(self):
        """测试：单方案 (需要至少 2 个)"""
        problem = DecisionProblem(
            alternatives=("A1",),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}}
        )

        with pytest.raises(TODIMError):
            todim(problem, theta=1.0)

    def test_todim_zero_all_weights(self):
        """测试：所有权重为零"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.0, direction="higher_better"),
                Criterion(name="C2", weight=0.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
            }
        )

        # 应该抛出错误或返回均匀权重
        with pytest.raises(TODIMError):
            todim(problem, theta=1.0)


class TestTODIMIntegration:
    """集成测试"""

    def test_todim_with_normalization(self):
        """测试：与标准化集成"""
        # TODIM 内部不需要标准化 (使用相对测度)
        # 但测试应该验证算法对不同尺度的处理
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.4, direction="higher_better"),
                Criterion(name="C2", weight=0.3, direction="higher_better"),
                Criterion(name="C3", weight=0.3, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 0.001, "C2": 50, "C3": 1000},
                "A2": {"C1": 0.002, "C2": 60, "C3": 900},
                "A3": {"C1": 0.003, "C2": 70, "C3": 800},
            }
        )

        result = todim(problem, theta=1.0)

        # 验证算法对不同尺度的处理
        assert len(result.rankings) == 3
        ranks = sorted([r.rank for r in result.rankings])
        assert ranks == [1, 2, 3]

    def test_todim_reproducibility(self):
        """测试：结果可重现"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
                "A3": {"C1": 6, "C2": 9},
            }
        )

        result1 = todim(problem, theta=1.0)
        result2 = todim(problem, theta=1.0)

        # 验证排名一致
        ranks1 = {r.alternative: r.rank for r in result1.rankings}
        ranks2 = {r.alternative: r.rank for r in result2.rankings}

        assert ranks1 == ranks2

        # 验证分数一致
        scores1 = {r.alternative: r.score for r in result1.rankings}
        scores2 = {r.alternative: r.score for r in result2.rankings}

        for alt in scores1:
            assert abs(scores1[alt] - scores2[alt]) < 1e-10


class TestTODIMProperties:
    """特性测试"""

    def test_todim_rank_properties(self):
        """测试：排名特性"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3", "A4"),
            criteria=(
                Criterion(name="C1", weight=0.6, direction="higher_better"),
                Criterion(name="C2", weight=0.4, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 10},
                "A2": {"C1": 8, "C2": 12},
                "A3": {"C1": 6, "C2": 8},
                "A4": {"C1": 4, "C2": 6},
            }
        )

        result = todim(problem, theta=1.0)

        # 验证排名连续性
        ranks = sorted([r.rank for r in result.rankings])
        assert ranks == list(range(1, 5))

        # 验证排名与分数的一致性
        sorted_by_rank = sorted(result.rankings, key=lambda x: x.rank)
        sorted_by_score = sorted(result.rankings, key=lambda x: x.score, reverse=True)

        assert sorted_by_rank == sorted_by_score

    def test_todim_theta_sensitivity(self):
        """测试：θ 参数敏感性"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
                "A3": {"C1": 6, "C2": 9},
            }
        )

        # 测试不同 θ 值
        theta_values = [0.5, 1.0, 1.5, 2.0, 2.5]
        results = [todim(problem, theta=theta) for theta in theta_values]

        # 所有结果应该都有排名
        for result in results:
            assert len(result.rankings) == 3
            ranks = sorted([r.rank for r in result.rankings])
            assert ranks == [1, 2, 3]

    def test_todim_metadata(self):
        """测试：元数据完整性"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
            }
        )

        theta = 1.5
        result = todim(problem, theta=theta)

        # 验证元数据
        assert hasattr(result, 'metadata')
        assert result.metadata.algorithm_name == "todim"
        assert "theta" in result.metadata.metrics
        assert result.metadata.metrics["theta"] == theta
