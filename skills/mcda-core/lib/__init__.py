"""
MCDA Core - Multi-Criteria Decision Analysis Core Framework

通用多准则决策分析核心框架，支持可插拔算法模型（WSM、AHP、TOPSIS 等）。
"""

__version__ = "0.3.0"

# 导入核心模块（供外部使用）
from . import models  # noqa: F401
from . import exceptions  # noqa: F401
from . import algorithms  # noqa: F401
from . import normalization  # noqa: F401
from . import validation  # noqa: F401
from . import reporter  # noqa: F401
from . import sensitivity  # noqa: F401
from . import utils  # noqa: F401
from . import loaders  # noqa: F401
from . import converters  # noqa: F401
from . import core  # noqa: F401
from . import cli  # noqa: F401
