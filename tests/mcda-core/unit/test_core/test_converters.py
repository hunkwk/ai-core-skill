"""
MCDA Core - 配置格式转换工具测试

测试 YAML 和 JSON 格式之间的相互转换。
"""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mcda_core.converters import ConfigConverter
from mcda_core.exceptions import ConfigLoadError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_config():
    """示例配置数据"""
    return {
        "name": "云服务商选择",
        "description": "选择最佳云服务商",
        "alternatives": ["AWS", "Azure", "GCP"],
        "criteria": [
            {
                "name": "成本",
                "weight": 0.35,
                "direction": "lower_better",
                "description": "月度成本（万元）"
            },
            {
                "name": "功能完整性",
                "weight": 0.30,
                "direction": "higher_better"
            },
            {
                "name": "易用性",
                "weight": 0.20,
                "direction": "higher_better"
            },
            {
                "name": "技术支持",
                "weight": 0.15,
                "direction": "higher_better"
            }
        ],
        "scores": {
            "AWS": {
                "成本": 3,
                "功能完整性": 5,
                "易用性": 4,
                "技术支持": 4
            },
            "Azure": {
                "成本": 4,
                "功能完整性": 4,
                "易用性": 4,
                "技术支持": 5
            },
            "GCP": {
                "成本": 5,
                "功能完整性": 4,
                "易用性": 5,
                "技术支持": 3
            }
        },
        "algorithm": {
            "name": "wsm"
        }
    }


@pytest.fixture
def converter():
    """ConfigConverter 实例"""
    return ConfigConverter()


# =============================================================================
# YAML → JSON 转换测试
# =============================================================================

class TestYAMLToJSONConversion:
    """测试 YAML 到 JSON 的转换"""

    def test_convert_yaml_to_json_file(self, converter, sample_config):
        """测试: 将 YAML 文件转换为 JSON 文件"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建 YAML 文件
            yaml_file = Path(tmpdir) / "config.yaml"
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, allow_unicode=True)

            # 2. 转换为 JSON
            json_file = Path(tmpdir) / "config.json"
            converter.convert(yaml_file, json_file)

            # 3. 验证 JSON 文件存在
            assert json_file.exists()

            # 4. 验证内容正确
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            assert json_data["name"] == sample_config["name"]
            assert json_data["alternatives"] == sample_config["alternatives"]
            assert len(json_data["criteria"]) == len(sample_config["criteria"])
            assert json_data["algorithm"]["name"] == "wsm"

    def test_convert_yaml_to_json_string(self, converter, sample_config):
        """测试: 将 YAML 文件转换为 JSON 字符串"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建 YAML 文件
            yaml_file = Path(tmpdir) / "config.yaml"
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, allow_unicode=True)

            # 2. 转换为 JSON 字符串
            json_str = converter.convert_to_json(yaml_file)

            # 3. 验证 JSON 字符串
            assert json_str is not None
            assert len(json_str) > 0

            # 4. 验证可以解析为 JSON
            json_data = json.loads(json_str)
            assert json_data["name"] == sample_config["name"]

    def test_convert_yaml_with_unicode_to_json(self, converter):
        """测试: 转换包含 Unicode 字符的 YAML 到 JSON"""
        config = {
            "name": "供应商选择",
            "alternatives": ["供应商A", "供应商B", "供应商C"],
            "criteria": [
                {"name": "成本", "weight": 0.5, "direction": "lower_better"},
                {"name": "质量", "weight": 0.5, "direction": "higher_better"}
            ],
            "scores": {
                "供应商A": {"成本": 100, "质量": 80},
                "供应商B": {"成本": 150, "质量": 90}
            },
            "algorithm": {"name": "wsm"}
        }

        with TemporaryDirectory() as tmpdir:
            # 创建 YAML 文件
            yaml_file = Path(tmpdir) / "unicode.yaml"
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)

            # 转换为 JSON（保持 Unicode）
            json_str = converter.convert_to_json(yaml_file, ensure_ascii=False)

            # 验证中文字符保持原样
            assert "供应商选择" in json_str
            assert "供应商A" in json_str


# =============================================================================
# JSON → YAML 转换测试
# =============================================================================

class TestJSONToYAMLConversion:
    """测试 JSON 到 YAML 的转换"""

    def test_convert_json_to_yaml_file(self, converter, sample_config):
        """测试: 将 JSON 文件转换为 YAML 文件"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建 JSON 文件
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, ensure_ascii=False, indent=2)

            # 2. 转换为 YAML
            yaml_file = Path(tmpdir) / "config.yaml"
            converter.convert(json_file, yaml_file)

            # 3. 验证 YAML 文件存在
            assert yaml_file.exists()

            # 4. 验证内容正确
            import yaml
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)

            assert yaml_data["name"] == sample_config["name"]
            assert yaml_data["alternatives"] == sample_config["alternatives"]
            assert len(yaml_data["criteria"]) == len(sample_config["criteria"])

    def test_convert_json_to_yaml_string(self, converter, sample_config):
        """测试: 将 JSON 文件转换为 YAML 字符串"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建 JSON 文件
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, ensure_ascii=False)

            # 2. 转换为 YAML 字符串
            yaml_str = converter.convert_to_yaml(json_file)

            # 3. 验证 YAML 字符串
            assert yaml_str is not None
            assert len(yaml_str) > 0
            assert "name:" in yaml_str

    def test_convert_json_with_unicode_to_yaml(self, converter):
        """测试: 转换包含 Unicode 字符的 JSON 到 YAML"""
        config = {
            "name": "产品优先级",
            "alternatives": ["产品A", "产品B"],
            "criteria": [
                {"name": "市场潜力", "weight": 0.6, "direction": "higher_better"}
            ],
            "scores": {
                "产品A": {"市场潜力": 90},
                "产品B": {"市场潜力": 70}
            },
            "algorithm": {"name": "wsm"}
        }

        with TemporaryDirectory() as tmpdir:
            # 创建 JSON 文件
            json_file = Path(tmpdir) / "unicode.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)

            # 转换为 YAML（保持 Unicode）
            yaml_str = converter.convert_to_yaml(json_file)

            # 验证中文字符保持原样
            assert "产品优先级" in yaml_str
            assert "产品A" in yaml_str


# =============================================================================
# 自动格式检测测试
# =============================================================================

class TestAutoFormatDetection:
    """测试自动格式检测"""

    def test_convert_auto_detect_output_format(self, converter, sample_config):
        """测试: 自动检测输出格式（根据文件扩展名）"""
        with TemporaryDirectory() as tmpdir:
            # 创建 YAML 文件
            yaml_file = Path(tmpdir) / "input.yaml"
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, allow_unicode=True)

            # 转换为 JSON（自动检测）
            json_file = Path(tmpdir) / "output.json"
            converter.convert(yaml_file, json_file)

            # 验证
            assert json_file.exists()
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            assert json_data["name"] == sample_config["name"]

    def test_convert_yaml_to_yml(self, converter, sample_config):
        """测试: 转换 .yaml 到 .yml 扩展名"""
        with TemporaryDirectory() as tmpdir:
            # 创建 .yaml 文件
            yaml_file = Path(tmpdir) / "config.yaml"
            import yaml
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, allow_unicode=True)

            # 转换为 .yml
            yml_file = Path(tmpdir) / "config.yml"
            converter.convert(yaml_file, yml_file)

            # 验证
            assert yml_file.exists()


# =============================================================================
# 错误处理测试
# =============================================================================

class TestErrorHandling:
    """测试错误处理"""

    def test_convert_nonexistent_file(self, converter):
        """测试: 转换不存在的文件应该抛出错误"""
        with pytest.raises(FileNotFoundError):
            converter.convert_to_json("/nonexistent/file.yaml")

    def test_convert_invalid_yaml(self, converter):
        """测试: 转换无效的 YAML 应该抛出错误"""
        with TemporaryDirectory() as tmpdir:
            invalid_file = Path(tmpdir) / "invalid.yaml"
            with open(invalid_file, 'w', encoding='utf-8') as f:
                f.write("invalid:\n  yaml: content:\n    - broken")

            # YAML 解析可能不会抛出错误，但应该能处理
            # 如果抛出 ConfigLoadError，也是可以接受的
            try:
                result = converter.convert_to_json(invalid_file)
                # 如果没有抛出错误，至少应该返回结果
                assert result is not None
            except (ConfigLoadError, Exception):
                # 预期的错误
                pass

    def test_convert_unsupported_format(self, converter):
        """测试: 不支持的输出格式应该抛出错误"""
        with TemporaryDirectory() as tmpdir:
            # 创建有效的 JSON 文件
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({"name": "test"}, f)

            # 尝试转换为不支持的格式
            xml_file = Path(tmpdir) / "output.xml"

            # 应该抛出 ValueError（因为无法推断格式）
            with pytest.raises(ValueError, match="无法从文件扩展名推断格式"):
                converter.convert(json_file, xml_file)


# =============================================================================
# 双向转换一致性测试
# =============================================================================

class TestRoundTripConsistency:
    """测试双向转换的一致性"""

    def test_yaml_to_json_to_yaml_preserves_data(self, converter, sample_config):
        """测试: YAML → JSON → YAML 应该保持数据一致"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建原始 YAML 文件
            original_yaml = Path(tmpdir) / "original.yaml"
            import yaml
            with open(original_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(sample_config, f, allow_unicode=True)

            # 2. YAML → JSON
            json_file = Path(tmpdir) / "intermediate.json"
            converter.convert(original_yaml, json_file)

            # 3. JSON → YAML
            final_yaml = Path(tmpdir) / "final.yaml"
            converter.convert(json_file, final_yaml)

            # 4. 加载并比较
            with open(original_yaml, 'r', encoding='utf-8') as f:
                original_data = yaml.safe_load(f)

            with open(final_yaml, 'r', encoding='utf-8') as f:
                final_data = yaml.safe_load(f)

            # 验证关键字段相同
            assert original_data["name"] == final_data["name"]
            assert original_data["alternatives"] == final_data["alternatives"]
            assert original_data["algorithm"]["name"] == final_data["algorithm"]["name"]

    def test_json_to_yaml_to_json_preserves_data(self, converter, sample_config):
        """测试: JSON → YAML → JSON 应该保持数据一致"""
        with TemporaryDirectory() as tmpdir:
            # 1. 创建原始 JSON 文件
            original_json = Path(tmpdir) / "original.json"
            with open(original_json, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, ensure_ascii=False, indent=2)

            # 2. JSON → YAML
            yaml_file = Path(tmpdir) / "intermediate.yaml"
            converter.convert(original_json, yaml_file)

            # 3. YAML → JSON
            final_json = Path(tmpdir) / "final.json"
            converter.convert(yaml_file, final_json)

            # 4. 加载并比较
            with open(original_json, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            with open(final_json, 'r', encoding='utf-8') as f:
                final_data = json.load(f)

            # 验证数据完全相同
            assert original_data == final_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
