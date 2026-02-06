"""报告生成模块

提供多种格式的报告生成功能：
- HTML 报告
- PDF 报告
- Markdown 报告（已有）
"""

from .html_generator import HTMLReportGenerator

# PDF 生成器是可选的（依赖 weasyprint）
try:
    from .pdf_generator import PDFReportGenerator
    _pdf_available = True
except ImportError:
    _pdf_available = False
    PDFReportGenerator = None  # type: ignore

__all__ = [
    "HTMLReportGenerator",
]

if _pdf_available:
    __all__.append("PDFReportGenerator")
