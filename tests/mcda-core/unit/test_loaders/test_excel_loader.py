"""
Excel Loader 单元测试

测试 Excel 配置文件加载器的功能，包括：
- 标准 Excel 格式
- 区间数格式
- 多 Sheet 支持
- 错误处理
"""

import pytest
from pathlib import Path

from mcda_core.loaders import ExcelLoader
from mcda_core.exceptions import ConfigLoadError


class TestExcelLoader:
    """Excel Loader 测试类"""

    def setup_method(self):
        """每个测试前的设置"""
        self.loader = ExcelLoader()
        self.fixtures_dir = Path(__file__).parent.parent.parent / 'fixtures'

    def test_load_standard_excel(self):
        """测试加载标准 Excel 格式"""
        excel_file = self.fixtures_dir / 'decision_data.xlsx'
        config = self.loader.load(excel_file)

        assert config is not None
        assert 'alternatives' in config
        assert 'criteria' in config
        assert 'matrix' in config
        assert len(config['alternatives']) == 3
        assert len(config['criteria']) == 4

    def test_load_interval_excel(self):
        """测试加载区间数 Excel 格式"""
        excel_file = self.fixtures_dir / 'decision_data_interval.xlsx'
        config = self.loader.load(excel_file)

        assert config is not None
        # 验证区间数解析
        from mcda_core.interval import Interval
        assert isinstance(config['matrix'][0][0], Interval)

    def test_load_specific_sheet(self):
        """测试加载指定 Sheet"""
        excel_file = self.fixtures_dir / 'decision_data.xlsx'
        config = self.loader.load(excel_file, sheet='Sheet1')

        assert config is not None
        assert config['metadata']['sheet'] == 'Sheet1'

    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            self.loader.load('nonexistent.xlsx')

    def test_invalid_format(self):
        """测试无效格式"""
        # TODO: 创建错误格式的 Excel 测试文件
        pass

    def test_openpyxl_not_installed(self, monkeypatch):
        """测试 openpyxl 未安装的情况"""
        # TODO: 模拟 openpyxl 未安装
        pass


class TestExcelLoaderIntegration:
    """Excel Loader 集成测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.loader = ExcelLoader()
        self.fixtures_dir = Path(__file__).parent.parent.parent / 'fixtures'

    def test_excel_to_mcda_workflow(self):
        """测试从 Excel 到 MCDA 决策的完整流程"""
        excel_file = self.fixtures_dir / 'decision_data.xlsx'
        config = self.loader.load(excel_file)

        # 验证配置结构
        assert config is not None
        assert 'alternatives' in config
        assert 'criteria' in config
        assert 'matrix' in config

        # 验证数据完整性
        assert len(config['alternatives']) == 3
        assert len(config['criteria']) == 4
        assert config['metadata']['format'] == 'excel'
        assert 'sheet' in config['metadata']
