"""
AHP (层次分析法) 服务测试

测试 AHP 权重计算和一致性检验功能。
"""

import pytest
import numpy as np
from mcda_core.services.ahp_service import AHPService, AHPValidationError


class TestPairwiseMatrixValidation:
    """成对比较矩阵验证测试"""

    def test_valid_pairwise_matrix(self):
        """测试：有效的成对比较矩阵"""
        # Saaty 标准案例
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        # 应该不抛出异常
        service._validate_matrix(matrix)

    def test_invalid_matrix_not_reciprocal(self):
        """测试：不满足互反性的矩阵"""
        # a_12 = 3, 但 a_21 = 2 (应该是 1/3)
        matrix = np.array([
            [1, 3, 5],
            [2, 1, 2],  # a_21 错误
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        with pytest.raises(AHPValidationError, match="互反性"):
            service._validate_matrix(matrix)

    def test_invalid_matrix_diagonal_not_one(self):
        """测试：对角线不为1的矩阵"""
        matrix = np.array([
            [2, 3, 5],  # a_11 = 2, 应该是 1
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        with pytest.raises(AHPValidationError, match="对角线"):
            service._validate_matrix(matrix)

    def test_invalid_matrix_not_square(self):
        """测试：非方阵"""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2]
        ])  # 2x3 矩阵，不是方阵

        service = AHPService()
        with pytest.raises(AHPValidationError, match="方阵"):
            service._validate_matrix(matrix)

    def test_invalid_matrix_negative_values(self):
        """测试：包含负值的矩阵"""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, -1/2, 1]  # 负值
        ])

        service = AHPService()
        with pytest.raises(AHPValidationError, match="正数"):
            service._validate_matrix(matrix)


class TestWeightCalculation:
    """权重计算测试"""

    def test_calculate_weights_standard_saaty(self):
        """测试：标准 Saaty 3准则案例"""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 验证权重和为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证权重顺序：成本 > 质量 > 功能
        # 成本权重应该最大（因为其明显重要于其他准则）
        assert weights[0] > weights[1] > weights[2]

        # 验证权重在合理范围内
        # 期望: 成本 ≈ 0.65, 质量 ≈ 0.23, 功能 ≈ 0.12
        assert abs(weights[0] - 0.65) < 0.05  # 成本
        assert abs(weights[1] - 0.23) < 0.05  # 质量
        assert abs(weights[2] - 0.12) < 0.05  # 功能

    def test_calculate_weights_four_criteria(self):
        """测试：4准则案例"""
        matrix = np.array([
            [1, 3, 5, 7],
            [1/3, 1, 2, 4],
            [1/5, 1/2, 1, 2],
            [1/7, 1/4, 1/2, 1]
        ])

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 验证权重和为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证所有权重为正数
        assert np.all(weights > 0)

        # 验证权重递减
        for i in range(len(weights) - 1):
            assert weights[i] > weights[i + 1]

    def test_calculate_weights_minimum_size(self):
        """测试：最小 2x2 矩阵"""
        matrix = np.array([
            [1, 3],
            [1/3, 1]
        ])

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 验证权重和为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证权重合理
        assert weights[0] > weights[1]  # 第一个准则更重要

    def test_calculate_weights_equal_importance(self):
        """测试：所有准则同等重要"""
        matrix = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ])

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 验证权重相等
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected, atol=0.0001)

    def test_weights_are_normalized(self):
        """测试：权重归一化"""
        # 任意规模的矩阵
        n = 5
        np.random.seed(42)  # 固定随机种子
        matrix = np.ones((n, n))

        # 生成满足互反性的随机矩阵
        for i in range(n):
            for j in range(i + 1, n):
                value = np.random.uniform(1, 9)
                matrix[i, j] = value
                matrix[j, i] = 1 / value

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 验证权重和严格为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001


class TestConsistencyCheck:
    """一致性检验测试"""

    def test_consistency_ratio_acceptable(self):
        """测试：可接受的一致性比率 (CR < 0.1)"""
        # 高一致性矩阵
        matrix = np.array([
            [1, 2, 3],
            [1/2, 1, 2],
            [1/3, 1/2, 1]
        ])

        service = AHPService()
        cr = service.calculate_consistency_ratio(matrix)

        # CR 应该小于 0.1
        assert cr < 0.1

    def test_consistency_ratio_warning(self):
        """测试：一致性比率警告 (CR > 0.1)"""
        # 低一致性矩阵（故意构造不一致）
        matrix = np.array([
            [1, 5, 9],
            [1/5, 1, 7],
            [1/9, 1/7, 1]
        ])

        service = AHPService()
        cr = service.calculate_consistency_ratio(matrix)

        # CR 应该大于 0.1
        assert cr > 0.1

    def test_perfect_consistency(self):
        """测试：完美一致性矩阵"""
        # 完美一致：a_ik = a_ij * a_jk
        matrix = np.array([
            [1, 2, 4],
            [1/2, 1, 2],
            [1/4, 1/2, 1]
        ])

        service = AHPService()
        cr = service.calculate_consistency_ratio(matrix)

        # 完美一致性时，CR 应该接近 0
        assert cr < 0.01

    def test_calculate_lambda_max(self):
        """测试：计算最大特征值"""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        lambda_max = service._calculate_lambda_max(matrix, np.array([0.65, 0.23, 0.12]))

        # λ_max 应该大于等于 n (n=3)
        assert lambda_max >= 3.0

        # 对于可接受的一致性，λ_max 通常不会远大于 n
        assert lambda_max < 3.5

    def test_consistency_index_calculation(self):
        """测试：一致性指标计算"""
        n = 3
        lambda_max = 3.1

        service = AHPService()
        ci = service._calculate_consistency_index(lambda_max, n)

        # CI = (λ_max - n) / (n - 1)
        # CI = (3.1 - 3) / (3 - 1) = 0.1 / 2 = 0.05
        expected_ci = 0.05
        assert abs(ci - expected_ci) < 0.0001

    def test_random_index_lookup(self):
        """测试：随机一致性指标查找"""
        service = AHPService()

        # 测试标准 n 值
        assert service._get_random_index(1) == 0
        assert service._get_random_index(2) == 0
        assert abs(service._get_random_index(3) - 0.58) < 0.01
        assert abs(service._get_random_index(4) - 0.90) < 0.01
        assert abs(service._get_random_index(5) - 1.12) < 0.01
        assert abs(service._get_random_index(10) - 1.49) < 0.01

    def test_random_index_interpolation(self):
        """测试：随机一致性指标插值（n > 10）"""
        service = AHPService()

        # n=15 应该插值计算
        ri_15 = service._get_random_index(15)
        assert ri_15 > 1.49  # 应该大于 n=10 的值

        # n=20
        ri_20 = service._get_random_index(20)
        assert ri_20 > ri_15  # 应该继续增长


class TestFullWorkflow:
    """完整工作流测试"""

    def test_ahp_full_workflow(self):
        """测试：完整的 AHP 工作流"""
        # 准则：成本、质量、功能
        criteria_names = ["Cost", "Quality", "Function"]
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        result = service.calculate_weights_with_consistency(matrix, criteria=criteria_names)

        # 验证返回结构
        assert "weights" in result
        assert "consistency_ratio" in result
        assert "criteria" in result
        assert "lambda_max" in result

        # 验证权重
        weights = result["weights"]
        assert abs(np.sum(weights) - 1.0) < 0.0001

        # 验证一致性比率
        cr = result["consistency_ratio"]
        assert cr >= 0
        assert cr < 0.2  # 即使不一致，也不应该太离谱

        # 验证准则名称
        assert result["criteria"] == criteria_names

        # 验证最大特征值
        assert result["lambda_max"] >= 3.0

    def test_ahp_with_consistency_warning(self):
        """测试：AHP 一致性警告"""
        # 构造不一致的矩阵
        matrix = np.array([
            [1, 9, 9],
            [1/9, 1, 9],
            [1/9, 1/9, 1]
        ])

        service = AHPService()
        result = service.calculate_weights_with_consistency(matrix)

        # 验证一致性比率很高
        assert result["consistency_ratio"] > 0.3

        # 验证仍然返回结果
        assert "weights" in result
        assert abs(np.sum(result["weights"]) - 1.0) < 0.0001

    def test_ahp_criteria_names_optional(self):
        """测试：准则名称可选"""
        matrix = np.array([
            [1, 2, 3],
            [1/2, 1, 2],
            [1/3, 1/2, 1]
        ])

        service = AHPService()

        # 不提供准则名称
        result = service.calculate_weights(matrix)

        # 应该正常返回权重
        assert len(result) == 3
        assert abs(np.sum(result) - 1.0) < 0.0001


class TestEdgeCases:
    """边界条件测试"""

    def test_large_matrix(self):
        """测试：大规模矩阵 (10x10)"""
        n = 10

        # 构造相对一致的矩阵
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                value = 1 + (j - i) * 0.3  # 相对一致的递增
                matrix[i, j] = value
                matrix[j, i] = 1 / value

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 验证
        assert len(weights) == n
        assert abs(np.sum(weights) - 1.0) < 0.0001
        assert np.all(weights > 0)

    def test_nearly_equal_weights(self):
        """测试：接近相等的权重"""
        # 所有值都接近 1
        matrix = np.array([
            [1, 1.1, 0.9],
            [1/1.1, 1, 1.05],
            [1/0.9, 1/1.05, 1]
        ])

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 权重应该接近相等
        expected = np.array([1/3, 1/3, 1/3])
        assert np.allclose(weights, expected, atol=0.05)

    def test_extreme_importance(self):
        """测试：极端重要性差异"""
        matrix = np.array([
            [1, 9, 9],
            [1/9, 1, 1],
            [1/9, 1, 1]
        ])

        service = AHPService()
        weights = service.calculate_weights(matrix)

        # 第一个准则应该占主导地位
        assert weights[0] > 0.8  # 应该超过 80%
        assert weights[1] < 0.15
        assert weights[2] < 0.15


class TestErrorHandling:
    """错误处理测试"""

    def test_empty_matrix(self):
        """测试：空矩阵"""
        matrix = np.array([])

        service = AHPService()
        with pytest.raises(AHPValidationError):
            service._validate_matrix(matrix)

    def test_single_element_matrix(self):
        """测试：单元素矩阵 (1x1)"""
        matrix = np.array([[1]])

        service = AHPService()
        # 1x1 矩阵应该有效（单个准则）
        weights = service.calculate_weights(matrix)
        assert len(weights) == 1
        assert abs(weights[0] - 1.0) < 0.0001

    def test_matrix_with_zeros(self):
        """测试：包含零值的矩阵"""
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 0],  # 零值
            [1/5, 1/2, 1]
        ])

        service = AHPService()
        with pytest.raises(AHPValidationError):
            service._validate_matrix(matrix)

    def test_invalid_input_type(self):
        """测试：无效输入类型"""
        service = AHPService()

        # 传入列表而不是 numpy 数组
        with pytest.raises((TypeError, AHPValidationError)):
            service.calculate_weights([[1, 2], [1/2, 1]])
