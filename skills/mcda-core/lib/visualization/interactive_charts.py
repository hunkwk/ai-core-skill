"""
交互式图表生成器

提供基于 Plotly 的交互式图表生成功能：
- 交互式排名柱状图
- 交互式雷达图
- 交互式散点图
- 交互式热力图
- HTML 导出功能
"""

from pathlib import Path
from typing import Any, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
from numpy import ndarray


class InteractiveChartGenerator:
    """交互式图表生成器

    使用 Plotly 生成交互式图表，支持 HTML 导出。

    Example:
        ```python
        generator = InteractiveChartGenerator()

        # 创建交互式排名图
        fig = generator.plot_rankings(
            alternatives=['方案A', '方案B'],
            scores=[0.85, 0.72],
            title='决策排名'
        )

        # 导出为 HTML
        generator.save_html(fig, 'rankings.html')
        ```
    """

    def __init__(self, theme: str = 'plotly'):
        """初始化交互式图表生成器

        Args:
            theme: Plotly 主题名称
        """
        self.theme = theme

    # ========================================================================
    # 排名图表
    # ========================================================================

    def plot_rankings(
        self,
        alternatives: list[str],
        scores: list[float],
        title: str = "方案排名",
        color: str = '#4472C4',
        orientation: str = 'v'
    ) -> go.Figure:
        """创建交互式排名柱状图

        Args:
            alternatives: 方案名称列表
            scores: 分数列表
            title: 图表标题
            color: 柱状图颜色
            orientation: 方向 ('v'=垂直, 'h'=水平)

        Returns:
            Plotly Figure 对象
        """
        if orientation == 'h':
            fig = go.Figure(data=[
                go.Bar(
                    x=scores,
                    y=alternatives,
                    orientation='h',
                    marker_color=color,
                    text=[f'{s:.4f}' for s in scores],
                    textposition='outside'
                )
            ])
            fig.update_layout(
                xaxis_title='分数',
                yaxis_title='方案'
            )
        else:
            fig = go.Figure(data=[
                go.Bar(
                    x=alternatives,
                    y=scores,
                    marker_color=color,
                    text=[f'{s:.4f}' for s in scores],
                    textposition='outside'
                )
            ])
            fig.update_layout(
                xaxis_title='方案',
                yaxis_title='分数'
            )

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template=self.theme
        )

        return fig

    # ========================================================================
    # 雷达图
    # ========================================================================

    def plot_radar(
        self,
        categories: list[str],
        values: Union[list[float], dict[str, list[float]]],
        title: str = "雷达图",
        fill: bool = True
    ) -> go.Figure:
        """创建交互式雷达图

        Args:
            categories: 类别名称列表
            values: 单系列值列表或多系列值字典
            title: 图表标题
            fill: 是否填充区域

        Returns:
            Plotly Figure 对象
        """
        fig = go.Figure()

        # 单系列
        if isinstance(values, list):
            # 闭合雷达图
            values_closed = values + [values[0]]
            categories_closed = categories + [categories[0]]

            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=categories_closed,
                fill='toself' if fill else None,
                name='方案',
                line_color='#4472C4'
            ))

        # 多系列
        elif isinstance(values, dict):
            colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5']

            for idx, (name, vals) in enumerate(values.items()):
                vals_closed = vals + [vals[0]]
                categories_closed = categories + [categories[0]]

                fig.add_trace(go.Scatterpolar(
                    r=vals_closed,
                    theta=categories_closed,
                    fill='toself' if fill else None,
                    name=name,
                    line_color=colors[idx % len(colors)]
                ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template=self.theme,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True if isinstance(values, dict) else False
        )

        return fig

    # ========================================================================
    # 散点图
    # ========================================================================

    def plot_scatter(
        self,
        x: list[float],
        y: list[float],
        labels: Optional[list[str]] = None,
        sizes: Optional[list[float]] = None,
        colors: Optional[list[str]] = None,
        title: str = "散点图",
        x_label: str = "X 轴",
        y_label: str = "Y 轴"
    ) -> go.Figure:
        """创建交互式散点图

        Args:
            x: X 坐标列表
            y: Y 坐标列表
            labels: 点标签列表
            sizes: 点大小列表
            colors: 点颜色列表
            title: 图表标题
            x_label: X 轴标签
            y_label: Y 轴标签

        Returns:
            Plotly Figure 对象
        """
        fig = go.Figure()

        # 如果没有指定颜色，使用默认颜色
        if colors is None:
            colors = ['#4472C4'] * len(x)

        # 添加散点
        for i in range(len(x)):
            hover_text = labels[i] if labels else f'Point {i+1}'
            size = sizes[i] if sizes else 10

            fig.add_trace(go.Scatter(
                x=[x[i]],
                y=[y[i]],
                mode='markers',
                name=hover_text,
                marker=dict(
                    size=size,
                    color=colors[i],
                    opacity=0.7
                ),
                hovertemplate=f'<b>{hover_text}</b><br>X: %{{x}}<br>Y: %{{y}}<extra></extra>'
            ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            xaxis_title=x_label,
            yaxis_title=y_label,
            template=self.theme,
            showlegend=False
        )

        return fig

    # ========================================================================
    # 热力图
    # ========================================================================

    def plot_heatmap(
        self,
        data: ndarray,
        row_labels: list[str],
        col_labels: list[str],
        title: str = "热力图",
        colorscale: str = 'YlOrRd',
        show_values: bool = True
    ) -> go.Figure:
        """创建交互式热力图

        Args:
            data: 2D 数组数据
            row_labels: 行标签列表
            col_labels: 列标签列表
            title: 图表标题
            colorscale: 颜色映射名称
            show_values: 是否显示数值

        Returns:
            Plotly Figure 对象
        """
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=col_labels,
            y=row_labels,
            colorscale=colorscale,
            text=data if show_values else None,
            texttemplate='%{text:.2f}' if show_values else None,
            textfont={"size": 10},
            hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Value: %{z:.2f}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            template=self.theme,
            xaxis_side='bottom'
        )

        return fig

    # ========================================================================
    # 折线图
    # ========================================================================

    def plot_line(
        self,
        x: list[float],
        y: Union[list[float], dict[str, list[float]]],
        title: str = "折线图",
        x_label: str = "X 轴",
        y_label: str = "Y 轴",
        marker: bool = True
    ) -> go.Figure:
        """创建交互式折线图

        Args:
            x: X 坐标列表
            y: 单系列 Y 值或多系列 Y 值字典
            title: 图表标题
            x_label: X 轴标签
            y_label: Y 轴标签
            marker: 是否显示标记点

        Returns:
            Plotly Figure 对象
        """
        fig = go.Figure()

        mode = 'lines+markers' if marker else 'lines'

        # 单系列
        if isinstance(y, list):
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode=mode,
                name='系列',
                line_color='#4472C4'
            ))

        # 多系列
        elif isinstance(y, dict):
            colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5']

            for idx, (name, vals) in enumerate(y.items()):
                fig.add_trace(go.Scatter(
                    x=x,
                    y=vals,
                    mode=mode,
                    name=name,
                    line_color=colors[idx % len(colors)]
                ))

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center'),
            xaxis_title=x_label,
            yaxis_title=y_label,
            template=self.theme,
            hovermode='x unified'
        )

        return fig

    # ========================================================================
    # HTML 导出
    # ========================================================================

    def save_html(
        self,
        fig: go.Figure,
        filepath: Union[str, Path],
        include_plotlyjs: bool = True,
        config: Optional[dict[str, Any]] = None
    ) -> None:
        """保存图表为 HTML 文件

        Args:
            fig: Plotly Figure 对象
            filepath: 输出文件路径
            include_plotlyjs: 是否包含 Plotly.js 库
            config: 图表配置选项
        """
        filepath = Path(filepath)

        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # 默认配置
        if config is None:
            config = {
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            }

        # 写入 HTML
        fig.write_html(
            str(filepath),
            include_plotlyjs=include_plotlyjs,
            config=config
        )

    def to_html(
        self,
        fig: go.Figure,
        include_plotlyjs: bool = True,
        full_html: bool = False,
        config: Optional[dict[str, Any]] = None
    ) -> str:
        """将图表转换为 HTML 字符串

        Args:
            fig: Plotly Figure 对象
            include_plotlyjs: 是否包含 Plotly.js 库
            full_html: 是否生成完整 HTML 文档
            config: 图表配置选项

        Returns:
            HTML 字符串
        """
        # 默认配置
        if config is None:
            config = {
                'displayModeBar': True,
                'displaylogo': False
            }

        return fig.to_html(
            include_plotlyjs=include_plotlyjs,
            full_html=full_html,
            config=config
        )

    # ========================================================================
    # 批量生成
    # ========================================================================

    def generate_report(
        self,
        figures: list[go.Figure],
        output_path: Union[str, Path],
        title: str = "MCDA 交互式报告"
    ) -> None:
        """生成包含多个图表的 HTML 报告

        Args:
            figures: Plotly Figure 对象列表
            output_path: 输出文件路径
            title: 报告标题
        """
        # 转换所有图表为 HTML
        charts_html = []
        for fig in figures:
            html = self.to_html(fig, include_plotlyjs=False, full_html=False)
            charts_html.append(html)

        # 生成完整 HTML
        full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        .chart {{
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
    </div>
    <div class="charts">
"""

        for i, chart_html in enumerate(charts_html, 1):
            full_html += f'        <div class="chart">\n            <h3>图表 {i}</h3>\n'
            full_html += f'            {chart_html}\n'
            full_html += '        </div>\n'

        full_html += """
    </div>
</body>
</html>
"""

        # 保存文件
        filepath = Path(output_path)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_html)
