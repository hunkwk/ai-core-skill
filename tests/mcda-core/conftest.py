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

# 添加 mcda-core/lib 到 Python 路径
mcda_core_lib_path = project_root / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_core_lib_path.resolve()))

# 创建 mcda_core 模块别名（因为 mcda-core 包名带连字符）
# 导入 lib 模块并将其注册为 mcda_core
import importlib.util
spec = importlib.util.spec_from_file_location("mcda_core", mcda_core_lib_path / "__init__.py")
mcda_core_module = importlib.util.module_from_spec(spec)
sys.modules["mcda_core"] = mcda_core_module
sys.modules["mcda_core"].__path__ = [str(mcda_core_lib_path)]
# 执行模块加载
spec.loader.exec_module(mcda_core_module)

