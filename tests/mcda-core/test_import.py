"""
测试 mcda_core 模块导入

用于调试导入问题
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 lib 目录
mcda_core_lib_path = project_root / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_core_lib_path.resolve()))

# 创建 mcda_core 模块别名
import importlib.util
spec = importlib.util.spec_from_file_location("mcda_core", mcda_core_lib_path / "__init__.py")
mcda_core_module = importlib.util.module_from_spec(spec)
sys.modules["mcda_core"] = mcda_core_module
sys.modules["mcda_core"].__path__ = [str(mcda_core_lib_path)]
spec.loader.exec_module(mcda_core_module)

# 测试导入
print("Testing imports...")

try:
    from mcda_core import models
    print("✅ from mcda_core import models - SUCCESS")
    print(f"   models module: {models}")
    print(f"   Criterion: {models.Criterion}")
except Exception as e:
    print(f"❌ from mcda_core import models - FAILED: {e}")

try:
    from mcda_core import exceptions
    print("✅ from mcda_core import exceptions - SUCCESS")
except Exception as e:
    print(f"❌ from mcda_core import exceptions - FAILED: {e}")

try:
    from mcda_core import validation
    print("✅ from mcda_core import validation - SUCCESS")
except Exception as e:
    print(f"❌ from mcda_core import validation - FAILED: {e}")

try:
    from mcda_core.models import Criterion
    print("✅ from mcda_core.models import Criterion - SUCCESS")
    print(f"   Criterion: {Criterion}")
except Exception as e:
    print(f"❌ from mcda_core.models import Criterion - FAILED: {e}")

print("\nAll imports tested!")
