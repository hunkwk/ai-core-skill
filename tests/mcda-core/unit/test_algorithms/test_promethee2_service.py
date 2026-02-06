"""
PROMETHEE-II 算法测试

测试基于偏好函数的排序方法。
"""

import pytest
import numpy as np
from mcda_core.algorithms.promethee2_service import (
    PROMETHEEService,
    PROMETHEEValidationError
)


class TestPreferenceFunctions:
    """偏好函数测试"""

    def test_usual_criterion(self):
        """测试：通常准则"""
        service = PROMETHEEService()

        # d ≤ 0: P(d) = 0
        assert service._usual_criterion(-5) == 0
        assert service._usual_criterion(0) == 0

        # d > 0: P(d) = 1
        assert service._usual_criterion(0.1) == 1
        assert service._usual_criterion(5) == 1

    def test_u_shape_criterion(self):
        """测试：U型准则"""
        service = PROMETHEEService()
        q = 2.0  # 无差异阈值

        # |d| ≤ q: P(d) = 0
        assert service._u_shape_criterion(-1.0, q) == 0
        assert service._u_shape_criterion(0, q) == 0
        assert service._u_shape_criterion(2.0, q) == 0

        # |d| > q: P(d) = 1
        assert service._u_shape_criterion(2.1, q) == 1
        assert service._u_shape_criterion(-3.0, q) == 1
        assert service._u_shape_criterion(5.0, q) == 1

    def test_v_shape_criterion(self):
        """测试：V型准则"""
        service = PROMETHEEService()
        p = 5.0  # 严格偏好阈值

        # d ≤ 0: P(d) = 0
        assert service._v_shape_criterion(-5, p) == 0
        assert service._v_shape_criterion(0, p) == 0

        # 0 < d ≤ p: P(d) = d/p
        assert abs(service._v_shape_criterion(2.5, p) - 0.5) < 0.0001
        assert abs(service._v_shape_criterion(5.0, p) - 1.0) < 0.0001

        # d > p: P(d) = 1
        assert service._v_shape_criterion(6.0, p) == 1
        assert service._v_shape_criterion(10.0, p) == 1

    def test_level_criterion(self):
        """测试：水平准则"""
        service = PROMETHEEService()
        q = 2.0  # 无差异阈值
        p = 5.0  # 严格偏好阈值

        # |d| ≤ q: P(d) = 0
        assert service._level_criterion(1.0, q, p) == 0
        assert service._level_criterion(-2.0, q, p) == 0

        # q < |d| ≤ p: P(d) = 0.5
        assert service._level_criterion(3.0, q, p) == 0.5
        assert service._level_criterion(-4.0, q, p) == 0.5

        # |d| > p: P(d) = 1
        assert service._level_criterion(6.0, q, p) == 1
        assert service._level_criterion(-5.1, q, p) == 1

    def test_v_shape_indifference(self):
        """测试：V型无差异准则"""
        service = PROMETHEEService()
        q = 2.0  # 无差异阈值
        p = 5.0  # 严格偏好阈值

        # |d| ≤ q: P(d) = 0
        assert service._v_shape_indifference(1.0, q, p) == 0
        assert service._v_shape_indifference(-2.0, q, p) == 0

        # q < |d| ≤ p: P(d) = (|d|-q)/(p-q)
        expected = (3.5 - 2.0) / (5.0 - 2.0)  # = 0.5
        assert abs(service._v_shape_indifference(3.5, q, p) - expected) < 0.0001

        # |d| > p: P(d) = 1
        assert service._v_shape_indifference(6.0, q, p) == 1

    def test_gaussian_criterion(self):
        """测试：高斯准则"""
        service = PROMETHEEService()
        s = 2.0  # 标准差参数

        # d = 0: P(0) = 0
        assert abs(service._gaussian_criterion(0, s) - 0) < 0.0001

        # d > 0: P(d) = 1 - exp(-d²/2σ²)
        # 当 d = σ 时: P = 1 - exp(-0.5) ≈ 0.3935
        expected = 1 - np.exp(-0.5)
        assert abs(service._gaussian_criterion(2.0, s) - expected) < 0.01

        # 当 d 很大时: P ≈ 1
        assert service._gaussian_criterion(10.0, s) > 0.99

    def test_preference_function_factory(self):
        """测试：偏好函数工厂方法"""
        service = PROMETHEEService()

        # 测试所有类型
        func_types = [
            "usual",
            "u_shape",
            "v_shape",
            "level",
            "v_shape_indifference",
            "gaussian"
        ]

        for func_type in func_types:
            func = service._get_preference_function(func_type)
            assert callable(func)

    def test_invalid_preference_function(self):
        """测试：无效的偏好函数类型"""
        service = PROMETHEEService()

        with pytest.raises(ValueError, match="偏好函数"):
            service._get_preference_function("invalid_type")


class TestPreferenceIndex:
    """偏好指数测试"""

    def test_calculate_preference_index(self):
        """测试：计算偏好指数"""
        # 简单案例：2个方案，2个准则
        decision_matrix = np.array([
            [10, 20],  # 方案 A
            [15, 25],  # 方案 B
        ])

        weights = np.array([0.6, 0.4])

        # 所有准则使用 usual 函数
        preference_functions = [
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()
        preference_index = service._calculate_preference_index(
            decision_matrix,
            weights,
            preference_functions
        )

        # 验证矩阵形状
        assert preference_index.shape == (2, 2)

        # 对角线应该为 0（自己对自己）
        assert abs(preference_index[0, 0] - 0) < 0.0001
        assert abs(preference_index[1, 1] - 0) < 0.0001

        # 验证 P(A, B) + P(B, A) 的关系
        # 对于 usual 函数，P(A, B) > 0 当 A 在某准则上优于 B
        assert preference_index[0, 1] >= 0
        assert preference_index[1, 0] >= 0

    def test_preference_matrix_properties(self):
        """测试：偏好矩阵性质"""
        # 3个方案
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        preference_functions = [
            {"type": "usual"},
            {"type": "u_shape", "q": 2.0},
            {"type": "v_shape", "p": 5.0}
        ]

        service = PROMETHEEService()
        preference_index = service._calculate_preference_index(
            decision_matrix,
            weights,
            preference_functions
        )

        # 验证对角线为 0
        np.fill_diagonal(preference_index, 0)
        assert np.allclose(np.diag(preference_index), 0)


class TestFlowCalculation:
    """流量计算测试"""

    def test_calculate_leaving_flow(self):
        """测试：计算离开流"""
        # 3个方案
        preference_matrix = np.array([
            [0.0, 0.6, 0.8],  # A 对 B, C 的偏好
            [0.4, 0.0, 0.5],  # B 对 A, C 的偏好
            [0.2, 0.5, 0.0],  # C 对 A, B 的偏好
        ])

        service = PROMETHEEService()
        leaving_flow = service._calculate_leaving_flow(preference_matrix)

        # A 的离开流: (0.6 + 0.8) / 3 = 0.467
        expected_a = (0.6 + 0.8) / 3
        assert abs(leaving_flow[0] - expected_a) < 0.001

        # 验证所有值非负
        assert np.all(leaving_flow >= 0)

    def test_calculate_entering_flow(self):
        """测试：计算进入流"""
        preference_matrix = np.array([
            [0.0, 0.6, 0.8],
            [0.4, 0.0, 0.5],
            [0.2, 0.5, 0.0],
        ])

        service = PROMETHEEService()
        entering_flow = service._calculate_entering_flow(preference_matrix)

        # A 的进入流: (0.4 + 0.2) / 3 = 0.2
        expected_a = (0.4 + 0.2) / 3
        assert abs(entering_flow[0] - expected_a) < 0.001

        # 验证所有值非负
        assert np.all(entering_flow >= 0)

    def test_calculate_net_flow(self):
        """测试：计算净流量"""
        leaving_flow = np.array([0.5, 0.3, 0.2])
        entering_flow = np.array([0.2, 0.4, 0.3])

        service = PROMETHEEService()
        net_flow = service._calculate_net_flow(leaving_flow, entering_flow)

        # Net flow = leaving - entering
        expected = np.array([0.3, -0.1, -0.1])
        assert np.allclose(net_flow, expected, atol=0.0001)

    def test_flow_symmetry(self):
        """测试：流量对称性"""
        # 对于偏好关系，P(a,b) + P(b,a) 不一定等于 1
        # 但净流量应该反映相对优势
        preference_matrix = np.array([
            [0.0, 0.7, 0.6],
            [0.3, 0.0, 0.8],
            [0.4, 0.2, 0.0],
        ])

        service = PROMETHEEService()

        leaving = service._calculate_leaving_flow(preference_matrix)
        entering = service._calculate_entering_flow(preference_matrix)
        net = service._calculate_net_flow(leaving, entering)

        # 所有净流量之和应该为 0
        assert abs(np.sum(net) - 0.0) < 0.0001


class TestRanking:
    """排序测试"""

    def test_promethee_ranking(self):
        """测试：完整排序"""
        decision_matrix = np.array([
            [10, 20, 30],  # A
            [15, 25, 35],  # B (全面优于 A)
            [20, 30, 40],  # C (全面优于 B)
        ])

        weights = np.array([0.5, 0.3, 0.2])

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        # 验证返回结构
        assert "rankings" in result
        assert "net_flows" in result
        assert "leaving_flows" in result
        assert "entering_flows" in result

        # C 应该排第一，B 第二，A 第三
        rankings = result["rankings"]
        assert rankings[0]["alternative"] == "A2"  # C
        assert rankings[1]["alternative"] == "A1"  # B
        assert rankings[2]["alternative"] == "A0"  # A

    def test_tie_handling(self):
        """测试：相同排名处理"""
        # A 和 C 在所有准则下相同
        decision_matrix = np.array([
            [10, 20],  # A
            [15, 25],  # B
            [10, 20],  # C (与 A 相同)
        ])

        weights = np.array([0.5, 0.5])

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        rankings = result["rankings"]
        net_flows = result["net_flows"]

        # A 和 C 的净流量应该相同
        assert abs(net_flows[0] - net_flows[2]) < 0.0001

    def test_ranking_with_alternative_names(self):
        """测试：带方案名称的排序"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
            [20, 30],
        ])

        weights = np.array([0.6, 0.4])

        preference_functions = [
            {"type": "v_shape", "p": 5.0},
            {"type": "u_shape", "q": 2.0}
        ]

        alternatives = ["Option A", "Option B", "Option C"]

        service = PROMETHEEService()
        result = service.rank(
            decision_matrix,
            weights,
            preference_functions,
            alternatives=alternatives
        )

        # 验证方案名称
        assert result["rankings"][0]["alternative"] == "Option C"
        assert result["rankings"][1]["alternative"] == "Option B"
        assert result["rankings"][2]["alternative"] == "Option A"


class TestFullWorkflow:
    """完整工作流测试"""

    def test_promethee_full_workflow(self):
        """测试：完整的 PROMETHEE 工作流"""
        # 供应商选择问题
        decision_matrix = np.array([
            [80, 5, 100],   # 供应商 A
            [90, 3, 120],   # 供应商 B
            [70, 7, 90],    # 供应商 C
        ])

        # 准则：质量(越高越好)、交货时间(越低越好)、价格(越低越好)
        weights = np.array([0.4, 0.3, 0.3])

        preference_functions = [
            {"type": "v_shape_indifference", "q": 5.0, "p": 15.0},  # 质量
            {"type": "level", "q": 1.0, "p": 3.0},                 # 时间
            {"type": "gaussian", "s": 10.0}                         # 价格
        ]

        alternatives = ["Supplier A", "Supplier B", "Supplier C"]

        service = PROMETHEEService()
        result = service.rank(
            decision_matrix,
            weights,
            preference_functions,
            alternatives=alternatives
        )

        # 验证返回结构
        assert "rankings" in result
        assert "net_flows" in result
        assert "leaving_flows" in result
        assert "entering_flows" in result
        assert "preference_matrix" in result

        # 验证流量范围
        net_flows = result["net_flows"]
        assert np.all(net_flows >= -1.0)
        assert np.all(net_flows <= 1.0)

        # 验证排名数量
        assert len(result["rankings"]) == 3

    def test_different_preference_functions(self):
        """测试：不同偏好函数组合"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.33, 0.33, 0.34])

        # 使用所有 6 种函数
        preference_functions = [
            {"type": "usual"},
            {"type": "u_shape", "q": 2.0},
            {"type": "v_shape", "p": 5.0}
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        # 应该成功排序
        assert "rankings" in result
        assert len(result["rankings"]) == 2


class TestEdgeCases:
    """边界条件测试"""

    def test_two_alternatives_minimum(self):
        """测试：最少2个方案"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = np.array([0.6, 0.4])

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        assert len(result["rankings"]) == 2

    def test_large_dataset(self):
        """测试：大规模数据集"""
        n_alternatives = 50
        n_criteria = 10

        # 生成随机数据
        np.random.seed(42)
        decision_matrix = np.random.rand(n_alternatives, n_criteria) * 100
        weights = np.random.rand(n_criteria)
        weights = weights / np.sum(weights)  # 归一化

        preference_functions = [
            {"type": "usual"} for _ in range(n_criteria)
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        # 验证
        assert len(result["rankings"]) == n_alternatives
        assert len(result["net_flows"]) == n_alternatives

    def test_single_criterion(self):
        """测试：单个准则"""
        decision_matrix = np.array([
            [10],
            [20],
            [30],
        ])

        weights = np.array([1.0])

        preference_functions = [
            {"type": "v_shape", "p": 5.0}
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        # 最大值应该排第一
        assert result["rankings"][0]["alternative"] == "A2"

    def test_equal_weights(self):
        """测试：相等权重"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([1/3, 1/3, 1/3])

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()
        result = service.rank(decision_matrix, weights, preference_functions)

        # 权重和应该为 1
        assert abs(np.sum(weights) - 1.0) < 0.0001


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_matrix_dimensions(self):
        """测试：无效矩阵维度"""
        decision_matrix = np.array([10, 20, 30])  # 1D 数组
        weights = np.array([0.5, 0.5])

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()

        with pytest.raises(PROMETHEEValidationError):
            service.rank(decision_matrix, weights, preference_functions)

    def test_mismatched_weights_count(self):
        """测试：权重数量不匹配"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.5, 0.5])  # 2个权重，但矩阵有3列

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()

        with pytest.raises(ValueError, match="权重"):
            service.rank(decision_matrix, weights, preference_functions)

    def test_mismatched_functions_count(self):
        """测试：偏好函数数量不匹配"""
        decision_matrix = np.array([
            [10, 20, 30],
            [15, 25, 35],
        ])

        weights = np.array([0.5, 0.3, 0.2])

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"}  # 只有2个函数，但矩阵有3列
        ]

        service = PROMETHEEService()

        with pytest.raises(ValueError, match="偏好函数"):
            service.rank(decision_matrix, weights, preference_functions)

    def test_negative_weights(self):
        """测试：负权重"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = np.array([0.6, -0.4])  # 负权重

        preference_functions = [
            {"type": "usual"},
            {"type": "usual"}
        ]

        service = PROMETHEEService()

        with pytest.raises(PROMETHEEValidationError, match="权重"):
            service.rank(decision_matrix, weights, preference_functions)

    def test_missing_function_parameters(self):
        """测试：缺少必需的函数参数"""
        decision_matrix = np.array([
            [10, 20],
            [15, 25],
        ])

        weights = np.array([0.5, 0.5])

        # v_shape 需要 p 参数
        preference_functions = [
            {"type": "v_shape"}  # 缺少 p
        ]

        service = PROMETHEEService()

        with pytest.raises(ValueError):
            service.rank(decision_matrix, weights, preference_functions)
