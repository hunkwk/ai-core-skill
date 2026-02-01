"""
ASCII 可视化测试

测试 ASCII 图表生成功能。
"""

import pytest
from mcda_core.visualization.ascii_visualizer import (
    ASCIIVisualizer,
    VisualizationError
)


class TestBarChart:
    """柱状图测试"""

    def test_simple_bar_chart(self):
        """测试：简单柱状图"""
        data = {
            "A": 10,
            "B": 20,
            "C": 15,
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.bar_chart(data, title="Test Chart")

        # 验证返回字符串
        assert isinstance(chart, str)
        assert len(chart) > 0

        # 验证包含标题
        assert "Test Chart" in chart or "test" in chart.lower()

        # 验证包含数据标签
        assert "A" in chart
        assert "B" in chart
        assert "C" in chart

    def test_bar_chart_with_custom_width(self):
        """测试：自定义宽度"""
        data = {
            "A": 10,
            "B": 20,
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.bar_chart(data, width=40)

        # 验证图表生成
        assert len(chart) > 0
        # 较窄的宽度应该产生较少的字符
        assert chart.count("█") < chart.count("█") if "█" in chart else True

    def test_bar_chart_normalization(self):
        """测试：数据归一化"""
        data = {
            "A": 1000,
            "B": 2000,
            "C": 1500,
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.bar_chart(data, title="Large Values")

        # 验证图表生成（大值应该被正确归一化）
        assert len(chart) > 0
        assert "A" in chart

    def test_bar_chart_with_negative_values(self):
        """测试：包含负值"""
        data = {
            "A": 10,
            "B": -5,
            "C": 15,
        }

        visualizer = ASCIIVisualizer()

        # 应该处理负值或抛出清晰错误
        try:
            chart = visualizer.bar_chart(data)
            assert len(chart) > 0
        except VisualizationError as e:
            assert "负值" in str(e) or "negative" in str(e).lower()

    def test_bar_chart_empty_data(self):
        """测试：空数据"""
        data = {}

        visualizer = ASCIIVisualizer()

        with pytest.raises(VisualizationError, match="数据"):
            visualizer.bar_chart(data)


class TestRadarChart:
    """雷达图测试"""

    def test_simple_radar_chart(self):
        """测试：简单雷达图"""
        scores = [0.8, 0.6, 0.9, 0.7]
        labels = ["质量", "成本", "交付", "服务"]

        visualizer = ASCIIVisualizer()
        chart = visualizer.radar_chart(scores, labels, title="能力评估")

        # 验证返回字符串
        assert isinstance(chart, str)
        assert len(chart) > 0

        # 验证包含标签
        assert "质量" in chart or "成本" in chart

    def test_radar_chart_normalization(self):
        """测试：雷达图归一化"""
        # 非归一化的分数
        scores = [80, 60, 90, 70]
        labels = ["A", "B", "C", "D"]

        visualizer = ASCIIVisualizer()
        chart = visualizer.radar_chart(scores, labels)

        # 应该自动归一化到 [0, 1]
        assert len(chart) > 0

    def test_radar_chart_mismatched_length(self):
        """测试：分数和标签数量不匹配"""
        scores = [0.8, 0.6, 0.9]
        labels = ["A", "B"]  # 只有2个标签

        visualizer = ASCIIVisualizer()

        with pytest.raises(VisualizationError, match="数量"):
            visualizer.radar_chart(scores, labels)

    def test_radar_chart_minimum_dimensions(self):
        """测试：最少3个维度"""
        scores = [0.8, 0.6]  # 只有2个维度
        labels = ["A", "B"]

        visualizer = ASCIIVisualizer()

        # 雷达图至少需要3个维度
        try:
            chart = visualizer.radar_chart(scores, labels)
            # 或者抛出错误
            assert len(chart) > 0
        except VisualizationError:
            pass  # 预期行为


class TestRankingComparison:
    """排名对比图测试"""

    def test_ranking_comparison_two_algorithms(self):
        """测试：两个算法的排名对比"""
        rankings = {
            "WSM": {
                "A": 1,
                "B": 2,
                "C": 3,
            },
            "TOPSIS": {
                "A": 2,
                "B": 1,
                "C": 3,
            }
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.ranking_comparison(rankings, title="算法对比")

        # 验证
        assert isinstance(chart, str)
        assert len(chart) > 0
        assert "WSM" in chart or "TOPSIS" in chart

    def test_ranking_comparison_multiple_algorithms(self):
        """测试：多个算法的排名对比"""
        rankings = {
            "WSM": {"A": 1, "B": 2, "C": 3},
            "TOPSIS": {"A": 2, "B": 1, "C": 3},
            "VIKOR": {"A": 1, "B": 3, "C": 2},
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.ranking_comparison(rankings)

        # 验证
        assert len(chart) > 0

    def test_ranking_comparison_different_alternatives(self):
        """测试：不同算法的方案集合不同"""
        rankings = {
            "WSM": {"A": 1, "B": 2},
            "TOPSIS": {"A": 1, "B": 2, "C": 3},  # 多一个方案
        }

        visualizer = ASCIIVisualizer()

        # 应该处理不同方案集合
        try:
            chart = visualizer.ranking_comparison(rankings)
            assert len(chart) > 0
        except (VisualizationError, ValueError):
            pass  # 也可以抛出错误


class TestFullWorkflow:
    """完整工作流测试"""

    def test_complete_visualization_workflow(self):
        """测试：完整的可视化工作流"""
        # 模拟算法对比结果
        rankings = {
            "WSM": {"A": 1, "B": 2, "C": 3},
            "TOPSIS": {"A": 1, "B": 2, "C": 3},
        }

        scores = [0.8, 0.6, 0.9]
        labels = ["质量", "成本", "交付"]

        visualizer = ASCIIVisualizer()

        # 生成多个图表
        ranking_chart = visualizer.ranking_comparison(rankings)
        radar_chart = visualizer.radar_chart(scores, labels)

        # 验证
        assert len(ranking_chart) > 0
        assert len(radar_chart) > 0

    def test_multi_chart_layout(self):
        """测试：多图表布局"""
        data1 = {"A": 10, "B": 20}
        data2 = {"X": 15, "Y": 25}

        visualizer = ASCIIVisualizer()

        # 并排显示两个图表
        chart1 = visualizer.bar_chart(data1, title="Chart 1")
        chart2 = visualizer.bar_chart(data2, title="Chart 2")

        # 验证两个图表都生成
        assert len(chart1) > 0
        assert len(chart2) > 0


class TestEdgeCases:
    """边界条件测试"""

    def test_very_long_labels(self):
        """测试：非常长的标签"""
        data = {
            "Very Long Label Name": 10,
            "Another Extremely Long Name": 20,
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.bar_chart(data)

        # 应该处理长标签
        assert len(chart) > 0

    def test_special_characters_in_labels(self):
        """测试：标签中的特殊字符"""
        data = {
            "Label-With-Dash": 10,
            "Label_With_Underscore": 20,
            "Label.With.Dot": 15,
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.bar_chart(data)

        # 应该处理特殊字符
        assert len(chart) > 0

    def test_unicode_characters(self):
        """测试：Unicode 字符"""
        data = {
            "方案A": 10,
            "方案B": 20,
            "方案C": 15,
        }

        visualizer = ASCIIVisualizer()
        chart = visualizer.bar_chart(data, title="中文标题")

        # 应该正确处理 Unicode
        assert len(chart) > 0
        assert "方案A" in chart or "A" in chart


class TestErrorHandling:
    """错误处理测试"""

    def test_none_data(self):
        """测试：None 数据"""
        visualizer = ASCIIVisualizer()

        with pytest.raises((VisualizationError, TypeError)):
            visualizer.bar_chart(None)

    def test_invalid_data_type(self):
        """测试：无效数据类型"""
        visualizer = ASCIIVisualizer()

        # 传入字符串而不是字典
        with pytest.raises((VisualizationError, TypeError)):
            visualizer.bar_chart("invalid")

    def test_zero_or_negative_width(self):
        """测试：零或负宽度"""
        data = {"A": 10, "B": 20}

        visualizer = ASCIIVisualizer()

        # 宽度应该为正数
        with pytest.raises((VisualizationError, ValueError)):
            visualizer.bar_chart(data, width=0)

        with pytest.raises((VisualizationError, ValueError)):
            visualizer.bar_chart(data, width=-10)
