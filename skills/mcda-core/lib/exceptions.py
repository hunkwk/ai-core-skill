"""MCDA Core - 异常定义"""
from typing import Any


class MCDAError(Exception):
    """MCDA 异常基类"""

    def __init__(self, message: str, details: dict[str, Any] | None = None, **kwargs: Any):
        self.message = message
        # 合并 details 和 kwargs
        self.details = {**(details or {}), **kwargs}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - 详情: {self.details}"
        return self.message


class ValidationError(MCDAError):
    """数据验证异常"""
    pass


class WeightValidationError(ValidationError):
    """权重验证异常"""
    pass


class ScoreValidationError(ValidationError):
    """评分验证异常"""
    pass


class CriteriaValidationError(ValidationError):
    """准则验证异常"""
    pass


class AlgorithmError(MCDAError):
    """算法执行异常"""
    pass


class AlgorithmNotFoundError(AlgorithmError):
    """算法未找到异常"""
    pass


class NormalizationError(AlgorithmError):
    """标准化异常"""
    pass


class DataSourceError(MCDAError):
    """数据源异常"""
    pass


class YAMLParseError(DataSourceError):
    """YAML 解析异常"""
    pass


class CSVParseError(DataSourceError):
    """CSV 解析异常"""
    pass


class ExcelParseError(DataSourceError):
    """Excel 解析异常"""
    pass


class ScoringRuleError(MCDAError):
    """评分规则异常"""
    pass


class ScoringRuleValidationError(ValidationError):
    """评分规则验证异常"""
    pass


class ReportError(MCDAError):
    """报告生成异常"""
    pass


class SensitivityAnalysisError(MCDAError):
    """敏感性分析异常"""
    pass


__all__ = [
    "MCDAError",
    "ValidationError",
    "WeightValidationError",
    "ScoreValidationError",
    "CriteriaValidationError",
    "AlgorithmError",
    "AlgorithmNotFoundError",
    "NormalizationError",
    "DataSourceError",
    "YAMLParseError",
    "CSVParseError",
    "ExcelParseError",
    "ScoringRuleError",
    "ScoringRuleValidationError",
    "ReportError",
    "SensitivityAnalysisError",
]
