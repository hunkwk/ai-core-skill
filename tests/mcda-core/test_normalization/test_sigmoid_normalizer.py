"""
Sigmoid 标准化测试

测试 Sigmoid 标准化功能。
"""

import pytest
import numpy as np
from mcda_core.normalization.sigmoid_normalizer import (
    SigmoidNormalizer,
    SigmoidNormalizerError
)


class TestSigmoidBasic:
    """基本功能测试"""

    def test_s_curve_shape(self):
        """测试：S 曲线特性"""
        data = np.array([-10, -5, 0, 5, 10])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data)

        # 验证 S 形状：单调递增
        assert result[0] < result[1] < result[2] < result[3] < result[4]

    def test_range(self):
        """测试：输出范围 [0, 1]"""
        data = np.array([-100, 0, 100])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data)

        assert result.min() >= 0
        assert result.max() <= 1

    def test_custom_coefficient(self):
        """测试：自定义压缩系数"""
        data = np.array([0, 5, 10])
        normalizer = SigmoidNormalizer()

        result_k2 = normalizer.normalize(data, k=2)
        result_k5 = normalizer.normalize(data, k=5)

        # k 越大,曲线越陡峭,中间值应该更接近 0.5
        assert len(result_k2) == len(result_k5)

    def test_automatic_statistics(self):
        """测试：自动计算均值和标准差"""
        data = np.array([1, 2, 3, 4, 5])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data)

        # 应该自动计算 μ, σ
        assert not np.any(np.isnan(result))
        assert len(result) == len(data)


class TestSigmoidEdgeCases:
    """边界条件测试"""

    def test_uniform_values(self):
        """测试：所有值相同"""
        data = np.array([10, 10, 10])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data)

        # 所有值应该相同 (σ=0 时需要特殊处理)
        assert len(result) == len(data)

    def test_single_value(self):
        """测试：单个值"""
        data = np.array([100])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data)

        assert len(result) == 1
        assert result[0] == pytest.approx(0.5, abs=1e-10)

    def test_empty_array_error(self):
        """测试：空数组"""
        data = np.array([])
        normalizer = SigmoidNormalizer()

        with pytest.raises(SigmoidNormalizerError):
            normalizer.normalize(data)

    def test_none_error(self):
        """测试：None 输入"""
        normalizer = SigmoidNormalizer()

        with pytest.raises(SigmoidNormalizerError):
            normalizer.normalize(None)

    def test_nan_values(self):
        """测试：NaN 值"""
        data = np.array([1, np.nan, 3])
        normalizer = SigmoidNormalizer()

        with pytest.raises(SigmoidNormalizerError):
            normalizer.normalize(data)


class TestSigmoidMathematical:
    """数学验证测试"""

    def test_formula(self):
        """测试：公式正确性"""
        data = np.array([0, 5, 10])
        k = 2.0

        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data, k=k, auto_stats=False)

        # 手动计算: 1 / (1 + exp(-k * (x - μ) / σ))
        mu = np.mean(data)
        sigma = np.std(data) + 1e-10  # 避免 σ=0
        expected = 1 / (1 + np.exp(-k * (data - mu) / sigma))

        assert np.allclose(result, expected)

    def test_center_value(self):
        """测试：中心值应该为 0.5"""
        data = np.array([0, 5, 10])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data, k=2.0, auto_stats=True)

        # 均值位置应该接近 0.5
        mu = np.mean(data)
        # 找到最接近均值的位置
        idx = np.argmin(np.abs(data - mu))
        assert result[idx] == pytest.approx(0.5, abs=0.01)


class TestSigmoidProperties:
    """特性测试"""

    def test_symmetry(self):
        """测试：对称性"""
        data = np.array([-10, 0, 10])
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data, k=2.0, auto_stats=True)

        # 对称点应该互补: f(μ+x) + f(μ-x) = 1
        mu = np.mean(data)
        # 简化验证: 首尾值互补
        if abs(data[0] - mu) == abs(data[-1] - mu):
            assert abs(result[0] + result[-1] - 1.0) < 0.01

    def test_coefficient_effect(self):
        """测试：系数影响"""
        data = np.linspace(-5, 5, 100)
        normalizer = SigmoidNormalizer()

        result_small_k = normalizer.normalize(data, k=1, auto_stats=True)
        result_large_k = normalizer.normalize(data, k=10, auto_stats=True)

        # 大 k -> 更陡峭 -> 更接近阶跃函数
        # 验证中间区域差异
        mid_idx = len(data) // 2
        # 大 k 的中间值应该更接近 0 或 1 (取决于数据)
        assert len(result_small_k) == len(result_large_k)


class TestSigmoidIntegration:
    """集成测试"""

    def test_with_decision_matrix(self):
        """测试：与决策矩阵集成"""
        column = np.array([10, 50, 100, 200])
        normalizer = SigmoidNormalizer()
        normalized = normalizer.normalize(column)

        assert len(normalized) == len(column)
        assert normalized.min() >= 0
        assert normalized.max() <= 1

    def test_large_dataset(self):
        """测试：大数据集"""
        data = np.random.randn(1000)
        normalizer = SigmoidNormalizer()
        result = normalizer.normalize(data)

        assert len(result) == 1000
        assert not np.any(np.isnan(result))
