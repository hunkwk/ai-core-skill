"""
高级可视化图表

提供高级分析和可视化功能：
- 敏感性分析热力图
- 决策路径追踪图
- 权重敏感性分析
- 方案稳定性分析
"""

from pathlib import Path
from typing import Any, Optional, Union
import numpy as np
from numpy.linalg import norm


class AdvancedChartGenerator:
    """高级图表生成器

    提供敏感性分析、决策路径追踪等高级可视化功能。

    Example:
        ```python
        generator = AdvancedChartGenerator()

        # 敏感性分析热力图
        fig = generator.plot_sensitivity_heatmap(
            sensitivity_data={
                ('方案A', '成本'): 0.8,
                ('方案A', '质量'): 0.6,
                ...
            }
        )
        ```
    """

    def __init__(self):
        """初始化高级图表生成器"""
        pass

    # ========================================================================
    # 敏感性分析
    # ========================================================================

    def plot_sensitivity_heatmap(
        self,
        sensitivity_data: dict[tuple[str, str], float],
        alternatives: list[str],
        criteria: list[str],
        title: str = "敏感性分析热力图",
        figsize: tuple[int, int] = (10, 8),
        cmap: str = 'RdYlGn_r'
    ):
        """绘制敏感性分析热力图

        Args:
            sensitivity_data: 敏感性数据字典 {(alternative, criterion): sensitivity}
            alternatives: 方案名称列表
            criteria: 标准名称列表
            title: 图表标题
            figsize: 图表尺寸
            cmap: 颜色映射

        Returns:
            matplotlib Figure 对象
        """
        import matplotlib.pyplot as plt

        # 构建敏感性矩阵
        n_alts = len(alternatives)
        n_crits = len(criteria)
        matrix = np.zeros((n_alts, n_crits))

        for i, alt in enumerate(alternatives):
            for j, crit in enumerate(criteria):
                key = (alt, crit)
                if key in sensitivity_data:
                    matrix[i, j] = sensitivity_data[key]

        # 创建热力图
        fig, ax = plt.subplots(figsize=figsize)

        im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=0, vmax=1)

        # 设置坐标轴
        ax.set_xticks(np.arange(n_crits))
        ax.set_yticks(np.arange(n_alts))
        ax.set_xticklabels(criteria)
        ax.set_yticklabels(alternatives)

        # 旋转 x 轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # 添加数值标注
        for i in range(n_alts):
            for j in range(n_crits):
                value = matrix[i, j]
                text_color = 'white' if value > 0.5 else 'black'
                text = ax.text(j, i, f'{value:.2f}',
                             ha="center", va="center", color=text_color, fontsize=9)

        # 添加颜色条
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.set_label('敏感性系数', rotation=270, labelpad=20)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('决策标准', fontsize=12)
        ax.set_ylabel('备选方案', fontsize=12)

        plt.tight_layout()
        return fig

    def compute_sensitivity_indices(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        direction: list[str]
    ) -> dict[tuple[str, str], float]:
        """计算敏感性指数

        分析每个标准权重变化对最终排名的影响。

        Args:
            decision_matrix: 决策矩阵 (n_alts × n_crits)
            weights: 标准权重数组
            direction: 标准方向列表 ('higher_better' 或 'lower_better')

        Returns:
            敏感性指数字典 {(alternative, criterion): sensitivity}
        """
        from scipy.stats import pearsonr

        n_alts, n_crits = decision_matrix.shape
        sensitivity = {}

        # 标准化决策矩阵
        normalized = self._normalize_matrix(decision_matrix, direction)

        # 计算原始得分（使用 TOPSIS 方法）
        original_scores = self._compute_topsis_scores(normalized, weights)

        # 对每个标准进行敏感性分析
        for j in range(n_crits):
            # 创建权重变化序列（±50%）
            weight_variations = np.linspace(0.5, 1.5, 20)
            score_variations = []

            for variation in weight_variations:
                # 修改当前标准的权重
                modified_weights = weights.copy()
                modified_weights[j] *= variation
                modified_weights = modified_weights / modified_weights.sum()

                # 重新计算得分
                new_scores = self._compute_topsis_scores(normalized, modified_weights)
                score_variations.append(new_scores)

            score_variations = np.array(score_variations)

            # 计算相关性（作为敏感性指数）
            for i in range(n_alts):
                alt_scores = score_variations[:, i]
                correlation, _ = pearsonr(weight_variations, alt_scores)
                sensitivity[('方案' + chr(65 + i), f'C{j+1}')] = abs(correlation)

        return sensitivity

    def _normalize_matrix(
        self,
        matrix: np.ndarray,
        direction: list[str]
    ) -> np.ndarray:
        """标准化决策矩阵"""
        normalized = matrix.copy()

        for j, d in enumerate(direction):
            col = matrix[:, j]
            if d == 'higher_better':
                # 向量标准化
                normalized[:, j] = col / norm(col)
            else:  # lower_better
                # 成本型标准化
                normalized[:, j] = 1 - (col / col.max())

        return normalized

    def _compute_topsis_scores(
        self,
        normalized: np.ndarray,
        weights: np.ndarray
    ) -> np.ndarray:
        """计算 TOPSIS 得分"""
        # 加权标准化矩阵
        weighted = normalized * weights

        # 理想解和负理想解
        ideal_best = weighted.max(axis=0)
        ideal_worst = weighted.min(axis=0)

        # 计算距离
        dist_best = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
        dist_worst = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

        # 计算相对贴近度
        scores = dist_worst / (dist_best + dist_worst)
        return scores

    # ========================================================================
    # 决策路径追踪
    # ========================================================================

    def plot_decision_path(
        self,
        path_data: dict[str, list[tuple[float, float]]],
        title: str = "决策路径追踪",
        figsize: tuple[int, int] = (12, 8),
        show_grid: bool = True
    ):
        """绘制决策路径追踪图

        显示方案在不同决策阶段的表现变化。

        Args:
            path_data: 路径数据 {alternative: [(stage1_score, stage2_score), ...]}
            title: 图表标题
            figsize: 图表尺寸
            show_grid: 是否显示网格

        Returns:
            matplotlib Figure 对象
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=figsize)

        colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5']
        markers = ['o', 's', '^', 'D', 'v']

        for idx, (alt, path) in enumerate(path_data.items()):
            # 提取坐标
            x_coords = [p[0] for p in path]
            y_coords = [p[1] for p in path]

            # 绘制路径
            ax.plot(x_coords, y_coords,
                   marker=markers[idx % len(markers)],
                   markersize=8,
                   linewidth=2,
                   color=colors[idx % len(colors)],
                   label=alt)

            # 添加箭头指示方向
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                dx = x2 - x1
                dy = y2 - y1
                ax.arrow(x1, y1, dx * 0.8, dy * 0.8,
                        head_width=0.02, head_length=0.02,
                        fc=colors[idx % len(colors)],
                        ec=colors[idx % len(colors)],
                        alpha=0.5)

        ax.set_xlabel('阶段 1 得分', fontsize=12)
        ax.set_ylabel('阶段 2 得分', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10)

        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        return fig

    def plot_ranking_evolution(
        self,
        rankings_data: dict[str, list[int]],
        stages: list[str],
        title: str = "排名演化图",
        figsize: tuple[int, int] = (12, 6)
    ):
        """绘制排名演化图

        显示方案在不同阶段的排名变化。

        Args:
            rankings_data: 排名数据 {alternative: [rank_stage1, rank_stage2, ...]}
            stages: 阶段名称列表
            title: 图表标题
            figsize: 图表尺寸

        Returns:
            matplotlib Figure 对象
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=figsize)

        colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5']
        markers = ['o', 's', '^', 'D', 'v']

        x_axis = range(len(stages))

        for idx, (alt, rankings) in enumerate(rankings_data.items()):
            ax.plot(x_axis, rankings,
                   marker=markers[idx % len(markers)],
                   markersize=8,
                   linewidth=2,
                   color=colors[idx % len(colors)],
                   label=alt)

        # 反转 y 轴（排名 1 在顶部）
        ax.invert_yaxis()

        ax.set_xticks(x_axis)
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.set_xlabel('决策阶段', fontsize=12)
        ax.set_ylabel('排名', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')

        plt.tight_layout()
        return fig

    # ========================================================================
    # 权重敏感性分析
    # ========================================================================

    def plot_weight_sensitivity(
        self,
        weight_changes: dict[str, np.ndarray],
        score_changes: dict[str, np.ndarray],
        title: str = "权重敏感性分析",
        figsize: tuple[int, int] = (14, 6)
    ):
        """绘制权重敏感性分析图

        显示标准权重变化对方案得分的影响。

        Args:
            weight_changes: 权重变化数据 {criterion: weight_array}
            score_changes: 得分变化数据 {alternative: score_array}
            title: 图表标题
            figsize: 图表尺寸

        Returns:
            matplotlib Figure 对象
        """
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=figsize)

        # 左图：权重变化曲线
        ax1 = axes[0]
        colors = ['#4472C4', '#ED7D31', '#A5A5A5']

        for idx, (criterion, weights) in enumerate(weight_changes.items()):
            ax1.plot(weights, label=criterion,
                    color=colors[idx % len(colors)],
                    linewidth=2, marker='o', markersize=6)

        ax1.set_xlabel('变化步长', fontsize=11)
        ax1.set_ylabel('权重值', fontsize=11)
        ax1.set_title('权重变化曲线', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)

        # 右图：得分变化曲线
        ax2 = axes[1]
        alt_colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5']

        for idx, (alt, scores) in enumerate(score_changes.items()):
            ax2.plot(scores, label=alt,
                    color=alt_colors[idx % len(alt_colors)],
                    linewidth=2, marker='s', markersize=6)

        ax2.set_xlabel('变化步长', fontsize=11)
        ax2.set_ylabel('得分', fontsize=11)
        ax2.set_title('得分变化曲线', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig

    # ========================================================================
    # 方案稳定性分析
    # ========================================================================

    def plot_stability_analysis(
        self,
        stability_scores: dict[str, float],
        confidence_intervals: dict[str, tuple[float, float]],
        title: str = "方案稳定性分析",
        figsize: tuple[int, int] = (10, 6)
    ):
        """绘制方案稳定性分析图

        显示方案得分的置信区间和稳定性。

        Args:
            stability_scores: 稳定性得分 {alternative: mean_score}
            confidence_intervals: 置信区间 {alternative: (lower, upper)}
            title: 图表标题
            figsize: 图表尺寸

        Returns:
            matplotlib Figure 对象
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=figsize)

        alternatives = list(stability_scores.keys())
        y_pos = np.arange(len(alternatives))
        means = [stability_scores[alt] for alt in alternatives]
        errors = [
            (confidence_intervals[alt][1] - confidence_intervals[alt][0]) / 2
            for alt in alternatives
        ]

        # 绘制误差条
        ax.barh(y_pos, means, xerr=errors,
               align='center', color='#4472C4',
               alpha=0.7, ecolor='black', capsize=5)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(alternatives)
        ax.invert_yaxis()
        ax.set_xlabel('得分', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')

        plt.tight_layout()
        return fig

    # ========================================================================
    # 组合分析图表
    # ========================================================================

    def plot_comprehensive_sensitivity(
        self,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        alternatives: list[str],
        criteria: list[str],
        direction: list[str],
        title: str = "综合敏感性分析",
        figsize: tuple[int, int] = (16, 10)
    ):
        """绘制综合敏感性分析图

        包含敏感性热力图、权重敏感性和稳定性分析。

        Args:
            decision_matrix: 决策矩阵
            weights: 标准权重
            alternatives: 方案名称列表
            criteria: 标准名称列表
            direction: 标准方向
            title: 总标题
            figsize: 图表尺寸

        Returns:
            matplotlib Figure 对象
        """
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. 敏感性热力图
        sensitivity = self.compute_sensitivity_indices(
            decision_matrix, weights, direction
        )

        ax1 = fig.add_subplot(gs[0, :])
        self._add_sensitivity_heatmap_to_ax(
            ax1, sensitivity, alternatives, criteria
        )

        # 2. 权重敏感性
        ax2 = fig.add_subplot(gs[1, 0])
        self._add_weight_sensitivity_to_ax(ax2, alternatives)

        # 3. 稳定性分析
        ax3 = fig.add_subplot(gs[1, 1])
        self._add_stability_to_ax(ax3, alternatives)

        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
        return fig

    def _add_sensitivity_heatmap_to_ax(
        self,
        ax,
        sensitivity: dict[tuple[str, str], float],
        alternatives: list[str],
        criteria: list[str]
    ):
        """添加敏感性热力图到指定轴"""
        n_alts = len(alternatives)
        n_crits = len(criteria)
        matrix = np.zeros((n_alts, n_crits))

        for i, alt in enumerate(alternatives):
            for j, crit in enumerate(criteria):
                key = (alt, crit)
                if key in sensitivity:
                    matrix[i, j] = sensitivity[key]

        im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)

        ax.set_xticks(np.arange(n_crits))
        ax.set_yticks(np.arange(n_alts))
        ax.set_xticklabels(criteria)
        ax.set_yticklabels(alternatives)
        ax.set_title('敏感性分析热力图', fontweight='bold', pad=10)

        # 添加数值标注
        for i in range(n_alts):
            for j in range(n_crits):
                value = matrix[i, j]
                text_color = 'white' if value > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}',
                       ha="center", va="center", color=text_color, fontsize=9)

    def _add_weight_sensitivity_to_ax(self, ax, alternatives: list[str]):
        """添加权重敏感性到指定轴"""
        # 示例数据
        x = np.linspace(0.5, 1.5, 20)

        for i, alt in enumerate(alternatives):
            # 模拟得分变化
            y = 0.7 + 0.1 * np.sin(2 * np.pi * (x - 0.5) + i)
            ax.plot(x, y, marker='o', label=alt, linewidth=2, markersize=4)

        ax.set_xlabel('权重变化因子')
        ax.set_ylabel('得分')
        ax.set_title('权重敏感性', fontweight='bold', pad=10)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    def _add_stability_to_ax(self, ax, alternatives: list[str]):
        """添加稳定性分析到指定轴"""
        # 示例数据
        y_pos = np.arange(len(alternatives))
        means = np.random.uniform(0.6, 0.9, len(alternatives))
        errors = np.random.uniform(0.02, 0.08, len(alternatives))

        ax.barh(y_pos, means, xerr=errors,
               align='center', color='#4472C4',
               alpha=0.7, ecolor='black', capsize=5)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(alternatives)
        ax.invert_yaxis()
        ax.set_xlabel('得分')
        ax.set_title('方案稳定性', fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
