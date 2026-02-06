"""
变异系数法赋权测试

测试基于数据离散程度的客观权重计算。
"""

import pytest
import numpy as np
from mcda_core.weighting.cv_weighting import (
    cv_weighting,
    CVWeightingError
)


class TestCVBasic:
    """基本功能测试"""

    def test_basic_weighting(self):
        """测试：基本权重计算"""
        matrix = np.array([
            [10, 50, 100],
            [12, 60, 90],
            [8, 40, 110],
        ])

        weights = cv_weighting(matrix)

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

        weights = cv_weighting(matrix)

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

        weights1 = cv_weighting(matrix)
        weights2 = cv_weighting(matrix)

        assert np.allclose(weights1, weights2)


class TestCVMathematical:
    """数学验证测试"""

    def test_high_variance_high_weight(self):
        """测试：高变异准则获得高权重"""
        matrix = np.array([
            [10, 10, 10],  # C1: 低变异
            [11, 11, 50],  # C2: 中变异
            [12, 12, 100], # C3: 高变异
        ])

        weights = cv_weighting(matrix)

        # C3 变异最大,应该获得最高权重
        assert weights[2] > weights[1]
        assert weights[2] > weights[0]

    def test_coefficient_calculation(self):
        """测试：变异系数计算正确性"""
        # 使用更明显的数据差异
        matrix = np.array([
            [10, 100],
            [11, 200],
            [12, 300],
            [13, 400],
            [14, 500],
        ])

        weights = cv_weighting(matrix)

        # C2 的变异系数应该更大
        assert weights[1] > weights[0]

    def test_uniform_variance(self):
        """测试：相同变异，相同权重"""
        matrix = np.array([
            [10, 20],
            [20, 40],
            [30, 60],
            [40, 80],
        ])

        weights = cv_weighting(matrix)

        # 两列变异系数相同，权重应该相同
        assert np.isclose(weights[0], weights[1])


class TestCVEdgeCases:
    """边界条件测试"""

    def test_minimal_matrix(self):
        """测试：最小矩阵 (2 方案 2 准则)"""
        matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = cv_weighting(matrix)

        assert len(weights) == 2
        assert np.isclose(weights.sum(), 1.0)

    def test_large_dataset(self):
        """测试：大数据集"""
        np.random.seed(42)
        matrix = np.random.randn(100, 10)

        weights = cv_weighting(matrix)

        assert len(weights) == 10
        assert np.isclose(weights.sum(), 1.0)

    def test_single_criterion(self):
        """测试：单准则"""
        matrix = np.array([[10], [20], [30]])

        weights = cv_weighting(matrix)

        assert len(weights) == 1
        assert weights[0] == pytest.approx(1.0, rel=1e-10)

    def test_zero_mean(self):
        """测试：零均值情况"""
        # 均值为 0 的数据
        matrix = np.array([
            [-5, 5],
            [0, 0],
            [5, -5],
        ])

        weights = cv_weighting(matrix)

        # 应该处理零均值（可能使用绝对值）
        assert len(weights) == 2

    def test_uniform_values(self):
        """测试：所有值相同"""
        matrix = np.array([
            [10, 10, 10],
            [10, 10, 10],
            [10, 10, 10],
        ])

        # 应该返回均匀权重
        weights = cv_weighting(matrix)
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected)


class TestCVErrorHandling:
    """错误处理测试"""

    def test_none_input(self):
        """测试：None 输入"""
        with pytest.raises(CVWeightingError):
            cv_weighting(None)

    def test_empty_matrix(self):
        """测试：空矩阵"""
        matrix = np.array([])

        with pytest.raises(CVWeightingError):
            cv_weighting(matrix)

    def test_nan_values(self):
        """测试：NaN 值"""
        matrix = np.array([
            [1, 2],
            [np.nan, 4],
            [3, 4],
        ])

        with pytest.raises(CVWeightingError):
            cv_weighting(matrix)

    def test_single_alternative_error(self):
        """测试：单方案（无法计算标准差）"""
        matrix = np.array([[10, 20, 30]])

        # 单方案无法计算变异
        try:
            weights = cv_weighting(matrix)
            # 如果不报错，应该返回均匀权重
            expected = np.array([1/3, 1/3, 1/3])
            assert np.allclose(weights, expected)
        except CVWeightingError:
            pass


class TestCVIntegration:
    """集成测试"""

    def test_with_decision_matrix(self):
        """测试：与决策矩阵集成"""
        matrix = np.array([
            [10, 50, 100, 200],
            [15, 60, 90, 180],
            [12, 55, 95, 190],
            [11, 58, 92, 185],
        ])

        weights = cv_weighting(matrix)

        assert len(weights) == 4
        assert np.isclose(weights.sum(), 1.0)
        assert np.all(weights > 0)

    def test_comparison_with_critic(self):
        """测试：与 CRITIC 方法对比"""
        # 变异系数法只考虑标准差，不考虑相关性
        matrix = np.array([
            [10, 10, 5],
            [12, 12, 15],
            [8, 8, 25],
        ])

        weights_cv = cv_weighting(matrix)

        # C1, C2 相关系数高，但变异系数法不考虑相关性
        # 所以 C1, C2 权重应该相近
        assert abs(weights_cv[0] - weights_cv[1]) < 0.1


class TestCVProperties:
    """特性测试"""

    def test_weight_range(self):
        """测试：权重范围"""
        matrix = np.array([
            [10, 20, 30, 40],
            [15, 25, 35, 45],
            [12, 22, 32, 42],
        ])

        weights = cv_weighting(matrix)

        # 所有权重在 (0, 1) 范围内
        assert all(w > 0 for w in weights)
        assert all(w < 1 for w in weights)

    def test_scale_invariance(self):
        """测试：尺度不变性"""
        matrix1 = np.array([
            [1, 2, 3],
            [4, 5, 6],
        ])

        matrix2 = matrix1 * 100  # 缩放 100 倍

        weights1 = cv_weighting(matrix1)
        weights2 = cv_weighting(matrix2)

        # 变异系数应该与尺度无关
        assert np.allclose(weights1, weights2)
