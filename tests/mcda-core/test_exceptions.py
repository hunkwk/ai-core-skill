"""
MCDA Core - 异常单元测试

测试所有异常类型的创建、继承和字符串表示。
"""

import pytest

from skills.mcda_core.lib.exceptions import (
    # 基类
    MCDAError,
    # 验证异常
    ValidationError,
    WeightValidationError,
    ScoreValidationError,
    CriteriaValidationError,
    # 算法异常
    AlgorithmError,
    AlgorithmNotFoundError,
    NormalizationError,
    # 数据源异常
    DataSourceError,
    YAMLParseError,
    CSVParseError,
    ExcelParseError,
    # 评分规则异常
    ScoringRuleError,
    ScoringRuleValidationError,
    # 报告异常
    ReportError,
    # 敏感性分析异常
    SensitivityAnalysisError,
)


# =============================================================================
# MCDAError 测试
# =============================================================================

class TestMCDAError:
    """测试 MCDAError 基类"""

    def test_create_basic_error(self):
        """测试创建基本异常"""
        error = MCDAError("基本错误消息")
        assert str(error) == "基本错误消息"
        assert error.message == "基本错误消息"
        assert error.details == {}

    def test_create_error_with_details(self):
        """测试带详情的异常"""
        error = MCDAError(
            "计算失败",
            details={"algorithm": "wsm", "step": "normalization"}
        )
        assert error.message == "计算失败"
        assert error.details == {"algorithm": "wsm", "step": "normalization"}
        assert "计算失败" in str(error)
        assert "algorithm" in str(error)

    def test_error_is_exception(self):
        """测试异常是 Exception 的子类"""
        error = MCDAError("错误")
        assert isinstance(error, Exception)
        assert isinstance(error, MCDAError)


# =============================================================================
# ValidationError 测试
# =============================================================================

class TestValidationError:
    """测试 ValidationError"""

    def test_create_basic_validation_error(self):
        """测试创建基本验证异常"""
        error = ValidationError("数据验证失败")
        assert str(error) == "数据验证失败"
        assert isinstance(error, MCDAError)

    def test_create_validation_error_with_field(self):
        """测试带字段名的验证异常"""
        error = ValidationError(
            "字段值无效",
            field="weight",
            value=1.5
        )
        assert error.details["field"] == "weight"
        assert error.details["value"] == 1.5
        assert "字段值无效" in str(error)

    def test_validation_error_inheritance(self):
        """测试继承关系"""
        error = ValidationError("验证失败")
        assert isinstance(error, ValidationError)
        assert isinstance(error, MCDAError)
        assert isinstance(error, Exception)


# =============================================================================
# WeightValidationError 测试
# =============================================================================

class TestWeightValidationError:
    """测试 WeightValidationError"""

    def test_create_weight_validation_error(self):
        """测试创建权重验证异常"""
        error = WeightValidationError(
            "权重总和不为 1.0",
            sum_weights=0.85,
            expected=1.0
        )
        assert isinstance(error, ValidationError)
        assert "权重总和不为 1.0" in str(error)

    def test_weight_validation_error_inheritance_chain(self):
        """测试继承链"""
        error = WeightValidationError("权重错误")
        assert isinstance(error, WeightValidationError)
        assert isinstance(error, ValidationError)
        assert isinstance(error, MCDAError)


# =============================================================================
# ScoreValidationError 测试
# =============================================================================

class TestScoreValidationError:
    """测试 ScoreValidationError"""

    def test_create_score_validation_error(self):
        """测试创建评分验证异常"""
        error = ScoreValidationError(
            "评分超出范围",
            alternative="AWS",
            criterion="成本",
            score=150,
            range_=(0, 100)
        )
        assert isinstance(error, ValidationError)
        assert error.details["alternative"] == "AWS"
        assert error.details["criterion"] == "成本"
        assert error.details["score"] == 150


# =============================================================================
# CriteriaValidationError 测试
# =============================================================================

class TestCriteriaValidationError:
    """测试 CriteriaValidationError"""

    def test_create_criteria_validation_error(self):
        """测试创建准则验证异常"""
        error = CriteriaValidationError(
            "至少需要 2 个评价准则",
            count=1,
            min_required=2
        )
        assert isinstance(error, ValidationError)
        assert error.details["count"] == 1
        assert error.details["min_required"] == 2


# =============================================================================
# AlgorithmError 测试
# =============================================================================

class TestAlgorithmError:
    """测试 AlgorithmError"""

    def test_create_basic_algorithm_error(self):
        """测试创建基本算法异常"""
        error = AlgorithmError("算法执行失败")
        assert isinstance(error, MCDAError)
        assert "算法执行失败" in str(error)

    def test_create_algorithm_error_with_algorithm_name(self):
        """测试带算法名称的异常"""
        error = AlgorithmError(
            "WSM 算法计算失败",
            algorithm="wsm",
            details={"division_by_zero": True}
        )
        assert error.details["algorithm"] == "wsm"
        assert error.details["division_by_zero"] is True


# =============================================================================
# AlgorithmNotFoundError 测试
# =============================================================================

class TestAlgorithmNotFoundError:
    """测试 AlgorithmNotFoundError"""

    def test_create_algorithm_not_found_error(self):
        """测试创建算法未找到异常"""
        error = AlgorithmNotFoundError(
            "算法 'xyz' 不存在",
            algorithm="xyz",
            available=["wsm", "wpm", "topsis", "vikor"]
        )
        assert isinstance(error, AlgorithmError)
        assert error.details["algorithm"] == "xyz"
        assert error.details["available"] == ["wsm", "wpm", "topsis", "vikor"]

    def test_algorithm_not_found_inheritance_chain(self):
        """测试继承链"""
        error = AlgorithmNotFoundError("算法未找到")
        assert isinstance(error, AlgorithmNotFoundError)
        assert isinstance(error, AlgorithmError)
        assert isinstance(error, MCDAError)


# =============================================================================
# NormalizationError 测试
# =============================================================================

class TestNormalizationError:
    """测试 NormalizationError"""

    def test_create_normalization_error(self):
        """测试创建标准化异常"""
        error = NormalizationError(
            "MinMax 标准化失败: 所有值相同",
            method="minmax",
            details={"all_values_equal": True}
        )
        assert isinstance(error, AlgorithmError)
        assert error.details["method"] == "minmax"
        assert error.details["all_values_equal"] is True


# =============================================================================
# DataSourceError 测试
# =============================================================================

class TestDataSourceError:
    """测试 DataSourceError"""

    def test_create_basic_data_source_error(self):
        """测试创建基本数据源异常"""
        error = DataSourceError("数据源加载失败")
        assert isinstance(error, MCDAError)

    def test_create_data_source_error_with_file(self):
        """测试带文件名的异常"""
        error = DataSourceError(
            "文件不存在",
            file="data.xlsx",
            sheet="Sheet1",
            details={"error": "File not found"}
        )
        assert error.details["file"] == "data.xlsx"
        assert error.details["sheet"] == "Sheet1"
        assert error.details["error"] == "File not found"

    def test_data_source_error_without_sheet(self):
        """测试不带 sheet 的异常（YAML/CSV）"""
        error = DataSourceError(
            "YAML 文件格式错误",
            file="config.yaml",
            details={"line": 10}
        )
        assert error.details["file"] == "config.yaml"
        assert "sheet" not in error.details


# =============================================================================
# YAMLParseError 测试
# =============================================================================

class TestYAMLParseError:
    """测试 YAMLParseError"""

    def test_create_yaml_parse_error(self):
        """测试创建 YAML 解析异常"""
        error = YAMLParseError(
            "YAML 格式错误",
            file="config.yaml",
            line=10,
            column=5,
            error="unexpected indent"
        )
        assert isinstance(error, DataSourceError)
        assert error.details["file"] == "config.yaml"
        assert error.details["line"] == 10
        assert error.details["column"] == 5
        assert error.details["error"] == "unexpected indent"


# =============================================================================
# CSVParseError 测试
# =============================================================================

class TestCSVParseError:
    """测试 CSVParseError"""

    def test_create_csv_parse_error(self):
        """测试创建 CSV 解析异常"""
        error = CSVParseError(
            "CSV 格式错误",
            file="data.csv",
            row=5,
            column=3,
            error="invalid number format"
        )
        assert isinstance(error, DataSourceError)
        assert error.details["file"] == "data.csv"
        assert error.details["row"] == 5
        assert error.details["column"] == 3


# =============================================================================
# ExcelParseError 测试
# =============================================================================

class TestExcelParseError:
    """测试 ExcelParseError"""

    def test_create_excel_parse_error(self):
        """测试创建 Excel 解析异常"""
        error = ExcelParseError(
            "Sheet 不存在",
            file="data.xlsx",
            sheet="不存在的Sheet",
            available=["Sheet1", "Sheet2"]
        )
        assert isinstance(error, DataSourceError)
        assert error.details["file"] == "data.xlsx"
        assert error.details["sheet"] == "不存在的Sheet"
        assert error.details["available"] == ["Sheet1", "Sheet2"]


# =============================================================================
# ScoringRuleError 测试
# =============================================================================

class TestScoringRuleError:
    """测试 ScoringRuleError"""

    def test_create_scoring_rule_error(self):
        """测试创建评分规则异常"""
        error = ScoringRuleError(
            "线性评分规则计算失败",
            rule_type="linear",
            value=150,
            range_=(0, 100)
        )
        assert isinstance(error, MCDAError)
        assert error.details["rule_type"] == "linear"
        assert error.details["value"] == 150
        assert error.details["range_"] == (0, 100)


# =============================================================================
# ScoringRuleValidationError 测试
# =============================================================================

class TestScoringRuleValidationError:
    """测试 ScoringRuleValidationError"""

    def test_create_scoring_rule_validation_error(self):
        """测试创建评分规则验证异常"""
        error = ScoringRuleValidationError(
            "阈值范围配置错误",
            field="ranges",
            rule_type="threshold"
        )
        assert isinstance(error, ValidationError)
        assert isinstance(error, MCDAError)
        assert error.details["field"] == "ranges"
        assert error.details["rule_type"] == "threshold"

    def test_scoring_rule_validation_inheritance_chain(self):
        """测试继承链"""
        error = ScoringRuleValidationError("验证失败")
        assert isinstance(error, ScoringRuleValidationError)
        assert isinstance(error, ValidationError)
        assert isinstance(error, MCDAError)


# =============================================================================
# ReportError 测试
# =============================================================================

class TestReportError:
    """测试 ReportError"""

    def test_create_report_error(self):
        """测试创建报告生成异常"""
        error = ReportError(
            "Markdown 报告生成失败",
            format="markdown",
            output="report.md"
        )
        assert isinstance(error, MCDAError)
        assert error.details["format"] == "markdown"
        assert error.details["output"] == "report.md"


# =============================================================================
# SensitivityAnalysisError 测试
# =============================================================================

class TestSensitivityAnalysisError:
    """测试 SensitivityAnalysisError"""

    def test_create_sensitivity_analysis_error(self):
        """测试创建敏感性分析异常"""
        error = SensitivityAnalysisError(
            "权重扰动测试失败",
            criterion="成本",
            delta=0.1,
            error="perturbed_weight > 1.0"
        )
        assert isinstance(error, MCDAError)
        assert error.details["criterion"] == "成本"
        assert error.details["delta"] == 0.1
        assert error.details["error"] == "perturbed_weight > 1.0"


# =============================================================================
# 异常捕获和传播测试
# =============================================================================

class TestExceptionHandling:
    """测试异常捕获和传播"""

    def test_catch_mcda_error_as_base_exception(self):
        """测试将 MCDAError 作为基类捕获"""
        with pytest.raises(MCDAError):
            raise WeightValidationError("权重错误")

    def test_catch_validation_error_as_mcda_error(self):
        """测试将 ValidationError 作为 MCDAError 捕获"""
        with pytest.raises(MCDAError):
            raise ScoreValidationError("评分错误")

    def test_catch_algorithm_error_as_mcda_error(self):
        """测试将 AlgorithmError 作为 MCDAError 捕获"""
        with pytest.raises(MCDAError):
            raise AlgorithmNotFoundError("算法未找到")

    def test_catch_specific_exception_before_general(self):
        """测试优先捕获特定异常"""
        try:
            raise WeightValidationError("权重错误")
        except WeightValidationError:
            # 捕获到特定异常
            assert True
        except MCDAError:
            # 不应该到这里
            assert False

    def test_exception_details_preserved_in_reraise(self):
        """测试异常详情在重新抛出时保留"""
        try:
            try:
                raise WeightValidationError("权重错误", sum_weights=0.85)
            except WeightValidationError as e:
                raise  # 重新抛出
        except WeightValidationError as e:
            assert e.details["sum_weights"] == 0.85

    def test_multiple_exception_types_in_try_except(self):
        """测试在 try-except 中捕获多种异常类型"""
        exceptions_to_raise = [
            WeightValidationError("权重错误"),
            ScoreValidationError("评分错误"),
            AlgorithmNotFoundError("算法未找到"),
        ]

        for exc in exceptions_to_raise:
            with pytest.raises(MCDAError):
                raise exc
