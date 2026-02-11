"""
交互式图表生成器单元测试

测试 Plotly 交互式图表功能：
- 排名柱状图
- 雷达图
- 散点图
- 热力图
- 折线图
- HTML 导出
"""

import pytest
from pathlib import Path
import sys
import numpy as np

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent
mcda_core_path = project_root / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from visualization.interactive_charts import InteractiveChartGenerator


class TestRankingsChart:
    """排名图表测试"""

    def test_plot_rankings_vertical(self):
        """测试垂直排名柱状图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_rankings(
            alternatives=['方案A', '方案B', '方案C'],
            scores=[0.85, 0.72, 0.63],
            title='决策排名'
        )

        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].type == 'bar'

    def test_plot_rankings_horizontal(self):
        """测试水平排名柱状图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_rankings(
            alternatives=['方案A', '方案B'],
            scores=[0.85, 0.72],
            orientation='h'
        )

        assert fig is not None
        assert fig.data[0].type == 'bar'

    def test_rankings_with_custom_color(self):
        """测试自定义颜色"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_rankings(
            alternatives=['方案A', '方案B'],
            scores=[0.85, 0.72],
            color='#FF5733'
        )

        assert fig is not None


class TestRadarChart:
    """雷达图测试"""

    def test_plot_radar_single_series(self):
        """测试单系列雷达图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_radar(
            categories=['成本', '质量', '时间', '风险'],
            values=[0.8, 0.9, 0.7, 0.6],
            title='方案评估'
        )

        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatterpolar'

    def test_plot_radar_multi_series(self):
        """测试多系列雷达图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_radar(
            categories=['成本', '质量', '时间', '风险'],
            values={
                '方案A': [0.8, 0.9, 0.7, 0.6],
                '方案B': [0.7, 0.8, 0.9, 0.7]
            }
        )

        assert fig is not None
        assert len(fig.data) == 2

    def test_radar_without_fill(self):
        """测试不填充雷达图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_radar(
            categories=['成本', '质量', '时间'],
            values=[0.8, 0.9, 0.7],
            fill=False
        )

        assert fig is not None


class TestScatterChart:
    """散点图测试"""

    def test_plot_scatter_basic(self):
        """测试基本散点图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_scatter(
            x=[1, 2, 3, 4],
            y=[10, 20, 15, 25],
            title='散点图测试'
        )

        assert fig is not None
        assert len(fig.data) == 4

    def test_plot_scatter_with_labels(self):
        """测试带标签的散点图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_scatter(
            x=[1, 2, 3],
            y=[10, 20, 15],
            labels=['方案A', '方案B', '方案C']
        )

        assert fig is not None

    def test_plot_scatter_with_sizes(self):
        """测试带大小映射的散点图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_scatter(
            x=[1, 2, 3],
            y=[10, 20, 15],
            sizes=[10, 20, 30]
        )

        assert fig is not None

    def test_plot_scatter_with_colors(self):
        """测试带颜色的散点图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_scatter(
            x=[1, 2, 3],
            y=[10, 20, 15],
            colors=['#FF5733', '#33FF57', '#3357FF']
        )

        assert fig is not None


class TestHeatmapChart:
    """热力图测试"""

    def test_plot_heatmap_basic(self):
        """测试基本热力图"""
        generator = InteractiveChartGenerator()

        data = np.array([
            [0.8, 0.6, 0.7],
            [0.6, 0.9, 0.5],
            [0.7, 0.5, 0.8]
        ])

        fig = generator.plot_heatmap(
            data=data,
            row_labels=['方案A', '方案B', '方案C'],
            col_labels=['方案A', '方案B', '方案C'],
            title='相关性矩阵'
        )

        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].type == 'heatmap'

    def test_plot_heatmap_with_values(self):
        """测试显示数值的热力图"""
        generator = InteractiveChartGenerator()

        data = np.array([
            [1.0, 0.5],
            [0.5, 1.0]
        ])

        fig = generator.plot_heatmap(
            data=data,
            row_labels=['A', 'B'],
            col_labels=['A', 'B'],
            show_values=True
        )

        assert fig is not None

    def test_heatmap_custom_colorscale(self):
        """测试自定义颜色映射"""
        generator = InteractiveChartGenerator()

        data = np.array([[0.5, 0.7], [0.7, 0.5]])

        fig = generator.plot_heatmap(
            data=data,
            row_labels=['A', 'B'],
            col_labels=['A', 'B'],
            colorscale='Viridis'
        )

        assert fig is not None


class TestLineChart:
    """折线图测试"""

    def test_plot_line_single_series(self):
        """测试单系列折线图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_line(
            x=[1, 2, 3, 4],
            y=[10, 20, 15, 25],
            title='趋势图'
        )

        assert fig is not None
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatter'

    def test_plot_line_multi_series(self):
        """测试多系列折线图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_line(
            x=[1, 2, 3],
            y={
                '方案A': [10, 20, 15],
                '方案B': [15, 25, 20]
            }
        )

        assert fig is not None
        assert len(fig.data) == 2

    def test_line_without_markers(self):
        """测试不带标记的折线图"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_line(
            x=[1, 2, 3],
            y=[10, 20, 15],
            marker=False
        )

        assert fig is not None


class TestHTMLExport:
    """HTML 导出测试"""

    def test_save_html(self, tmp_path):
        """测试保存为 HTML 文件"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_rankings(
            alternatives=['方案A', '方案B'],
            scores=[0.85, 0.72]
        )

        output_file = tmp_path / 'test_chart.html'
        generator.save_html(fig, output_file)

        assert output_file.exists()

        # 验证文件内容
        content = output_file.read_text(encoding='utf-8')
        assert '<!DOCTYPE html>' in content
        assert 'plotly' in content.lower()

    def test_to_html_string(self):
        """测试转换为 HTML 字符串"""
        generator = InteractiveChartGenerator()

        fig = generator.plot_rankings(
            alternatives=['方案A', '方案B'],
            scores=[0.85, 0.72]
        )

        html = generator.to_html(fig)

        assert isinstance(html, str)
        assert len(html) > 0
        assert 'div' in html

    def test_generate_report(self, tmp_path):
        """测试生成包含多个图表的报告"""
        generator = InteractiveChartGenerator()

        fig1 = generator.plot_rankings(
            alternatives=['方案A', '方案B'],
            scores=[0.85, 0.72]
        )

        fig2 = generator.plot_radar(
            categories=['成本', '质量'],
            values=[0.8, 0.9]
        )

        output_file = tmp_path / 'report.html'
        generator.generate_report(
            figures=[fig1, fig2],
            output_path=output_file,
            title='测试报告'
        )

        assert output_file.exists()

        # 验证文件内容
        content = output_file.read_text(encoding='utf-8')
        assert '测试报告' in content
        assert '<!DOCTYPE html>' in content


class TestThemeSupport:
    """主题支持测试"""

    def test_different_themes(self):
        """测试不同主题"""
        for theme in ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn']:
            generator = InteractiveChartGenerator(theme=theme)

            fig = generator.plot_rankings(
                alternatives=['方案A', '方案B'],
                scores=[0.85, 0.72]
            )

            assert fig is not None
            assert fig.layout.template is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
