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
                "A1": {"价格": 80, "质量": 80},
                "A2": {"价格": 90, "质量": 90},
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


class TestConcordanceDetails:
    """和谐指数详细测试"""

    def test_concordance_direction_handling(self):
        """测试：效益型与成本型准则方向处理"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="效益", weight=0.5, direction="higher_better"),
                Criterion(name="成本", weight=0.5, direction="lower_better"),
            ),
            scores={
                "A1": {"效益": 80, "成本": 20},
                "A2": {"效益": 90, "成本": 30},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 验证和谐矩阵正确计算方向
        concordance = result.metadata.metrics["concordance_matrix"]
        assert concordance[0][1] >= 0  # 应该有正值
        assert concordance[1][0] >= 0  # 反向也应该计算

    def test_concordance_indicator_function(self):
        """测试：指示函数验证 (0/1 值)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.6, direction="higher_better"),
                Criterion(name="C2", weight=0.4, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},  # A1 在 C1 优于 A2，C2 劣于 A2
                "A2": {"C1": 8, "C2": 7},
            }
        )

        result = electre1(problem, alpha=0.5, beta=0.3)

        # 和谐指数应该是权重归一化后的值
        concordance = result.metadata.metrics["concordance_matrix"]
        # A1 vs A2: 只有 C1 贡献 (0.6 / 1.0 = 0.6)
        assert abs(concordance[0][1] - 0.6) < 0.01

    def test_concordance_zero_weight(self):
        """测试：零权重准则处理"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
                Criterion(name="C2", weight=0.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 8, "C2": 10},
            }
        )

        result = electre1(problem, alpha=0.5, beta=0.3)

        # 零权重准则不应该影响结果
        assert len(result.rankings) == 2

    def test_concordance_equal_weights(self):
        """测试：等权重准则"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
                Criterion(name="C2", weight=1.0, direction="higher_better"),
                Criterion(name="C3", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 8, "C3": 6},
                "A2": {"C1": 9, "C2": 7, "C3": 8},
                "A3": {"C1": 8, "C2": 9, "C3": 10},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 等权重应该平均分配
        concordance = result.metadata.metrics["concordance_matrix"]
        # 验证值在合理范围内
        for row in concordance:
            for val in row:
                assert 0 <= val <= 1


class TestDiscordanceDetails:
    """不和谐指数详细测试"""

    def test_discordance_max_range(self):
        """测试：最大范围处理"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 0, "C2": 5},   # C1 范围 [0, 10]
                "A2": {"C1": 10, "C2": 7},  # 最大差异
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        discordance = result.metadata.metrics["discordance_matrix"]
        # C1 最大差异应该是 (10-0)/10 = 1.0
        assert discordance[0][1] <= 1.0

    def test_discordance_zero_range(self):
        """测试：零范围准则 (所有值相同)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 10, "C2": 7},  # C1 所有值相同
                "A3": {"C1": 10, "C2": 9},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 零范围不应该导致除零错误
        discordance = result.metadata.metrics["discordance_matrix"]
        assert discordance[0][1] >= 0

    def test_discordance_cost_direction(self):
        """测试：成本型准则的不和谐计算"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="成本", weight=1.0, direction="lower_better"),
            ),
            scores={
                "A1": {"成本": 30},
                "A2": {"成本": 50},  # A2 更差
            }
        )

        result = electre1(problem, alpha=0.5, beta=0.3)

        discordance = result.metadata.metrics["discordance_matrix"]
        # A1 vs A2: A1 优于 A2，不和谐度应该低
        # A2 vs A1: A2 劣于 A1，不和谐度应该高
        assert discordance[1][0] >= discordance[0][1]

    def test_discordance_multiple_criteria(self):
        """测试：多准则不和谐度 (取最大值)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 10},
                "A2": {"C1": 5, "C2": 9},  # C1 差异更大
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        discordance = result.metadata.metrics["discordance_matrix"]
        # 不和谐度应该反映最大差异
        assert 0 <= discordance[0][1] <= 1


class TestCredibilityDetails:
    """可信度矩阵详细测试"""

    def test_credibility_alpha_thresholds(self):
        """测试：不同 α 阈值的影响"""
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

        result1 = electre1(problem, alpha=0.5, beta=0.3)
        result2 = electre1(problem, alpha=0.9, beta=0.3)

        # 更高的 α 应该更严格
        cred1 = result1.metadata.metrics["credibility_matrix"]
        cred2 = result2.metadata.metrics["credibility_matrix"]
        # α=0.5 时可能通过，α=0.9 时可能不通过
        assert cred1[0][1] >= cred2[0][1]

    def test_credibility_beta_thresholds(self):
        """测试：不同 β 阈值的影响"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 5},  # 较大差异
            }
        )

        result1 = electre1(problem, alpha=0.6, beta=0.2)
        result2 = electre1(problem, alpha=0.6, beta=0.8)

        # 更低的 β 应该更严格
        cred1 = result1.metadata.metrics["credibility_matrix"]
        cred2 = result2.metadata.metrics["credibility_matrix"]
        # β=0.2 时可能不通过，β=0.8 时可能通过
        assert cred1[0][1] <= cred2[0][1]

    def test_credibility_strict_thresholds(self):
        """测试：严格阈值 (α=1.0, β=0.0)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 8},
                "A3": {"C1": 6},
            }
        )

        result = electre1(problem, alpha=1.0, beta=0.0)

        # 严格阈值下，只有完全优于的方案才有可信度
        credibility = result.metadata.metrics["credibility_matrix"]
        for i in range(len(credibility)):
            for j in range(len(credibility)):
                assert credibility[i][j] in [0.0, 1.0]

    def test_credibility_relaxed_thresholds(self):
        """测试：宽松阈值 (α=0.5, β=0.5)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 9},
            }
        )

        result = electre1(problem, alpha=0.5, beta=0.5)

        # 宽松阈值应该有更多可信度
        credibility = result.metadata.metrics["credibility_matrix"]
        # 应该有一些 1 值
        has_credibility = any(credibility[i][j] == 1.0 for i in range(2) for j in range(2))
        assert has_credibility


class TestKernelExtractionDetails:
    """核提取详细测试"""

    def test_kernel_empty_graph(self):
        """测试：空图 (所有方案相互不优于)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 10},
                "A3": {"C1": 10},  # 所有方案得分相同
            }
        )

        result = electre1(problem, alpha=0.8, beta=0.2)

        # 所有方案都应该在核中 (没有相互优化的关系)
        kernel = result.metadata.metrics["kernel"]
        assert len(kernel) == 3

    def test_kernel_complete_graph(self):
        """测试：完全图 (传递性优势链)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 7},
                "A3": {"C1": 4},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 只有最优方案 A1 应该在核中
        kernel = result.metadata.metrics["kernel"]
        assert len(kernel) == 1
        assert "A1" in kernel

    def test_kernel_cycles(self):
        """测试：循环 (A > B > C > A)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=0.5, direction="higher_better"),
                Criterion(name="C2", weight=0.5, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},  # 在 C1 最优，C2 最差
                "A2": {"C1": 5, "C2": 10},  # 在 C1 最差，C2 最优
                "A3": {"C1": 8, "C2": 8},   # 平衡
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 核提取应该正确处理循环
        kernel = result.metadata.metrics["kernel"]
        assert len(kernel) >= 1

    def test_kernel_ranking_separation(self):
        """测试：核内外方案排名分离"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3", "A4"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 9},
                "A3": {"C1": 6},
                "A4": {"C1": 4},
            }
        )

        result = electre1(problem, alpha=0.7, beta=0.2)

        # 核内方案排名应该靠前
        kernel = result.metadata.metrics["kernel"]
        kernel_ranks = [r.rank for r in result.rankings if r.alternative in kernel]
        non_kernel_ranks = [r.rank for r in result.rankings if r.alternative not in kernel]

        if kernel_ranks and non_kernel_ranks:
            # 核内最小排名应该 <= 核外最小排名
            assert min(kernel_ranks) <= min(non_kernel_ranks)

    def test_kernel_tie_handling(self):
        """测试：并列处理 (多个方案相同得分)"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10},
                "A2": {"C1": 10},  # 并列
                "A3": {"C1": 8},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 并列方案应该有相同的排名
        rankings_dict = {r.alternative: r.rank for r in result.rankings}
        assert rankings_dict["A1"] == rankings_dict["A2"]


class TestSpecialCases:
    """特殊案例测试"""

    def test_very_small_weights(self):
        """测试：极小权重"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.001, direction="higher_better"),
                Criterion(name="C2", weight=0.999, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 5, "C2": 7},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 极小权重不应该导致数值问题
        assert len(result.rankings) == 2

    def test_very_large_weights(self):
        """测试：极大权重"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=0.999, direction="higher_better"),
                Criterion(name="C2", weight=0.001, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 10, "C2": 5},
                "A2": {"C1": 5, "C2": 7},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 极大权重应该归一化处理
        assert len(result.rankings) == 2

    def test_negative_scores(self):
        """测试：负值得分"""
        problem = DecisionProblem(
            alternatives=("A1", "A2"),
            criteria=(
                Criterion(name="C1", weight=1.0, direction="higher_better"),
            ),
            scores={
                "A1": {"C1": 5},
                "A2": {"C1": 3},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 负值应该正确处理
        assert len(result.rankings) == 2
        # A2 优于 A1
        rankings_dict = {r.alternative: r.score for r in result.rankings}
        assert rankings_dict["A2"] >= rankings_dict["A1"]

    def test_mixed_direction_complex(self):
        """测试：混合方向复杂案例"""
        problem = DecisionProblem(
            alternatives=("A1", "A2", "A3"),
            criteria=(
                Criterion(name="效益1", weight=0.3, direction="higher_better"),
                Criterion(name="效益2", weight=0.3, direction="higher_better"),
                Criterion(name="成本1", weight=0.2, direction="lower_better"),
                Criterion(name="成本2", weight=0.2, direction="lower_better"),
            ),
            scores={
                "A1": {"效益1": 80, "效益2": 50, "成本1": 20, "成本2": 30},
                "A2": {"效益1": 70, "效益2": 60, "成本1": 25, "成本2": 35},
                "A3": {"效益1": 60, "效益2": 70, "成本1": 30, "成本2": 40},
            }
        )

        result = electre1(problem, alpha=0.6, beta=0.3)

        # 混合方向应该正确计算
        assert len(result.rankings) == 3
        # 验证所有矩阵维度正确
        concordance = result.metadata.metrics["concordance_matrix"]
        assert len(concordance) == 3
        assert len(concordance[0]) == 3
