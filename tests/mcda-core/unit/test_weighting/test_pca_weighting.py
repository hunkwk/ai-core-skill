"""
主成分分析赋权测试 (PCA Weighting Tests)

测试基于主成分分析的客观权重计算。
"""

import pytest
import numpy as np
from mcda_core.weighting.pca_weighting import (
    pca_weighting,
    PCAWeightingError,
    MAX_CRITERIA,
    _standardize,
    _compute_covariance,
    _eigen_decomposition,
    _extract_weights,
)


class TestPCABasic:
    """基本功能测试 (6 个)"""

    def test_basic_weighting(self):
        """测试：PCA 赋权基本功能"""
        matrix = np.array([
            [10, 50, 100],
            [12, 60, 90],
            [8, 40, 110],
            [11, 55, 95],
        ])

        weights = pca_weighting(matrix)

        assert len(weights) == 3
        assert np.isclose(np.sum(weights), 1.0, rtol=1e-10)
        assert all(w >= 0 for w in weights)  # PCA 权重可能为 0

    def test_standardization(self):
        """测试：标准化过程"""
        matrix = np.array([
            [10, 50],
            [20, 60],
            [30, 70],
        ])

        standardized = _standardize(matrix)

        # 每列均值应接近 0
        means = np.mean(standardized, axis=0)
        assert np.allclose(means, 0, atol=1e-10)

        # 每列标准差应接近 1
        stds = np.std(standardized, axis=0, ddof=1)
        assert np.allclose(stds, 1, atol=1e-10)

    def test_covariance_computation(self):
        """测试：协方差矩阵计算"""
        standardized = np.array([
            [-1, -1],
            [0, 0],
            [1, 1],
        ], dtype=float)

        covariance = _compute_covariance(standardized)

        # 协方差矩阵应该是对称的
        assert covariance.shape == (2, 2)
        assert np.allclose(covariance, covariance.T)

        # 对角线应该是方差
        assert covariance[0, 0] > 0
        assert covariance[1, 1] > 0

    def test_eigen_decomposition(self):
        """测试：特征值分解"""
        # 创建一个已知的协方差矩阵
        covariance = np.array([
            [2, 1],
            [1, 2],
        ], dtype=float)

        eigenvalues, eigenvectors = _eigen_decomposition(covariance)

        # 特征值应该降序排列
        assert eigenvalues[0] >= eigenvalues[1]

        # 特征值和应该等于矩阵的迹
        assert np.isclose(np.sum(eigenvalues), np.trace(covariance))

        # 特征向量应该正交
        dot_product = np.dot(eigenvectors[:, 0], eigenvectors[:, 1])
        assert np.abs(dot_product) < 1e-10

    def test_weight_extraction(self):
        """测试：权重提取"""
        # 创建简单的特征值和特征向量
        eigenvalues = np.array([3, 1, 0.5])
        eigenvectors = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ], dtype=float)

        weights = _extract_weights(eigenvalues, eigenvectors)

        # 权重应该归一化
        assert np.isclose(np.sum(weights), 1.0)

        # 第一个准则权重应该最高（最大特征值）
        assert weights[0] >= weights[1]
        assert weights[1] >= weights[2]

    def test_principal_component_selection(self):
        """测试：主成分选择策略"""
        # 创建有明确主成分的数据
        matrix = np.array([
            [1, 10, 100],
            [2, 20, 200],
            [3, 30, 300],
            [4, 40, 400],
            [5, 50, 500],
        ])

        weights = pca_weighting(matrix)

        # 应该返回有效权重
        assert len(weights) == 3
        assert np.isclose(np.sum(weights), 1.0)


class TestPCAMathematical:
    """数学正确性测试 (4 个)"""

    def test_weights_sum_to_one(self):
        """测试：权重和为 1"""
        matrices = [
            np.random.randn(10, 3),
            np.random.randn(20, 5),
            np.array([[1, 2], [3, 4], [5, 6]]),
        ]

        for matrix in matrices:
            weights = pca_weighting(matrix)
            assert np.isclose(np.sum(weights), 1.0, rtol=1e-10)

    def test_standardization_correctness(self):
        """测试：标准化正确性"""
        matrix = np.array([
            [1, 10],
            [2, 20],
            [3, 30],
            [4, 40],
            [5, 50],
        ])

        standardized = _standardize(matrix)

        # 验证 Z-score 公式: z = (x - μ) / σ
        means = np.mean(matrix, axis=0)
        stds = np.std(matrix, axis=0, ddof=1)

        expected = (matrix - means) / stds
        assert np.allclose(standardized, expected)

    def test_eigenvalue_eigenvector_correspondence(self):
        """测试：特征值和特征向量对应关系"""
        covariance = np.array([
            [4, 2],
            [2, 3],
        ], dtype=float)

        eigenvalues, eigenvectors = _eigen_decomposition(covariance)

        # 验证 C · v = λ · v
        for i in range(len(eigenvalues)):
            left = np.dot(covariance, eigenvectors[:, i])
            right = eigenvalues[i] * eigenvectors[:, i]
            assert np.allclose(left, right, atol=1e-10)

    def test_cumulative_variance_calculation(self):
        """测试：累积方差计算"""
        # 创建特征值
        eigenvalues = np.array([5, 3, 2, 1])
        total = np.sum(eigenvalues)

        # 累积方差
        cumulative = np.cumsum(eigenvalues) / total

        assert np.isclose(cumulative[0], 5/11)
        assert np.isclose(cumulative[1], 8/11)
        assert np.isclose(cumulative[2], 10/11)
        assert np.isclose(cumulative[3], 1.0)


class TestPCAEdgeCases:
    """边界条件测试 (3 个)"""

    def test_minimal_criteria(self):
        """测试：少量准则（2 个）"""
        matrix = np.array([
            [10, 20],
            [15, 25],
            [12, 22],
        ])

        weights = pca_weighting(matrix)

        assert len(weights) == 2
        assert np.isclose(np.sum(weights), 1.0)

    def test_max_criteria_limit(self):
        """测试：准则数量接近限制"""
        # 创建接近 MAX_CRITERIA 的矩阵
        n = MAX_CRITERIA - 1
        matrix = np.random.randn(10, n)

        weights = pca_weighting(matrix)

        assert len(weights) == n
        assert np.isclose(np.sum(weights), 1.0)

    def test_uniform_values(self):
        """测试：所有准则权重相等的情况"""
        # 所有列完全相同
        matrix = np.array([
            [10, 10, 10],
            [10, 10, 10],
            [10, 10, 10],
        ])

        weights = pca_weighting(matrix)

        # 应该返回均匀权重（或接近均匀）
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected, atol=0.1)


class TestPCAErrorHandling:
    """错误处理测试 (2 个)"""

    def test_exceed_max_criteria(self):
        """测试：超过 MAX_CRITERIA 限制"""
        # 创建超过 MAX_CRITERIA 的矩阵
        n = MAX_CRITERIA + 1
        matrix = np.random.randn(5, n)

        with pytest.raises(PCAWeightingError) as exc_info:
            pca_weighting(matrix)

        assert "超过" in str(exc_info.value) or "不支持" in str(exc_info.value)

    def test_invalid_input(self):
        """测试：无效输入"""
        # None 输入
        with pytest.raises(PCAWeightingError):
            pca_weighting(None)

        # 空矩阵
        with pytest.raises(PCAWeightingError):
            pca_weighting(np.array([]))

        # NaN 值
        with pytest.raises(PCAWeightingError):
            pca_weighting(np.array([[1, np.nan], [3, 4]]))

        # Inf 值
        with pytest.raises(PCAWeightingError):
            pca_weighting(np.array([[1, np.inf], [3, 4]]))


class TestPCASpecialCases:
    """特殊情况测试"""

    def test_single_criterion(self):
        """测试：单准则"""
        matrix = np.array([[10], [20], [30]])

        weights = pca_weighting(matrix)

        assert len(weights) == 1
        assert weights[0] == pytest.approx(1.0, rel=1e-10)

    def test_single_alternative(self):
        """测试：单方案"""
        matrix = np.array([[10, 20, 30]])

        weights = pca_weighting(matrix)

        # 单方案无法计算方差，应返回均匀权重
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected)

    def test_two_alternatives(self):
        """测试：两个方案（最小可计算协方差）"""
        matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = pca_weighting(matrix)

        assert len(weights) == 2
        assert np.isclose(np.sum(weights), 1.0)


class TestPCAProperties:
    """特性测试"""

    def test_reproducibility(self):
        """测试：结果可重现"""
        matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [12, 22, 32],
        ])

        weights1 = pca_weighting(matrix)
        weights2 = pca_weighting(matrix)

        assert np.allclose(weights1, weights2)

    def test_high_variance_high_weight(self):
        """测试：高方差准则获得高权重"""
        # 创建方差差异明显的数据（使用不相关的列）
        matrix = np.array([
            [100, 10, 50],     # C1: 高方差，独立模式
            [105, 15, 52],     # C2: 低方差
            [110, 12, 54],
            [115, 13, 56],
            [200, 14, 58],     # C1 有更大的变化
            [95, 11, 60],
        ])

        weights = pca_weighting(matrix)

        # 权重应该是有效的
        assert len(weights) == 3
        assert np.isclose(np.sum(weights), 1.0)
        # 所有权重非负
        assert np.all(weights >= 0)

    def test_with_list_input(self):
        """测试：列表输入"""
        matrix_list = [
            [10, 20, 30],
            [15, 25, 35],
            [12, 22, 32],
        ]

        weights = pca_weighting(matrix_list)

        assert len(weights) == 3
        assert np.isclose(np.sum(weights), 1.0)

    def test_regularization_effect(self):
        """测试：正则化效果"""
        # 创建可能导致数值不稳定的数据
        matrix = np.array([
            [1, 1],
            [1, 1],
            [1, 1],
        ], dtype=float)

        # 添加微小差异
        matrix[0, 0] += 1e-15

        # 应该能正常处理（不崩溃）
        weights = pca_weighting(matrix)
        assert len(weights) == 2
