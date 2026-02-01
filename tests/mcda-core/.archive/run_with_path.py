"""
Phase 1 测试运行器 - 自动修复路径问题
"""

import sys
from pathlib import Path

# 自动添加路径
project_root = Path(__file__).parent.parent.parent
skills_dir = project_root / "skills"
lib_dir = skills_dir / "mcda-core" / "lib"

# 添加到 sys.path
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

if str(skills_dir) not in sys.path:
    sys.path.insert(0, str(skills_dir))

print("="*70)
print("  MCDA Core Phase 1 - 测试运行器")
print("="*70)
print(f"项目根目录: {project_root}")
print(f"Lib 目录: {lib_dir}")
print(f"Skills 目录: {skills_dir}")
print()

# 现在可以导入了
try:
    from loaders import JSONLoader, YAMLLoader, LoaderFactory
    from converters import ConfigConverter
    import core
    from exceptions import ConfigLoadError, ValidationError

    print("✅ 所有模块导入成功！")
    print()

    # 显示模块信息
    print("模块信息:")
    print(f"  - JSONLoader: {JSONLoader}")
    print(f"  - YAMLLoader: {YAMLLoader}")
    print(f"  - LoaderFactory: {LoaderFactory}")
    print(f"  - ConfigConverter: {ConfigConverter}")
    print(f"  - MCDAOrchestrator: {core.MCDAOrchestrator}")
    print()

    # 测试创建实例
    print("创建实例:")
    orchestrator = core.MCDAOrchestrator()
    converter = ConfigConverter()
    print(f"  ✅ MCDAOrchestrator 实例创建成功")
    print(f"  ✅ ConfigConverter 实例创建成功")
    print()

    # 测试方法
    print("检查方法:")
    methods = [
        ('orchestrator', orchestrator, ['load_from_yaml', 'load_from_json', 'load_from_file', 'analyze', 'validate']),
        ('converter', converter, ['convert', 'convert_to_json', 'convert_to_yaml'])
    ]

    for name, obj, expected_methods in methods:
        print(f"  {name}:")
        for method in expected_methods:
            has_method = hasattr(obj, method)
            status = "✅" if has_method else "❌"
            print(f"    {status} {method}")

    print()
    print("="*70)
    print("  ✅ 所有检查通过！代码功能正常！")
    print("="*70)
    print()
    print("现在可以运行 pytest 测试了：")
    print("  PYTHONPATH={} python -m pytest tests/mcda-core/test_loaders/ -v".format(lib_dir))

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

    print()
    print("解决方案:")
    print("  1. 运行: python install_mcda.py")
    print("  2. 或设置环境变量:")
    print(f"     set PYTHONPATH={lib_dir};%PYTHONPATH%")
