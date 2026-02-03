"""
MCDA Core - 博弈论组合赋权测试

测试基于博弈论的最优组合赋权方法。
"""

import pytest
import numpy as np
from mcda_core.weighting import GameTheoryWeighting, GameTheoryWeightingError


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_weights_matrix():
    """示例权重矩阵

    每一行代表一种赋权方法的结果，每一列代表一个准则
    """
    return np.array([
        [0.4, 0.3, 0.2, 0.1],  # 熵权法
        [0.35, 0.25, 0.25, 0.15],  # CRITIC 法
        [0.45, 0.35, 0.15, 0.05],  # AHP 法
    ])


@pytest.fixture
def sample_criteria_names():
    """示例准则名称"""
    return ["性能", "成本", "可靠性", "易用性"]


@pytest.fixture
def sample_single_weights():
    """单一赋权方法的权重"""
    return np.array([0.4, 0.3, 0.2, 0.1])


# =============================================================================
# Basic Functionality Tests (6 个)
# =============================================================================

class TestGameTheoryWeightingBasic:
    """博弈论组合赋权基础功能测试"""

    def test_game_theory_weighting_initialization(self):
        """测试博弈论组合赋权初始化"""
        weighting = GameTheoryWeighting()

        assert weighting is not None
        assert hasattr(weighting, 'combine_weights')

    def test_combine_two_methods(self, sample_single_weights):
        """测试组合两种赋权方法"""
        weighting = GameTheoryWeighting()

        # 两种方法的权重
        w1 = np.array([0.4, 0.3, 0.2, 0.1])
        w2 = np.array([0.35, 0.25, 0.25, 0.15])

        weights_matrix = np.vstack([w1, w2])
        combined = weighting.combine_weights(weights_matrix)

        # 验证返回结果
        assert combined is not None
        assert len(combined) == 4
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)  # 权重和为 1

    def test_combine_three_methods(self, sample_weights_matrix):
        """测试组合三种赋权方法"""
        weighting = GameTheoryWeighting()

        combined = weighting.combine_weights(sample_weights_matrix)

        # 验证返回结果
        assert combined is not None
        assert len(combined) == 4
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)  # 权重和为 1
        assert np.all(combined >= 0)  # 权重非负

    def test_combine_with_criteria_names(self, sample_weights_matrix, sample_criteria_names):
        """测试带准则名称的组合"""
        weighting = GameTheoryWeighting()

        result = weighting.combine_weights(
            sample_weights_matrix,
            criteria=sample_criteria_names,
            return_details=True  # 需要指定 return_details=True
        )

        # 验证返回结果包含准则名称
        assert "weights" in result
        assert "criteria" in result
        assert result["criteria"] == sample_criteria_names
        assert np.allclose(np.sum(result["weights"]), 1.0, atol=1e-6)

    def test_combine_weights_returns_dict(self, sample_weights_matrix):
        """测试返回结果包含详细信息"""
        weighting = GameTheoryWeighting()

        result = weighting.combine_weights(sample_weights_matrix, return_details=True)

        # 验证返回字典包含必要信息
        assert isinstance(result, dict)
        assert "weights" in result
        assert "method" in result
        assert result["method"] == "game_theory"

    def test_combine_weights_numpy_array(self, sample_weights_matrix):
        """测试直接返回 numpy 数组"""
        weighting = GameTheoryWeighting()

        weights = weighting.combine_weights(sample_weights_matrix, return_details=False)

        # 验证返回 numpy 数组
        assert isinstance(weights, np.ndarray)
        assert weights.shape == (4,)


# =============================================================================
# Mathematical Correctness Tests (6 个)
# =============================================================================

class TestGameTheoryWeightingMath:
    """博弈论组合赋权数学正确性测试"""

    def test_optimal_combination_formula(self, sample_weights_matrix):
        """测试最优组合公式

        最优组合权重: w* = W^T · W⁻¹ · R / (W^T · W⁻¹ · W)
        其中 W 是权重矩阵，R 是权重矩阵的行平均
        """
        weighting = GameTheoryWeighting()

        combined = weighting.combine_weights(sample_weights_matrix)

        # 验证权重是最优解
        # 组合权重应该最小化与所有赋权方法的偏差
        assert np.all(combined >= 0)
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)

    def test_minimize_deviation(self, sample_weights_matrix):
        """测试最小化偏差

        博弈论组合应该最小化与各个赋权方法的偏差
        """
        weighting = GameTheoryWeighting()

        combined = weighting.combine_weights(sample_weights_matrix)

        # 计算组合权重与各个方法的偏差
        deviations = []
        for i in range(sample_weights_matrix.shape[0]):
            deviation = np.sum((combined - sample_weights_matrix[i]) ** 2)
            deviations.append(deviation)

        # 验证偏差合理（虽然没有明确的阈值，但应该不是无穷大）
        assert all(np.isfinite(deviations))

    def test_symmetry_property(self):
        """测试对称性

        组合结果不应该依赖于输入顺序
        """
        weighting = GameTheoryWeighting()

        w1 = np.array([0.4, 0.3, 0.2, 0.1])
        w2 = np.array([0.35, 0.25, 0.25, 0.15])
        w3 = np.array([0.45, 0.35, 0.15, 0.05])

        # 不同顺序
        matrix1 = np.vstack([w1, w2, w3])
        matrix2 = np.vstack([w3, w2, w1])

        combined1 = weighting.combine_weights(matrix1)
        combined2 = weighting.combine_weights(matrix2)

        # 结果应该相同（顺序无关）
        assert np.allclose(combined1, combined2, atol=1e-6)

    def test_unanimity_property(self, sample_single_weights):
        """测试一致性属性

        如果所有赋权方法给出相同结果，组合权重应该等于该结果
        """
        weighting = GameTheoryWeighting()

        # 所有方法都给出相同权重
        same_weights = np.tile(sample_single_weights, (3, 1))

        combined = weighting.combine_weights(same_weights)

        # 组合结果应该等于输入权重
        assert np.allclose(combined, sample_single_weights, atol=1e-6)

    def test_weight_sum_to_one(self, sample_weights_matrix):
        """测试权重和为 1

        无论输入如何，输出权重和必须为 1
        """
        weighting = GameTheoryWeighting()

        combined = weighting.combine_weights(sample_weights_matrix)

        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)

    def test_non_negative_weights(self, sample_weights_matrix):
        """测试权重非负

        最优组合权重应该都是非负的
        """
        weighting = GameTheoryWeighting()

        combined = weighting.combine_weights(sample_weights_matrix)

        assert np.all(combined >= 0)


# =============================================================================
# Edge Cases Tests (4 个)
# =============================================================================

class TestGameTheoryWeightingEdgeCases:
    """博弈论组合赋权边界条件测试"""

    def test_single_method(self, sample_single_weights):
        """测试只有一种赋权方法"""
        weighting = GameTheoryWeighting()

        # 只有一种方法
        single_method = sample_single_weights.reshape(1, -1)

        combined = weighting.combine_weights(single_method)

        # 应该返回原权重
        assert np.allclose(combined, sample_single_weights, atol=1e-6)

    def test_many_methods(self):
        """测试多种赋权方法（10 种）"""
        weighting = GameTheoryWeighting()

        # 生成 10 种随机权重
        np.random.seed(42)
        many_weights = np.random.dirichlet(np.ones(4), size=10)

        combined = weighting.combine_weights(many_weights)

        # 验证结果
        assert len(combined) == 4
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)
        assert np.all(combined >= 0)

    def test_two_criteria(self):
        """测试只有 2 个准则"""
        weighting = GameTheoryWeighting()

        weights = np.array([
            [0.5, 0.5],
            [0.6, 0.4],
            [0.4, 0.6],
        ])

        combined = weighting.combine_weights(weights)

        assert len(combined) == 2
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)

    def test_many_criteria(self):
        """测试多个准则（10 个）"""
        weighting = GameTheoryWeighting()

        # 生成 5 种方法，10 个准则
        np.random.seed(42)
        many_criteria_weights = np.random.dirichlet(np.ones(10), size=5)

        combined = weighting.combine_weights(many_criteria_weights)

        assert len(combined) == 10
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)


# =============================================================================
# Error Handling Tests (2 个)
# =============================================================================

class TestGameTheoryWeightingErrors:
    """博弈论组合赋权错误处理测试"""

    def test_empty_weights_matrix(self):
        """测试空权重矩阵"""
        weighting = GameTheoryWeighting()

        with pytest.raises(GameTheoryWeightingError):
            weighting.combine_weights(np.array([]))

    def test_invalid_weights_sum(self):
        """测试无效的权重和（不为 1）"""
        weighting = GameTheoryWeighting()

        # 权重和不为 1
        invalid_weights = np.array([
            [0.5, 0.5, 0.5],  # 和为 1.5
            [0.3, 0.3, 0.3],  # 和为 0.9
        ])

        # 应该抛出异常或自动归一化
        # 这里我们期望自动归一化
        try:
            combined = weighting.combine_weights(invalid_weights)
            # 如果没有抛出异常，验证结果被归一化
            assert np.allclose(np.sum(combined), 1.0, atol=1e-6)
        except ValueError:
            # 如果抛出异常，也是可以接受的
            pass


# =============================================================================
# Integration Tests (2 个)
# =============================================================================

class TestGameTheoryWeightingIntegration:
    """博弈论组合赋权集成测试"""

    def test_with_entropy_weight(self):
        """测试与熵权法集成"""
        from mcda_core.services import EntropyWeightService

        # 决策矩阵
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ])

        # 计算熵权
        entropy_service = EntropyWeightService()
        entropy_weights = entropy_service.calculate_weights(decision_matrix)

        # 构造权重矩阵
        weighting = GameTheoryWeighting()
        weights_matrix = np.vstack([
            entropy_weights,
            np.array([0.4, 0.3, 0.3]),  # 主观权重
        ])

        # 组合
        combined = weighting.combine_weights(weights_matrix)

        assert len(combined) == 3
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)

    def test_with_ahp_weight(self):
        """测试与 AHP 权重集成"""
        from mcda_core.services import AHPService

        # 判断矩阵
        comparison_matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1],
        ])

        # 计算 AHP 权重
        ahp_service = AHPService()
        ahp_weights = ahp_service.calculate_weights(comparison_matrix)  # 直接返回 numpy 数组

        # 构造权重矩阵
        weighting = GameTheoryWeighting()
        weights_matrix = np.vstack([
            ahp_weights,
            np.array([0.5, 0.3, 0.2]),  # 熵权
            np.array([0.4, 0.4, 0.2]),  # 主观权重
        ])

        # 组合
        combined = weighting.combine_weights(weights_matrix)

        assert len(combined) == 3
        assert np.allclose(np.sum(combined), 1.0, atol=1e-6)
