"""
CRITIC 赋权方法测试

测试基于对比强度和冲突性的权重计算。
"""

import pytest
import numpy as np
from mcda_core.weighting.critic_weighting import (
    critic_weighting,
    CRITICWeightingError
)


class TestCRITICBasic:
    """基本功能测试"""

    def test_basic_weighting(self):
        """测试：基本权重计算"""
        matrix = np.array([
            [10, 5, 8],
            [8, 7, 6],
            [9, 6, 7],
        ])

        weights = critic_weighting(matrix)

        assert len(weights) == 3
        assert np.isclose(np.sum(weights), 1.0, rtol=1e-10)
        assert all(w > 0 for w in weights)

    def test_three_criteria(self):
        """测试：3 个准则"""
        matrix = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ])

        weights = critic_weighting(matrix)

        assert len(weights) == 3
        assert np.all(weights > 0)
        assert np.isclose(weights.sum(), 1.0)

    def test_reproducibility(self):
        """测试：结果可重现"""
        matrix = np.array([
            [10, 20],
            [15, 25],
            [12, 22],
        ])

        weights1 = critic_weighting(matrix)
        weights2 = critic_weighting(matrix)

        assert np.allclose(weights1, weights2)


class TestCRITICProperties:
    """特性测试"""

    def test_high_correlation_low_weight(self):
        """测试：高相关性准则获得低权重"""
        # C1 和 C2 高度相关
        matrix = np.array([
            [10, 10, 5],
            [8, 8, 7],
            [9, 9, 6],
        ])

        weights = critic_weighting(matrix)

        # C1 和 C2 权重应该相近
        assert abs(weights[0] - weights[1]) < 0.1

    def test_weight_range(self):
        """测试：权重范围"""
        matrix = np.array([
            [10, 20, 30, 40],
            [15, 25, 35, 45],
            [12, 22, 32, 42],
        ])

        weights = critic_weighting(matrix)

        assert all(w > 0 for w in weights)
        assert all(w < 1 for w in weights)


class TestCRITICEdgeCases:
    """边界条件测试"""

    def test_minimal_matrix(self):
        """测试：最小矩阵 (2 方案 2 准则)"""
        matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = critic_weighting(matrix)

        assert len(weights) == 2
        assert np.isclose(weights.sum(), 1.0)

    def test_large_dataset(self):
        """测试：大数据集"""
        np.random.seed(42)
        matrix = np.random.randn(100, 10)

        weights = critic_weighting(matrix)

        assert len(weights) == 10
        assert np.isclose(weights.sum(), 1.0)

    def test_single_criterion(self):
        """测试：单准则"""
        matrix = np.array([[10], [20], [30]])

        weights = critic_weighting(matrix)

        assert len(weights) == 1
        assert weights[0] == pytest.approx(1.0, rel=1e-10)

    def test_uniform_values(self):
        """测试：所有值相同"""
        matrix = np.array([
            [10, 10, 10],
            [10, 10, 10],
            [10, 10, 10],
        ])

        weights = critic_weighting(matrix)

        # 应该返回均匀权重
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected)


class TestCRITICMathematical:
    """数学验证测试"""

    def test_information_calculation(self):
        """测试：信息量计算正确性"""
        # 使用不同变异的数据
        matrix = np.array([
            [10, 10, 5],  # C1, C2 相关, C3 独立
            [12, 12, 15],
            [8, 8, 25],
            [11, 11, 20],
        ])

        weights = critic_weighting(matrix)

        # C3 应该获得最高权重（独立且变异大）
        assert weights[2] > weights[0]
        assert weights[2] > weights[1]


class TestCRITICErrorHandling:
    """错误处理测试"""

    def test_none_input(self):
        """测试：None 输入"""
        with pytest.raises(CRITICWeightingError):
            critic_weighting(None)

    def test_empty_matrix(self):
        """测试：空矩阵"""
        matrix = np.array([])

        with pytest.raises(CRITICWeightingError):
            critic_weighting(matrix)

    def test_nan_values(self):
        """测试：NaN 值"""
        matrix = np.array([
            [1, 2],
            [np.nan, 4],
            [3, 4],
        ])

        with pytest.raises(CRITICWeightingError):
            critic_weighting(matrix)


class TestCRITICIntegration:
    """集成测试"""

    def test_with_decision_matrix(self):
        """测试：与决策矩阵集成"""
        matrix = np.array([
            [10, 50, 100, 200],
            [15, 60, 90, 180],
            [12, 55, 95, 190],
        ])

        weights = critic_weighting(matrix)

        assert len(weights) == 4
        assert np.isclose(weights.sum(), 1.0)
        assert np.all(weights > 0)
