"""
MCDA Core - 聚合方法单元测试

测试评分聚合方法的功能。
"""

import pytest

from mcda_core.aggregation import (
    AggregationRegistry,
    WeightedAverageAggregation,
)


class TestAggregationRegistry:
    """测试聚合方法注册表"""

    def test_register_and_retrieve_method(self):
        """测试注册和检索方法"""
        # 获取已注册的方法
        method_class = AggregationRegistry.get("weighted_average")
        assert method_class is WeightedAverageAggregation

    def test_list_methods(self):
        """测试列出所有方法"""
        methods = AggregationRegistry.list_methods()
        assert "weighted_average" in methods

    def test_is_registered(self):
        """测试检查方法是否已注册"""
        assert AggregationRegistry.is_registered("weighted_average") is True
        assert AggregationRegistry.is_registered("nonexistent") is False

    def test_get_nonexistent_method_raises_error(self):
        """测试获取不存在的方法抛出异常"""
        with pytest.raises(KeyError, match="未知的聚合方法"):
            AggregationRegistry.get("nonexistent")

    def test_create_nonexistent_method_raises_error(self):
        """测试创建不存在的方法实例抛出异常"""
        with pytest.raises(KeyError, match="未知的聚合方法"):
            AggregationRegistry.create("nonexistent")


class TestWeightedAverageAggregation:
    """测试加权平均聚合方法"""

    @pytest.fixture
    def aggregation(self):
        """创建聚合方法实例"""
        return WeightedAverageAggregation()

    def test_get_name(self, aggregation):
        """测试获取方法名称"""
        assert aggregation.get_name() == "weighted_average"

    def test_aggregate_with_equal_weights(self, aggregation):
        """测试等权重聚合"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        result = aggregation.aggregate(scores)
        # (80 + 90 + 85) / 3 = 85
        assert result == pytest.approx(85.0)

    def test_aggregate_with_custom_weights(self, aggregation):
        """测试自定义权重聚合"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.3, "DM3": 0.2}
        result = aggregation.aggregate(scores, weights)
        # 0.5*80 + 0.3*90 + 0.2*85 = 40 + 27 + 17 = 84
        assert result == pytest.approx(84.0)

    def test_aggregate_with_none_weights_uses_equal_weights(self, aggregation):
        """测试 None 权重使用等权重"""
        scores = {"DM1": 80.0, "DM2": 90.0}
        result = aggregation.aggregate(scores, None)
        assert result == pytest.approx(85.0)

    def test_aggregate_empty_scores_raises_error(self, aggregation):
        """测试空评分抛出异常"""
        with pytest.raises(ValueError, match="评分不能为空"):
            aggregation.aggregate({})

    def test_aggregate_mismatched_ids_raises_error(self, aggregation):
        """测试 ID 不匹配抛出异常"""
        scores = {"DM1": 80.0, "DM2": 90.0}
        weights = {"DM1": 0.5, "DM3": 0.5}  # DM3 不在评分中
        with pytest.raises(ValueError, match="权重中存在未评分的决策者"):
            aggregation.aggregate(scores, weights)

    def test_aggregate_missing_weight_raises_error(self, aggregation):
        """测试缺少权重抛出异常"""
        scores = {"DM1": 80.0, "DM2": 90.0, "DM3": 85.0}
        weights = {"DM1": 0.5, "DM2": 0.5}  # 缺少 DM3
        with pytest.raises(ValueError, match="缺少决策者的权重"):
            aggregation.aggregate(scores, weights)

    def test_aggregate_zero_total_weights_raises_error(self, aggregation):
        """测试总权重为零抛出异常"""
        scores = {"DM1": 80.0, "DM2": 90.0}
        weights = {"DM1": 0.0, "DM2": 0.0}
        with pytest.raises(ValueError, match="权重总和不能为 0"):
            aggregation.aggregate(scores, weights)

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
        assert result["AWS"]["成本"] == pytest.approx(82.5)  # (80+85)/2
        assert result["AWS"]["质量"] == pytest.approx(85.0)   # (90+80)/2
        assert result["Azure"]["成本"] == pytest.approx(72.5)  # (70+75)/2
        assert result["Azure"]["质量"] == pytest.approx(87.5)  # (85+90)/2

    def test_aggregate_matrix_with_weights(self, aggregation):
        """测试带权重的评分矩阵聚合"""
        score_matrix = {
            "AWS": {
                "成本": {"DM1": 80.0, "DM2": 90.0},
                "质量": {"DM1": 90.0, "DM2": 80.0},
            },
        }
        weights = {"DM1": 0.6, "DM2": 0.4}

        result = aggregation.aggregate_matrix(score_matrix, weights)

        # 0.6*80 + 0.4*90 = 48 + 36 = 84
        assert result["AWS"]["成本"] == pytest.approx(84.0)
        # 0.6*90 + 0.4*80 = 54 + 32 = 86
        assert result["AWS"]["质量"] == pytest.approx(86.0)

    def test_aggregate_single_decision_maker(self, aggregation):
        """测试单个决策者聚合"""
        scores = {"DM1": 85.0}
        result = aggregation.aggregate(scores)
        assert result == pytest.approx(85.0)

    def test_aggregate_with_extreme_weights(self, aggregation):
        """测试极端权重值"""
        scores = {"DM1": 80.0, "DM2": 90.0}
        weights = {"DM1": 0.99, "DM2": 0.01}
        result = aggregation.aggregate(scores, weights)
        # 接近 80 但受 DM2 稍微影响
        assert result == pytest.approx(80.1)

    def test_aggregate_with_negative_scores(self, aggregation):
        """测试负评分（不常见但应支持）"""
        scores = {"DM1": -10.0, "DM2": 10.0}
        result = aggregation.aggregate(scores)
        assert result == pytest.approx(0.0)

    def test_aggregate_matrix_empty(self, aggregation):
        """测试空评分矩阵聚合"""
        result = aggregation.aggregate_matrix({})
        assert result == {}

    def test_aggregate_with_different_weights_sum(self, aggregation):
        """测试权重和不等于 1 的情况（应自动归一化）"""
        scores = {"DM1": 80.0, "DM2": 90.0}
        weights = {"DM1": 2.0, "DM2": 1.0}  # 总和为 3
        # (2*80 + 1*90) / 3 = (160 + 90) / 3 = 250 / 3 ≈ 83.33
        result = aggregation.aggregate(scores, weights)
        assert result == pytest.approx(83.3333333)
