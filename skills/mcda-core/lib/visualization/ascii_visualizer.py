"""
ASCII 可视化工具

提供基于文本的图表生成功能。
"""

from typing import Literal


class VisualizationError(Exception):
    """可视化错误"""
    pass


class ASCIIVisualizer:
    """ASCII 可视化器

    生成基于文本的图表（柱状图、雷达图等）。

    Example:
        ```python
        visualizer = ASCIIVisualizer()

        # 柱状图
        data = {"A": 10, "B": 20, "C": 15}
        chart = visualizer.bar_chart(data, title="销售数据")
        print(chart)

        # 雷达图
        scores = [0.8, 0.6, 0.9]
        labels = ["质量", "成本", "交付"]
        chart = visualizer.radar_chart(scores, labels)
        print(chart)
        ```
    """

    def __init__(self):
        """初始化可视化器"""
        self.bar_char = "█"
        self.axis_char = "│"

    # ========================================================================
    # 柱状图
    # ========================================================================

    def bar_chart(
        self,
        data: dict[str, float | int],
        title: str = "",
        width: int = 60,
        height: int = 10
    ) -> str:
        """生成 ASCII 柱状图

        Args:
            data: 数据字典 {label: value}
            title: 图表标题
            width: 图表宽度（字符数）
            height: 图表高度（字符数）

        Returns:
            ASCII 柱状图字符串
        """
        # 验证输入
        if not data:
            raise VisualizationError("数据不能为空")

        if not isinstance(data, dict):
            raise VisualizationError(
                f"数据必须是字典类型，当前类型: {type(data)}"
            )

        if width <= 0 or height <= 0:
            raise VisualizationError("宽度和高度必须为正数")

        # 检查负值
        if any(v < 0 for v in data.values()):
            raise VisualizationError("柱状图不支持负值")

        # 归一化数据
        max_value = max(data.values())
        min_value = min(data.values())

        if max_value == 0:
            # 所有值都为0
            normalized = {k: 0 for k in data}
        else:
            normalized = {
                k: v / max_value
                for k, v in data.items()
            }

        # 生成图表
        lines = []

        # 标题
        if title:
            lines.append(title)
            lines.append("=" * len(title))

        # 柱状图
        bar_width = width - 20  # 留出标签空间

        for label, value in data.items():
            norm_value = normalized[label]
            bar_length = int(norm_value * bar_width)

            # 构建柱状
            bar = self.bar_char * bar_length
            line = f"{label:15s} {self.axis_char} {bar} {value:.2f}"
            lines.append(line)

        # 底部
        lines.append("-" * width)

        return "\n".join(lines)

    # ========================================================================
    # 雷达图
    # ========================================================================

    def radar_chart(
        self,
        scores: list[float],
        labels: list[str],
        title: str = ""
    ) -> str:
        """生成 ASCII 雷达图（简化版）

        Args:
            scores: 分数列表（建议归一化到 [0, 1]）
            labels: 标签列表
            title: 图表标题

        Returns:
            ASCII 雷达图字符串
        """
        # 验证输入
        if len(scores) != len(labels):
            raise VisualizationError(
                f"分数数量 ({len(scores)}) 必须等于标签数量 ({len(labels)})"
            )

        if len(scores) < 3:
            raise VisualizationError("雷达图至少需要 3 个维度")

        # 归一化到 [0, 1]
        max_score = max(scores)
        if max_score > 0:
            normalized = [s / max_score for s in scores]
        else:
            normalized = scores

        # 生成图表
        lines = []

        # 标题
        if title:
            lines.append(title)
            lines.append("=" * len(title))

        # 维度信息（简化版）
        lines.append("雷达图（简化版）:")
        lines.append("")

        for label, score, norm_score in zip(labels, scores, normalized):
            bar_length = int(norm_score * 30)
            bar = self.bar_char * bar_length
            lines.append(f"{label:15s} {self.axis_char} {bar} {score:.2f}")

        lines.append("")
        lines.append(f"最大值: {max_score:.2f}")

        return "\n".join(lines)

    # ========================================================================
    # 排名对比图
    # ========================================================================

    def ranking_comparison(
        self,
        rankings: dict[str, dict[str, int]],
        title: str = "算法排名对比"
    ) -> str:
        """生成排名对比图

        Args:
            rankings: 排名字典 {algorithm: {alternative: rank}}
            title: 图表标题

        Returns:
            ASCII 排名对比图
        """
        if not rankings:
            raise VisualizationError("排名数据不能为空")

        # 获取所有方案
        all_alternatives = set()
        for algo_ranking in rankings.values():
            all_alternatives.update(algo_ranking.keys())

        if not all_alternatives:
            raise VisualizationError("排名中没有方案")

        # 排序方案
        sorted_alternatives = sorted(all_alternatives)

        # 生成图表
        lines = []

        # 标题
        if title:
            lines.append(title)
            lines.append("=" * len(title))
        lines.append("")

        # 表头
        algo_names = list(rankings.keys())
        header = f"{'方案':15s}"
        for algo in algo_names:
            header += f" {algo.upper():>10s}"
        lines.append(header)
        lines.append("-" * (15 + 10 * len(algo_names)))

        # 每个方案的排名
        for alt in sorted_alternatives:
            line = f"{str(alt):15s}"
            for algo in algo_names:
                rank = rankings[algo].get(alt, "-")
                line += f" {str(rank):>10s}"
            lines.append(line)

        return "\n".join(lines)

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def _create_horizontal_bar(
        self,
        value: float,
        max_value: float,
        width: int = 40
    ) -> str:
        """创建水平柱状

        Args:
            value: 当前值
            max_value: 最大值
            width: 柱状宽度

        Returns:
            柱状字符串
        """
        if max_value == 0:
            ratio = 0
        else:
            ratio = value / max_value

        ratio = max(0, min(1, ratio))  # 限制在 [0, 1]
        bar_length = int(ratio * width)

        return self.bar_char * bar_length

    def _format_value(self, value: float, precision: int = 2) -> str:
        """格式化数值

        Args:
            value: 数值
            precision: 小数位数

        Returns:
            格式化后的字符串
        """
        return f"{value:.{precision}f}"
