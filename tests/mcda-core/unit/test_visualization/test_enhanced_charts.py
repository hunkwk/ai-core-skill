"""
增强图表生成器单元测试

测试新增的图表类型：
- 雷达图（Radar Chart）
- 热力图（Heatmap）
- 散点图（Scatter Plot）
- 通用折线图（Line Chart）
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent
mcda_core_path = project_root / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from visualization.charts import ChartGenerator


class TestRadarChart:
    """雷达图测试"""

    def test_radar_chart_basic(self):
        """测试基本雷达图生成"""
        generator = ChartGenerator()

        # 测试数据：3个维度
        categories = ['质量', '成本', '交付']
        values = [0.8, 0.6, 0.9]

        fig = generator.plot_radar(
            categories=categories,
            values=values,
            title="测试雷达图"
        )

        assert fig is not None
        assert hasattr(fig, 'axes')
        assert len(fig.axes) > 0

        generator.clear_figures()

    def test_radar_chart_multiple_series(self):
        """测试多系列雷达图"""
        generator = ChartGenerator()

        categories = ['质量', '成本', '交付', '服务']
        series_data = {
            '方案A': [0.8, 0.6, 0.9, 0.7],
            '方案B': [0.7, 0.8, 0.6, 0.9]
        }

        fig = generator.plot_radar(
            categories=categories,
            values=series_data,
            title="多方案对比"
        )

        assert fig is not None
        generator.clear_figures()

    def test_radar_chart_invalid_input(self):
        """测试无效输入"""
        generator = ChartGenerator()

        # 维度数量不匹配
        with pytest.raises(ValueError):
            generator.plot_radar(
                categories=['A', 'B', 'C'],
                values=[0.5, 0.6]  # 少于类别数
            )

    def test_radar_chart_normalization(self):
        """测试数据归一化"""
        generator = ChartGenerator()

        categories = ['A', 'B', 'C']
        values = [100, 200, 150]  # 未归一化

        fig = generator.plot_radar(
            categories=categories,
            values=values,
            normalize=True,
            title="归一化测试"
        )

        assert fig is not None
        generator.clear_figures()


class TestHeatmap:
    """热力图测试"""

    def test_heatmap_basic(self):
        """测试基本热力图生成"""
        generator = ChartGenerator()

        # 测试数据：3个方案 × 4个准则
        data = np.array([
            [0.8, 0.6, 0.9, 0.7],
            [0.7, 0.8, 0.6, 0.9],
            [0.9, 0.5, 0.7, 0.8]
        ])
        alternatives = ['方案A', '方案B', '方案C']
        criteria = ['质量', '成本', '交付', '服务']

        fig = generator.plot_heatmap(
            data=data,
            row_labels=alternatives,
            col_labels=criteria,
            title="准则评分热力图"
        )

        assert fig is not None
        generator.clear_figures()

    def test_heatmap_correlation(self):
        """测试相关性热力图"""
        generator = ChartGenerator()

        # 相关性矩阵（4x4）
        correlation_matrix = np.array([
            [1.0, 0.3, -0.2, 0.5],
            [0.3, 1.0, 0.4, 0.1],
            [-0.2, 0.4, 1.0, 0.6],
            [0.5, 0.1, 0.6, 1.0]
        ])
        criteria = ['C1', 'C2', 'C3', 'C4']

        fig = generator.plot_heatmap(
            data=correlation_matrix,
            row_labels=criteria,
            col_labels=criteria,
            title="准则相关性矩阵",
            cmap='coolwarm',
            show_values=True
        )

        assert fig is not None
        generator.clear_figures()

    def test_heatmap_invalid_shape(self):
        """测试数据形状不匹配"""
        generator = ChartGenerator()

        data = np.array([[1, 2], [3, 4]])  # 2x2
        row_labels = ['A', 'B', 'C']  # 3行标签
        col_labels = ['X', 'Y']  # 2列标签

        with pytest.raises(ValueError):
            generator.plot_heatmap(
                data=data,
                row_labels=row_labels,
                col_labels=col_labels
            )


class TestScatterPlot:
    """散点图测试"""

    def test_scatter_basic(self):
        """测试基本散点图"""
        generator = ChartGenerator()

        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        labels = ['A', 'B', 'C', 'D', 'E']

        fig = generator.plot_scatter(
            x=x,
            y=y,
            labels=labels,
            title="方案分布图"
        )

        assert fig is not None
        generator.clear_figures()

    def test_scatter_with_groups(self):
        """测试分组散点图"""
        generator = ChartGenerator()

        group_a = {'x': [1, 2, 3], 'y': [2, 4, 6], 'label': '组A'}
        group_b = {'x': [4, 5, 6], 'y': [3, 5, 7], 'label': '组B'}

        fig = generator.plot_scatter(
            groups=[group_a, group_b],
            title="分组散点图"
        )

        assert fig is not None
        generator.clear_figures()

    def test_scatter_with_size(self):
        """测试带大小映射的散点图"""
        generator = ChartGenerator()

        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        sizes = [50, 100, 150, 200, 250]
        labels = ['A', 'B', 'C', 'D', 'E']

        fig = generator.plot_scatter(
            x=x,
            y=y,
            labels=labels,
            sizes=sizes,
            title="带大小映射的散点图"
        )

        assert fig is not None
        generator.clear_figures()


class TestLineChart:
    """折线图测试"""

    def test_line_chart_basic(self):
        """测试基本折线图"""
        generator = ChartGenerator()

        x = [1, 2, 3, 4, 5]
        y = [10, 20, 15, 25, 30]

        fig = generator.plot_line(
            x=x,
            y=y,
            title="趋势分析"
        )

        assert fig is not None
        generator.clear_figures()

    def test_line_chart_multiple_series(self):
        """测试多系列折线图"""
        generator = ChartGenerator()

        x = [1, 2, 3, 4, 5]
        series_data = {
            '方案A': [10, 20, 15, 25, 30],
            '方案B': [15, 18, 20, 22, 28]
        }

        fig = generator.plot_line(
            x=x,
            y=series_data,
            title="多方案趋势对比"
        )

        assert fig is not None
        generator.clear_figures()

    def test_line_chart_with_markers(self):
        """测试带标记的折线图"""
        generator = ChartGenerator()

        x = [1, 2, 3, 4, 5]
        y = [10, 20, 15, 25, 30]

        fig = generator.plot_line(
            x=x,
            y=y,
            marker='o',
            linestyle='--',
            title="带标记的折线图"
        )

        assert fig is not None
        generator.clear_figures()


class TestChartExport:
    """图表导出测试"""

    def test_export_radar_chart(self, tmp_path):
        """测试导出雷达图"""
        generator = ChartGenerator()

        fig = generator.plot_radar(
            categories=['A', 'B', 'C'],
            values=[0.8, 0.6, 0.9]
        )

        output_file = tmp_path / "radar_chart.png"
        generator.export_chart(fig, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

        generator.clear_figures()

    def test_export_heatmap(self, tmp_path):
        """测试导出热力图"""
        generator = ChartGenerator()

        data = np.array([[1, 2], [3, 4]])
        fig = generator.plot_heatmap(
            data=data,
            row_labels=['A', 'B'],
            col_labels=['X', 'Y']
        )

        output_file = tmp_path / "heatmap.png"
        generator.export_chart(fig, output_file)

        assert output_file.exists()

        generator.clear_figures()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
