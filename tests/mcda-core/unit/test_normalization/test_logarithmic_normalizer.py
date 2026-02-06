"""
Logarithmic 标准化测试

测试对数标准化功能。
"""

import pytest
import numpy as np
from mcda_core.normalization.logarithmic_normalizer import (
    LogarithmicNormalizer,
    LogarithmicNormalizerError
)


class TestLogarithmicBasic:
    """基本功能测试"""

    def test_positive_values_benefit(self):
        """测试：正数数据（效益型）"""
        data = np.array([1, 10, 100, 1000])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 验证结果在 [0, 1] 范围内
        assert result.min() >= 0
        assert result.max() <= 1

        # 验证单调性：原值越大，标准化后越大
        assert result[0] < result[1] < result[2] < result[3]

    def test_positive_values_cost(self):
        """测试：正数数据（成本型）"""
        data = np.array([10, 50, 100, 200])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=False)

        # 验证结果有效性（对数标准化的成本型可能 > 1）
        # 公式: log(max) / log(x)，最小值对应最大原始值
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

        # 验证单调性：原值越大，标准化后越小（成本型）
        # 成本型: 最小值标准化为 1，其他值可能 > 1
        assert result[-1] == pytest.approx(1.0, rel=1e-10)  # 最大原始值 -> 1
        assert result[0] > result[1] > result[2] > result[3]

    def test_with_zeros(self):
        """测试：包含零值"""
        data = np.array([0, 1, 10, 100])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 零值应该被正确处理（加偏移）
        assert len(result) == len(data)
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))

    def test_unifrom_values(self):
        """测试：所有值相同"""
        data = np.array([10, 10, 10, 10])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 所有值应该相同
        assert np.allclose(result, result[0])

    def test_single_value(self):
        """测试：单个值"""
        data = np.array([100])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 单个值应该标准化为 1
        assert len(result) == 1
        assert result[0] == pytest.approx(1.0, rel=1e-10)


class TestLogarithmicEdgeCases:
    """边界条件测试"""

    def test_very_small_values(self):
        """测试：非常小的值"""
        data = np.array([0.001, 0.01, 0.1, 1.0])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 应该正确处理小值
        assert len(result) == len(data)
        assert not np.any(np.isnan(result))

    def test_very_large_values(self):
        """测试：非常大的值"""
        data = np.array([1e6, 1e7, 1e8, 1e9])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 应该正确处理大值
        assert len(result) == len(data)
        assert not np.any(np.isnan(result))

    def test_mixed_magnitude(self):
        """测试：混合数量级"""
        data = np.array([0.1, 1, 10, 100, 1000, 10000])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 应该正确处理混合数量级
        assert result.min() >= 0
        assert result.max() <= 1

    def test_negative_values_error(self):
        """测试：负值应该抛出错误"""
        data = np.array([-10, 0, 10])

        normalizer = LogarithmicNormalizer()

        # 负值应该抛出错误
        with pytest.raises(LogarithmicNormalizerError):
            normalizer.normalize(data, maximize=True)

    def test_all_zeros_error(self):
        """测试：全零数据应该抛出错误"""
        data = np.array([0, 0, 0])

        normalizer = LogarithmicNormalizer()

        # 全零应该抛出错误
        with pytest.raises(LogarithmicNormalizerError):
            normalizer.normalize(data, maximize=True)

    def test_empty_array_error(self):
        """测试：空数组应该抛出错误"""
        data = np.array([])

        normalizer = LogarithmicNormalizer()

        # 空数组应该抛出错误
        with pytest.raises(LogarithmicNormalizerError):
            normalizer.normalize(data, maximize=True)


class TestLogarithmicMathematical:
    """数学验证测试"""

    def test_normalization_formula_benefit(self):
        """测试：效益型公式正确性"""
        data = np.array([1, 10, 100])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 手动计算验证（包含偏移）
        # x'_ij = log(x_ij + offset) / log(max(x_j) + offset)
        offset = normalizer.offset
        max_val = np.max(data)
        expected = np.log(data + offset) / np.log(max_val + offset)

        assert np.allclose(result, expected)

    def test_normalization_formula_cost(self):
        """测试：成本型公式正确性"""
        data = np.array([10, 50, 100])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=False)

        # 手动计算验证（包含偏移）
        # x'_ij = log(max(x_j) + offset) / log(x_ij + offset)
        offset = normalizer.offset
        max_val = np.max(data)
        expected = np.log(max_val + offset) / np.log(data + offset)

        assert np.allclose(result, expected)

    def test_with_offset_formula(self):
        """测试：带零值的偏移公式"""
        data = np.array([0, 1, 10, 100])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 验证偏移后的计算
        # log(x + offset) / log(max + offset)
        # 其中 offset = 1 (默认)
        offset = 1
        max_val = np.max(data)
        expected = np.log(data + offset) / np.log(max_val + offset)

        assert np.allclose(result, expected)


class TestLogarithmicProperties:
    """特性测试"""

    def test_benefit_max_value_is_one(self):
        """测试：效益型最大值为 1"""
        data = np.array([1, 10, 100, 1000])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 最大值应该为 1
        assert result.max() == pytest.approx(1.0, rel=1e-10)

    def test_cost_min_value_is_one(self):
        """测试：成本型最小值为 1"""
        data = np.array([10, 50, 100, 200])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=False)

        # 最小值应该为 1
        assert result.min() == pytest.approx(1.0, rel=1e-10)

    def test_logarithmic_compression(self):
        """测试：对数压缩特性"""
        data = np.array([1, 10, 100, 1000])

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 对数标准化应该压缩大值之间的差距
        # 原始比例: 1:10:100:1000
        # 标准化后差距应该更小
        diff_original = np.diff(data)
        diff_normalized = np.diff(result)

        # 标准化后的差异应该相对更均匀
        assert diff_normalized.max() / (diff_normalized.min() + 1e-10) < \
               diff_original.max() / (diff_original.min() + 1e-10)

    def test_reproducibility(self):
        """测试：结果可重现性"""
        data = np.array([1, 10, 100])

        normalizer = LogarithmicNormalizer()
        result1 = normalizer.normalize(data, maximize=True)
        result2 = normalizer.normalize(data, maximize=True)

        # 多次调用结果应该相同
        assert np.array_equal(result1, result2)


class TestLogarithmicErrorHandling:
    """错误处理测试"""

    def test_none_input(self):
        """测试：None 输入"""
        normalizer = LogarithmicNormalizer()

        with pytest.raises(LogarithmicNormalizerError):
            normalizer.normalize(None, maximize=True)

    def test_list_input(self):
        """测试：列表输入（应该自动转换）"""
        data = [1, 10, 100]

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 应该自动转换为 numpy array
        assert isinstance(result, np.ndarray)

    def test_invalid_type(self):
        """测试：无效类型"""
        normalizer = LogarithmicNormalizer()

        with pytest.raises(LogarithmicNormalizerError):
            normalizer.normalize("invalid", maximize=True)

    def test_nan_values(self):
        """测试：包含 NaN 的数据"""
        data = np.array([1, np.nan, 100])

        normalizer = LogarithmicNormalizer()

        # NaN 应该抛出错误或返回有效结果
        try:
            result = normalizer.normalize(data, maximize=True)
            # 如果不抛错，应该过滤 NaN
            assert not np.any(np.isnan(result))
        except LogarithmicNormalizerError:
            # 或者抛出错误
            pass


class TestLogarithmicIntegration:
    """集成测试"""

    def test_with_decision_matrix(self):
        """测试：与决策矩阵集成"""
        # 模拟决策矩阵的一列
        column = np.array([10, 50, 100, 200])

        normalizer = LogarithmicNormalizer()
        normalized = normalizer.normalize(column, maximize=False)

        # 验证结果可用于 MCDA 计算
        assert len(normalized) == len(column)
        assert not np.any(np.isnan(normalized))
        # 成本型对数标准化的最小值为 1，其他值可能 > 1
        assert normalized[-1] == pytest.approx(1.0, rel=1e-10)

    def test_comparison_with_linear(self):
        """测试：与线性标准化对比"""
        data = np.array([1, 10, 100, 1000])

        # 对数标准化
        log_normalizer = LogarithmicNormalizer()
        log_result = log_normalizer.normalize(data, maximize=True)

        # 对数标准化应该更"压缩"极值
        # 最大值都是 1
        assert log_result.max() == pytest.approx(1.0)

        # 但对数标准化的最小值应该更大（因为压缩效应）
        assert log_result.min() > 0

    def test_large_dataset(self):
        """测试：大数据集性能"""
        # 1000 个数据点
        data = np.random.uniform(1, 1000, 1000)

        normalizer = LogarithmicNormalizer()
        result = normalizer.normalize(data, maximize=True)

        # 应该能处理大数据集
        assert len(result) == 1000
        assert not np.any(np.isnan(result))
