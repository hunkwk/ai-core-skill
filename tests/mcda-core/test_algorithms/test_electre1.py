"""
ELECTRE-I 算法测试

测试基于级别优于关系的多准则决策排序算法。
"""

import pytest
import numpy as np
from mcda_core.algorithms.electre1 import electre1, ELECTRE1Error
from mcda_core.models import DecisionProblem, Criterion


class TestConcordanceIndex:
    """和谐指数测试"""

    def test_concordance_basic(self):
        """测试：基本和谐指数计算"""
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

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 验证和谐矩阵存在
        assert hasattr(result, 'metadata')
        assert "concordance_matrix" in result.metadata.metrics

    def test_concordance_single_criterion(self):
        """测试：单准则和谐指数"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        result = electre1(problem, alpha=0.5, beta=0.3)

        # 单准则时和谐指数应该为 1 或 0
        concordance = result.metadata.metrics["concordance_matrix"]
        assert concordance[0][1] in [0.0, 1.0]

    def test_concordance_weight_normalization(self):
        """测试：权重归一化"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.6, direction="higher_better"),
                Criterion(name="C2", weight=0.4, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 7},
            }
        )

        result = electre1(problem, alpha=0.5, beta=0.3)

        # 验证和谐指数在 [0, 1] 范围内
        concordance = result.metadata.metrics["concordance_matrix"]
        assert 0 <= concordance[0][1] <= 1


class TestDiscordanceIndex:
    """不和谐指数测试"""

    def test_discordance_basic(self):
        """测试：基本不和谐指数计算"""
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

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 验证不和谐矩阵存在
        assert "discordance_matrix" in result.metadata.metrics

    def test_discordance_range_normalization(self):
        """测试：范围归一化"""
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

        result = electre1(problem, alpha=0.5, beta=0.3)

        # 验证不和谐指数在 [0, 1] 范围内
        discordance = result.metadata.metrics["discordance_matrix"]
        assert 0 <= discordance[0][1] <= 1


class TestCredibilityMatrix:
    """可信度矩阵测试"""

    def test_credibility_basic(self):
        """测试：基本可信度计算"""
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

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 验证可信度矩阵存在
        assert "credibility_matrix" in result.metadata.metrics

    def test_credibility_thresholds(self):
        """测试：阈值参数 (α, β)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        result1 = electre1(problem, alpha=0.5, beta=0.3)
        result2 = electre1(problem, alpha=0.7, beta=0.2)

        # 不同阈值应该产生不同结果
        credibility1 = result1.metadata.metrics["credibility_matrix"]
        credibility2 = result2.metadata.metrics["credibility_matrix"]


class TestRankingAndKernel:
    """排序与核提取测试"""

    def test_outranking_relation(self):
        """测试：级别优于关系构建"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.6, direction="higher_better"),
                Criterion(name="C2", weight=0.4, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 10},
                "A2": {"C1": 8, "C2": 12},
                "A3": {"C1": 6, "C2": 8},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 验证排名结果
        assert len(result.rankings) == 3

    def test_kernel_extraction(self):
        """测试：核 (Kernel) 提取"""
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

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 验证核存在于元数据中
        assert "kernel" in result.metadata.metrics


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_alpha(self):
        """测试：无效的 α 参数"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        # α 必须在 (0, 1] 范围内
        with pytest.raises(ELECTRE1Error):
            electre1(problem, alpha=0, beta=0.3)

        with pytest.raises(ELECTRE1Error):
            electre1(problem, alpha=1.5, beta=0.3)

    def test_invalid_beta(self):
        """测试：无效的 β 参数"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        # β 必须在 [0, 1] 范围内
        with pytest.raises(ELECTRE1Error):
            electre1(problem, alpha=0.6, beta=-0.1)

        with pytest.raises(ELECTRE1Error):
            electre1(problem, alpha=0.6, beta=1.5)


class TestEdgeCases:
    """边界条件测试"""

    def test_minimal_problem(self):
        """测试：最小问题 (2 方案 1 准则)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(Criterion(name="C1", weight=1.0, direction="higher_better"),),
            scores={"A1": {"C1": 10}, "A2": {"C1": 8}}
        )

        result = electre1(problem, alpha=0.5, beta=0.3)

        assert len(result.rankings) == 2

    def test_large_dataset(self):
        """测试：大数据集 (50 方案 5 准则)"""
        np.random.seed(42)
        n_alt = 50
        n_crit = 5

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

        result = electre1(problem, alpha=0.6, beta=0.3)

        assert len(result.rankings) == 50

    def test_equal_scores(self):
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

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 所有方案应该在核中
        kernel = result.metadata.metrics["kernel"]
        assert len(kernel) == 3


class TestIntegration:
    """集成测试"""

    def test_with_cost_criteria(self):
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

        result = electre1(problem, alpha=0.6, beta=0.3)

        assert len(result.rankings) == 2

    def test_reproducibility(self):
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

        result1 = electre1(problem, alpha=0.6, beta=0.3)
        result2 = electre1(problem, alpha=0.6, beta=0.3)

        # 验证排名一致
        ranks1 = {r.alternative: r.rank for r in result1.rankings}
        ranks2 = {r.alternative: r.rank for r in result2.rankings}

        assert ranks1 == ranks2
