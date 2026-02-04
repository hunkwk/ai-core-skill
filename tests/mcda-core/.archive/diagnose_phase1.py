"""
Phase 1 测试诊断脚本
用于详细诊断测试失败的原因
"""

import sys
from pathlib import Path
import traceback

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("="*70)
print("  MCDA Core v0.3 Phase 1 - 测试诊断")
print("="*70)

# 测试结果记录
results = []

# =============================================================================
# 测试 1: Loader 抽象层导入
# =============================================================================
print("\n[测试 1/4] Loader 抽象层导入")
print("-"*70)

try:
    from mcda_core.loaders import (
        ConfigLoader,
        JSONLoader,
        YAMLLoader,
        LoaderFactory
    )
    print("✅ 导入成功")

    # 测试创建实例
    json_loader = JSONLoader()
    yaml_loader = YAMLLoader()
    factory = LoaderFactory()

    print("✅ 实例创建成功")

    # 测试 get_loader 方法
    loader_json = factory.get_loader("test.json")
    loader_yaml = factory.get_loader("test.yaml")

    assert isinstance(loader_json, JSONLoader), "get_loader('.json') 应该返回 JSONLoader"
    assert isinstance(loader_yaml, YAMLLoader), "get_loader('.yaml') 应该返回 YAMLLoader"

    print("✅ LoaderFactory.get_loader() 工作正常")

    results.append(("Loader 抽象层", True, None))

except Exception as e:
    print(f"❌ 失败: {e}")
    traceback.print_exc()
    results.append(("Loader 抽象层", False, str(e)))

# =============================================================================
# 测试 2: JSONLoader 功能测试
# =============================================================================
print("\n[测试 2/4] JSONLoader 功能测试")
print("-"*70)

try:
    import json
    import tempfile

    from mcda_core.loaders import JSONLoader
    from mcda_core.exceptions import ConfigLoadError

    # 创建测试 JSON 文件
    test_data = {
        "name": "测试问题",
        "alternatives": ["A", "B"],
        "criteria": [
            {"name": "成本", "weight": 0.6, "direction": "lower_better"}
        ],
        "scores": {
            "A": {"成本": 100},
            "B": {"成本": 150}
        },
        "algorithm": {"name": "wsm"}
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_file = f.name

    try:
        # 测试加载
        loader = JSONLoader()
        data = loader.load(temp_file)

        assert data["name"] == "测试问题", "数据加载不正确"
        assert len(data["alternatives"]) == 2, "备选方案数量不正确"

        print("✅ JSONLoader.load() 工作正常")

        # 测试验证
        is_valid = loader.validate(data)
        assert is_valid == True, "验证应该通过"

        print("✅ JSONLoader.validate() 工作正常")

        results.append(("JSONLoader 功能", True, None))

    finally:
        # 清理临时文件
        Path(temp_file).unlink()

except Exception as e:
    print(f"❌ 失败: {e}")
    traceback.print_exc()
    results.append(("JSONLoader 功能", False, str(e)))

# =============================================================================
# 测试 3: JSON 集成测试
# =============================================================================
print("\n[测试 3/4] JSON 集成测试")
print("-"*70)

try:
    import json
    import tempfile

    from mcda_core.core import MCDAOrchestrator
    from mcda_core.exceptions import ValidationError

    # 创建测试 JSON 文件
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

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f, ensure_ascii=False)
        temp_file = f.name

    try:
        # 测试 load_from_json
        orchestrator = MCDAOrchestrator()
        problem = orchestrator.load_from_json(temp_file)

        assert problem is not None, "load_from_json 返回 None"
        assert len(problem.alternatives) == 2, "备选方案数量不正确"
        assert len(problem.criteria) == 2, "准则数量不正确"

        print("✅ MCDAOrchestrator.load_from_json() 工作正常")

        # 测试 load_from_file（自动检测）
        problem2 = orchestrator.load_from_file(temp_file)

        assert problem2 is not None, "load_from_file 返回 None"
        assert len(problem2.alternatives) == 2, "load_from_file 备选方案数量不正确"

        print("✅ MCDAOrchestrator.load_from_file() 工作正常")

        results.append(("JSON 集成", True, None))

    finally:
        # 清理临时文件
        Path(temp_file).unlink()

except Exception as e:
    print(f"❌ 失败: {e}")
    traceback.print_exc()
    results.append(("JSON 集成", False, str(e)))

# =============================================================================
# 测试 4: ConfigConverter 测试
# =============================================================================
print("\n[测试 4/4] ConfigConverter 测试")
print("-"*70)

try:
    import json
    import tempfile
    import yaml

    from mcda_core.converters import ConfigConverter

    # 创建测试数据
    test_config = {
        "name": "测试",
        "alternatives": ["A", "B"],
        "criteria": [
            {"name": "成本", "weight": 0.6, "direction": "lower_better"}
        ],
        "scores": {
            "A": {"成本": 100},
            "B": {"成本": 150}
        },
        "algorithm": {"name": "wsm"}
    }

    # 创建 YAML 文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_config, f, allow_unicode=True)
        yaml_file = f.name

    try:
        converter = ConfigConverter()

        # 测试 YAML → JSON
        json_file = tempfile.mktemp(suffix='.json')
        converter.convert(yaml_file, json_file)

        assert Path(json_file).exists(), "JSON 文件未创建"

        # 验证 JSON 内容
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        assert json_data["name"] == "测试", "转换后数据不正确"

        print("✅ ConfigConverter.convert() YAML→JSON 工作正常")

        # 清理
        Path(json_file).unlink()

        results.append(("ConfigConverter", True, None))

    finally:
        # 清理临时文件
        Path(yaml_file).unlink()

except Exception as e:
    print(f"❌ 失败: {e}")
    traceback.print_exc()
    results.append(("ConfigConverter", False, str(e)))

# =============================================================================
# 汇总结果
# =============================================================================
print("\n" + "="*70)
print("  测试结果汇总")
print("="*70)

passed = sum(1 for _, success, _ in results if success)
total = len(results)

for name, success, error in results:
    status = "✅ 通过" if success else "❌ 失败"
    print(f"  {name}: {status}")
    if error:
        print(f"    错误: {error}")

print(f"\n总计: {passed}/{total} 通过")

if passed == total:
    print("\n🎉 所有测试通过！")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} 个测试失败")
    sys.exit(1)
