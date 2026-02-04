"""
MCDA Core - 模块入口点

这个文件让 skills/mcda-core 成为一个 Python 包（mcda_core）
"""

# 导出版本号
from .lib import __version__  # noqa: F401

# 重新导出 lib 的所有内容
from .lib import *  # noqa: F401, F403
