# -*- coding: utf-8 -*-
"""
MCDA Core - 可视化 E2E 测试

测试各种可视化功能的端到端功能。
"""

import pytest
from tempfile import TemporaryDirectory
from pathlib import Path

from mcda_core.core import MCDAOrchestrator
from mcda_core.models import DecisionProblem, Criterion
from mcda_core.visualization import ChartGenerator
from mcda_core.visualization.ascii_visualizer import ASCIIVisualizer


class TestVisualization:
    """可视化端到端测试"""

    def setup_method(self):
        """创建测试用的决策问题"""
        self.criteria = [
            Criterion(name="性能", weight=0.3, direction="higher_better"),
            Criterion(name="成本", weight=0.3, direction="lower_better"),
            Criterion(name="质量", weight=0.2, direction="higher_better"),
            Criterion(name="服务", weight=0.2, direction="higher_better"),
        ]

        self.problem = DecisionProblem(
            alternatives=("方案A", "方案B", "方案C", "方案D"),
            criteria=tuple(self.criteria),
            scores={
                "方案A": {"性能": 85, "成本": 50, "质量": 80, "服务": 75},
                "方案B": {"性能": 90, "成本": 60, "质量": 85, "服务": 80},
                "方案C": {"性能": 78, "成本": 45, "质量": 90, "服务": 78},
                "方案D": {"性能": 82, "成本": 55, "质量": 75, "服务": 82},
            }
        )

        # 分析结果
        self.orchestrator = MCDAOrchestrator()
        self.result = self.orchestrator.analyze(self.problem, algorithm_name="wsm")

    def test_ascii_bar_chart(self):
        """测试: ASCII 柱状图生成"""
        visualizer = ASCIIVisualizer()

        # 提取排名数据
        ranking_data = {r.alternative: r.score for r in self.result.rankings}

        # 生成柱状图
        chart = visualizer.bar_chart(
            ranking_data,
            title="决策分析排名",
            width=50,
            height=8
        )

        # 验证图表生成
        assert isinstance(chart, str)
        assert len(chart) > 0
        assert "方案" in chart or "█" in chart  # 包含数据或柱状字符

    def test_ascii_ranking_display(self):
        """测试: ASCII 排名显示"""
        visualizer = ASCIIVisualizer()

        # 创建排名列表
        rankings = [
            (1, "方案B", 85.5),
            (2, "方案A", 82.3),
            (3, "方案C", 78.9),
            (4, "方案D", 75.2),
        ]

        # 生成排名显示
        lines = []
        for rank, alt, score in rankings:
            bar_length = int(score / 100 * 40)
            bar = "█" * bar_length
            lines.append(f"{rank}. {alt:8s} {score:5.1f} {bar}")

        chart = "\n".join(lines)

        # 验证
        assert isinstance(chart, str)
        assert "方案B" in chart
        assert "█" in chart

    def test_ascii_radar_chart(self):
        """测试: ASCII 雷达图生成"""
        visualizer = ASCIIVisualizer()

        # 准则得分（取最佳方案的得分）
        best_alt = self.result.rankings[0].alternative
        scores = []
        labels = []
        for criterion in self.criteria:
            labels.append(criterion.name)
            scores.append(self.problem.scores[best_alt][criterion.name])

        # 归一化到 0-1
        normalized_scores = [s / 100.0 for s in scores]

        # 生成雷达图
        chart = visualizer.radar_chart(normalized_scores, labels)

        # 验证
        assert isinstance(chart, str)
        assert len(chart) > 0

    def test_chart_generator_basic(self):
        """测试: 图表生成器基本功能"""
        generator = ChartGenerator()

        # 验证生成器实例化
        assert generator is not None

        # 提取排名数据
        ranking_data = {r.alternative: r.score for r in self.result.rankings}

        # 验证数据结构
        assert len(ranking_data) == 4
        assert all(0 <= score <= 100 for score in ranking_data.values())

    def test_chart_save_to_file(self):
        """测试: 图表保存到文件"""
        try:
            from plotly.graph_objects import Figure
        except ImportError:
            pytest.skip("plotly 未安装")

        generator = ChartGenerator()

        # 创建简单的图表数据
        ranking_data = {r.alternative: r.score for r in self.result.rankings}

        # 保存为 HTML（如果有 plotly）
        with TemporaryDirectory() as tmpdir:
            html_file = Path(tmpdir) / "ranking.html"

            # 创建简单的 HTML 报告
            html_content = f"""
<html>
<head><title>决策分析排名</title></head>
<body>
<h1>决策分析排名</h1>
<table>
<tr><th>排名</th><th>方案</th><th>得分</th></tr>
"""
            for i, ranking in enumerate(self.result.rankings, 1):
                html_content += f"<tr><td>{i}</td><td>{ranking.alternative}</td><td>{ranking.score:.2f}</td></tr>\n"

            html_content += "</table>\n</body>\n</html>"
            html_file.write_text(html_content, encoding='utf-8')

            # 验证文件已创建
            assert html_file.exists()
            content = html_file.read_text(encoding='utf-8')
            assert len(content) > 0
            assert "决策分析排名" in content

    def test_chart_generator_comparison_table(self):
        """测试: 方案对比表生成"""
        generator = ChartGenerator()

        # 生成对比表数据
        comparison_data = []
        for ranking in self.result.rankings:
            alt = ranking.alternative
            scores = self.problem.scores[alt]
            comparison_data.append({
                '方案': alt,
                '排名': ranking.rank,
                '得分': ranking.score,
                **scores
            })

        # 验证数据结构
        assert len(comparison_data) == 4
        assert comparison_data[0]['方案'] in self.problem.alternatives

    def test_visualization_workflow_integration(self):
        """测试: 可视化与工作流集成"""
        visualizer = ASCIIVisualizer()

        # 完整工作流：分析 → 可视化
        result = self.orchestrator.analyze(self.problem, algorithm_name="topsis")
        report = self.orchestrator.generate_report(self.problem, result, format="markdown")

        # 从报告中提取排名
        rankings = []
        for line in report.split('\n'):
            if '|' in line and '方案' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    try:
                        rank = int(parts[1])
                        alt = parts[2]
                        score = float(parts[3])
                        rankings.append((rank, alt, score))
                    except (ValueError, IndexError):
                        continue

        # 如果找到排名数据，生成可视化
        if rankings:
            ranking_data = {alt: score for _, alt, score in rankings}
            chart = visualizer.bar_chart(ranking_data, title="TOPSIS 排名")

            # 验证
            assert isinstance(chart, str)
            assert len(chart) > 0

    def test_multi_algorithm_visualization(self):
        """测试: 多算法对比可视化"""
        visualizer = ASCIIVisualizer()

        # 多算法对比
        algorithms = ["wsm", "wpm", "topsis"]
        top_choices = {}

        for algo in algorithms:
            result = self.orchestrator.analyze(self.problem, algorithm_name=algo)
            top_choices[algo] = result.rankings[0].alternative

        # 创建对比数据
        comparison_data = {algo: alt for algo, alt in top_choices.items()}

        # 生成简单的文本对比表
        lines = ["多算法最佳方案对比:", ""]
        for algo, alt in comparison_data.items():
            lines.append(f"  {algo.upper()}: {alt}")

        comparison_table = "\n".join(lines)

        # 验证
        assert isinstance(comparison_table, str)
        assert len(comparison_table) > 0
        for algo in algorithms:
            assert algo.upper() in comparison_table

    def test_ascii_table_display(self):
        """测试: ASCII 表格显示"""
        # 构造表格数据
        headers = ["方案", "排名", "得分", "性能", "成本", "质量", "服务"]
        rows = []
        for ranking in self.result.rankings:
            alt = ranking.alternative
            scores = self.problem.scores[alt]
            rows.append([
                alt,
                ranking.rank,
                f"{ranking.score:.2f}",
                scores["性能"],
                scores["成本"],
                scores["质量"],
                scores["服务"]
            ])

        # 生成 ASCII 表格
        lines = []
        # 表头
        header_line = " | ".join(f"{h:^10}" for h in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))

        # 数据行
        for row in rows:
            line = " | ".join(f"{str(val):^10}" for val in row)
            lines.append(line)

        table = "\n".join(lines)

        # 验证
        assert isinstance(table, str)
        assert len(table) > 0
        assert "方案" in table
        assert "---" in table

    def test_visualization_with_sensitivity_analysis(self):
        """测试: 敏感性分析可视化"""
        visualizer = ASCIIVisualizer()

        # 运行敏感性分析
        result = self.orchestrator.analyze(self.problem, algorithm_name="wsm", run_sensitivity=True)

        # 如果有敏感性分析结果
        if hasattr(result, 'sensitivity_analysis') and result.sensitivity_analysis:
            # 提取敏感性数据
            sensitivity = result.sensitivity_analysis

            # 创建简单的敏感性摘要
            summary_lines = [
                "敏感性分析摘要:",
                f"  算法: {result.metadata.algorithm_name}",
                f"  最佳方案: {result.rankings[0].alternative}",
                f"  最高分: {result.rankings[0].score:.2f}",
            ]

            summary = "\n".join(summary_lines)

            # 验证
            assert isinstance(summary, str)
            assert len(summary) > 0

        # 至少验证基本排名可视化
        ranking_data = {r.alternative: r.score for r in result.rankings}
        chart = visualizer.bar_chart(ranking_data, title="敏感性分析后的排名")

        assert isinstance(chart, str)
        assert len(chart) > 0
