"""
MCDA Core - AggregationConfig 数据模型单元测试

测试聚合配置数据模型的创建和验证。
"""

import pytest

from mcda_core.group.models import AggregationConfig


class TestAggregationConfig:
    """测试 AggregationConfig 数据模型"""

    def test_create_valid_config_with_defaults(self):
        """测试使用默认值创建有效配置"""
        config = AggregationConfig()

        assert config.score_aggregation == "weighted_average"
        assert config.consensus_strategy == "none"
        assert config.consensus_threshold == 0.7

    def test_create_config_with_custom_values(self):
        """测试创建自定义配置"""
        config = AggregationConfig(
            score_aggregation="weighted_geometric",
            consensus_strategy="threshold",
            consensus_threshold=0.8
        )

        assert config.score_aggregation == "weighted_geometric"
        assert config.consensus_strategy == "threshold"
        assert config.consensus_threshold == 0.8

    def test_config_with_borda_count(self):
        """测试 Borda 计数聚合方法"""
        config = AggregationConfig(score_aggregation="borda_count")
        assert config.score_aggregation == "borda_count"

    def test_config_with_copeland(self):
        """测试 Copeland 聚合方法"""
        config = AggregationConfig(score_aggregation="copeland")
        assert config.score_aggregation == "copeland"

    def test_config_with_feedback_strategy(self):
        """测试反馈共识策略"""
        config = AggregationConfig(consensus_strategy="feedback")
        assert config.consensus_strategy == "feedback"

    def test_invalid_score_aggregation_raises_error(self):
        """测试无效聚合方法抛出异常"""
        with pytest.raises(ValueError, match="score_aggregation.*必须是"):
            AggregationConfig(score_aggregation="invalid_method")

    def test_invalid_consensus_strategy_raises_error(self):
        """测试无效共识策略抛出异常"""
        with pytest.raises(ValueError, match="consensus_strategy.*必须是"):
            AggregationConfig(consensus_strategy="invalid_strategy")

    def test_consensus_threshold_out_of_range_high_raises_error(self):
        """测试共识阈值超出上限抛出异常"""
        with pytest.raises(ValueError, match="consensus_threshold.*必须在 0-1 范围内"):
            AggregationConfig(consensus_threshold=1.5)

    def test_consensus_threshold_out_of_range_low_raises_error(self):
        """测试共识阈值超出下限抛出异常"""
        with pytest.raises(ValueError, match="consensus_threshold.*必须在 0-1 范围内"):
            AggregationConfig(consensus_threshold=-0.1)

    def test_consensus_threshold_at_boundary(self):
        """测试共识阈值边界值"""
        config_low = AggregationConfig(consensus_threshold=0.0)
        assert config_low.consensus_threshold == 0.0

        config_high = AggregationConfig(consensus_threshold=1.0)
        assert config_high.consensus_threshold == 1.0

    def test_config_immutability(self):
        """测试配置不可变性"""
        config = AggregationConfig()

        with pytest.raises(Exception):  # FrozenInstanceError
            config.consensus_threshold = 0.8

    def test_all_valid_aggregation_methods(self):
        """测试所有有效的聚合方法"""
        valid_methods = [
            "weighted_average",
            "weighted_geometric",
            "borda_count",
            "copeland",
        ]

        for method in valid_methods:
            config = AggregationConfig(score_aggregation=method)
            assert config.score_aggregation == method

    def test_all_valid_consensus_strategies(self):
        """测试所有有效的共识策略"""
        valid_strategies = ["none", "threshold", "feedback"]

        for strategy in valid_strategies:
            config = AggregationConfig(consensus_strategy=strategy)
            assert config.consensus_strategy == strategy

    def test_config_with_threshold_strategy_requires_threshold(self):
        """测试阈值策略配置（阈值是可选的，有默认值）"""
        config = AggregationConfig(
            consensus_strategy="threshold",
            # 不指定 threshold，使用默认值 0.7
        )
        assert config.consensus_strategy == "threshold"
        assert config.consensus_threshold == 0.7
