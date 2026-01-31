"""
MCDA Core 报告服务

功能:
- Markdown 报告生成
- JSON 导出
- 排名可视化
"""

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcda_core.models import DecisionProblem, DecisionResult


# ============================================================================
# ReportService
# ============================================================================

class ReportService:
    """报告服务"""

    def generate_markdown(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        *,
        title: str = "MCDA 决策分析报告",
    ) -> str:
        """
        生成 Markdown 报告

        Args:
            problem: 决策问题
            result: 决策结果
            title: 报告标题

        Returns:
            str: Markdown 报告
        """
        lines = []

        # 标题
        lines.append(f"# {title}")
        lines.append("")

        # 生成时间
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 决策问题
        lines.append("## 决策问题")
        lines.append("")
        lines.append(f"### 备选方案（{len(problem.alternatives)} 个）")
        lines.append("")
        for i, alt in enumerate(problem.alternatives, 1):
            lines.append(f"{i}. {alt}")
        lines.append("")

        lines.append(f"### 评价准则（{len(problem.criteria)} 个）")
        lines.append("")
        lines.append("| 准则 | 权重 | 方向 |")
        lines.append("|------|------|------|")
        for crit in problem.criteria:
            direction_symbol = "↑" if crit.direction == "higher_better" else "↓"
            direction_text = "越高越好" if crit.direction == "higher_better" else "越低越好"
            lines.append(f"| {crit.name} | {crit.weight:.2%} | {direction_text} {direction_symbol} |")
        lines.append("")

        # 决策结果
        lines.append("## 决策结果")
        lines.append("")
        lines.append("### 排名")
        lines.append("")
        lines.append(self.generate_ranking_table(result))
        lines.append("")

        # 算法信息
        lines.append("## 算法信息")
        lines.append("")
        lines.append(f"- **算法名称**: {result.metadata.algorithm_name}")
        lines.append(f"- **备选方案数**: {result.metadata.problem_size[0]}")
        lines.append(f"- **准则数**: {result.metadata.problem_size[1]}")
        lines.append("")

        # 元数据
        lines.append("## 元数据")
        lines.append("")
        lines.append(f"- **算法名称**: {result.metadata.algorithm_name}")
        lines.append(f"- **问题规模**: {result.metadata.problem_size[0]} 个备选方案 × {result.metadata.problem_size[1]} 个准则")
        lines.append("")

        return "\n".join(lines)

    def generate_ranking_table(self, result: "DecisionResult") -> str:
        """
        生成排名表格

        Args:
            result: 决策结果

        Returns:
            str: Markdown 表格
        """
        lines = []
        lines.append("| 排名 | 方案 | 评分 |")
        lines.append("|------|------|------|")

        for ranking in result.rankings:
            lines.append(f"| {ranking.rank} | {ranking.alternative} | {ranking.score:.2f} |")

        return "\n".join(lines)

    def generate_score_chart(self, result: "DecisionResult") -> str:
        """
        生成分数图表（文本形式）

        Args:
            result: 决策结果

        Returns:
            str: 文本图表
        """
        lines = []

        max_score = max(ranking.score for ranking in result.rankings)
        min_score = min(ranking.score for ranking in result.rankings)

        for ranking in result.rankings:
            # 计算条形长度（最多 50 个字符）
            bar_length = int((ranking.score - min_score) / (max_score - min_score + 1e-10) * 50)
            bar = "█" * bar_length
            lines.append(f"{ranking.alternative:15} {bar} {ranking.score:.4f}")

        return "\n".join(lines)

    def generate_comparison_table(self, problem: "DecisionProblem") -> str:
        """
        生成方案对比表

        Args:
            problem: 决策问题

        Returns:
            str: Markdown 表格
        """
        lines = []

        # 表头
        header = "| 方案 |"
        separator = "|------|"
        for crit in problem.criteria:
            header += f" {crit.name} |"
            separator += "------|"
        lines.append(header)
        lines.append(separator)

        # 数据行
        for alt in problem.alternatives:
            row = f"| {alt} |"
            for crit in problem.criteria:
                score = problem.scores[alt][crit.name]
                row += f" {score:.1f} |"
            lines.append(row)

        return "\n".join(lines)

    def export_json(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
    ) -> str:
        """
        导出为 JSON

        Args:
            problem: 决策问题
            result: 决策结果

        Returns:
            str: JSON 字符串
        """
        # 构建问题数据
        problem_data = {
            "alternatives": list(problem.alternatives),
            "criteria": [
                {
                    "name": crit.name,
                    "weight": crit.weight,
                    "direction": crit.direction,
                }
                for crit in problem.criteria
            ],
            "scores": problem.scores,
        }

        # 构建结果数据
        result_data = {
            "rankings": [
                {
                    "alternative": ranking.alternative,
                    "rank": ranking.rank,
                    "score": ranking.score,
                }
                for ranking in result.rankings
            ],
            "raw_scores": result.raw_scores,
            "metadata": {
                "algorithm_name": result.metadata.algorithm_name,
                "problem_size": list(result.metadata.problem_size),
                "metrics": result.metadata.metrics,
            },
        }

        # 组合数据
        data = {
            "problem": problem_data,
            "result": result_data,
        }

        return json.dumps(data, ensure_ascii=False, indent=2)

    def save_markdown(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        file_path: str,
        *,
        title: str = "MCDA 决策分析报告",
    ) -> None:
        """
        保存 Markdown 报告到文件

        Args:
            problem: 决策问题
            result: 决策结果
            file_path: 文件路径
            title: 报告标题

        Raises:
            ReportError: 文件保存失败
        """
        from mcda_core.exceptions import ReportError

        try:
            markdown = self.generate_markdown(problem, result, title=title)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown)
        except Exception as e:
            raise ReportError(f"保存 Markdown 报告失败: {e}")

    def save_json(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        file_path: str,
    ) -> None:
        """
        保存 JSON 报告到文件

        Args:
            problem: 决策问题
            result: 决策结果
            file_path: 文件路径

        Raises:
            ReportError: 文件保存失败
        """
        from mcda_core.exceptions import ReportError

        try:
            json_str = self.export_json(problem, result)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)
        except Exception as e:
            raise ReportError(f"保存 JSON 报告失败: {e}")
