"""
MCDA Core - TOPSIS 区间版本文档示例测试

测试文档中示例代码的可运行性和正确性。
"""

import pytest
import numpy as np
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.interval import Interval
from mcda_core.algorithms import IntervalTOPSISAlgorithm


# =============================================================================
# 文档示例测试
# =============================================================================

class TestTOPSISIntervalDocumentationExamples:
    """TOPSIS 区间版本文档示例测试"""

    def test_basic_example_from_guide(self):
        """测试使用指南中的基础示例"""
        # 定义备选方案
        alternatives = ("A1", "A2", "A3")

        # 定义准则
        criteria = (
            Criterion(name="质量", weight=0.4, direction="higher_better"),
            Criterion(name="价格", weight=0.3, direction="lower_better"),
            Criterion(name="可靠性", weight=0.2, direction="higher_better"),
            Criterion(name="易用性", weight=0.1, direction="higher_better"),
        )

        # 定义评分矩阵（区间数）
        scores = {
            "A1": {
                "质量": Interval(70.0, 90.0),
                "价格": Interval(80.0, 100.0),
                "可靠性": Interval(70.0, 80.0),
                "易用性": Interval(60.0, 80.0),
            },
            "A2": {
                "质量": Interval(80.0, 90.0),
                "价格": Interval(90.0, 100.0),
                "可靠性": Interval(80.0, 90.0),
                "易用性": Interval(70.0, 90.0),
            },
            "A3": {
                "质量": Interval(60.0, 80.0),
                "价格": Interval(70.0, 90.0),
                "可靠性": Interval(60.0, 70.0),
                "易用性": Interval(50.0, 70.0),
            },
        }

        # 创建决策问题
        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        # 执行 TOPSIS 区间版本
        algo = IntervalTOPSISAlgorithm()
        result = algo.calculate(problem)

        # 验证结果
        assert len(result.rankings) == 3
        assert result.metadata.algorithm_name == "topsis_interval"

        # 验证排名在有效范围内
        for item in result.rankings:
            assert 0 <= item.score <= 1  # 相对接近度在 [0, 1] 范围内

    def test_supplier_selection_example(self):
        """测试供应商选择案例"""
        alternatives = ("供应商A", "供应商B", "供应商C")

        criteria = (
            Criterion(name="质量", weight=0.35, direction="higher_better"),
            Criterion(name="价格", weight=0.25, direction="lower_better"),
            Criterion(name="交付期", weight=0.20, direction="lower_better"),
            Criterion(name="服务", weight=0.20, direction="higher_better"),
        )

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
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = IntervalTOPSISAlgorithm()
        result = algo.calculate(problem)

        # 验证结果结构
        assert len(result.rankings) == 3
        assert "distance_to_ideal" in result.metadata.metrics
        assert "distance_to_negative_ideal" in result.metadata.metrics

    def test_mixed_criteria_types(self):
        """测试混合准则类型（效益型和成本型）"""
        alternatives = ("方案1", "方案2")

        criteria = (
            Criterion(name="效益", weight=0.5, direction="higher_better"),
            Criterion(name="成本", weight=0.5, direction="lower_better"),
        )

        scores = {
            "方案1": {
                "效益": Interval(80.0, 90.0),
                "成本": Interval(30.0, 40.0),
            },
            "方案2": {
                "效益": Interval(70.0, 80.0),
                "成本": Interval(20.0, 30.0),
            },
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = IntervalTOPSISAlgorithm()
        result = algo.calculate(problem)

        # 验证排名
        assert len(result.rankings) == 2

    def test_metadata_structure(self):
        """测试元数据结构"""
        alternatives = ("A", "B")
        criteria = (
            Criterion(name="C1", weight=0.5, direction="higher_better"),
            Criterion(name="C2", weight=0.5, direction="higher_better"),
        )
        scores = {
            "A": {"C1": Interval(8.0, 9.0), "C2": Interval(7.0, 8.0)},
            "B": {"C1": Interval(7.0, 8.0), "C2": Interval(8.0, 9.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = IntervalTOPSISAlgorithm()
        result = algo.calculate(problem)

        # 验证元数据包含必需的字段
        metadata = result.metadata.metrics
        assert "normalized" in metadata
        assert "weighted" in metadata
        assert "ideal" in metadata
        assert "negative_ideal" in metadata
        assert "distance_to_ideal" in metadata
        assert "distance_to_negative_ideal" in metadata


# =============================================================================
# 数学公式验证测试
# =============================================================================

class TestTOPSISIntervalMathematicalFormulas:
    """TOPSIS 区间版本数学公式验证"""

    def test_vector_normalization_formula(self):
        """验证 Vector 标准化公式"""
        # r_ij = x_ij / sqrt(Σ x_ik²)
        values = [Interval(3.0, 5.0), Interval(4.0, 6.0), Interval(5.0, 7.0)]

        # 计算范数（基于中点）
        sum_squares = sum(v.midpoint ** 2 for v in values)
        norm = np.sqrt(sum_squares)

        # 验证标准化后的值
        normalized = [v.midpoint / norm for v in values]

        # 验证标准化后向量范数为 1
        new_norm = np.sqrt(sum(n ** 2 for n in normalized))
        assert abs(new_norm - 1.0) < 1e-10

    def test_closeness_formula(self):
        """验证相对接近度公式"""
        # C_i = D_i⁻ / (D_i⁺ + D_i⁻)
        d_plus = 0.3
        d_minus = 0.7

        closeness = d_minus / (d_plus + d_minus)

        # 相对接近度应在 [0, 1] 范围内
        assert 0 <= closeness <= 1
        # 验证计算
        expected = 0.7 / 1.0
        assert abs(closeness - expected) < 1e-10

    def test_distance_formula(self):
        """验证距离公式（欧氏距离）"""
        # D = sqrt(Σ (v_ij - v_j)²)
        point = np.array([0.5, 0.7, 0.3])
        ideal = np.array([0.8, 0.9, 0.6])

        distance = np.sqrt(sum((p - i) ** 2 for p, i in zip(point, ideal)))

        # 距离应为非负数
        assert distance >= 0


# =============================================================================
# 文档一致性测试
# =============================================================================

class TestTOPSISIntervalDocumentationConsistency:
    """文档一致性测试"""

    def test_algorithm_name_consistency(self):
        """验证算法名称一致性"""
        algo = IntervalTOPSISAlgorithm()
        assert algo.name == "topsis_interval"
        assert "TOPSIS" in algo.description
        assert "区间" in algo.description

    def test_interval_class_consistency(self):
        """验证 Interval 类使用一致性"""
        interval = Interval(2.0, 6.0)

        # 验证属性
        assert hasattr(interval, "lower")
        assert hasattr(interval, "upper")
        assert hasattr(interval, "midpoint")
        assert hasattr(interval, "width")

        # 验证值
        assert interval.lower == 2.0
        assert interval.upper == 6.0
        assert interval.midpoint == 4.0
        assert interval.width == 4.0

    def test_criterion_direction_consistency(self):
        """验证准则方向一致性"""
        # 效益型准则
        benefit = Criterion(name="效益", weight=0.5, direction="higher_better")
        assert benefit.direction == "higher_better"

        # 成本型准则
        cost = Criterion(name="成本", weight=0.5, direction="lower_better")
        assert cost.direction == "lower_better"


# =============================================================================
# 边界条件测试（用于文档说明）
# =============================================================================

class TestTOPSISIntervalEdgeCaseDocumentation:
    """边界条件文档测试"""

    def test_degenerate_interval(self):
        """测试退化区间（用于文档说明）"""
        degenerate = Interval(5.0, 5.0)
        assert degenerate.width == 0
        assert degenerate.midpoint == 5.0

    def test_wide_interval(self):
        """测试宽区间（用于文档说明）"""
        wide = Interval(0.0, 100.0)
        assert wide.width == 100.0
        assert wide.midpoint == 50.0

    def test_minimum_alternatives(self):
        """测试最小备选方案数量"""
        alternatives = ("A", "B")
        criteria = (
            Criterion(name="C1", weight=1.0, direction="higher_better"),
        )
        scores = {
            "A": {"C1": Interval(5.0, 7.0)},
            "B": {"C1": Interval(6.0, 8.0)},
        }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores
        )

        algo = IntervalTOPSISAlgorithm()
        result = algo.calculate(problem)

        assert len(result.rankings) == 2
