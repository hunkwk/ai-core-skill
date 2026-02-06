# -*- coding: utf-8 -*-
"""
MCDA Core - 数据加载 E2E 测试

测试各种数据格式的加载功能。
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import yaml
import json

from mcda_core.core import MCDAOrchestrator
from mcda_core.loaders import (
    YAMLLoader,
    JSONLoader,
    CSVLoader,
    ExcelLoader,
    LoaderFactory,
)
from mcda_core.exceptions import ConfigLoadError


class TestDataLoaders:
    """数据加载器端到端测试"""

    def test_yaml_loader(self):
        """测试: YAML 加载器"""
        loader = YAMLLoader()

        # 创建临时 YAML 文件
        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text("""name: 测试问题
alternatives:
  - 方案A
  - 方案B
criteria:
  - name: 性能
    weight: 0.6
    direction: higher_better
  - name: 成本
    weight: 0.4
    direction: lower_better
scores:
  方案A:
    性能: 85
    成本: 50
  方案B:
    性能: 90
    成本: 60
algorithm:
  name: wsm
""", encoding='utf-8')

            # 加载配置
            config = loader.load(yaml_file)

            # 验证
            assert config['name'] == '测试问题'
            assert len(config['alternatives']) == 2
            assert len(config['criteria']) == 2
            assert config['scores']['方案A']['性能'] == 85

    def test_json_loader(self):
        """测试: JSON 加载器"""
        loader = JSONLoader()

        with TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "test.json"
            data = {
                "name": "测试问题",
                "alternatives": ["方案A", "方案B"],
                "criteria": [
                    {"name": "性能", "weight": 0.6, "direction": "higher_better"},
                    {"name": "成本", "weight": 0.4, "direction": "lower_better"}
                ],
                "scores": {
                    "方案A": {"性能": 85, "成本": 50},
                    "方案B": {"性能": 90, "成本": 60}
                },
                "algorithm": {"name": "wsm"}
            }

            json_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

            # 加载配置
            config = loader.load(json_file)

            # 验证
            assert config['name'] == '测试问题'
            assert len(config['alternatives']) == 2
            assert config['scores']['方案A']['性能'] == 85

    def test_csv_loader(self):
        """测试: CSV 加载器"""
        loader = CSVLoader()

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "test.csv"
            csv_content = """方案A,方案B,方案C
性能,0.4,higher,85,90,88
成本,0.3,lower,5000,6000,5500
质量,0.3,higher,80,85,82
"""
            csv_file.write_text(csv_content, encoding='utf-8')

            # 加载配置
            config = loader.load(csv_file)

            # 验证 CSV 格式
            assert len(config['alternatives']) == 3
            assert len(config['criteria']) == 3
            assert config['criteria'][0]['name'] == '性能'
            assert config['criteria'][0]['weight'] == 0.4
            # CSV 返回 matrix 而不是 scores
            assert config['matrix'][0][0] == 85  # 方案A 的性能得分

    def test_csv_with_interval_scores(self):
        """测试: CSV 加载器 - 区间数格式"""
        loader = CSVLoader()

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "test_interval.csv"
            # 每个方案 2 个数值（区间数）
            csv_content = """方案A,方案B
性能,0.6,higher,"80,90","85,95"
成本,0.4,lower,"40,50","30,40"
"""
            csv_file.write_text(csv_content, encoding='utf-8')

            # 加载配置
            config = loader.load(csv_file)

            # 验证区间数格式
            from mcda_core.interval import Interval
            assert config['matrix'][0][0] == Interval(80, 90)  # 方案A 的性能（区间）
            assert config['matrix'][0][1] == Interval(85, 95)  # 方案B 的性能（区间）

    def test_loader_factory_auto_detection(self):
        """测试: 加载器工厂自动检测格式"""
        with TemporaryDirectory() as tmpdir:
            # 创建不同格式的文件
            yaml_file = Path(tmpdir) / "test.yaml"
            json_file = Path(tmpdir) / "test.json"
            csv_file = Path(tmpdir) / "test.csv"

            yaml_file.write_text("name: test\nalternatives: [A, B]\n", encoding='utf-8')
            json_file.write_text('{"name": "test"}', encoding='utf-8')
            csv_file.write_text("A,B\n性能,0.5,higher,80,90\n", encoding='utf-8')

            # 测试自动检测
            yaml_loader = LoaderFactory.get_loader(yaml_file)
            json_loader = LoaderFactory.get_loader(json_file)
            csv_loader = LoaderFactory.get_loader(csv_file)

            assert isinstance(yaml_loader, YAMLLoader)
            assert isinstance(json_loader, JSONLoader)
            assert isinstance(csv_loader, CSVLoader)

    def test_csv_to_yaml_conversion(self):
        """测试: CSV 转换为 YAML 格式"""
        loader = CSVLoader()

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "vendor_data.csv"
            csv_content = """供应商A,供应商B,供应商C,供应商D
性能,0.3,higher,85,90,88,82
成本,0.3,lower,5000,6000,4500,5500
质量,0.2,higher,80,85,82,78
服务,0.2,higher,75,80,78,76
"""
            csv_file.write_text(csv_content, encoding='utf-8')

            # 加载 CSV
            csv_config = loader.load(csv_file)

            # 转换为 YAML 格式（构建 scores 字典）
            alternatives = csv_config['alternatives']
            criteria = csv_config['criteria']
            matrix = csv_config['matrix']

            # 构建 scores 字典
            scores = {}
            for i, alt in enumerate(alternatives):
                scores[alt] = {}
                for j, criterion in enumerate(criteria):
                    scores[alt][criterion['name']] = matrix[j][i]

            # 构建 YAML 配置
            yaml_config = {
                'name': '供应商选择',
                'alternatives': alternatives,
                'criteria': criteria,
                'scores': scores,
                'algorithm': {'name': 'wsm'}
            }

            # 验证转换结果
            assert len(yaml_config['alternatives']) == 4
            assert len(yaml_config['criteria']) == 4
            assert yaml_config['scores']['供应商A']['性能'] == 85

    def test_unsupported_format(self):
        """测试: 不支持的文件格式"""
        with TemporaryDirectory() as tmpdir:
            txt_file = Path(tmpdir) / "test.txt"
            txt_file.write_text("some text", encoding='utf-8')

            # 应该抛出 ValueError
            with pytest.raises(ValueError, match="不支持的文件格式"):
                LoaderFactory.get_loader(txt_file)

    def test_csv_with_chinese_encoding(self):
        """测试: CSV 中文编码支持"""
        loader = CSVLoader()

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "test_gbk.csv"

            # 尝试 GBK 编码（常见于 Windows Excel 导出）
            content = """供应商A,供应商B
性能,0.6,higher,85,90
成本,0.4,lower,5000,6000
"""
            csv_file.write_bytes(content.encode('gbk'))

            # 应该能正常加载（自动检测编码）
            config = loader.load(csv_file)

            assert len(config['alternatives']) == 2
            assert config['criteria'][0]['name'] == '性能'

    def test_csv_injection_protection(self):
        """测试: CSV 注入防护"""
        loader = CSVLoader()

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "test_injection.csv"
            # 尝试注入公式
            csv_content = """方案A
性能,0.5,higher,=SUM(1+1)
"""
            csv_file.write_text(csv_content, encoding='utf-8')

            # 应该抛出 ValueError（危险字符）
            with pytest.raises(ValueError, match="CSV 文件格式错误"):
                loader.load(csv_file)

    def test_yaml_complex_example(self):
        """测试: 复杂 YAML 配置加载"""
        loader = YAMLLoader()

        with TemporaryDirectory() as tmpdir:
            yaml_file = Path(tmpdir) / "complex.yaml"
            yaml_file.write_text("""name: 产品优先级排序
alternatives:
  - 产品A
  - 产品B
  - 产品C
  - 产品D
criteria:
  - name: 市场需求
    weight: 0.3
    direction: higher_better
  - name: 技术可行性
    weight: 0.25
    direction: higher_better
  - name: 成本效益
    weight: 0.25
    direction: higher_better
  - name: 战略契合度
    weight: 0.2
    direction: higher_better
scores:
  产品A:
    市场需求: 85
    技术可行性: 75
    成本效益: 80
    战略契合度: 70
  产品B:
    市场需求: 90
    技术可行性: 85
    成本效益: 75
    战略契合度: 85
  产品C:
    市场需求: 78
    技术可行性: 90
    成本效益: 85
    战略契合度: 75
  产品D:
    市场需求: 82
    技术可行性: 80
    成本效益: 70
    战略契合度: 80
algorithm:
  name: topsis
""", encoding='utf-8')

            # 加载配置
            config = loader.load(yaml_file)

            # 验证
            assert config['name'] == '产品优先级排序'
            assert len(config['alternatives']) == 4
            assert len(config['criteria']) == 4
            assert config['algorithm']['name'] == 'topsis'

            # 验证所有评分都存在
            for alt in config['alternatives']:
                for criterion in config['criteria']:
                    assert criterion['name'] in config['scores'][alt]
