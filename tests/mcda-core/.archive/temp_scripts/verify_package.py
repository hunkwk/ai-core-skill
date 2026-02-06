"""
验证 mcda_core 包设置

这个脚本验证 skills/mcda-core 能否作为 mcda_core 包被导入
"""

import sys
from pathlib import Path

print("="*70)
print("  验证 mcda_core 包设置")
print("="*70)

# 项目路径
project_root = Path(__file__).parent.parent.parent
skills_dir = project_root / "skills"
mcda_core_dir = skills_dir / "mcda-core"

print(f"\n目录信息:")
print(f"  项目根目录: {project_root}")
print(f"  Skills 目录: {skills_dir}")
print(f"  MCDA Core 目录: {mcda_core_dir}")

# 检查关键文件
print(f"\n文件检查:")
init_file = mcda_core_dir / "__init__.py"
lib_init = mcda_core_dir / "lib" / "__init__.py"

print(f"  mcda-core/__init__.py: {'✅ 存在' if init_file.exists() else '❌ 不存在'}")
print(f"  mcda-core/lib/__init__.py: {'✅ 存在' if lib_init.exists() else '❌ 不存在'}")

# 添加 skills 到路径
if str(skills_dir) not in sys.path:
    sys.path.insert(0, str(skills_dir))
    print(f"\n✅ 已添加 {skills_dir} 到 sys.path")

# 尝试导入
print(f"\n导入测试:")
print("-"*70)

try:
    # 方式 1: 直接导入 mcda_core
    print("[1/3] 尝试: import mcda_core")
    import mcda_core
    print(f"  ✅ 成功！版本: {mcda_core.__version__}")
    print(f"     文件: {mcda_core.__file__}")

except ImportError as e:
    print(f"  ❌ 失败: {e}")

try:
    # 方式 2: 从 mcda_core 导入子模块
    print("\n[2/3] 尝试: from mcda_core import loaders")
    from mcda_core import loaders
    print(f"  ✅ 成功！")
    print(f"     loaders: {loaders}")

except ImportError as e:
    print(f"  ❌ 失败: {e}")

try:
    # 方式 3: 从 mcda_core.loaders 导入
    print("\n[3/3] 尝试: from mcda_core.loaders import JSONLoader")
    from mcda_core.loaders import JSONLoader, YAMLLoader, LoaderFactory
    print(f"  ✅ 成功！")
    print(f"     JSONLoader: {JSONLoader}")
    print(f"     YAMLLoader: {YAMLLoader}")
    print(f"     LoaderFactory: {LoaderFactory}")

    # 测试创建实例
    loader = JSONLoader()
    print(f"     ✅ 实例创建成功")

except ImportError as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("  结论")
print("="*70)

try:
    import mcda_core
    from mcda_core.loaders import JSONLoader
    from mcda_core.converters import ConfigConverter
    from mcda_core.core import MCDAOrchestrator

    print("\n✅ 所有导入成功！")
    print("\n可以运行以下命令进行 pytest 测试:")
    print(f"  cd {project_root}")
    print("  pytest tests/mcda-core/test_loaders/test_loaders.py -v")

except ImportError as e:
    print(f"\n❌ 导入失败: {e}")
    print("\n可能的原因:")
    print("  1. skills 目录不在 Python 路径中")
    print("  2. pytest.ini 配置不正确")
    print("\n解决方案:")
    print(f"  确保 pytest.ini 包含: pythonpath = skills")
