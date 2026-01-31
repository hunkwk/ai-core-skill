"""
MCDA Core - 标准化服务单元测试

测试 MinMax 和 Vector 标准化算法的正确性。
"""

import pytest
import math
from skills.mcda_core.lib.normalization import (
    NormalizationService,
    MinMaxNormalization,
    VectorNormalization,
)


# =============================================================================
# 测试夹具
# =============================================================================

@pytest.fixture
def sample_costs():
    """样本成本数据（越低越好）"""
    return {"AWS": 20.0, "Azure": 50.0, "GCP": 35.0}


@pytest.fixture
def sample_scores():
    """样本评分数据（越高越好）"""
    return {"AWS": 85.0, "Azure": 92.0, "GCP": 88.0}


@pytest.fixture
def normalization_service():
    """标准化服务实例"""
    return NormalizationService()


# =============================================================================
# MinMax 标准化测试
# =============================================================================

class TestMinMaxNormalization:
    """MinMax 标准化算法测试"""

    def test_minmax_higher_better(self, sample_scores):
        """测试 MinMax 标准化（越高越好）"""
        method = MinMaxNormalization()
        result = method.normalize(sample_scores, direction="higher_better")

        # 验证输出
        assert len(result.normalized_scores) == 3
        assert "AWS" in result.normalized_scores
        assert "Azure" in result.normalized_scores
        assert "GCP" in result.normalized_scores

        # Azure (92) 应该得分最高
        assert result.normalized_scores["Azure"] == 1.0
        # AWS (85) 应该得分最低
        assert result.normalized_scores["AWS"] == 0.0
        # GCP (88) 在中间
        assert result.normalized_scores["GCP"] == pytest.approx(3.0 / 7.0, rel=1e-5)

        # 验证元数据
        assert result.metadata["method"] == "minmax"
        assert result.metadata["direction"] == "higher_better"
        assert result.metadata["min"] == 85.0
        assert result.metadata["max"] == 92.0

    def test_minmax_lower_better(self, sample_costs):
        """测试 MinMax 标准化（越低越好）"""
        method = MinMaxNormalization()
        result = method.normalize(sample_costs, direction="lower_better")

        # AWS (20) 应该得分最高（成本最低）
        assert result.normalized_scores["AWS"] == 1.0
        # Azure (50) 应该得分最低（成本最高）
        assert result.normalized_scores["Azure"] == 0.0
        # GCP (35) 在中间
        assert result.normalized_scores["GCP"] == pytest.approx(15.0 / 30.0, rel=1e-5)

    def test_minmax_constant_values(self):
        """测试所有值相同的情况"""
        method = MinMaxNormalization()
        values = {"A": 50.0, "B": 50.0, "C": 50.0}
        result = method.normalize(values, direction="higher_better")

        # 所有值应该标准化为 1.0
        assert all(score == 1.0 for score in result.normalized_scores.values())
        assert result.metadata["note"] == "constant"

    def test_minmax_empty_input_raises_error(self):
        """测试空输入抛出异常"""
        method = MinMaxNormalization()
        with pytest.raises(ValueError, match="输入值不能为空"):
            method.normalize({}, direction="higher_better")

    def test_minmax_single_value_raises_error(self):
        """测试单个值抛出异常"""
        method = MinMaxNormalization()
        with pytest.raises(ValueError, match="至少需要 2 个备选方案"):
            method.normalize({"A": 50.0}, direction="higher_better")

    def test_minmax_property_name(self):
        """测试 name 属性"""
        method = MinMaxNormalization()
        assert method.name == "minmax"

    def test_minmax_property_description(self):
        """测试 description 属性"""
        method = MinMaxNormalization()
        assert method.description == "线性映射到 [0, 1] 区间"


# =============================================================================
# Vector 标准化测试
# =============================================================================

class TestVectorNormalization:
    """Vector 标准化算法测试"""

    def test_vector_normalize(self, sample_scores):
        """测试 Vector 标准化"""
        method = VectorNormalization()
        result = method.normalize(sample_scores, direction="higher_better")

        # 计算期望的范数
        norm = math.sqrt(85.0**2 + 92.0**2 + 88.0**2)

        # 验证输出
        assert len(result.normalized_scores) == 3
        assert result.normalized_scores["AWS"] == pytest.approx(85.0 / norm, rel=1e-5)
        assert result.normalized_scores["Azure"] == pytest.approx(92.0 / norm, rel=1e-5)
        assert result.normalized_scores["GCP"] == pytest.approx(88.0 / norm, rel=1e-5)

        # 验证元数据
        assert result.metadata["method"] == "vector"
        assert result.metadata["norm"] == pytest.approx(norm, rel=1e-5)

    def test_vector_zero_values(self):
        """测试全零向量"""
        method = VectorNormalization()
        values = {"A": 0.0, "B": 0.0, "C": 0.0}
        result = method.normalize(values, direction="higher_better")

        # 所有值应该为 0.0
        assert all(score == 0.0 for score in result.normalized_scores.values())
        assert result.metadata["note"] == "zero_norm"

    def test_vector_empty_input_raises_error(self):
        """测试空输入抛出异常"""
        method = VectorNormalization()
        with pytest.raises(ValueError, match="输入值不能为空"):
            method.normalize({}, direction="higher_better")

    def test_vector_single_value_raises_error(self):
        """测试单个值抛出异常"""
        method = VectorNormalization()
        with pytest.raises(ValueError, match="至少需要 2 个备选方案"):
            method.normalize({"A": 50.0}, direction="higher_better")

    def test_vector_property_name(self):
        """测试 name 属性"""
        method = VectorNormalization()
        assert method.name == "vector"

    def test_vector_property_description(self):
        """测试 description 属性"""
        method = VectorNormalization()
        assert method.description == "向量归一化（欧几里得范数）"


# =============================================================================
# NormalizationService 测试
# =============================================================================

class TestNormalizationService:
    """标准化服务测试"""

    def test_service_minmax_normalize(self, normalization_service, sample_costs):
        """测试服务调用 MinMax 标准化"""
        from skills.mcda_core.lib.models import NormalizationConfig

        config = NormalizationConfig(type="minmax", direction="lower_better")
        result = normalization_service.normalize(sample_costs, config)

        # 验证结果
        assert result.normalized_scores["AWS"] == 1.0
        assert result.normalized_scores["Azure"] == 0.0
        assert result.normalized_scores["GCP"] == pytest.approx(0.5, rel=1e-5)

    def test_service_vector_normalize(self, normalization_service, sample_scores):
        """测试服务调用 Vector 标准化"""
        from skills.mcda_core.lib.models import NormalizationConfig

        config = NormalizationConfig(type="vector", direction="higher_better")
        result = normalization_service.normalize(sample_scores, config)

        # 验证结果
        norm = math.sqrt(85.0**2 + 92.0**2 + 88.0**2)
        assert result.normalized_scores["AWS"] == pytest.approx(85.0 / norm, rel=1e-5)

    def test_service_unknown_method_raises_error(self, normalization_service, sample_scores):
        """测试未知方法抛出异常"""
        from skills.mcda_core.lib.models import NormalizationConfig

        config = NormalizationConfig(type="unknown_method", direction="higher_better")

        with pytest.raises(ValueError, match="未知的标准化方法"):
            normalization_service.normalize(sample_scores, config)

    def test_service_normalize_batch(self, normalization_service):
        """测试批量标准化"""
        from skills.mcda_core.lib.models import NormalizationConfig

        data = {
            "成本": {"AWS": 20.0, "Azure": 50.0, "GCP": 35.0},
            "性能": {"AWS": 85.0, "Azure": 92.0, "GCP": 88.0},
        }

        configs = {
            "成本": NormalizationConfig(type="minmax", direction="lower_better"),
            "性能": NormalizationConfig(type="vector", direction="higher_better"),
        }

        result = normalization_service.normalize_batch(data, configs)

        # 验证结果
        assert "成本" in result
        assert "性能" in result
        assert len(result["成本"]) == 3
        assert len(result["性能"]) == 3


# =============================================================================
# 边界情况测试
# =============================================================================

class TestNormalizationEdgeCases:
    """标准化算法边界情况测试"""

    def test_minmax_negative_values(self):
        """测试 MinMax 处理负值"""
        method = MinMaxNormalization()
        values = {"A": -10.0, "B": 0.0, "C": 10.0}
        result = method.normalize(values, direction="higher_better")

        assert result.normalized_scores["A"] == 0.0
        assert result.normalized_scores["B"] == 0.5
        assert result.normalized_scores["C"] == 1.0

    def test_minmax_large_range(self):
        """测试 MinMax 处理大范围数值"""
        method = MinMaxNormalization()
        values = {"A": 0.0001, "B": 10000.0, "C": 5000.0}
        result = method.normalize(values, direction="higher_better")

        assert result.normalized_scores["A"] == pytest.approx(0.0, rel=1e-5)
        assert result.normalized_scores["B"] == pytest.approx(1.0, rel=1e-5)
        assert 0.0 < result.normalized_scores["C"] < 1.0

    def test_vector_negative_values(self):
        """测试 Vector 处理负值"""
        method = VectorNormalization()
        values = {"A": -3.0, "B": 4.0, "C": 0.0}
        result = method.normalize(values, direction="higher_better")

        norm = math.sqrt(9.0 + 16.0 + 0.0)
        assert result.normalized_scores["A"] == pytest.approx(-3.0 / norm, rel=1e-5)
        assert result.normalized_scores["B"] == pytest.approx(4.0 / norm, rel=1e-5)
        assert result.normalized_scores["C"] == 0.0
