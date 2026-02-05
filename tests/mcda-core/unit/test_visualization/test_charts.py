"""
图表生成器单元测试

测试 ChartGenerator 的各种图表生成功能。
"""

import pytest
from pathlib import Path
import tempfile

# 尝试导入 matplotlib，如果未安装则跳过测试
pytest.importorskip("matplotlib")

from mcda_core.visualization import ChartGenerator


class TestChartGenerator:
    """ChartGenerator 测试类"""

    def setup_method(self):
        """每个测试前的设置"""
        self.generator = ChartGenerator()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试后的清理"""
        self.generator.clear_figures()

    def test_plot_rankings_bar(self):
        """测试绘制排名柱状图"""
        rankings = ['方案A', '方案B', '方案C']
        scores = {'方案A': 0.85, '方案B': 0.72, '方案C': 0.65}

        fig = self.generator.plot_rankings(rankings, scores)

        assert fig is not None
        assert len(self.generator.figures) == 1

    def test_plot_sensitivity_line(self):
        """测试绘制敏感性分析折线图"""
        parameter_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        rankings_changes = [
            ['方案A', '方案B', '方案C'],
            ['方案B', '方案A', '方案C'],
            ['方案B', '方案C', '方案A'],
            ['方案C', '方案B', '方案A'],
            ['方案C', '方案A', '方案B'],
        ]

        fig = self.generator.plot_sensitivity(parameter_values, rankings_changes)

        assert fig is not None
        assert len(self.generator.figures) == 1

    def test_plot_weights_pie(self):
        """测试绘制权重饼图"""
        criteria = ['性能', '成本', '可靠性', '易用性']
        weights = [0.4, 0.3, 0.2, 0.1]

        fig = self.generator.plot_weights(criteria, weights)

        assert fig is not None
        assert len(self.generator.figures) == 1

    def test_plot_interval_comparison(self):
        """测试绘制区间数对比图"""
        alternatives = ['方案A', '方案B', '方案C']
        intervals = [(0.80, 0.90), (0.85, 0.95), (0.75, 0.82)]

        fig = self.generator.plot_interval_comparison(alternatives, intervals)

        assert fig is not None
        assert len(self.generator.figures) == 1

    def test_export_chart_to_png(self):
        """测试导出图表为 PNG"""
        rankings = ['方案A', '方案B', '方案C']
        scores = {'方案A': 0.85, '方案B': 0.72, '方案C': 0.65}

        fig = self.generator.plot_rankings(rankings, scores)
        output_path = Path(self.temp_dir) / 'test_chart.png'

        self.generator.export_chart(fig, output_path)

        assert output_path.exists()

    def test_export_chart_to_svg(self):
        """测试导出图表为 SVG"""
        rankings = ['方案A', '方案B', '方案C']
        scores = {'方案A': 0.85, '方案B': 0.72, '方案C': 0.65}

        fig = self.generator.plot_rankings(rankings, scores)
        output_path = Path(self.temp_dir) / 'test_chart.svg'

        self.generator.export_chart(fig, output_path)

        assert output_path.exists()

    def test_clear_figures(self):
        """测试清除所有图表"""
        rankings = ['方案A', '方案B', '方案C']
        scores = {'方案A': 0.85, '方案B': 0.72, '方案C': 0.65}

        self.generator.plot_rankings(rankings, scores)
        assert len(self.generator.figures) == 1

        self.generator.clear_figures()
        assert len(self.generator.figures) == 0
