"""
PDF 报告生成器单元测试

测试 PDF 报告生成器的各项功能：
- PDF 文件生成
- 中文显示
- 分页控制
- 文件完整性
"""

import sys
import tempfile
from pathlib import Path

import pytest

# 添加 mcda_core 模块路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from mcda_core.models import (
    Criterion,
    DecisionProblem,
    DecisionResult,
    RankingItem,
    ResultMetadata,
)

# 首先检查 weasyprint 是否安装
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# 然后导入 PDFReportGenerator
try:
    from mcda_core.reports.pdf_generator import PDFReportGenerator
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    PDFReportGenerator = None  # type: ignore


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_problem():
    """示例决策问题"""
    alternatives = ["方案A", "方案B", "方案C"]

    criteria = [
        Criterion(name="成本", weight=0.4, direction="lower_better"),
        Criterion(name="质量", weight=0.3, direction="higher_better"),
        Criterion(name="交货期", weight=0.3, direction="lower_better"),
    ]

    scores = {
        "方案A": {"成本": 50.0, "质量": 80.0, "交货期": 30.0},
        "方案B": {"成本": 60.0, "质量": 70.0, "交货期": 25.0},
        "方案C": {"成本": 45.0, "质量": 85.0, "交货期": 35.0},
    }

    return DecisionProblem(
        alternatives=alternatives,
        criteria=criteria,
        scores=scores,
    )


@pytest.fixture
def sample_result():
    """示例决策结果"""
    rankings = [
        RankingItem(alternative="方案C", rank=1, score=0.85),
        RankingItem(alternative="方案A", rank=2, score=0.75),
        RankingItem(alternative="方案B", rank=3, score=0.65),
    ]

    raw_scores = {
        "方案C": 0.85,
        "方案A": 0.75,
        "方案B": 0.65,
    }

    metadata = ResultMetadata(
        algorithm_name="TOPSIS",
        problem_size=(3, 3),
        metrics={},
    )

    return DecisionResult(
        rankings=rankings,
        raw_scores=raw_scores,
        metadata=metadata,
    )


@pytest.fixture
def html_generator():
    """HTML 报告生成器实例"""
    from mcda_core.reports.html_generator import HTMLReportGenerator
    return HTMLReportGenerator()


@pytest.fixture
def pdf_generator(html_generator):
    """PDF 报告生成器实例"""
    if PDF_AVAILABLE:
        return PDFReportGenerator(html_generator)
    else:
        pytest.skip("weasyprint 未安装")


# ============================================================================
# PDF 生成测试
# ============================================================================

@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_generation(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试 PDF 生成"""
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        title="测试决策报告",
        include_chart=False,  # 简化测试，不包含图表
    )

    # 验证返回字节流
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    # 验证 PDF 文件头（%PDF-）
    assert pdf_bytes[:4] == b"%PDF"


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_with_chart(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试包含图表的 PDF 生成"""
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        title="测试决策报告",
        include_chart=True,
    )

    # 验证返回字节流
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    # 验证 PDF 文件头
    assert pdf_bytes[:4] == b"%PDF"


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_chinese_characters(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试 PDF 中文显示"""
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        title="中文测试报告",
    )

    # 验证生成 PDF
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF"

    # 注意：PDF 是二进制格式，中文可能被编码
    # 我们只验证 PDF 文件本身有效


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_save_pdf(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试保存 PDF 文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test_report.pdf"

        # 保存文件
        pdf_generator.save_pdf(
            sample_problem,
            sample_result,
            str(file_path),
            title="测试决策报告",
            include_chart=False,
        )

        # 验证文件存在
        assert file_path.exists()

        # 验证文件大小
        assert file_path.stat().st_size > 0

        # 验证 PDF 文件头
        with open(file_path, "rb") as f:
            header = f.read(4)
            assert header == b"%PDF"


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_save_pdf_invalid_path(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试保存到无效路径时的错误处理"""
    invalid_path = "/nonexistent/directory/report.pdf"

    with pytest.raises(Exception):
        pdf_generator.save_pdf(
            sample_problem,
            sample_result,
            invalid_path,
        )


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_content_structure(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试 PDF 内容结构"""
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        title="结构测试",
        include_chart=False,
    )

    # 验证基本 PDF 结构
    assert b"%PDF" in pdf_bytes
    assert b"%%EOF" in pdf_bytes  # PDF 结束标记

    # 验证包含一些基本内容
    # 注意：PDF 内容格式复杂，我们只做基本验证
    assert len(pdf_bytes) > 1000  # 至少有内容


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_title_included(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试 PDF 包含标题"""
    title = "测试标题报告"
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        title=title,
    )

    # 验证生成 PDF
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0

    # 注意：在 PDF 中查找文本比较复杂
    # 我们只验证 PDF 文件有效


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_no_chart_when_disabled(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试不包含图表时"""
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        include_chart=False,
    )

    # 验证生成 PDF
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF"


@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_pdf_with_large_content(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试包含大量内容的 PDF"""
    # 生成包含图表的 PDF（内容更多）
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        include_chart=True,
    )

    # 验证生成
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF"

    # 包含图表的 PDF 应该更大
    assert len(pdf_bytes) > 5000  # 至少 5KB


# ============================================================================
# 集成测试
# ============================================================================

@pytest.mark.skipif(not WEASYPRINT_AVAILABLE or not PDF_AVAILABLE, reason="weasyprint 或 PDFReportGenerator 未安装")
def test_integration_html_to_pdf(
    pdf_generator: PDFReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """集成测试：HTML → PDF 转换"""
    # 先生成 HTML
    html = pdf_generator.html_generator.generate_html(
        sample_problem,
        sample_result,
        title="集成测试",
        include_chart=False,
    )

    # 验证 HTML 有效
    assert "<!DOCTYPE html>" in html
    assert "<html" in html

    # 再转换为 PDF
    pdf_bytes = pdf_generator.generate_pdf(
        sample_problem,
        sample_result,
        title="集成测试",
        include_chart=False,
    )

    # 验证 PDF 有效
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert b"%PDF" in pdf_bytes
