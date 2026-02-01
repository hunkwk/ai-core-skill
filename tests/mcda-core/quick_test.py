"""
快速验证修复 - 只测试最基本的导入和创建
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*60)
print("  快速验证修复")
print("="*60)

success_count = 0
total_count = 4

# 测试 1: 导入 loaders
print("\n[1/4] 导入 mcda_core.loaders...")
try:
    from mcda_core.loaders import JSONLoader, YAMLLoader, LoaderFactory
    print("  ✅ 成功")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 测试 2: 导入 converters
print("\n[2/4] 导入 mcda_core.converters...")
try:
    from mcda_core.converters import ConfigConverter
    print("  ✅ 成功")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 测试 3: 导入 core
print("\n[3/4] 导入 mcda_core.core...")
try:
    from mcda_core.core import MCDAOrchestrator
    print("  ✅ 成功")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 测试 4: 创建实例并检查方法
print("\n[4/4] 创建实例并检查方法...")
try:
    from mcda_core.core import MCDAOrchestrator
    from mcda_core.converters import ConfigConverter

    orchestrator = MCDAOrchestrator()
    converter = ConfigConverter()

    # 检查方法
    assert hasattr(orchestrator, 'load_from_json'), "缺少 load_from_json"
    assert hasattr(orchestrator, 'load_from_file'), "缺少 load_from_file"
    assert hasattr(converter, 'convert'), "缺少 convert"

    print("  ✅ 成功")
    success_count += 1
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 总结
print("\n" + "="*60)
print(f"  结果: {success_count}/{total_count} 通过")
print("="*60)

if success_count == total_count:
    print("\n✅ 所有基本导入测试通过！")
    print("\n下一步：运行完整的 pytest 测试")
    sys.exit(0)
else:
    print(f"\n❌ 还有 {total_count - success_count} 个测试失败")
    print("\n请检查上面的错误信息")
    sys.exit(1)
