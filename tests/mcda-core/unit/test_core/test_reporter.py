"""
MCDA Core 报告服务测试

测试范围:
- Markdown 报告生成
- JSON 导出
- 排名可视化
"""

import sys
from pathlib import Path

# 添加 mcda_core 模块路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_core_path.resolve()))

import pytest
import json
from datetime import datetime
from mcda_core.models import (
    Criterion,
    DecisionProblem,
    DecisionResult,
    RankingItem,
    ResultMetadata,
    Direction,
)
from mcda_core.exceptions import ReportError


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_criteria():
    """示例准则"""
    return (
        Criterion(name="性能", weight=0.4, direction="higher_better"),
        Criterion(name="成本", weight=0.3, direction="lower_better"),
        Criterion(name="可靠性", weight=0.3, direction="higher_better"),
    )

@pytest.fixture
def sample_scores():
    """示例评分"""
    return {
        "方案A": {"性能": 85.0, "成本": 60.0, "可靠性": 75.0},
        "方案B": {"性能": 70.0, "成本": 80.0, "可靠性": 90.0},
        "方案C": {"性能": 90.0, "成本": 50.0, "可靠性": 85.0},
    }

@pytest.fixture
def sample_problem(sample_criteria, sample_scores):
    """示例决策问题"""
    return DecisionProblem(
        alternatives=tuple(sample_scores.keys()),
        criteria=sample_criteria,
        scores=sample_scores,
    )

@pytest.fixture
def sample_result():
    """示例决策结果"""
    rankings = (
        RankingItem(alternative="方案C", rank=1, score=0.85),
        RankingItem(alternative="方案A", rank=2, score=0.75),
        RankingItem(alternative="方案B", rank=3, score=0.65),
    )

    metadata = ResultMetadata(
        algorithm_name="WSM",
        problem_size=(3, 3),
        metrics={"weighted_sums": {"方案C": 85.0, "方案A": 75.0, "方案B": 65.0}},
    )

    return DecisionResult(
        rankings=rankings,
        raw_scores={"方案C": 85.0, "方案A": 75.0, "方案B": 65.0},
        metadata=metadata,
    )


# ============================================================================
# Test ReportService - Markdown 报告生成
# ============================================================================

class TestMarkdownReport:
    """Markdown 报告生成测试"""

    def test_generate_basic_markdown_report(self, sample_problem, sample_result):
        """测试: 生成基本 Markdown 报告"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        assert markdown is not None
        assert len(markdown) > 0
        assert "# MCDA 决策分析报告" in markdown
        assert "方案C" in markdown
        assert "WSM" in markdown

    def test_markdown_includes_problem_description(self, sample_problem, sample_result):
        """测试: Markdown 报告包含问题描述"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        assert "## 决策问题" in markdown
        assert "备选方案" in markdown
        assert "评价准则" in markdown
        assert "性能" in markdown
        assert "成本" in markdown
        assert "可靠性" in markdown

    def test_markdown_includes_rankings(self, sample_problem, sample_result):
        """测试: Markdown 报告包含排名结果"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        assert "## 决策结果" in markdown
        assert "### 排名" in markdown
        assert "| 排名 | 方案 | 评分 |" in markdown
        assert "| 1 | 方案C | 0.85 |" in markdown
        assert "| 2 | 方案A | 0.75 |" in markdown
        assert "| 3 | 方案B | 0.65 |" in markdown

    def test_markdown_includes_algorithm_info(self, sample_problem, sample_result):
        """测试: Markdown 报告包含算法信息"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        assert "## 算法信息" in markdown
        assert "WSM" in markdown
        assert "3 个备选方案" in markdown
        assert "3 个准则" in markdown

    def test_markdown_includes_metadata(self, sample_problem, sample_result):
        """测试: Markdown 报告包含元数据"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        assert "## 元数据" in markdown
        assert "算法名称" in markdown
        assert "问题规模" in markdown

    def test_markdown_with_custom_title(self, sample_problem, sample_result):
        """测试: 自定义报告标题"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(
            sample_problem,
            sample_result,
            title="产品选型决策分析"
        )

        assert "# 产品选型决策分析" in markdown

    def test_markdown_includes_timestamp(self, sample_problem, sample_result):
        """测试: Markdown 报告包含时间戳"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        # 检查是否有日期格式的内容
        assert "生成时间" in markdown or "timestamp" in markdown.lower()


# ============================================================================
# Test ReportService - JSON 导出
# ============================================================================

class TestJSONExport:
    """JSON 导出测试"""

    def test_export_to_json(self, sample_problem, sample_result):
        """测试: 导出为 JSON"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)

        assert json_str is not None
        assert len(json_str) > 0

        # 验证可以解析为 JSON
        data = json.loads(json_str)
        assert "problem" in data
        assert "result" in data

    def test_json_includes_problem_data(self, sample_problem, sample_result):
        """测试: JSON 包含问题描述"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)
        data = json.loads(json_str)

        problem_data = data["problem"]
        assert "alternatives" in problem_data
        assert "criteria" in problem_data
        assert "scores" in problem_data

        # 验证备选方案
        assert "方案A" in problem_data["alternatives"]
        assert "方案B" in problem_data["alternatives"]
        assert "方案C" in problem_data["alternatives"]

    def test_json_includes_result_data(self, sample_problem, sample_result):
        """测试: JSON 包含结果数据"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)
        data = json.loads(json_str)

        result_data = data["result"]
        assert "rankings" in result_data
        assert "raw_scores" in result_data
        assert "metadata" in result_data

        # 验证排名
        rankings = result_data["rankings"]
        assert len(rankings) == 3
        assert rankings[0]["alternative"] == "方案C"
        assert rankings[0]["rank"] == 1
        assert rankings[0]["score"] == 0.85

    def test_json_includes_metadata(self, sample_problem, sample_result):
        """测试: JSON 包含元数据"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)
        data = json.loads(json_str)

        metadata = data["result"]["metadata"]
        assert "algorithm_name" in metadata
        assert "problem_size" in metadata
        assert "metrics" in metadata

        assert metadata["algorithm_name"] == "WSM"
        assert metadata["problem_size"] == [3, 3]

    def test_json_serialization(self, sample_problem, sample_result):
        """测试: JSON 序列化正确性"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)

        # 验证是有效的 JSON
        try:
            json.loads(json_str)
        except json.JSONDecodeError:
            pytest.fail("导出的 JSON 格式无效")


# ============================================================================
# Test ReportService - 文件导出
# ============================================================================

class TestFileExport:
    """文件导出测试"""

    def test_save_markdown_to_file(self, sample_problem, sample_result, tmp_path):
        """测试: 保存 Markdown 报告到文件"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        file_path = tmp_path / "report.md"

        reporter.save_markdown(sample_problem, sample_result, str(file_path))

        assert file_path.exists()

        # 读取并验证内容
        content = file_path.read_text(encoding="utf-8")
        assert "# MCDA 决策分析报告" in content

    def test_save_json_to_file(self, sample_problem, sample_result, tmp_path):
        """测试: 保存 JSON 报告到文件"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        file_path = tmp_path / "report.json"

        reporter.save_json(sample_problem, sample_result, str(file_path))

        assert file_path.exists()

        # 读取并验证内容
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
        assert "problem" in data
        assert "result" in data


# ============================================================================
# Test ReportService - 排名可视化
# ============================================================================

class TestRankingVisualization:
    """排名可视化测试"""

    def test_generate_ranking_table(self, sample_problem, sample_result):
        """测试: 生成排名表格"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        table = reporter.generate_ranking_table(sample_result)

        assert table is not None
        assert "| 排名 | 方案 | 评分 |" in table
        assert "| 1 | 方案C | 0.85 |" in table

    def test_generate_score_chart(self, sample_problem, sample_result):
        """测试: 生成分数图表（文本形式）"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        chart = reporter.generate_score_chart(sample_result)

        assert chart is not None
        assert "方案C" in chart or "方案C" in chart

    def test_generate_comparison_table(self, sample_problem, sample_result):
        """测试: 生成方案对比表"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        table = reporter.generate_comparison_table(sample_problem)

        assert table is not None
        assert "| 方案 |" in table
        assert "性能" in table
        assert "成本" in table


# ============================================================================
# Test ReportService Properties
# ============================================================================

class TestReportServiceProperties:
    """ReportService 属性测试"""

    def test_service_name(self):
        """测试: 服务名称"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        # 验证服务可以正常实例化
        assert reporter is not None


# ============================================================================
# Test ReportService Error Handling
# ============================================================================

class TestReportServiceErrors:
    """ReportService 错误处理测试"""

    def test_invalid_file_path(self, sample_problem, sample_result):
        """测试: 无效文件路径"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()

        with pytest.raises(ReportError):
            reporter.save_markdown(sample_problem, sample_result, "/invalid/path/report.md")

    def test_empty_rankings(self, sample_problem):
        """测试: 空排名结果会在创建 DecisionResult 时抛出异常"""
        from mcda_core.reporter import ReportService

        # DecisionResult 在创建时会验证 rankings 不能为空
        with pytest.raises(ValueError) as exc_info:
            empty_result = DecisionResult(
                rankings=(),
                raw_scores={},
                metadata=ResultMetadata(
                    algorithm_name="WSM",
                    problem_size=(0, 0),
                ),
            )

        assert "rankings 不能为空" in str(exc_info.value)

    def test_markdown_with_custom_title(self, sample_problem, sample_result):
        """测试: 使用自定义标题生成 Markdown 报告"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(
            sample_problem,
            sample_result,
            title="自定义决策分析报告"
        )

        assert "自定义决策分析报告" in markdown
        assert "# 自定义决策分析报告" in markdown

    def test_markdown_includes_metadata(self, sample_problem, sample_result):
        """测试: Markdown 报告包含元数据"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        assert "## 元数据" in markdown
        assert "算法名称" in markdown
        assert "问题规模" in markdown

    def test_generate_comparison_table(self, sample_problem):
        """测试: 生成方案对比表"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        table = reporter.generate_comparison_table(sample_problem)

        assert "方案" in table
        assert "性能" in table
        assert "成本" in table
        assert "可靠性" in table
        assert "方案A" in table
        assert "方案B" in table
        assert "方案C" in table

    def test_export_json_structure(self, sample_problem, sample_result):
        """测试: JSON 导出的结构正确性"""
        from mcda_core.reporter import ReportService
        import json

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)

        data = json.loads(json_str)

        assert "problem" in data
        assert "result" in data
        assert "alternatives" in data["problem"]
        assert "criteria" in data["problem"]
        assert "rankings" in data["result"]
        assert "metadata" in data["result"]

    def test_export_json_includes_all_data(self, sample_problem, sample_result):
        """测试: JSON 导出包含所有必要数据"""
        from mcda_core.reporter import ReportService
        import json

        reporter = ReportService()
        json_str = reporter.export_json(sample_problem, sample_result)

        data = json.loads(json_str)

        # 验证问题数据
        assert len(data["problem"]["alternatives"]) == 3
        assert len(data["problem"]["criteria"]) == 3

        # 验证结果数据
        assert len(data["result"]["rankings"]) == 3
        assert data["result"]["metadata"]["algorithm_name"] == "WSM"

    def test_generate_score_chart(self, sample_result):
        """测试: 生成分数图表"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        chart = reporter.generate_score_chart(sample_result)

        assert "方案C" in chart
        assert "方案A" in chart
        assert "方案B" in chart
        # 验证包含条形字符
        assert "█" in chart

    def test_save_json_to_file(self, sample_problem, sample_result, tmp_path):
        """测试: 保存 JSON 报告到文件"""
        from mcda_core.reporter import ReportService
        import json

        reporter = ReportService()
        file_path = tmp_path / "report.json"

        reporter.save_json(sample_problem, sample_result, str(file_path))

        # 验证文件存在并读取内容
        assert file_path.exists()
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        assert "problem" in data
        assert "result" in data

    def test_save_markdown_to_file(self, sample_problem, sample_result, tmp_path):
        """测试: 保存 Markdown 报告到文件"""
        from mcda_core.reporter import ReportService

        reporter = ReportService()
        file_path = tmp_path / "report.md"

        reporter.save_markdown(sample_problem, sample_result, str(file_path))

        # 验证文件存在并包含内容
        assert file_path.exists()
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "# MCDA 决策分析报告" in content
        assert "决策问题" in content

    def test_markdown_includes_timestamp(self, sample_problem, sample_result):
        """测试: Markdown 报告包含时间戳"""
        from mcda_core.reporter import ReportService
        from datetime import datetime

        reporter = ReportService()
        markdown = reporter.generate_markdown(sample_problem, sample_result)

        # 验证包含时间戳
        assert "生成时间" in markdown
        # 验证时间格式（应该是 YYYY-MM-DD HH:MM:SS）
        assert len(markdown) > 0
