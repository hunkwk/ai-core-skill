"""
PDF 报告生成器

使用 weasyprint 将 HTML 报告转换为 PDF 格式：
- HTML → PDF 转换
- 支持中文显示
- 分页控制
"""

from pathlib import Path
from typing import TYPE_CHECKING

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    HTML = None  # type: ignore
    CSS = None  # type: ignore

if TYPE_CHECKING:
    from .html_generator import HTMLReportGenerator
    from ..models import DecisionProblem, DecisionResult


class PDFReportGenerator:
    """PDF 报告生成器

    使用 weasyprint 将 HTML 报告转换为 PDF 格式。
    """

    def __init__(self, html_generator: "HTMLReportGenerator"):
        """
        初始化 PDF 生成器

        Args:
            html_generator: HTML 报告生成器实例

        Raises:
            ImportError: weasyprint 未安装
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "weasyprint 未安装，请安装：pip install weasyprint"
            )

        self.html_generator = html_generator

    def generate_pdf(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> bytes:
        """
        生成 PDF 字节流

        Args:
            problem: 决策问题
            result: 决策结果
            title: 报告标题
            include_chart: 是否包含图表

        Returns:
            bytes: PDF 字节流

        Raises:
            Exception: PDF 生成失败
        """
        # 首先生成 HTML
        html = self.html_generator.generate_html(
            problem,
            result,
            title=title,
            include_chart=include_chart,
        )

        # 将 HTML 转换为 PDF
        try:
            # 创建 HTML 对象
            html_obj = HTML(string=html, base_url="")

            # 添加中文字体支持（可选）
            # weasyprint 会自动使用系统字体

            # 生成 PDF
            pdf_bytes = html_obj.write_pdf()

            return pdf_bytes

        except Exception as e:
            raise Exception(f"PDF 生成失败: {e}")

    def save_pdf(
        self,
        problem: "DecisionProblem",
        result: "DecisionResult",
        file_path: str,
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> None:
        """
        保存 PDF 报告到文件

        Args:
            problem: 决策问题
            result: 决策结果
            file_path: 文件路径
            title: 报告标题
            include_chart: 是否包含图表

        Raises:
            IOError: 文件保存失败
            Exception: PDF 生成失败
        """
        # 生成 PDF 字节流
        pdf_bytes = self.generate_pdf(
            problem,
            result,
            title=title,
            include_chart=include_chart,
        )

        # 保存到文件
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            f.write(pdf_bytes)
