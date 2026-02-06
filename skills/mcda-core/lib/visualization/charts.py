"""
图表生成器

提供决策结果的可视化功能：
- 排名柱状图
- 敏感性分析折线图
- 权重分布图
- 区间数雷达图

新增图表类型（v0.13）：
- 雷达图（Radar Chart）
- 热力图（Heatmap）
- 散点图（Scatter Plot）
- 通用折线图（Line Chart）
"""

from pathlib import Path
from typing import Any, Optional, Union
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.projections.polar import PolarAxes


# 配置中文字体
try:
    mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
    mpl.rcParams['axes.unicode_minus'] = False
except Exception:
    # 如果中文字体不可用，使用默认字体
    pass


class ChartGenerator:
    """图表生成器

    提供多种图表类型的生成功能，用于可视化 MCDA 决策结果。
    """

    def __init__(self):
        """初始化图表生成器"""
        self.figures = []

    def plot_rankings(
        self,
        rankings: list[str],
        scores: dict[str, float],
        title: str = "决策结果排名",
        figsize: tuple[int, int] = (10, 6)
    ) -> plt.Figure:
        """绘制排名柱状图

        Args:
            rankings: 排名列表（方案名称）
            scores: 得分字典 {方案名称: 得分}
            title: 图表标题
            figsize: 图表大小

        Returns:
            matplotlib Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 提取对应排名的得分
        values = [scores.get(rank, 0) for rank in rankings]

        # 绘制柱状图
        bars = ax.bar(rankings, values, color='steelblue', edgecolor='black', alpha=0.7)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{height:.4f}',
                ha='center',
                va='bottom',
                fontsize=10
            )

        ax.set_xlabel('备选方案', fontsize=12)
        ax.set_ylabel('得分', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        self.figures.append(fig)
        return fig

    def plot_sensitivity(
        self,
        parameter_values: list[float],
        rankings_changes: list[list[str]],
        param_name: str = "参数值",
        title: str = "敏感性分析",
        figsize: tuple[int, int] = (10, 6)
    ) -> plt.Figure:
        """绘制敏感性分析折线图

        Args:
            parameter_values: 参数值列表
            rankings_changes: 排名变化列表 [[方案1, 方案2, ...], ...]
            param_name: 参数名称
            title: 图表标题
            figsize: 图表大小

        Returns:
            matplotlib Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 获取所有唯一的方案名称
        all_alternatives = []
        for rankings in rankings_changes:
            for alt in rankings:
                if alt not in all_alternatives:
                    all_alternatives.append(alt)

        # 为每个方案绘制一条线
        for alt in all_alternatives:
            rankings_for_alt = []
            for rankings in rankings_changes:
                try:
                    rank = rankings.index(alt) + 1
                except ValueError:
                    rank = None
                rankings_for_alt.append(rank)

            # 绘制排名变化（反向，排名越小越靠上）
            ax.plot(
                parameter_values,
                rankings_for_alt,
                marker='o',
                label=alt,
                linewidth=2,
                markersize=6
            )

        ax.set_xlabel(param_name, fontsize=12)
        ax.set_ylabel('排名', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(alpha=0.3, linestyle='--')

        # 反转 y 轴（排名 1 在顶部）
        ax.invert_yaxis()

        plt.tight_layout()

        self.figures.append(fig)
        return fig

    def plot_weights(
        self,
        criteria: list[str],
        weights: list[float],
        title: str = "准则权重分布",
        figsize: tuple[int, int] = (8, 8)
    ) -> plt.Figure:
        """绘制权重饼图

        Args:
            criteria: 准则名称列表
            weights: 权重列表
            title: 图表标题
            figsize: 图表大小

        Returns:
            matplotlib Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 绘制饼图
        colors = plt.cm.Set3(range(len(criteria)))
        wedges, texts, autotexts = ax.pie(
            weights,
            labels=criteria,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            shadow=True
        )

        # 美化文本
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        for text in texts:
            text.set_fontsize(11)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        self.figures.append(fig)
        return fig

    def plot_interval_comparison(
        self,
        alternatives: list[str],
        intervals: list[tuple[float, float]],
        title: str = "区间数对比",
        figsize: tuple[int, int] = (10, 6)
    ) -> plt.Figure:
        """绘制区间数对比图（误差条）

        Args:
            alternatives: 备选方案列表
            intervals: 区间数列表 [(下界, 上界), ...]
            title: 图表标题
            figsize: 图表大小

        Returns:
            matplotlib Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        # 计算区间中点
        midpoints = [(low + high) / 2 for low, high in intervals]
        lower_bounds = [low for low, high in intervals]
        upper_bounds = [high for low, high in intervals]

        # 计算误差
        yerr_lower = [mid - lower for mid, lower in zip(midpoints, lower_bounds)]
        yerr_upper = [upper - mid for mid, upper in zip(midpoints, upper_bounds)]

        # 绘制误差条
        ax.errorbar(
            alternatives,
            midpoints,
            yerr=[yerr_lower, yerr_upper],
            fmt='o',
            color='steelblue',
            ecolor='red',
            elinewidth=2,
            capsize=5,
            markersize=8,
            capthick=2
        )

        ax.set_xlabel('备选方案', fontsize=12)
        ax.set_ylabel('得分', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        self.figures.append(fig)
        return fig

    def export_chart(
        self,
        fig: plt.Figure,
        filepath: Union[str, Path],
        dpi: int = 300,
        format: Optional[str] = None
    ) -> None:
        """导出图表为文件

        Args:
            fig: matplotlib Figure 对象
            filepath: 输出文件路径
            dpi: 分辨率（DPI）
            format: 文件格式（默认从扩展名推断）
        """
        filepath = Path(filepath)

        if format is None:
            format = filepath.suffix.lstrip('.')

        fig.savefig(
            filepath,
            dpi=dpi,
            format=format,
            bbox_inches='tight',
            facecolor='white'
        )

    # ========================================================================
    # 新增图表类型（v0.13）
    # ========================================================================

    def plot_radar(
        self,
        categories: list[str],
        values: Union[list[float], dict[str, list[float]]],
        title: str = "雷达图",
        figsize: tuple[int, int] = (8, 8),
        normalize: bool = False
    ) -> plt.Figure:
        """绘制雷达图（spider chart）

        Args:
            categories: 类别标签列表
            values: 值列表或多系列字典 {系列名: [值列表]}
            title: 图表标题
            figsize: 图表大小
            normalize: 是否归一化到 [0, 1]

        Returns:
            matplotlib Figure 对象

        Raises:
            ValueError: 类别数量与值数量不匹配
        """
        # 判断是单系列还是多系列
        if isinstance(values, dict):
            # 多系列
            series_names = list(values.keys())
            series_values = list(values.values())

            # 验证每个系列的长度
            for series_value in series_values:
                if len(series_value) != len(categories):
                    raise ValueError(
                        f"值数量 ({len(series_value)}) 必须等于类别数量 ({len(categories)})"
                    )

            # 归一化（如果需要）
            if normalize:
                all_values = [v for series in series_values for v in series]
                max_val = max(all_values) if all_values else 1
                if max_val > 0:
                    series_values = [[v / max_val for v in series] for series in series_values]

        else:
            # 单系列
            if len(values) != len(categories):
                raise ValueError(
                    f"值数量 ({len(values)}) 必须等于类别数量 ({len(categories)})"
                )

            # 归一化（如果需要）
            if normalize:
                max_val = max(values) if values else 1
                if max_val > 0:
                    values = [v / max_val for v in values]

            series_names = ['数据']
            series_values = [values]

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形

        # 创建极坐标图
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, polar=True)

        # 绘制每个系列
        colors = plt.cm.Set1(range(len(series_values)))
        for i, (series_name, series_value) in enumerate(zip(series_names, series_values)):
            values_closed = series_value + series_value[:1]  # 闭合图形
            ax.plot(angles, values_closed, 'o-', linewidth=2, label=series_name, color=colors[i])
            ax.fill(angles, values_closed, alpha=0.15, color=colors[i])

        # 设置类别标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

        # 设置 y 轴范围
        ax.set_ylim(0, 1 if normalize else max(max(v) for v in series_values))

        # 添加标题和图例
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()

        self.figures.append(fig)
        return fig

    def plot_heatmap(
        self,
        data: np.ndarray,
        row_labels: list[str],
        col_labels: list[str],
        title: str = "热力图",
        figsize: tuple[int, int] = (10, 8),
        cmap: str = 'YlOrRd',
        show_values: bool = False
    ) -> plt.Figure:
        """绘制热力图

        Args:
            data: 2D 数组 (行数 × 列数)
            row_labels: 行标签列表
            col_labels: 列标签列表
            title: 图表标题
            figsize: 图表大小
            cmap: 颜色映射
            show_values: 是否显示数值

        Returns:
            matplotlib Figure 对象

        Raises:
            ValueError: 数据形状与标签数量不匹配
        """
        data = np.array(data)

        # 验证数据形状
        if data.shape != (len(row_labels), len(col_labels)):
            raise ValueError(
                f"数据形状 {data.shape} 与标签数量不匹配 "
                f"({len(row_labels)} 行 × {len(col_labels)} 列)"
            )

        fig, ax = plt.subplots(figsize=figsize)

        # 绘制热力图
        im = ax.imshow(data, cmap=cmap, aspect='auto', interpolation='nearest')

        # 设置刻度标签
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_xticklabels(col_labels)
        ax.set_yticklabels(row_labels)

        # 旋转 x 轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # 添加数值标注
        if show_values:
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    text = ax.text(
                        j, i, f'{data[i, j]:.2f}',
                        ha="center", va="center", color="black", fontsize=9
                    )

        # 添加颜色条
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel(title, rotation=-90, va="bottom")

        # 设置标题
        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()

        self.figures.append(fig)
        return fig

    def plot_scatter(
        self,
        x: Optional[list[float]] = None,
        y: Optional[list[float]] = None,
        labels: Optional[list[str]] = None,
        groups: Optional[list[dict]] = None,
        sizes: Optional[list[float]] = None,
        title: str = "散点图",
        figsize: tuple[int, int] = (10, 6),
        alpha: float = 0.6
    ) -> plt.Figure:
        """绘制散点图

        Args:
            x: x 坐标列表
            y: y 坐标列表
            labels: 点标签列表
            groups: 分组数据 [{'x': [...], 'y': [...], 'label': '组名'}, ...]
            sizes: 点大小列表
            title: 图表标题
            figsize: 图表大小
            alpha: 透明度

        Returns:
            matplotlib Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        if groups is not None:
            # 分组散点图
            colors = plt.cm.Set1(range(len(groups)))

            for i, group in enumerate(groups):
                x_data = group.get('x', [])
                y_data = group.get('y', [])
                label = group.get('label', f'组{i+1}')

                ax.scatter(
                    x_data, y_data,
                    label=label,
                    color=colors[i],
                    alpha=alpha,
                    s=100
                )

            ax.legend()

        else:
            # 单一散点图
            if x is None or y is None:
                raise ValueError("必须提供 x 和 y 坐标")

            if len(x) != len(y):
                raise ValueError(f"x 和 y 长度不匹配: {len(x)} vs {len(y)}")

            # 默认点大小
            if sizes is None:
                sizes = [100] * len(x)

            if len(sizes) != len(x):
                raise ValueError(f"sizes 和 x 长度不匹配: {len(sizes)} vs {len(x)}")

            # 绘制散点
            scatter = ax.scatter(x, y, s=sizes, alpha=alpha)

            # 添加标签
            if labels is not None:
                if len(labels) != len(x):
                    raise ValueError(f"labels 和 x 长度不匹配: {len(labels)} vs {len(x)}")

                for i, label in enumerate(labels):
                    ax.annotate(
                        label,
                        (x[i], y[i]),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=9
                    )

        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3, linestyle='--')

        plt.tight_layout()

        self.figures.append(fig)
        return fig

    def plot_line(
        self,
        x: list[float],
        y: Union[list[float], dict[str, list[float]]],
        title: str = "折线图",
        figsize: tuple[int, int] = (10, 6),
        marker: str = 'o',
        linestyle: str = '-',
        linewidth: int = 2
    ) -> plt.Figure:
        """绘制折线图

        Args:
            x: x 坐标列表
            y: y 坐标列表或多系列字典 {系列名: [y值列表]}
            title: 图表标题
            figsize: 图表大小
            marker: 标记样式
            linestyle: 线条样式
            linewidth: 线条宽度

        Returns:
            matplotlib Figure 对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        if isinstance(y, dict):
            # 多系列折线图
            colors = plt.cm.Set1(range(len(y)))

            for i, (series_name, y_data) in enumerate(y.items()):
                if len(y_data) != len(x):
                    raise ValueError(
                        f"系列 '{series_name}' 的 y 值数量 ({len(y_data)}) "
                        f"与 x 值数量 ({len(x)}) 不匹配"
                    )

                ax.plot(
                    x, y_data,
                    marker=marker,
                    linestyle=linestyle,
                    linewidth=linewidth,
                    label=series_name,
                    color=colors[i]
                )

            ax.legend()

        else:
            # 单系列折线图
            if len(y) != len(x):
                raise ValueError(
                    f"y 值数量 ({len(y)}) 与 x 值数量 ({len(x)}) 不匹配"
                )

            ax.plot(x, y, marker=marker, linestyle=linestyle, linewidth=linewidth)

        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3, linestyle='--')

        plt.tight_layout()

        self.figures.append(fig)
        return fig

    # ========================================================================
    # 原有方法
    # ========================================================================

    def clear_figures(self) -> None:
        """清除所有缓存的图表"""
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()

    def __del__(self):
        """析构函数，确保所有图表都被关闭

        注意: Python 不保证 __del__ 的调用时机，建议使用上下文管理器模式。
        """
        self.clear_figures()

    def __enter__(self):
        """进入上下文管理器

        Returns:
            ChartGenerator 实例
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器，清理所有图表

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常跟踪

        Returns:
            False (不抑制异常)
        """
        self.clear_figures()
        return False
