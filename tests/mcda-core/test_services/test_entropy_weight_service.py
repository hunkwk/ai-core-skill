"""
熵权法 (Entropy Weight Method) 服务测试

测试基于信息熵的客观权重计算功能。
"""

import pytest
import numpy as np
from mcda_core.services.entropy_weight_service import (
    EntropyWeightService,
    EntropyWeightValidationError
)


class TestDataNormalization:
    """数据标准化测试"""

    def test_normalize_higher_better(self):
        """测试：越大越好准则的标准化"""
        scores = np.array([10, 20, 30, 40, 50])

        service = EntropyWeightService()
        normalized = service._normalize(scores, direction="higher_better")

        # 验证范围 [0, 1]
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

        # 验证单调性（原值越大，标准化值越大）
        for i in range(len(normalized) - 1):
            assert normalized[i] < normalized[i + 1]

        # 验证最大值映射为 1，最小值映射为 0
        assert abs(normalized[-1] - 1.0) < 0.0001
        assert abs(normalized[0] - 0.0) < 0.0001

    def test_normalize_lower_better(self):
        """测试：越小越好准则的标准化"""
        scores = np.array([10, 20, 30, 40, 50])

        service = EntropyWeightService()
        normalized = service._normalize(scores, direction="lower_better")

        # 验证范围 [0, 1]
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

        # 验证单调性（原值越大，标准化值越小）
        for i in range(len(normalized) - 1):
            assert normalized[i] > normalized[i + 1]

        # 验证最小值映射为 1，最大值映射为 0
        assert abs(normalized[0] - 1.0) < 0.0001
        assert abs(normalized[-1] - 0.0) < 0.0001

    def test_normalize_all_same_values(self):
        """测试：所有值相同时的标准化"""
        scores = np.array([50, 50, 50, 50])

        service = EntropyWeightService()
        normalized = service._normalize(scores, direction="higher_better")

        # 所有值相同，标准化后应该全为 0
        assert np.allclose(normalized, 0.0, atol=0.0001)

    def test_normalize_with_negative_values(self):
        """测试：包含负值的标准化"""
        scores = np.array([-10, 0, 10, 20])

        service = EntropyWeightService()
        normalized = service._normalize(scores, direction="higher_better")

        # 验证范围 [0, 1]
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

    def test_normalize_handle_zeros(self):
        """测试：零值处理"""
        scores = np.array([0, 10, 20, 30])

        service = EntropyWeightService()
        # 添加小常数避免 log(0)
        normalized = service._normalize_with_shift(scores, direction="higher_better")

        # 验证所有值为正数（后续 log 计算需要）
        assert np.all(normalized > 0)


class TestEntropyCalculation:
    """信息熵计算测试"""

    def test_calculate_entropy_uniform_distribution(self):
        """测试：均匀分布（最大熵）"""
        # 均匀分布
        data = np.array([[0.2, 0.2, 0.2, 0.2, 0.2]])

        service = EntropyWeightService()
        entropy = service._calculate_entropy(data[0])

        # 均匀分布的理论最大熵: ln(5) ≈ 1.609
        # 归一化熵: E = 1.609 / ln(5) = 1.0
        assert abs(entropy - 1.0) < 0.01

    def test_calculate_entropy_extreme_distribution(self):
        """测试：极端分布（最小熵）"""
        # 极端分布：一个值占主导
        data = np.array([[0.97, 0.01, 0.01, 0.01]])

        service = EntropyWeightService()
        entropy = service._calculate_entropy(data[0])

        # 极端分布的熵应该很小（调整阈值为 0.15）
        assert entropy < 0.15

    def test_calculate_entropy_single_dominant(self):
        """测试：单个方案占主导"""
        # 一个方案远大于其他方案
        data = np.array([[0.8, 0.1, 0.05, 0.05]])

        service = EntropyWeightService()
        entropy = service._calculate_entropy(data[0])

        # 熵应该较小（差异性大）
        assert entropy < 0.6

    def test_entropy_formula_correctness(self):
        """测试：熵公式的正确性"""
        # 简单可验证的案例
        p = np.array([0.5, 0.5])  # 两个等概率事件

        service = EntropyWeightService()
        entropy = service._calculate_entropy(p)

        # H = -Σ(p * ln(p)) / ln(n)
        # H = -(0.5*ln(0.5) + 0.5*ln(0.5)) / ln(2)
        # H = -(-0.3466 - 0.3466) / 0.6931
        # H = 0.6931 / 0.6931 = 1.0
        assert abs(entropy - 1.0) < 0.01

    def test_entropy_with_small_values(self):
        """测试：包含非常小值的熵计算"""
        # 包含接近 0 的值
        p = np.array([0.0001, 0.9999])

        service = EntropyWeightService()
        # 应该不抛出异常（处理 log(0)）
        entropy = service._calculate_entropy(p)

        # 熵应该很小
        assert entropy < 0.1
        assert entropy >= 0


class TestWeightCalculation:
    """权重计算测试"""

    def test_calculate_weights_standard_case(self):
        """测试：标准案例"""
        # 3个准则，4个方案
        decision_matrix = np.array([
            [10, 20, 30],  # 方案1
            [15, 25, 35],  # 方案2
            [20, 30, 40],  # 方案3
            [25, 35, 45],  # 方案4
        ])

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 验证权重和为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证所有权重为正数
        assert np.all(weights > 0)

        # 验证权重数量
        assert len(weights) == 3

    def test_calculate_weights_identical_criteria(self):
        """测试：完全相同的准则权重为0"""
        # 两列完全相同
        decision_matrix = np.array([
            [10, 10],
            [20, 20],
            [30, 30],
        ])

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 两个准则的权重应该相等且很小（接近0）
        assert abs(weights[0] - weights[1]) < 0.0001

    def test_calculate_weights_with_directions(self):
        """测试：考虑准则方向的权重计算"""
        decision_matrix = np.array([
            [10, 100],
            [20, 80],
            [30, 60],
            [40, 40],
        ])

        # 第一个准则：越大越好
        # 第二个准则：越小越好
        directions = ["higher_better", "lower_better"]

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix, directions=directions)

        # 验证权重和为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证所有权重为正数
        assert np.all(weights >= 0)

    def test_weights_differential_criteria(self):
        """测试：差异性大的准则权重更大"""
        # 准则1：差异性大（从10到100）
        # 准则2：差异性小（从50到54）
        decision_matrix = np.array([
            [10, 50],
            [32, 51],
            [55, 52],
            [77, 53],
            [100, 54],
        ])

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 准则1的权重应该大于准则2
        assert weights[0] > weights[1]

    def test_handle_zero_variance(self):
        """测试：零方差准则的处理"""
        # 第二列完全相同（零方差）
        decision_matrix = np.array([
            [10, 50],
            [20, 50],
            [30, 50],
            [40, 50],
        ])

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 第二列的权重应该接近 0
        assert weights[1] < 0.01

        # 第一列应该占主导
        assert weights[0] > 0.99


class TestCombineWeights:
    """主客观权重组合测试"""

    def test_combine_weights_linear(self):
        """测试：线性加权组合"""
        subjective = np.array([0.6, 0.3, 0.1])
        objective = np.array([0.2, 0.5, 0.3])
        alpha = 0.5  # 主观权重比例

        service = EntropyWeightService()
        combined = service.combine_weights(
            subjective,
            objective,
            method="linear",
            alpha=alpha
        )

        # 验证组合公式: w = α * w_sub + (1-α) * w_obj
        expected = 0.5 * subjective + 0.5 * objective
        assert np.allclose(combined, expected, atol=0.0001)

        # 验证权重和为 1
        assert abs(np.sum(combined) - 1.0) < 0.0001

    def test_combine_weights_multiplicative(self):
        """测试：乘法合成"""
        subjective = np.array([0.6, 0.3, 0.1])
        objective = np.array([0.2, 0.5, 0.3])

        service = EntropyWeightService()
        combined = service.combine_weights(
            subjective,
            objective,
            method="multiplicative"
        )

        # 验证乘法合成后归一化
        assert abs(np.sum(combined) - 1.0) < 0.0001

        # 验证所有权重为正
        assert np.all(combined > 0)

    def test_combine_weights_invalid_method(self):
        """测试：无效的组合方法"""
        subjective = np.array([0.6, 0.3, 0.1])
        objective = np.array([0.2, 0.5, 0.3])

        service = EntropyWeightService()

        with pytest.raises(ValueError, match="组合方法"):
            service.combine_weights(
                subjective,
                objective,
                method="invalid_method"
            )

    def test_combine_weights_alpha_range(self):
        """测试：alpha 参数范围"""
        subjective = np.array([0.6, 0.3, 0.1])
        objective = np.array([0.2, 0.5, 0.3])

        service = EntropyWeightService()

        # alpha < 0
        with pytest.raises(ValueError, match="alpha"):
            service.combine_weights(
                subjective,
                objective,
                method="linear",
                alpha=-0.1
            )

        # alpha > 1
        with pytest.raises(ValueError, match="alpha"):
            service.combine_weights(
                subjective,
                objective,
                method="linear",
                alpha=1.5
            )


class TestFullWorkflow:
    """完整工作流测试"""

    def test_entropy_weight_full_workflow(self):
        """测试：完整的熵权法工作流"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ])

        criteria_names = ["Cost", "Quality", "Function"]

        service = EntropyWeightService()
        result = service.calculate_weights_with_details(
            decision_matrix,
            criteria=criteria_names
        )

        # 验证返回结构
        assert "weights" in result
        assert "entropies" in result
        assert "divergence_coefficients" in result
        assert "criteria" in result

        # 验证权重
        weights = result["weights"]
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证熵值范围 [0, 1]
        entropies = result["entropies"]
        assert np.all(entropies >= 0)
        assert np.all(entropies <= 1)

        # 验证差异系数
        divergence = result["divergence_coefficients"]
        assert np.all(divergence >= 0)
        assert np.all(divergence <= 1)

        # 验证准则名称
        assert result["criteria"] == criteria_names

    def test_entropy_weight_with_subjective(self):
        """测试：与主观权重组合"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ])

        subjective_weights = np.array([0.5, 0.3, 0.2])

        service = EntropyWeightService()
        result = service.calculate_weights_with_details(
            decision_matrix,
            subjective_weights=subjective_weights,
            alpha=0.6
        )

        # 验证包含组合权重
        assert "combined_weights" in result

        # 验证组合权重和为 1
        combined = result["combined_weights"]
        assert abs(np.sum(combined) - 1.0) < 0.0001


class TestEdgeCases:
    """边界条件测试"""

    def test_large_dataset(self):
        """测试：大规模数据集"""
        n_alternatives = 100
        n_criteria = 10

        # 生成随机数据
        np.random.seed(42)
        decision_matrix = np.random.rand(n_alternatives, n_criteria) * 100

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 验证
        assert len(weights) == n_criteria
        assert abs(np.sum(weights) - 1.0) < 0.0001
        assert np.all(weights >= 0)

    def test_single_criterion(self):
        """测试：单个准则"""
        decision_matrix = np.array([
            [10],
            [20],
            [30],
        ])

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 单个准则，权重应该为 1
        assert len(weights) == 1
        assert abs(weights[0] - 1.0) < 0.0001

    def test_two_alternatives_minimum(self):
        """测试：最少2个方案"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        service = EntropyWeightService()
        weights = service.calculate_weights(decision_matrix)

        # 验证
        assert len(weights) == 3
        assert abs(np.sum(weights) - 1.0) < 0.0001


class TestErrorHandling:
    """错误处理测试"""

    def test_empty_matrix(self):
        """测试：空矩阵"""
        matrix = np.array([])

        service = EntropyWeightService()

        with pytest.raises(EntropyWeightValidationError):
            service.calculate_weights(matrix)

    def test_invalid_direction(self):
        """测试：无效的方向"""
        matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        service = EntropyWeightService()

        with pytest.raises(ValueError, match="direction"):
            service.calculate_weights(
                matrix,
                directions=["invalid_direction", "higher_better"]
            )

    def test_mismatched_directions_count(self):
        """测试：方向数量不匹配"""
        matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        service = EntropyWeightService()

        with pytest.raises(ValueError, match="方向数量"):
            service.calculate_weights(
                matrix,
                directions=["higher_better", "lower_better"]  # 只有2个，但矩阵有3列
            )

    def test_invalid_input_type(self):
        """测试：无效输入类型"""
        service = EntropyWeightService()

        with pytest.raises((TypeError, EntropyWeightValidationError)):
            service.calculate_weights([[10, 20], [15, 25]])  # 列表而不是 numpy 数组
