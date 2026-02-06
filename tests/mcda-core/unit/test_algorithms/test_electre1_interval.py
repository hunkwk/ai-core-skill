"""
ELECTRE-I 区间版本算法测试

测试 ELECTRE-I 算法的区间数版本实现。
"""

import pytest
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import ELECTRE1IntervalAlgorithm


class TestELECTRE1IntervalBasic:
    """ELECTRE-I 区间版本基础测试"""

    def test_algorithm_initialization(self):
        """测试算法初始化"""
        algo = ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
        assert algo.alpha == 0.6
        assert algo.beta == 0.3

    def test_algorithm_name_and_description(self):
        """测试算法名称和描述"""
        algo = ELECTRE1IntervalAlgorithm()
        assert algo.name == "electre1_interval"
        assert "ELECTRE-I" in algo.description
        assert "区间" in algo.description

    def test_algorithm_default_parameters(self):
        """测试默认参数"""
        algo = ELECTRE1IntervalAlgorithm()
        assert algo.alpha == 0.6
        assert algo.beta == 0.3


class TestELECTRE1IntervalSimpleCase:
    """ELECTRE-I 区间版本简单案例测试"""

    def test_three_alternatives_two_criteria(self):
        """测试 3 个备选方案、2 个准则的简单案例"""
        # 创建备选方案（字符串）
        alternatives = ("A1", "A2", "A3")

        # 创建准则（效益型）
        criteria = (
            Criterion(name="C1", weight=0.6, direction="higher_better"),
            Criterion(name="C2", weight=0.4, direction="higher_better"),
        )

        # 创建评分矩阵（区间数）
        scores = {
            "A1": {"C1": Interval(2.0, 4.0), "C2": Interval(3.0, 5.0)},
            "A2": {"C1": Interval(3.0, 5.0), "C2": Interval(2.0, 4.0)},
            "A3": {"C1": Interval(1.0, 3.0), "C2": Interval(4.0, 6.0)},
        }

        # 创建决策问题
        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        # 执行 ELECTRE-I 区间版本
        algo = ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 3
        assert all(r.score >= 0 for r in result.rankings)

        # 验证元数据
        assert result.metadata.algorithm_name == "electre1_interval"
        assert "alpha" in result.metadata.metrics
        assert "beta" in result.metadata.metrics
        assert result.metadata.metrics["alpha"] == 0.6
        assert result.metadata.metrics["beta"] == 0.3

    def test_mixed_benefit_cost_criteria(self):
        """测试混合效益型和成本型准则"""
        # 创建备选方案
        alternatives = ("A1", "A2")

        # 创建准则（混合型）
        criteria = (
            Criterion(name="收益", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        )

        # 创建评分矩阵（区间数）
        scores = {
            "A1": {"收益": Interval(3.0, 5.0), "成本": Interval(2.0, 4.0)},
            "A2": {"收益": Interval(4.0, 6.0), "成本": Interval(3.0, 5.0)},
        }

        # 创建决策问题
        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        # 执行 ELECTRE-I 区间版本
        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 2


class TestELECTRE1IntervalConcordance:
    """ELECTRE-I 区间版本和谐指数测试"""

    def test_concordance_matrix_calculation(self):
        """测试和谐矩阵计算"""
        # 创建简单案例
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=0.5, direction="higher_better"),
            Criterion(name="C2", weight=0.5, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(3.0, 5.0), "C2": Interval(4.0, 6.0)},
            "A2": {"C1": Interval(2.0, 4.0), "C2": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证和谐矩阵存在
        assert "concordance_matrix" in result.metadata.metrics
        concordance = result.metadata.metrics["concordance_matrix"]

        # 和谐矩阵应该是 n×n
        assert len(concordance) == 2
        assert all(len(row) == 2 for row in concordance)

        # 和谐指数应该在 [0, 1] 范围内
        for i in range(2):
            for j in range(2):
                if i != j:
                    assert 0 <= concordance[i][j] <= 1

    def test_concordance_with_interval_scores(self):
        """测试区间评分的和谐指数计算"""
        # 创建备选方案
        alternatives = ("A1", "A2", "A3")

        criteria = (
            Criterion(name="C1", weight=0.4, direction="higher_better"),
            Criterion(name="C2", weight=0.3, direction="higher_better"),
            Criterion(name="C3", weight=0.3, direction="higher_better"),
        )

        # 区间评分（有重叠）
        scores = {
            "A1": {"C1": Interval(2.0, 4.0), "C2": Interval(3.0, 5.0), "C3": Interval(1.0, 3.0)},
            "A2": {"C1": Interval(3.0, 5.0), "C2": Interval(2.0, 4.0), "C3": Interval(2.0, 4.0)},
            "A3": {"C1": Interval(4.0, 6.0), "C2": Interval(1.0, 3.0), "C3": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证和谐矩阵
        assert "concordance_matrix" in result.metadata.metrics


class TestELECTRE1IntervalDiscordance:
    """ELECTRE-I 区间版本不和谐指数测试"""

    def test_discordance_matrix_calculation(self):
        """测试不和谐矩阵计算"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=0.6, direction="higher_better"),
            Criterion(name="C2", weight=0.4, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(2.0, 4.0), "C2": Interval(3.0, 5.0)},
            "A2": {"C1": Interval(4.0, 6.0), "C2": Interval(1.0, 3.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证不和谐矩阵存在
        assert "discordance_matrix" in result.metadata.metrics
        discordance = result.metadata.metrics["discordance_matrix"]

        # 不和谐矩阵应该是 n×n
        assert len(discordance) == 2
        assert all(len(row) == 2 for row in discordance)

        # 不和谐指数应该在 [0, 1] 范围内
        for i in range(2):
            for j in range(2):
                if i != j:
                    assert 0 <= discordance[i][j] <= 1

    def test_discordance_with_lower_better_criteria(self):
        """测试成本型准则的不和谐指数"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="成本", weight=1.0, direction="lower_better"),
        )

        scores = {
            "A1": {"成本": Interval(2.0, 4.0)},
            "A2": {"成本": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证不和谐矩阵
        assert "discordance_matrix" in result.metadata.metrics


class TestELECTRE1IntervalCredibility:
    """ELECTRE-I 区间版本可信度测试"""

    def test_credibility_matrix_calculation(self):
        """测试可信度矩阵计算"""
        alternatives = ("A1", "A2", "A3")

        criteria = (
            Criterion(name="C1", weight=0.5, direction="higher_better"),
            Criterion(name="C2", weight=0.5, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(4.0, 6.0), "C2": Interval(3.0, 5.0)},
            "A2": {"C1": Interval(2.0, 4.0), "C2": Interval(4.0, 6.0)},
            "A3": {"C1": Interval(3.0, 5.0), "C2": Interval(2.0, 4.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm(alpha=0.6, beta=0.3)
        result = algo.calculate(problem)

        # 验证可信度矩阵
        assert "credibility_matrix" in result.metadata.metrics
        credibility = result.metadata.metrics["credibility_matrix"]

        # 可信度矩阵应该是 n×n
        assert len(credibility) == 3
        assert all(len(row) == 3 for row in credibility)

        # 可信度应该是 0 或 1（二元）
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert credibility[i][j] in [0.0, 1.0]

    def test_credibility_with_different_thresholds(self):
        """测试不同阈值下的可信度"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=0.5, direction="higher_better"),
            Criterion(name="C2", weight=0.5, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(3.0, 5.0), "C2": Interval(3.0, 5.0)},
            "A2": {"C1": Interval(2.0, 4.0), "C2": Interval(2.0, 4.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        # 测试严格阈值
        algo_strict = ELECTRE1IntervalAlgorithm(alpha=0.8, beta=0.2)
        result_strict = algo_strict.calculate(problem)

        # 测试宽松阈值
        algo_relaxed = ELECTRE1IntervalAlgorithm(alpha=0.5, beta=0.4)
        result_relaxed = algo_relaxed.calculate(problem)

        # 验证两种情况都有结果
        assert result_strict is not None
        assert result_relaxed is not None


class TestELECTRE1IntervalKernel:
    """ELECTRE-I 区间版本核提取测试"""

    def test_kernel_extraction(self):
        """测试核提取"""
        alternatives = ("A1", "A2", "A3", "A4")

        criteria = (
            Criterion(name="C1", weight=0.6, direction="higher_better"),
            Criterion(name="C2", weight=0.4, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(5.0, 7.0), "C2": Interval(4.0, 6.0)},
            "A2": {"C1": Interval(3.0, 5.0), "C2": Interval(5.0, 7.0)},
            "A3": {"C1": Interval(1.0, 3.0), "C2": Interval(2.0, 4.0)},
            "A4": {"C1": Interval(2.0, 4.0), "C2": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证核存在
        assert "kernel" in result.metadata.metrics
        kernel = result.metadata.metrics["kernel"]

        # 核应该是非空列表
        assert isinstance(kernel, list)
        assert len(kernel) >= 1

        # 核中的方案应该是备选方案的子集
        alternative_names = set(alternatives)
        assert all(k in alternative_names for k in kernel)

    def test_kernel_with_all_dominated(self):
        """测试所有方案都被支配的情况"""
        alternatives = ("A1", "A2", "A3")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(5.0, 7.0)},
            "A2": {"C1": Interval(3.0, 5.0)},
            "A3": {"C1": Interval(1.0, 3.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证核存在且至少有一个方案
        assert "kernel" in result.metadata.metrics
        kernel = result.metadata.metrics["kernel"]
        assert len(kernel) >= 1


class TestELECTRE1IntervalEdgeCases:
    """ELECTRE-I 区间版本边界条件测试"""

    def test_degenerate_intervals(self):
        """测试退化区间（点区间）"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        # 退化区间（精确值）
        scores = {
            "A1": {"C1": Interval(5.0, 5.0)},
            "A2": {"C1": Interval(3.0, 3.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 2

    def test_overlapping_intervals(self):
        """测试重叠区间"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        # 完全重叠的区间
        scores = {
            "A1": {"C1": Interval(3.0, 5.0)},
            "A2": {"C1": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None

    def test_wide_intervals(self):
        """测试宽区间（高不确定性）"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        # 宽区间
        scores = {
            "A1": {"C1": Interval(1.0, 10.0)},
            "A2": {"C1": Interval(2.0, 11.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None


class TestELECTRE1IntervalErrors:
    """ELECTRE-I 区间版本错误处理测试"""

    def test_invalid_alpha(self):
        """测试无效的 alpha 参数"""
        # 应该在初始化时抛出异常
        with pytest.raises(ValueError, match="alpha"):
            ELECTRE1IntervalAlgorithm(alpha=1.5, beta=0.3)

    def test_invalid_beta(self):
        """测试无效的 beta 参数"""
        # 应该在初始化时抛出异常
        with pytest.raises(ValueError, match="beta"):
            ELECTRE1IntervalAlgorithm(alpha=0.6, beta=1.5)

    def test_minimum_alternatives(self):
        """测试最小备选方案数"""
        # DecisionProblem 在初始化时会验证备选方案数
        # 所以这里测试算法层面的验证
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(3.0, 5.0)},
            "A2": {"C1": Interval(2.0, 4.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm()

        # 正常情况应该成功
        result = algo.calculate(problem)
        assert result is not None


class TestELECTRE1IntervalIntegration:
    """ELECTRE-I 区间版本集成测试"""

    def test_realistic_decision_problem(self):
        """测试真实决策问题"""
        # 供应商选择问题（区间评分）
        alternatives = ("供应商A", "供应商B", "供应商C", "供应商D")

        criteria = (
            Criterion(name="质量", weight=0.35, direction="higher_better"),
            Criterion(name="价格", weight=0.25, direction="lower_better"),
            Criterion(name="交付期", weight=0.20, direction="lower_better"),
            Criterion(name="服务", weight=0.20, direction="higher_better"),
        )

        # 区间评分（反映不确定性）
        scores = {
            "供应商A": {
                "质量": Interval(70.0, 90.0),
                "价格": Interval(80.0, 100.0),
                "交付期": Interval(5.0, 10.0),
                "服务": Interval(60.0, 80.0),
            },
            "供应商B": {
                "质量": Interval(80.0, 90.0),
                "价格": Interval(90.0, 100.0),
                "交付期": Interval(7.0, 12.0),
                "服务": Interval(70.0, 90.0),
            },
            "供应商C": {
                "质量": Interval(60.0, 80.0),
                "价格": Interval(70.0, 90.0),
                "交付期": Interval(3.0, 7.0),
                "服务": Interval(50.0, 70.0),
            },
            "供应商D": {
                "质量": Interval(70.0, 80.0),
                "价格": Interval(85.0, 100.0),
                "交付期": Interval(6.0, 11.0),
                "服务": Interval(80.0, 90.0),
            },
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = ELECTRE1IntervalAlgorithm(alpha=0.65, beta=0.35)
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 4

        # 验证核存在
        assert "kernel" in result.metadata.metrics
        kernel = result.metadata.metrics["kernel"]
        assert len(kernel) >= 1

        # 验证元数据
        assert result.metadata.algorithm_name == "electre1_interval"
        assert result.metadata.metrics["alpha"] == 0.65
        assert result.metadata.metrics["beta"] == 0.35
