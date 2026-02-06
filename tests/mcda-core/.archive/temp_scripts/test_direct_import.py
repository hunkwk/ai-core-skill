"""
直接导入测试 - 不依赖 mcda_core 包

直接从文件系统导入模块进行测试
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
skills_dir = project_root / "skills"
sys.path.insert(0, str(skills_dir))

print("="*70)
print("  直接导入测试（绕过包安装）")
print("="*70)
print(f"项目根目录: {project_root}")
print(f"Skills 目录: {skills_dir}")
print(f"Python 路径已添加")
print()

success_count = 0
total_count = 5

# =============================================================================
# 测试 1: 直接导入 loaders 模块
# =============================================================================
print("[测试 1/5] 直接导入 loaders 模块")
try:
    # 直接从文件导入
    loaders_module_path = skills_dir / "mcda-core" / "lib" / "loaders"
    if loaders_module_path.exists():
        # 添加到路径
        sys.path.insert(0, str(loaders_module_path.parent))

        # 导入
        from loaders import JSONLoader, YAMLLoader, LoaderFactory
        print("  ✅ 成功导入 loaders")
        success_count += 1
    else:
        print(f"  ❌ loaders 模块路径不存在: {loaders_module_path}")
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 测试 2: 直接导入 converters 模块
# =============================================================================
print("\n[测试 2/5] 直接导入 converters 模块")
try:
    lib_dir = skills_dir / "mcda-core" / "lib"
    sys.path.insert(0, str(lib_dir))

    # 导入
    from converters import ConfigConverter
    print("  ✅ 成功导入 converters")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 测试 3: 直接导入 core 模块
# =============================================================================
print("\n[测试 3/5] 直接导入 core 模块")
try:
    lib_dir = skills_dir / "mcda-core" / "lib"
    sys.path.insert(0, str(lib_dir))

    # 导入
    import core
    MCDAOrchestrator = core.MCDAOrchestrator
    print("  ✅ 成功导入 core.MCDAOrchestrator")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 测试 4: 创建实例
# =============================================================================
print("\n[测试 4/5] 创建实例")
try:
    lib_dir = skills_dir / "mcda-core" / "lib"
    sys.path.insert(0, str(lib_dir))

    from loaders import JSONLoader, YAMLLoader, LoaderFactory
    from converters import ConfigConverter
    import core

    # 创建实例
    json_loader = JSONLoader()
    yaml_loader = YAMLLoader()
    converter = ConfigConverter()
    orchestrator = core.MCDAOrchestrator()

    print("  ✅ 成功创建所有实例")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 测试 5: 测试基本功能
# =============================================================================
print("\n[测试 5/5] 测试基本功能")
try:
    import tempfile
    import json

    lib_dir = skills_dir / "mcda-core" / "lib"
    sys.path.insert(0, str(lib_dir))

    from loaders import JSONLoader
    from converters import ConfigConverter

    # 测试 JSONLoader
    test_data = {"name": "测试", "value": 123}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    loader = JSONLoader()
    data = loader.load(temp_file)

    assert data["name"] == "测试", "数据加载失败"
    Path(temp_file).unlink()

    print("  ✅ JSONLoader 功能正常")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# 总结
# =============================================================================
print("\n" + "="*70)
print(f"  结果: {success_count}/{total_count} 通过")
print("="*70)

if success_count == total_count:
    print("\n✅ 所有测试通过！")
    print("\n说明: 代码本身没有问题，只是包安装的问题。")
    print("\n解决方案:")
    print("  方案 1: 运行 python install_mcda.py")
    print("  方案 2: 设置环境变量 PYTHONPATH")
    print(f"           export PYTHONPATH={skills_dir}:$PYTHONPATH")
    print("  方案 3: 使用相对导入运行测试")
else:
    print(f"\n❌ 还有 {total_count - success_count} 个测试失败")
    print("\n请检查上面的错误信息")
