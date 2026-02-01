"""
快速测试导入是否正常
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*60)
print("  测试模块导入")
print("="*60)

# 测试 1: 导入 loaders
print("\n[1/5] 测试导入 mcda_core.loaders...")
try:
    from mcda_core.loaders import JSONLoader, YAMLLoader, LoaderFactory
    print("✅ mcda_core.loaders 导入成功")
except Exception as e:
    print(f"❌ mcda_core.loaders 导入失败: {e}")
    sys.exit(1)

# 测试 2: 导入 converters
print("\n[2/5] 测试导入 mcda_core.converters...")
try:
    from mcda_core.converters import ConfigConverter
    print("✅ mcda_core.converters 导入成功")
except Exception as e:
    print(f"❌ mcda_core.converters 导入失败: {e}")
    sys.exit(1)

# 测试 3: 导入 core
print("\n[3/5] 测试导入 mcda_core.core...")
try:
    from mcda_core.core import MCDAOrchestrator
    print("✅ mcda_core.core 导入成功")
except Exception as e:
    print(f"❌ mcda_core.core 导入失败: {e}")
    sys.exit(1)

# 测试 4: 创建实例
print("\n[4/5] 测试创建实例...")
try:
    orchestrator = MCDAOrchestrator()
    converter = ConfigConverter()
    print("✅ 实例创建成功")
except Exception as e:
    print(f"❌ 实例创建失败: {e}")
    sys.exit(1)

# 测试 5: 检查方法存在
print("\n[5/5] 检查新方法是否存在...")
try:
    assert hasattr(orchestrator, 'load_from_json'), "缺少 load_from_json 方法"
    assert hasattr(orchestrator, 'load_from_file'), "缺少 load_from_file 方法"
    assert hasattr(converter, 'convert'), "缺少 convert 方法"
    assert hasattr(converter, 'convert_to_json'), "缺少 convert_to_json 方法"
    assert hasattr(converter, 'convert_to_yaml'), "缺少 convert_to_yaml 方法"
    print("✅ 所有方法都存在")
except AssertionError as e:
    print(f"❌ 方法检查失败: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("  ✅ 所有导入测试通过！")
print("="*60)
