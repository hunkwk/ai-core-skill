"""
图表生成器

提供决策结果的可视化功能：
- 排名柱状图
- 敏感性分析折线图
- 权重分布图
- 区间数雷达图
"""

from pathlib import Path
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import matplotlib as mpl


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

    def clear_figures(self) -> None:
        """清除所有缓存的图表"""
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()

    def __del__(self):
        """析构函数，确保所有图表都被关闭"""
        self.clear_figures()
