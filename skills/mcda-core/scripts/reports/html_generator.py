"""
HTML 报告生成器

提供带样式的 HTML 报告生成功能：
- 完整的 HTML 结构
- CSS 样式
- 响应式设计
- 图表嵌入
"""

import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from ..models import DecisionProblem, DecisionResult


class HTMLReportGenerator:
    """HTML 报告生成器"""

    def generate_html(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> str:
        """
        生成 HTML 报告

        Args:
            problem: 决策问题
            result: 决策结果
            title: 报告标题
            include_chart: 是否包含图表

        Returns:
            str: HTML 报告
        """
        # 生成各个部分
        html_parts = []

        # HTML 头部
        html_parts.append(self._generate_html_head(title))

        # HTML 主体
        body_content = self._generate_body_content(
            problem, result, title, include_chart
        )
        html_parts.append(body_content)

        # HTML 尾部
        html_parts.append("</body>\n</html>")

        return "\n".join(html_parts)

    def _generate_html_head(self, title: str) -> str:
        """生成 HTML 头部"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* CSS 样式将在 GREEN Phase 实现 */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
        }}
        @media print {{
            body {{
                max-width: 100%;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
"""

    def _generate_body_content(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        title: str,
        include_chart: bool,
    ) -> str:
        """生成 HTML 主体内容"""
        content_parts = []

        # 标题
        content_parts.append(f'<body>\n    <h1>{title}</h1>')

        # 生成时间
        content_parts.append(
            f"    <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        )

        # 决策问题
        content_parts.append("    <h2>决策问题</h2>")

        # 备选方案
        content_parts.append(
            f"    <h3>备选方案（{len(problem.alternatives)} 个）</h3>"
        )
        content_parts.append("    <ul>")
        for alt in problem.alternatives:
            content_parts.append(f"        <li>{alt}</li>")
        content_parts.append("    </ul>")

        # 评价准则
        content_parts.append(
            f"    <h3>评价准则（{len(problem.criteria)} 个）</h3>"
        )
        content_parts.append("    <table>")
        content_parts.append("        <tr>")
        content_parts.append("            <th>准则</th>")
        content_parts.append("            <th>权重</th>")
        content_parts.append("            <th>方向</th>")
        content_parts.append("        </tr>")
        for crit in problem.criteria:
            direction_text = (
                "越高越好 ↑"
                if crit.direction == "higher_better"
                else "越低越好 ↓"
            )
            content_parts.append("        <tr>")
            content_parts.append(f"            <td>{crit.name}</td>")
            content_parts.append(f"            <td>{crit.weight:.2%}</td>")
            content_parts.append(f"            <td>{direction_text}</td>")
            content_parts.append("        </tr>")
        content_parts.append("    </table>")

        # 决策结果
        content_parts.append("    <h2>决策结果</h2>")

        # 排名表格
        content_parts.append("    <h3>排名</h3>")
        content_parts.append("    <table>")
        content_parts.append("        <tr>")
        content_parts.append("            <th>排名</th>")
        content_parts.append("            <th>方案</th>")
        content_parts.append("            <th>评分</th>")
        content_parts.append("        </tr>")
        for ranking in result.rankings:
            content_parts.append("        <tr>")
            content_parts.append(f"            <td>{ranking.rank}</td>")
            content_parts.append(f"            <td>{ranking.alternative}</td>")
            content_parts.append(f"            <td>{ranking.score:.4f}</td>")
            content_parts.append("        </tr>")
        content_parts.append("    </table>")

        # 图表
        if include_chart:
            chart_html = self._generate_chart_html(result)
            content_parts.append(chart_html)

        # 评分矩阵
        content_parts.append("    <h3>评分矩阵</h3>")
        content_parts.append("    <table>")
        content_parts.append("        <tr>")
        content_parts.append("            <th>方案</th>")
        for crit in problem.criteria:
            content_parts.append(f"            <th>{crit.name}</th>")
        content_parts.append("        </tr>")
        for alt in problem.alternatives:
            content_parts.append("        <tr>")
            content_parts.append(f"            <td>{alt}</td>")
            for crit in problem.criteria:
                score = problem.scores[alt][crit.name]
                content_parts.append(f"            <td>{score:.1f}</td>")
            content_parts.append("        </tr>")
        content_parts.append("    </table>")

        # 算法信息
        content_parts.append("    <h2>算法信息</h2>")
        content_parts.append("    <ul>")
        content_parts.append(
            f"        <li><strong>算法名称:</strong> {result.metadata.algorithm_name}</li>"
        )
        content_parts.append(
            f"        <li><strong>备选方案数:</strong> {result.metadata.problem_size[0]}</li>"
        )
        content_parts.append(
            f"        <li><strong>准则数:</strong> {result.metadata.problem_size[1]}</li>"
        )
        content_parts.append("    </ul>")

        return "\n".join(content_parts)

    def _generate_chart_html(self, result: "DecisionResult") -> str:
        """生成图表 HTML"""
        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))

            # 提取排名和得分
            rankings = [r.rank for r in result.rankings]
            alternatives = [r.alternative for r in result.rankings]
            scores = [r.score for r in result.rankings]

            # 绘制柱状图
            ax.bar(alternatives, scores, color="steelblue", alpha=0.7)

            # 添加数值标签
            for i, score in enumerate(scores):
                ax.text(
                    i,
                    score,
                    f"{score:.4f}",
                    ha="center",
                    va="bottom",
                )

            ax.set_xlabel("备选方案")
            ax.set_ylabel("得分")
            ax.set_title("决策结果排名")

            # 保存为 base64 编码的图片
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            plt.close(fig)

            # 返回 HTML
            return f"""    <div class="chart-container">
        <img src="data:image/png;base64,{img_base64}" alt="决策结果排名图">
    </div>"""

        except Exception:
            # 如果图表生成失败，返回空字符串
            return ""

    def save_html(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        file_path: str,
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> None:
        """
        保存 HTML 报告到文件

        Args:
            problem: 决策问题
            result: 决策结果
            file_path: 文件路径
            title: 报告标题
            include_chart: 是否包含图表

        Raises:
            IOError: 文件保存失败
        """
        html = self.generate_html(
            problem, result, title=title, include_chart=include_chart
        )

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
