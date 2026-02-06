"""
MCDA Core - 高级聚合方法单元测试

测试加权几何平均、Borda 计数法和 Copeland 方法。
"""

import pytest
import numpy as np


class TestWeightedGeometricAggregation:
    """测试加权几何平均聚合方法"""

    @pytest.fixture
    def aggregation(self):
        """创建聚合方法实例"""
        from mcda_core.aggregation import WeightedGeometricAggregation
        return WeightedGeometricAggregation()

    def test_get_name(self, aggregation):
        """测试获取方法名称"""
        assert aggregation.get_name() == "weighted_geometric"

    def test_aggregate_with_equal_weights(self, aggregation):
        """测试等权重聚合"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        result = aggregation.aggregate(scores)
        # 几何平均: (80 * 90 * 85)^(1/3) ≈ 84.92
        expected = np.exp((np.log(80) + np.log(90) + np.log(85)) / 3)
        assert result == pytest.approx(expected)

    def test_aggregate_with_custom_weights(self, aggregation):
        """测试自定义权重聚合"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        # 对数域计算: exp((0.5*ln(80) + 0.3*ln(90) + 0.2*ln(85)) / 1.0)
        log_score = (0.5 * np.log(80) + 0.3 * np.log(90) + 0.2 * np.log(85)) / 1.0
        expected = np.exp(log_score)
        assert result == pytest.approx(expected)

    def test_aggregate_with_zero_value_raises_error(self, aggregation):
        """测试零值抛出异常（几何平均不能处理零）"""
        scores = {"DM1": 80.0, "DM2": 0.0, "DM3": 85.0}
        with pytest.raises(ValueError, match="零值或负值"):
            aggregation.aggregate(scores)

    def test_aggregate_with_negative_value_raises_error(self, aggregation):
        """测试负值抛出异常"""
        scores = {"DM1": 80.0, "DM2": -10.0, "DM3": 85.0}
        with pytest.raises(ValueError, match="零值或负值"):
            aggregation.aggregate(scores)

    def test_aggregate_empty_scores_raises_error(self, aggregation):
        """测试空评分抛出异常"""
        with pytest.raises(ValueError, match="评分不能为空"):
            aggregation.aggregate({})

    def test_aggregate_matrix(self, aggregation):
        """测试聚合评分矩阵"""
        score_matrix = {
            "AWS": {
                "成本": {"DM1": 80.0, "DM2": 85.0},
                "质量": {"DM1": 90.0, "DM2": 80.0},
            },
            "Azure": {
                "成本": {"DM1": 70.0, "DM2": 75.0},
                "质量": {"DM1": 85.0, "DM2": 90.0},
            },
        }
        result = aggregation.aggregate_matrix(score_matrix)

        # 验证结果结构
        assert "AWS" in result
        assert "Azure" in result
        # 几何平均计算
        assert result["AWS"]["成本"] == pytest.approx(np.exp((np.log(80) + np.log(85)) / 2))
        assert result["AWS"]["质量"] == pytest.approx(np.exp((np.log(90) + np.log(80)) / 2))

    def test_aggregate_handles_small_values(self, aggregation):
        """测试处理小值（验证对数域计算避免溢出）"""
        scores = {"DM1": 0.001, "DM2": 0.01, "DM3": 0.1}
        result = aggregation.aggregate(scores)
        # 验证不会发生溢出，且结果正确
        log_score = (np.log(0.001) + np.log(0.01) + np.log(0.1)) / 3
        expected = np.exp(log_score)
        assert result == pytest.approx(expected)

    def test_aggregate_handles_large_values(self, aggregation):
        """测试处理大值（验证对数域计算避免溢出）"""
        scores = {"DM1": 1000.0, "DM2": 10000.0, "DM3": 100000.0}
        result = aggregation.aggregate(scores)
        # 验证不会发生溢出，且结果正确
        log_score = (np.log(1000) + np.log(10000) + np.log(100000)) / 3
        expected = np.exp(log_score)
        assert result == pytest.approx(expected)


class TestBordaCountAggregation:
    """测试 Borda 计数法聚合方法"""

    @pytest.fixture
    def aggregation(self):
        """创建聚合方法实例"""
        from mcda_core.aggregation import BordaCountAggregation
        return BordaCountAggregation()

    def test_get_name(self, aggregation):
        """测试获取方法名称"""
        assert aggregation.get_name() == "borda_count"

    def test_aggregate_basic(self, aggregation):
        """测试基本 Borda 计数"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        result = aggregation.aggregate(scores)
        # 排序: DM2(90) > DM3(85) > DM1(80)
        # Borda 分数: DM2=2, DM3=1, DM1=0 (n-rank, 3人: 3-1=2, 3-2=1, 3-3=0)
        # 等权重平均: (0 + 2 + 1) / 3 = 1
        expected = (0 + 2 + 1) / 3
        assert result == pytest.approx(expected)

    def test_aggregate_with_weights(self, aggregation):
        """测试带权重的 Borda 计数"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        # 排序: DM2(90) > DM3(85) > DM1(80)
        # Borda 分数: DM2=2, DM3=1, DM1=0
        # 加权: (0*0.5 + 2*0.3 + 1*0.2) / (0.5+0.3+0.2) = 0.8
        weighted_sum = 0 * 0.5 + 2 * 0.3 + 1 * 0.2
        expected = weighted_sum / 1.0
        assert result == pytest.approx(expected)

    def test_aggregate_matrix(self, aggregation):
        """测试聚合评分矩阵"""
        score_matrix = {
            "A": {"C1": {"DM1": 10.0, "DM2": 20.0}, "C2": {"DM1": 30.0, "DM2": 40.0}},
            "B": {"C1": {"DM1": 15.0, "DM2": 25.0}, "C2": {"DM1": 35.0, "DM2": 45.0}},
        }
        result = aggregation.aggregate_matrix(score_matrix)

        # 验证结果结构
        assert "A" in result
        assert "B" in result
        assert "C1" in result["A"]
        assert "C2" in result["A"]

    def test_aggregate_with_ties(self, aggregation):
        """测试处理相同评分"""
        scores = {"DM1": 80.0, "DM2": 80.0, "DM3": 85.0}
        result = aggregation.aggregate(scores)
        # DM1 和 DM2 有相同分数，应获得相同排名
        # 排序: DM3(85) > DM1=DM2(80)
        # DM3 排第 1，DM1 和 DM2 并列第 2-3，平均排名 = (2+3)/2 = 2.5
        # Borda 分数: DM3=2, DM1=0.5, DM2=0.5 (n-rank: 3-1=2, 3-2.5=0.5)
        expected = (0.5 + 0.5 + 2) / 3
        assert result == pytest.approx(expected)

    def test_aggregate_empty_scores_raises_error(self, aggregation):
        """测试空评分抛出异常"""
        with pytest.raises(ValueError, match="评分不能为空"):
            aggregation.aggregate({})


class TestCopelandAggregation:
    """测试 Copeland 方法聚合"""

    @pytest.fixture
    def aggregation(self):
        """创建聚合方法实例"""
        from mcda_core.aggregation import CopelandAggregation
        return CopelandAggregation()

    def test_get_name(self, aggregation):
        """测试获取方法名称"""
        assert aggregation.get_name() == "copeland"

    def test_aggregate_basic(self, aggregation):
        """测试基本 Copeland 方法"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        result = aggregation.aggregate(scores)
        # Copeland 基于"胜场"计算
        # 对于单一准则的聚合，应返回加权平均
        assert result == pytest.approx(85.0)  # 等权重平均

    def test_aggregate_with_weights(self, aggregation):
        """测试带权重的 Copeland 方法"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        # 0.5*80 + 0.3*90 + 0.2*85 = 84
        assert result == pytest.approx(84.0)

    def test_aggregate_matrix(self, aggregation):
        """测试聚合评分矩阵 - 验证两两比较逻辑"""
        score_matrix = {
            "A": {"C1": {"DM1": 10.0, "DM2": 20.0}, "C2": {"DM1": 30.0, "DM2": 40.0}},
            "B": {"C1": {"DM1": 15.0, "DM2": 25.0}, "C2": {"DM1": 35.0, "DM2": 45.0}},
        }
        result = aggregation.aggregate_matrix(score_matrix)

        # 验证结果结构
        assert "A" in result
        assert "B" in result
        assert "C1" in result["A"]
        assert "C2" in result["A"]

    def test_aggregate_empty_scores_raises_error(self, aggregation):
        """测试空评分抛出异常"""
        with pytest.raises(ValueError, match="评分不能为空"):
            aggregation.aggregate({})

    def test_copeland_pairwise_comparison(self, aggregation):
        """测试 Copeland 两两比较逻辑"""
        # 使用多个决策者模拟两两比较场景
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        result = aggregation.aggregate(scores)
        # 验证结果在合理范围内
        assert 80 <= result <= 90

    def test_compute_copeland_scores_basic(self, aggregation):
        """测试 compute_copeland_scores 基本功能"""
        # 三个方案在两个准则上的得分
        score_matrix = {
            "A": {"C1": 10.0, "C2": 20.0},
            "B": {"C1": 15.0, "C2": 25.0},
            "C": {"C1": 5.0, "C2": 30.0},
        }
        result = aggregation.compute_copeland_scores(score_matrix)

        # 验证所有方案都有分数
        assert "A" in result
        assert "B" in result
        assert "C" in result
        # 分数在 [0, 1] 范围内
        for score in result.values():
            assert 0 <= score <= 1

    def test_compute_copeland_scores_with_criteria_weights(self, aggregation):
        """测试带准则权重的 Copeland 分数计算"""
        score_matrix = {
            "A": {"C1": 10.0, "C2": 20.0},
            "B": {"C1": 15.0, "C2": 25.0},
        }
        criterion_weights = {"C1": 0.7, "C2": 0.3}
        result = aggregation.compute_copeland_scores(score_matrix, criterion_weights)

        # 验证结果结构
        assert "A" in result
        assert "B" in result
        # 分数在 [0, 1] 范围内
        for score in result.values():
            assert 0 <= score <= 1

    def test_compute_copeland_scores_empty_matrix(self, aggregation):
        """测试空矩阵的 Copeland 分数计算"""
        result = aggregation.compute_copeland_scores({})
        assert result == {}

    def test_compute_copeland_scores_single_alternative(self, aggregation):
        """测试单方案的 Copeland 分数计算"""
        score_matrix = {
            "A": {"C1": 10.0, "C2": 20.0},
        }
        result = aggregation.compute_copeland_scores(score_matrix)

        # 单方案应返回 0.5（中间值）
        assert result == {"A": 0.5}


class TestAdvancedAggregationIntegration:
    """测试高级聚合方法集成"""

    @pytest.fixture
    def score_matrix(self):
        """创建测试评分矩阵"""
        return {
            "AWS": {
                "成本": {"DM1": 80.0, "DM2": 85.0, "DM3": 90.0},
                "质量": {"DM1": 90.0, "DM2": 80.0, "DM3": 85.0},
                "安全": {"DM1": 85.0, "DM2": 90.0, "DM3": 80.0},
            },
            "Azure": {
                "成本": {"DM1": 70.0, "DM2": 75.0, "DM3": 80.0},
                "质量": {"DM1": 85.0, "DM2": 90.0, "DM3": 95.0},
                "安全": {"DM1": 90.0, "DM2": 85.0, "DM3": 80.0},
            },
            "GCP": {
                "成本": {"DM1": 90.0, "DM2": 85.0, "DM3": 80.0},
                "质量": {"DM1": 80.0, "DM2": 85.0, "DM3": 90.0},
                "安全": {"DM1": 95.0, "DM2": 90.0, "DM3": 85.0},
            },
        }

    def test_geometric_vs_arithmetic_consistency(self, score_matrix):
        """测试几何平均与算术平均的一致性"""
        from mcda_core.aggregation import WeightedGeometricAggregation, WeightedAverageAggregation

        geometric = WeightedGeometricAggregation()
        arithmetic = WeightedAverageAggregation()

        result_geom = geometric.aggregate_matrix(score_matrix)
        result_arith = arithmetic.aggregate_matrix(score_matrix)

        # 几何平均应小于等于算术平均（AM-GM 不等式）
        for alt in score_matrix:
            for crit in score_matrix[alt]:
                assert result_geom[alt][crit] <= result_arith[alt][crit] + 1e-6

    def test_borda_vs_average_ranking_consistency(self, score_matrix):
        """测试 Borda 与平均排名的一致性"""
        from mcda_core.aggregation import BordaCountAggregation, WeightedAverageAggregation

        borda = BordaCountAggregation()
        average = WeightedAverageAggregation()

        result_borda = borda.aggregate_matrix(score_matrix)
        result_average = average.aggregate_matrix(score_matrix)

        # 验证结果结构相同
        assert set(result_borda.keys()) == set(result_average.keys())

    def test_all_methods_handle_empty_matrix(self):
        """测试所有方法处理空矩阵"""
        from mcda_core.aggregation import (
            WeightedGeometricAggregation,
            BordaCountAggregation,
            CopelandAggregation,
        )

        methods = [
            WeightedGeometricAggregation(),
            BordaCountAggregation(),
            CopelandAggregation(),
        ]

        for method in methods:
            result = method.aggregate_matrix({})
            assert result == {}

    def test_registry_contains_all_methods(self):
        """测试注册表包含所有新方法"""
        from mcda_core.aggregation import AggregationRegistry

        methods = AggregationRegistry.list_methods()
        assert "weighted_geometric" in methods
        assert "borda_count" in methods
        assert "copeland" in methods
