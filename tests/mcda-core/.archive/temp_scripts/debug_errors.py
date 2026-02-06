"""
详细错误捕获脚本 - 捕获完整的错误堆栈
"""

import sys
from pathlib import Path
import traceback
import tempfile
import json

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*70)
print("  详细错误诊断")
print("="*70)
print(f"项目根目录: {project_root}")
print(f"Python 路径: {sys.executable}")
print()

# =============================================================================
# 测试 1: Loader 抽象层
# =============================================================================
print("[测试 1] Loader 抽象层")
print("-"*70)

try:
    print("步骤 1: 导入 mcda_core.loaders...")
    from mcda_core.loaders import ConfigLoader, JSONLoader, YAMLLoader, LoaderFactory
    print("  ✅ 导入成功")

    print("步骤 2: 创建实例...")
    json_loader = JSONLoader()
    yaml_loader = YAMLLoader()
    factory = LoaderFactory()
    print("  ✅ 实例创建成功")

    print("步骤 3: 测试 get_loader...")
    loader = factory.get_loader("test.json")
    assert isinstance(loader, JSONLoader), "应该返回 JSONLoader"
    print("  ✅ get_loader 工作正常")

    print("\n✅ Loader 抽象层: 通过\n")

except Exception as e:
    print(f"\n❌ Loader 抽象层: 失败")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("\n完整堆栈:")
    traceback.print_exc()
    print()

# =============================================================================
# 测试 2: JSONLoader 实际功能
# =============================================================================
print("[测试 2] JSONLoader 实际功能")
print("-"*70)

try:
    print("步骤 1: 创建测试 JSON 文件...")
    test_data = {
        "name": "测试",
        "alternatives": ["A", "B"],
        "criteria": [{"name": "成本", "weight": 0.6, "direction": "lower_better"}],
        "scores": {"A": {"成本": 100}, "B": {"成本": 150}},
        "algorithm": {"name": "wsm"}
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name

    print(f"  临时文件: {temp_file}")

    print("步骤 2: 使用 JSONLoader 加载...")
    from mcda_core.loaders import JSONLoader
    loader = JSONLoader()
    data = loader.load(temp_file)

    print(f"  加载的数据: {data}")
    assert data["name"] == "测试", "数据不匹配"
    print("  ✅ 数据加载成功")

    print("步骤 3: 验证数据...")
    is_valid = loader.validate(data)
    assert is_valid == True, "验证失败"
    print("  ✅ 验证通过")

    # 清理
    Path(temp_file).unlink()
    print("  ✅ 临时文件已清理")

    print("\n✅ JSONLoader 功能: 通过\n")

except Exception as e:
    print(f"\n❌ JSONLoader 功能: 失败")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("\n完整堆栈:")
    traceback.print_exc()

    # 尝试清理
    try:
        Path(temp_file).unlink()
    except:
        pass
    print()

# =============================================================================
# 测试 3: MCDAOrchestrator.load_from_json
# =============================================================================
print("[测试 3] MCDAOrchestrator.load_from_json")
print("-"*70)

try:
    print("步骤 1: 创建测试 JSON 配置...")
    test_config = {
        "name": "云服务商选择",
        "alternatives": ["AWS", "Azure"],
        "criteria": [
            {"name": "成本", "weight": 0.6, "direction": "lower_better"},
            {"name": "功能", "weight": 0.4, "direction": "higher_better"}
        ],
        "scores": {
            "AWS": {"成本": 3, "功能": 5},
            "Azure": {"成本": 4, "功能": 4}
        },
        "algorithm": {"name": "wsm"}
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)
        temp_file = f.name

    print(f"  临时文件: {temp_file}")

    print("步骤 2: 导入 MCDAOrchestrator...")
    from mcda_core.core import MCDAOrchestrator
    print("  ✅ 导入成功")

    print("步骤 3: 调用 load_from_json...")
    orchestrator = MCDAOrchestrator()
    problem = orchestrator.load_from_json(temp_file)

    print(f"  加载的决策问题:")
    print(f"    - 备选方案: {problem.alternatives}")
    print(f"    - 准则数量: {len(problem.criteria)}")
    print(f"    - 算法: {problem.algorithm}")

    assert problem is not None, "返回 None"
    assert len(problem.alternatives) == 2, "备选方案数量错误"
    assert len(problem.criteria) == 2, "准则数量错误"

    print("  ✅ load_from_json 工作正常")

    # 清理
    Path(temp_file).unlink()
    print("  ✅ 临时文件已清理")

    print("\n✅ MCDAOrchestrator.load_from_json: 通过\n")

except Exception as e:
    print(f"\n❌ MCDAOrchestrator.load_from_json: 失败")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("\n完整堆栈:")
    traceback.print_exc()

    # 尝试清理
    try:
        Path(temp_file).unlink()
    except:
        pass
    print()

# =============================================================================
# 测试 4: ConfigConverter
# =============================================================================
print("[测试 4] ConfigConverter")
print("-"*70)

try:
    print("步骤 1: 导入 ConfigConverter...")
    from mcda_core.converters import ConfigConverter
    print("  ✅ 导入成功")

    print("步骤 2: 创建测试 YAML 文件...")
    import yaml

    test_config = {
        "name": "测试",
        "alternatives": ["A", "B"],
        "criteria": [{"name": "成本", "weight": 0.6, "direction": "lower_better"}],
        "scores": {"A": {"成本": 100}, "B": {"成本": 150}},
        "algorithm": {"name": "wsm"}
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(test_config, f, allow_unicode=True)
        yaml_file = f.name

    print(f"  临时文件: {yaml_file}")

    print("步骤 3: 执行转换 YAML → JSON...")
    converter = ConfigConverter()
    json_file = tempfile.mktemp(suffix='.json')

    converter.convert(yaml_file, json_file)

    assert Path(json_file).exists(), "JSON 文件未创建"
    print(f"  JSON 文件创建: {json_file}")

    print("步骤 4: 验证 JSON 内容...")
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    print(f"  转换后的数据: {json_data}")
    assert json_data["name"] == "测试", "转换数据错误"
    print("  ✅ 转换成功")

    # 清理
    Path(yaml_file).unlink()
    Path(json_file).unlink()
    print("  ✅ 临时文件已清理")

    print("\n✅ ConfigConverter: 通过\n")

except Exception as e:
    print(f"\n❌ ConfigConverter: 失败")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("\n完整堆栈:")
    traceback.print_exc()

    # 尝试清理
    try:
        Path(yaml_file).unlink()
        Path(json_file).unlink()
    except:
        pass
    print()

# =============================================================================
# 总结
# =============================================================================
print("="*70)
print("  诊断完成")
print("="*70)
print("\n如果所有测试都显示 ✅ 通过，说明代码功能正常。")
print("如果仍有 ❌ 失败，请查看上面的详细错误信息。")
