"""
MCDA Core - 工具函数单元测试

测试 YAML 加载、权重归一化、方向反转等工具函数。
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from mcda_core.utils import (
    load_yaml,
    normalize_weights,
    reverse_direction,
)
from mcda_core.exceptions import (
    YAMLParseError,
)


# =============================================================================
# load_yaml 测试
# =============================================================================

class TestLoadYAML:
    """测试 YAML 加载函数"""

    def test_load_simple_yaml(self):
        """测试: 加载简单 YAML 文件"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("""
name: test
value: 42
""", encoding="utf-8")

            data = load_yaml(yaml_file)
            assert data == {"name": "test", "value": 42}

    def test_load_yaml_with_nested_structure(self):
        """测试: 加载嵌套结构的 YAML"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("""
alternatives:
  - 方案A
  - 方案B
criteria:
  - name: 成本
    weight: 0.4
    direction: lower_better
  - name: 质量
    weight: 0.6
    direction: higher_better
""", encoding="utf-8")

            data = load_yaml(yaml_file)
            assert "alternatives" in data
            assert len(data["alternatives"]) == 2
            assert len(data["criteria"]) == 2

    def test_load_yaml_nonexistent_file(self):
        """测试: 加载不存在的文件"""
        with pytest.raises(YAMLParseError) as exc_info:
            load_yaml(Path("nonexistent.yaml"))

        assert "不存在" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    def test_load_yaml_invalid_syntax(self):
        """测试: 加载语法错误的 YAML"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "invalid.yaml"
            # 缩进错误的 YAML
            yaml_file.write_text("""
name: test
  nested: value
""", encoding="utf-8")

            with pytest.raises(YAMLParseError) as exc_info:
                load_yaml(yaml_file)

            assert exc_info.value.details["file"] == str(yaml_file)

    def test_load_yaml_with_unicode(self):
        """测试: 加载包含中文的 YAML"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "chinese.yaml"
            yaml_file.write_text("""
项目: MCDA决策分析
方案:
  - 方案A
  - 方案B
准则:
  - 名称: 成本
    权重: 0.5
  - 名称: 质量
    权重: 0.5
""", encoding="utf-8")

            data = load_yaml(yaml_file)
            assert data["项目"] == "MCDA决策分析"
            assert "方案A" in data["方案"]


# =============================================================================
# normalize_weights 测试
# =============================================================================

class TestNormalizeWeights:
    """测试权重归一化函数"""

    def test_normalize_weights_sum_not_one(self):
        """测试: 权重和不为 1 时归一化"""
        weights = {"成本": 0.5, "质量": 0.6, "服务": 0.4}
        normalized = normalize_weights(weights)

        # 验证权重和为 1
        assert abs(sum(normalized.values()) - 1.0) < 1e-6

        # 验证比例保持不变
        total = sum(weights.values())
        for key in weights:
            expected = weights[key] / total
            assert abs(normalized[key] - expected) < 1e-6

    def test_normalize_weights_already_normalized(self):
        """测试: 已经归一化的权重"""
        weights = {"成本": 0.5, "质量": 0.5}
        normalized = normalize_weights(weights)

        assert normalized == weights

    def test_normalize_weights_zero_sum(self):
        """测试: 权重和为 0 时抛出异常"""
        weights = {"成本": 0.0, "质量": 0.0}

        with pytest.raises(ValueError) as exc_info:
            normalize_weights(weights)

        assert "权重总和不能为 0" in str(exc_info.value) or "cannot be zero" in str(exc_info.value).lower()

    def test_normalize_weights_single_criterion(self):
        """测试: 单个准则的权重"""
        weights = {"成本": 1.0}
        normalized = normalize_weights(weights)

        assert normalized == {"成本": 1.0}

    def test_normalize_weights_negative_weight(self):
        """测试: 包含负权重时抛出异常"""
        weights = {"成本": 0.8, "质量": -0.3, "服务": 0.5}

        with pytest.raises(ValueError) as exc_info:
            normalize_weights(weights)

        assert "负数" in str(exc_info.value) or "negative" in str(exc_info.value).lower()

    def test_normalize_weights_many_criteria(self):
        """测试: 多个准则的权重归一化"""
        weights = {f"准则{i}": i * 0.1 for i in range(1, 11)}
        normalized = normalize_weights(weights)

        assert abs(sum(normalized.values()) - 1.0) < 1e-6
        assert len(normalized) == 10


# =============================================================================
# reverse_direction 测试
# =============================================================================

class TestReverseDirection:
    """测试方向反转函数"""

    def test_reverse_higher_better(self):
        """测试: 反转 higher_better"""
        assert reverse_direction("higher_better") == "lower_better"

    def test_reverse_lower_better(self):
        """测试: 反转 lower_better"""
        assert reverse_direction("lower_better") == "higher_better"

    def test_reverse_invalid_direction(self):
        """测试: 反转无效方向"""
        with pytest.raises(ValueError) as exc_info:
            reverse_direction("invalid")

        assert "无效的方向" in str(exc_info.value) or "invalid direction" in str(exc_info.value).lower()


# =============================================================================
# 集成测试
# =============================================================================

class TestUtilsIntegration:
    """工具函数集成测试"""

    def test_load_and_normalize_weights(self):
        """测试: 加载 YAML 并归一化权重"""
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("""
criteria:
  - name: 成本
    weight: 4
  - name: 质量
    weight: 6
  - name: 服务
    weight: 5
""", encoding="utf-8")

            data = load_yaml(yaml_file)

            # 提取权重
            weights = {c["name"]: c["weight"] for c in data["criteria"]}

            # 归一化
            normalized = normalize_weights(weights)

            # 验证
            assert abs(sum(normalized.values()) - 1.0) < 1e-6
            assert abs(normalized["成本"] - 0.26666666666666666) < 1e-6
            assert abs(normalized["质量"] - 0.4) < 1e-6
            assert abs(normalized["服务"] - 0.3333333333333333) < 1e-6
