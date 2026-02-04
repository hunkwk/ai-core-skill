"""
MCDA Core - 汇总算法模块

提供多种 MCDA 汇总算法实现。
"""

from .base import (
    MCDAAlgorithm,
    register_algorithm,
    get_algorithm,
    list_algorithms,
)

# 导入具体算法（导入时自动注册）
from .wsm import WSMAlgorithm
from .wpm import WPMAlgorithm
from .topsis import TOPSISAlgorithm
from .topsis_interval import IntervalTOPSISAlgorithm
from .vikor import VIKORAlgorithm
from .vikor_interval import IntervalVIKORAlgorithm
from .todim_interval import IntervalTODIMAlgorithm
from .electre1_interval import ELECTRE1IntervalAlgorithm
from .promethee2_interval import PROMETHEE2IntervalAlgorithm
from .promethee2_service import (
    PROMETHEEService,
    PROMETHEEValidationError
)
from .todim import todim, TODIMError
from .electre1 import electre1, ELECTRE1Error

__all__ = [
    # 基类和注册
    "MCDAAlgorithm",
    "register_algorithm",
    "get_algorithm",
    "list_algorithms",
    # 算法
    "WSMAlgorithm",
    "WPMAlgorithm",
    "TOPSISAlgorithm",
    "IntervalTOPSISAlgorithm",
    "VIKORAlgorithm",
    "IntervalVIKORAlgorithm",
    "ELECTRE1IntervalAlgorithm",
    "PROMETHEE2IntervalAlgorithm",
    # TODIM
    "todim",
    "TODIMError",
    # ELECTRE-I
    "electre1",
    "ELECTRE1Error",
    # 服务
    "PROMETHEEService",
    "PROMETHEEValidationError",
]
