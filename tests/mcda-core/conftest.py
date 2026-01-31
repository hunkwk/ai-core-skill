"""
MCDA Core - pytest 配置文件

配置测试路径和共享 fixtures，处理带连字符的包名。
"""

import sys
from pathlib import Path
import types

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 处理带连字符的包名：mcda-core -> mcda_core
# Python 模块名不能包含连字符，所以需要创建模块别名
mcda_core_path = project_root / "skills" / "mcda-core"

# 创建 skills.mcda_core 模块别名
mcda_core_module = types.ModuleType("skills.mcda_core")
mcda_core_module.__path__ = [str(mcda_core_path)]
sys.modules["skills.mcda_core"] = mcda_core_module

# 创建 skills.mcda_core.lib 子模块
lib_module = types.ModuleType("skills.mcda_core.lib")
lib_module.__path__ = [str(mcda_core_path / "lib")]
sys.modules["skills.mcda_core.lib"] = lib_module
