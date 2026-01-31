"""
MCDA Core - 汇总算法模块

提供多种 MCDA 汇总算法实现。
"""

from skills.mcda_core.lib.algorithms.base import (
    MCDAAlgorithm,
    register_algorithm,
    get_algorithm,
    list_algorithms,
)

# 导入具体算法（导入时自动注册）
from skills.mcda_core.lib.algorithms.wsm import WSMAlgorithm
from skills.mcda_core.lib.algorithms.wpm import WPMAlgorithm
from skills.mcda_core.lib.algorithms.topsis import TOPSISAlgorithm
from skills.mcda_core.lib.algorithms.vikor import VIKORAlgorithm

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
