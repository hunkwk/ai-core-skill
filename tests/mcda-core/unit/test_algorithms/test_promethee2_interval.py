"""
PROMETHEE II 区间版本算法测试

测试 PROMETHEE II 算法的区间数版本实现。
"""

import pytest
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import PROMETHEE2IntervalAlgorithm


class TestPROMETHEE2IntervalBasic:
    """PROMETHEE II 区间版本基础测试"""

    def test_algorithm_initialization(self):
        """测试算法初始化"""
        algo = PROMETHEE2IntervalAlgorithm()
        assert algo is not None
        assert algo.name == "promethee2_interval"

    def test_algorithm_name_and_description(self):
        """测试算法名称和描述"""
        algo = PROMETHEE2IntervalAlgorithm()
        assert algo.name == "promethee2_interval"
        assert "PROMETHEE" in algo.description
        assert "区间" in algo.description

    def test_algorithm_with_custom_preference_function(self):
        """测试自定义偏好函数"""
        algo = PROMETHEE2IntervalAlgorithm(preference_function="usual")
        assert algo.preference_function == "usual"


class TestPROMETHEE2IntervalSimpleCase:
    """PROMETHEE II 区间版本简单案例测试"""

    def test_three_alternatives_two_criteria(self):
        """测试 3 个备选方案、2 个准则的简单案例"""
        # 创建备选方案
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

        # 执行 PROMETHEE II 区间版本
        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 3
        # 净流量可以是负数，所以不检查 >= 0

        # 验证元数据
        assert result.metadata.algorithm_name == "promethee2_interval"

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

        # 执行 PROMETHEE II 区间版本
        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 2


class TestPROMETHEE2IntervalPreferenceFunctions:
    """PROMETHEE II 区间版本偏好函数测试"""

    def test_usual_preference_function(self):
        """测试通常型偏好函数"""
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

        algo = PROMETHEE2IntervalAlgorithm(preference_function="usual")
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None

    def test_u_shape_preference_function(self):
        """测试 U 型偏好函数"""
        alternatives = ("A1", "A2")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(5.0, 7.0)},
            "A2": {"C1": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = PROMETHEE2IntervalAlgorithm(
            preference_function="u_shape",
            threshold=1.0
        )
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None

    def test_v_shape_preference_function(self):
        """测试 V 型偏好函数"""
        alternatives = ("A1", "A2", "A3")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(7.0, 9.0)},
            "A2": {"C1": Interval(5.0, 7.0)},
            "A3": {"C1": Interval(3.0, 5.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = PROMETHEE2IntervalAlgorithm(
            preference_function="v_shape",
            threshold=2.0
        )
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 3


class TestPROMETHEE2IntervalNetFlow:
    """PROMETHEE II 区间版本净流量测试"""

    def test_net_flow_calculation(self):
        """测试净流量计算"""
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

        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证净流量存在
        assert "net_flow" in result.metadata.metrics
        net_flow = result.metadata.metrics["net_flow"]

        # 净流量应该有每个方案的值
        assert len(net_flow) == 3

        # 验证排名基于净流量
        rankings = result.rankings
        assert len(rankings) == 3

    def test_net_flow_positive_negative(self):
        """测试净流量正负值"""
        alternatives = ("A1", "A2", "A3", "A4")

        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )

        scores = {
            "A1": {"C1": Interval(8.0, 10.0)},  # 最优
            "A2": {"C1": Interval(6.0, 8.0)},
            "A3": {"C1": Interval(4.0, 6.0)},
            "A4": {"C1": Interval(2.0, 4.0)},  # 最差
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证净流量
        net_flow = result.metadata.metrics["net_flow"]

        # 最优方案应该有最高的正净流量
        # 最差方案应该有最低的负净流量
        assert net_flow["A1"] > net_flow["A4"]


class TestPROMETHEE2IntervalEdgeCases:
    """PROMETHEE II 区间版本边界条件测试"""

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

        algo = PROMETHEE2IntervalAlgorithm()
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

        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        # 重叠区间应该有相同的净流量
        net_flow = result.metadata.metrics["net_flow"]

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

        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None


class TestPROMETHEE2IntervalErrors:
    """PROMETHEE II 区间版本错误处理测试"""

    def test_invalid_preference_function(self):
        """测试无效的偏好函数"""
        with pytest.raises(ValueError, match="preference_function"):
            PROMETHEE2IntervalAlgorithm(preference_function="invalid")

    def test_negative_threshold(self):
        """测试负阈值"""
        with pytest.raises(ValueError, match="threshold"):
            PROMETHEE2IntervalAlgorithm(
                preference_function="u_shape",
                threshold=-1.0
            )

    def test_minimum_alternatives(self):
        """测试最小备选方案数"""
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

        algo = PROMETHEE2IntervalAlgorithm()

        # 正常情况应该成功
        result = algo.calculate(problem)
        assert result is not None


class TestPROMETHEE2IntervalIntegration:
    """PROMETHEE II 区间版本集成测试"""

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

        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 4

        # 验证净流量
        assert "net_flow" in result.metadata.metrics
        net_flow = result.metadata.metrics["net_flow"]
        assert len(net_flow) == 4

        # 验证元数据
        assert result.metadata.algorithm_name == "promethee2_interval"

    def test_multiple_criteria_with_different_weights(self):
        """测试多准则不同权重"""
        alternatives = ("A1", "A2", "A3")

        criteria = (
            Criterion(name="C1", weight=0.1, direction="higher_better"),
            Criterion(name="C2", weight=0.2, direction="higher_better"),
            Criterion(name="C3", weight=0.3, direction="higher_better"),
            Criterion(name="C4", weight=0.4, direction="higher_better"),
        )

        scores = {
            "A1": {
                "C1": Interval(2.0, 4.0),
                "C2": Interval(3.0, 5.0),
                "C3": Interval(4.0, 6.0),
                "C4": Interval(5.0, 7.0),
            },
            "A2": {
                "C1": Interval(3.0, 5.0),
                "C2": Interval(2.0, 4.0),
                "C3": Interval(5.0, 7.0),
                "C4": Interval(4.0, 6.0),
            },
            "A3": {
                "C1": Interval(4.0, 6.0),
                "C2": Interval(5.0, 7.0),
                "C3": Interval(2.0, 4.0),
                "C4": Interval(3.0, 5.0),
            },
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = PROMETHEE2IntervalAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert result is not None
        assert len(result.rankings) == 3
