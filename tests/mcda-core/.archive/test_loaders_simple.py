"""简化版测试运行器 - 不依赖pytest"""

import sys
import traceback
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "skills" / "mcda-core" / "lib"))

# 测试统计
PASSED = 0
FAILED = 0
ERRORS = []

def test_json_loader_valid():
    """测试 JSONLoader 加载有效配置"""
    try:
        from loaders import JSONLoader
        import json
        from tempfile import NamedTemporaryFile

        config = {
            "name": "Test Problem",
            "alternatives": ["A", "B", "C"],
            "criteria": [
                {"name": "Cost", "weight": 0.5, "direction": "minimize"}
            ]
        }

        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()

            loader = JSONLoader()
            data = loader.load(f.name)

            assert data["name"] == "Test Problem"
            assert len(data["alternatives"]) == 3

        return True
    except Exception as e:
        ERRORS.append(f"test_json_loader_valid: {str(e)}\n{traceback.format_exc()}")
        return False

def test_json_loader_invalid():
    """测试 JSONLoader 加载无效配置"""
    try:
        from loaders import JSONLoader
        from tempfile import NamedTemporaryFile
        from loaders import ConfigLoadError

        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            f.flush()

            loader = JSONLoader()

            try:
                loader.load(f.name)
                ERRORS.append("test_json_loader_invalid: Should have raised ConfigLoadError")
                return False
            except ConfigLoadError:
                return True  # 期望的异常
            except Exception as e:
                ERRORS.append(f"test_json_loader_invalid: Wrong exception: {type(e).__name__}")
                return False
    except Exception as e:
        ERRORS.append(f"test_json_loader_invalid: {str(e)}\n{traceback.format_exc()}")
        return False

def test_yaml_loader_valid():
    """测试 YAMLLoader 加载有效配置"""
    try:
        from loaders import YAMLLoader
        from tempfile import NamedTemporaryFile

        config = """
name: Test Problem
alternatives:
  - A
  - B
criteria:
  - name: Cost
    weight: 0.5
    direction: minimize
"""

        with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config)
            f.flush()

            loader = YAMLLoader()
            data = loader.load(f.name)

            assert data["name"] == "Test Problem"
            assert len(data["alternatives"]) == 2

        return True
    except ImportError as e:
        # YAML module not installed - this is expected
        if "yaml" in str(e):
            print("[SKIP] (yaml not installed)")
            return True  # Skip test, not a failure
        raise
    except Exception as e:
        ERRORS.append(f"test_yaml_loader_valid: {str(e)}\n{traceback.format_exc()}")
        return False

def test_loader_factory_json():
    """测试 LoaderFactory 获取 JSONLoader"""
    try:
        from loaders import LoaderFactory, JSONLoader

        factory = LoaderFactory()
        loader = factory.get_loader("config.json")

        assert isinstance(loader, JSONLoader)
        return True
    except Exception as e:
        ERRORS.append(f"test_loader_factory_json: {str(e)}\n{traceback.format_exc()}")
        return False

def test_loader_factory_yaml():
    """测试 LoaderFactory 获取 YAMLLoader"""
    try:
        from loaders import LoaderFactory, YAMLLoader

        factory = LoaderFactory()
        loader1 = factory.get_loader("config.yaml")
        loader2 = factory.get_loader("config.yml")

        assert isinstance(loader1, YAMLLoader)
        assert isinstance(loader2, YAMLLoader)
        return True
    except Exception as e:
        ERRORS.append(f"test_loader_factory_yaml: {str(e)}\n{traceback.format_exc()}")
        return False

def test_loader_factory_unsupported():
    """测试 LoaderFactory 不支持的格式"""
    try:
        from loaders import LoaderFactory

        factory = LoaderFactory()

        try:
            factory.get_loader("config.xml")
            ERRORS.append("test_loader_factory_unsupported: Should have raised ValueError")
            return False
        except ValueError:
            return True  # 期望的异常
        except Exception as e:
            ERRORS.append(f"test_loader_factory_unsupported: Wrong exception: {type(e).__name__}")
            return False
    except Exception as e:
        ERRORS.append(f"test_loader_factory_unsupported: {str(e)}\n{traceback.format_exc()}")
        return False

# 运行所有测试
TESTS = [
    test_json_loader_valid,
    test_json_loader_invalid,
    test_yaml_loader_valid,
    test_loader_factory_json,
    test_loader_factory_yaml,
    test_loader_factory_unsupported,
]

print("=" * 60)
print("MCDA Core v0.3 Phase 1 - Config Loader Tests")
print("=" * 60)

for test in TESTS:
    print(f"\nRunning {test.__name__}...", end=" ")
    try:
        if test():
            print("[PASS]")
            PASSED += 1
        else:
            print("[FAIL]")
            FAILED += 1
    except Exception as e:
        print(f"[ERROR] {e}")
        FAILED += 1

print("\n" + "=" * 60)
print(f"Test Results: {PASSED} passed, {FAILED} failed")
print("=" * 60)

if ERRORS:
    print("\nError Details:")
    for i, error in enumerate(ERRORS, 1):
        print(f"\n{i}. {error}")

sys.exit(0 if FAILED == 0 else 1)
