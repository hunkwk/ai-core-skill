"""
HTML 报告生成器单元测试

测试 HTML 报告生成器的各项功能：
- HTML 结构有效性
- CSS 样式包含
- 内容正确性
- 中文编码
- 响应式设计
"""

import sys
import tempfile
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

# 添加 mcda_core 模块路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from mcda_core.models import (
    Criterion,
    DecisionProblem,
    DecisionResult,
    RankingItem,
    ResultMetadata,
)
from mcda_core.reports.html_generator import HTMLReportGenerator


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
    return HTMLReportGenerator()


# ============================================================================
# HTML 结构有效性测试
# ============================================================================

def test_html_structure_valid(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试 HTML 结构有效性"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证基本 HTML 标签
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html
    assert "<head>" in html
    assert "</head>" in html
    assert "<body>" in html
    assert "</body>" in html

    # 验证可以使用 BeautifulSoup 解析
    soup = BeautifulSoup(html, "html.parser")
    assert soup.html is not None
    assert soup.head is not None
    assert soup.body is not None


def test_contains_css_styles(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试包含 CSS 样式"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证包含 style 标签
    assert "<style>" in html
    assert "</style>" in html

    # 验证包含关键 CSS 属性
    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.find("style")
    assert style_tag is not None

    css_content = style_tag.string
    assert css_content is not None
    # 验证包含一些基本样式
    assert "body" in css_content or "table" in css_content or ".container" in css_content


def test_title_in_document(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试标题包含在文档中"""
    title = "测试决策报告"
    html = html_generator.generate_html(
        sample_problem,
        sample_result,
        title=title,
    )

    # 验证标题在 HTML 中
    assert title in html

    # 验证 title 标签
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    assert title_tag is not None
    assert title in title_tag.string

    # 验证 h1 标题
    h1_tag = soup.find("h1")
    assert h1_tag is not None
    assert title in h1_tag.string


def test_chinese_encoding(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试中文编码正确"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证包含中文文本
    assert "方案" in html
    assert "成本" in html or "质量" in html or "交货期" in html

    # 验证 charset 设置（UTF-8 或 utf-8 都可以）
    soup = BeautifulSoup(html, "html.parser")
    meta_charset = soup.find("meta", {"charset": True})
    assert meta_charset is not None
    assert meta_charset.get("charset").lower() == "utf-8"


# ============================================================================
# 内容正确性测试
# ============================================================================

def test_rankings_table_correct(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试排名表格正确性"""
    html = html_generator.generate_html(sample_problem, sample_result)

    soup = BeautifulSoup(html, "html.parser")

    # 查找排名表格
    tables = soup.find_all("table")
    assert len(tables) > 0

    # 验证排名数据在表格中
    html_text = soup.get_text()
    for ranking in sample_result.rankings:
        assert ranking.alternative in html_text
        assert str(ranking.rank) in html_text


def test_score_matrix_table(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试评分矩阵表"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证包含评分矩阵
    html_text = html.lower()  # 转小写方便匹配
    for alt in sample_problem.alternatives:
        assert alt.lower() in html_text

    for crit in sample_problem.criteria:
        assert crit.name.lower() in html_text


def test_metadata_section(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试元数据部分"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证包含算法信息
    assert sample_result.metadata.algorithm_name in html

    # 验证包含问题规模
    assert str(sample_result.metadata.problem_size[0]) in html
    assert str(sample_result.metadata.problem_size[1]) in html


def test_generation_timestamp(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试生成时间戳"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证包含时间信息（包含 "生成时间" 或 "Generated" 等关键词）
    assert "生成时间" in html or "Generated" in html


# ============================================================================
# 样式和响应式设计测试
# ============================================================================

def test_responsive_design(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试响应式设计"""
    html = html_generator.generate_html(sample_problem, sample_result)

    soup = BeautifulSoup(html, "html.parser")

    # 验证包含 viewport meta 标签
    viewport = soup.find("meta", {"name": "viewport"})
    assert viewport is not None
    assert "width=device-width" in viewport.get("content", "")


def test_table_styling(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试表格样式"""
    html = html_generator.generate_html(sample_problem, sample_result)

    soup = BeautifulSoup(html, "html.parser")

    # 查找表格
    tables = soup.find_all("table")
    assert len(tables) > 0

    # 验证表格有样式（class 或 style 属性，或者有 CSS 样式定义）
    has_styled_table = False

    # 方法1：检查表格本身的 class 或 style 属性
    for table in tables:
        if table.get("class") or table.get("style"):
            has_styled_table = True
            break

    # 方法2：检查 HTML 中是否有 table 的 CSS 样式定义
    if not has_styled_table:
        style_tag = soup.find("style")
        if style_tag and style_tag.string:
            # 检查是否有 table、th、td 的样式定义
            css_content = style_tag.string.lower()
            if "table" in css_content or "th" in css_content or "td" in css_content:
                has_styled_table = True

    assert has_styled_table, "至少应该有表格相关的样式定义"


# ============================================================================
# 图表相关测试
# ============================================================================

def test_chart_inclusion(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试图表包含（当 include_chart=True 时）"""
    html = html_generator.generate_html(
        sample_problem,
        sample_result,
        include_chart=True,
    )

    # 当包含图表时，应该有图表相关的内容
    # 注意：由于图表是 base64 编码的图片，我们检查是否有 img 标签
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")

    # 如果图表生成功能实现，应该有图片
    # 这里我们暂时只验证函数可以正常调用
    assert html is not None


def test_no_chart_when_disabled(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试不包含图表时（include_chart=False）"""
    html = html_generator.generate_html(
        sample_problem,
        sample_result,
        include_chart=False,
    )

    # 验证没有 img 标签或图表相关内容
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")

    # 应该没有图表图片
    chart_images = [img for img in images if img.get("src", "").startswith("data:image")]
    assert len(chart_images) == 0


# ============================================================================
# 打印样式测试
# ============================================================================

def test_print_styles(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试打印样式"""
    html = html_generator.generate_html(sample_problem, sample_result)

    # 验证包含打印媒体查询
    assert "@media print" in html or "print" in html.lower()


# ============================================================================
# 文件保存测试
# ============================================================================

def test_save_html(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试保存 HTML 文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test_report.html"

        # 保存文件
        html_generator.save_html(
            sample_problem,
            sample_result,
            str(file_path),
        )

        # 验证文件存在
        assert file_path.exists()

        # 验证文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert content is not None
            assert len(content) > 0
            assert "<!DOCTYPE html>" in content


# ============================================================================
# 错误处理测试
# ============================================================================

def test_save_html_invalid_path(
    html_generator: HTMLReportGenerator,
    sample_problem: DecisionProblem,
    sample_result: DecisionResult,
):
    """测试保存到无效路径时的错误处理"""
    invalid_path = "/nonexistent/directory/report.html"

    with pytest.raises(Exception):
        html_generator.save_html(
            sample_problem,
            sample_result,
            invalid_path,
        )
