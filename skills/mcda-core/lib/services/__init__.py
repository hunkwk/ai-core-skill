"""
MCDA Core - 服务模块

提供各种专业服务，如 AHP 权重计算、熵权法、敏感性分析等。
"""

from mcda_core.services.ahp_service import AHPService, AHPValidationError
from mcda_core.services.comparison_service import (
    ComparisonService,
    ComparisonValidationError
)
from mcda_core.services.constraint_service import ConstraintService
from mcda_core.services.entropy_weight_service import (
    EntropyWeightService,
    EntropyWeightValidationError
)

__all__ = [
    "AHPService",
    "AHPValidationError",
    "ComparisonService",
    "ComparisonValidationError",
    "ConstraintService",
    "EntropyWeightService",
    "EntropyWeightValidationError",
]
