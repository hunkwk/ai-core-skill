"""测试配置加载器抽象层和相关实现

这个测试模块验证：
1. ConfigLoader 抽象接口
2. JSONLoader 和 YAMLLoader 实现
3. LoaderFactory 自动检测
4. YAML/JSON 加载一致性
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
import json

from mcda_core.loaders import (
    ConfigLoader,
    JSONLoader,
    YAMLLoader,
    LoaderFactory,
)
from mcda_core.exceptions import ConfigLoadError


class TestJSONLoader:
    """测试 JSONLoader"""

    def test_load_valid_json_config(self):
        """测试加载有效的 JSON 配置"""
        config = {
            "name": "Test Problem",
            "description": "Test description",
            "alternatives": ["A", "B", "C"],
            "criteria": [
                {"name": "Cost", "weight": 0.5, "direction": "lower_better"},
                {"name": "Quality", "weight": 0.5, "direction": "higher_better"}
            ],
            "scores": {
                "A": {"Cost": 100, "Quality": 80},
                "B": {"Cost": 150, "Quality": 90},
                "C": {"Cost": 120, "Quality": 85}
            }
        }

        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()

            loader = JSONLoader()
            data = loader.load(f.name)

            assert data["name"] == "Test Problem"
            assert len(data["alternatives"]) == 3
            assert len(data["criteria"]) == 2
            assert "scores" in data

        Path(f.name).unlink()

    def test_load_invalid_json(self):
        """测试加载无效的 JSON 文件"""
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json content")
            f.flush()

            loader = JSONLoader()

            with pytest.raises(ConfigLoadError):
                loader.load(f.name)

        Path(f.name).unlink()

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        loader = JSONLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/file.json")


class TestYAMLLoader:
    """测试 YAMLLoader"""

    def test_load_valid_yaml_config(self):
        """测试加载有效的 YAML 配置"""
        config = """
name: Test Problem
description: Test description
alternatives:
  - A
  - B
  - C
criteria:
  - name: Cost
    weight: 0.5
    direction: lower_better
  - name: Quality
    weight: 0.5
    direction: higher_better
scores:
  A:
    Cost: 100
    Quality: 80
  B:
    Cost: 150
    Quality: 90
  C:
    Cost: 120
    Quality: 85
"""

        with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config)
            f.flush()

            loader = YAMLLoader()
            data = loader.load(f.name)

            assert data["name"] == "Test Problem"
            assert len(data["alternatives"]) == 3
            assert len(data["criteria"]) == 2
            assert "scores" in data

        Path(f.name).unlink()

    def test_load_invalid_yaml(self):
        """测试加载无效的 YAML 文件"""
        with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid:\n  yaml: content:\n    - broken")
            f.flush()

            loader = YAMLLoader()

            # 无效的 YAML 应该抛出 ConfigLoadError
            from mcda_core.exceptions import ConfigLoadError
            with pytest.raises(ConfigLoadError):
                loader.load(f.name)

        Path(f.name).unlink()


class TestLoaderFactory:
    """测试 LoaderFactory"""

    def test_get_json_loader(self):
        """测试获取 JSON 加载器"""
        factory = LoaderFactory()
        loader = factory.get_loader("config.json")

        assert isinstance(loader, JSONLoader)

    def test_get_yaml_loader(self):
        """测试获取 YAML 加载器"""
        factory = LoaderFactory()

        # 测试 .yaml 扩展名
        loader1 = factory.get_loader("config.yaml")
        assert isinstance(loader1, YAMLLoader)

        # 测试 .yml 扩展名
        loader2 = factory.get_loader("config.yml")
        assert isinstance(loader2, YAMLLoader)

    def test_unsupported_format(self):
        """测试不支持的文件格式"""
        factory = LoaderFactory()

        with pytest.raises(ValueError, match="不支持的文件格式"):
            factory.get_loader("config.xml")

    def test_register_custom_loader(self):
        """测试注册自定义加载器"""
        class CustomLoader(ConfigLoader):
            def load(self, source):
                return {"custom": True}

            def validate(self, data):
                return True

        factory = LoaderFactory()
        factory.register_loader(".custom", CustomLoader)

        loader = factory.get_loader("config.custom")
        assert isinstance(loader, CustomLoader)


class TestYAMLJSONConsistency:
    """测试 YAML 和 JSON 加载一致性"""

    def test_same_content_different_format(self):
        """测试相同内容、不同格式应该产生相同的数据"""
        config_data = {
            "name": "Test Problem",
            "alternatives": ["A", "B"],
            "criteria": [
                {"name": "Cost", "weight": 0.6, "direction": "lower_better"},
                {"name": "Quality", "weight": 0.4, "direction": "higher_better"}
            ],
            "scores": {
                "A": {"Cost": 100, "Quality": 80},
                "B": {"Cost": 150, "Quality": 90}
            }
        }

        with TemporaryDirectory() as tmpdir:
            # 创建 JSON 文件
            json_file = Path(tmpdir) / "config.json"
            with open(json_file, 'w') as f:
                json.dump(config_data, f)

            # 创建 YAML 文件（相同内容）
            yaml_file = Path(tmpdir) / "config.yaml"
            with open(yaml_file, 'w') as f:
                from mcda_core.loaders import YAMLLoader
                # 简单地将数据转换为 YAML 格式
                f.write(f"name: {config_data['name']}\n")
                f.write("alternatives:\n")
                for alt in config_data['alternatives']:
                    f.write(f"  - {alt}\n")
                f.write("criteria:\n")
                for crit in config_data['criteria']:
                    f.write(f"  - name: {crit['name']}\n")
                    f.write(f"    weight: {crit['weight']}\n")
                    f.write(f"    direction: {crit['direction']}\n")
                f.write("scores:\n")
                for alt, scores in config_data['scores'].items():
                    f.write(f"  {alt}:\n")
                    for key, value in scores.items():
                        f.write(f"    {key}: {value}\n")

            # 加载并比较
            json_loader = JSONLoader()
            yaml_loader = YAMLLoader()

            json_data = json_loader.load(json_file)
            yaml_data = yaml_loader.load(yaml_file)

            # 验证关键字段相同
            assert json_data["name"] == yaml_data["name"]
            assert json_data["alternatives"] == yaml_data["alternatives"]
            assert len(json_data["criteria"]) == len(yaml_data["criteria"])
            assert len(json_data["scores"]) == len(yaml_data["scores"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
