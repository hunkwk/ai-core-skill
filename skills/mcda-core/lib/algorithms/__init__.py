"""
MCDA Core - 汇总算法模块

提供多种 MCDA 汇总算法实现。
"""

from mcda_core.algorithms.base import (
    MCDAAlgorithm,
    register_algorithm,
    get_algorithm,
    list_algorithms,
)

# 导入具体算法（导入时自动注册）
from mcda_core.algorithms.wsm import WSMAlgorithm
from mcda_core.algorithms.wpm import WPMAlgorithm
from mcda_core.algorithms.topsis import TOPSISAlgorithm
from mcda_core.algorithms.vikor import VIKORAlgorithm

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
    "VIKORAlgorithm",
]
