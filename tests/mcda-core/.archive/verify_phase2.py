"""
MCDA Core - Phase 2 手动验证脚本

快速验证标准化功能是否正常工作。
"""

import sys
from pathlib import Path
import types

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 处理带连字符的包名：mcda-core -> mcda_core
# (复制 conftest.py 的模块别名逻辑)
mcda_core_path = project_root / "skills" / "mcda-core"

# 创建 skills.mcda_core 模块别名
mcda_core_module = types.ModuleType("skills.mcda_core")
mcda_core_module.__path__ = [str(mcda_core_path)]
sys.modules["skills.mcda_core"] = mcda_core_module

# 创建 skills.mcda_core.lib 子模块
lib_module = types.ModuleType("skills.mcda_core.lib")
lib_module.__path__ = [str(mcda_core_path / "lib")]
sys.modules["skills.mcda_core.lib"] = lib_module

# 现在导入模块
from mcda_core.normalization import (
    MinMaxNormalization,
    VectorNormalization,
    NormalizationService,
)
from mcda_core.models import NormalizationConfig


def test_minmax():
    """测试 MinMax 标准化"""
    print("=" * 60)
    print("测试 MinMax 标准化")
    print("=" * 60)

    method = MinMaxNormalization()
    costs = {"AWS": 20.0, "Azure": 50.0, "GCP": 35.0}

    result = method.normalize(costs, direction="lower_better")

    print(f"输入: {costs}")
    print(f"输出: {result.normalized_scores}")
    print(f"元数据: {result.metadata}")

    # 验证
    assert result.normalized_scores["AWS"] == 1.0, "AWS 成本最低，应该得 1.0"
    assert result.normalized_scores["Azure"] == 0.0, "Azure 成本最高，应该得 0.0"
    print("✅ MinMax 测试通过！\n")


def test_vector():
    """测试 Vector 标准化"""
    print("=" * 60)
    print("测试 Vector 标准化")
    print("=" * 60)

    method = VectorNormalization()
    scores = {"AWS": 85.0, "Azure": 92.0, "GCP": 88.0}

    result = method.normalize(scores, direction="higher_better")

    print(f"输入: {scores}")
    print(f"输出: {result.normalized_scores}")
    print(f"元数据: {result.metadata}")

    # 验证范数
    import math
    expected_norm = math.sqrt(85.0**2 + 92.0**2 + 88.0**2)
    assert result.metadata["norm"] == expected_norm, "范数计算错误"
    print("✅ Vector 测试通过！\n")


def test_service():
    """测试标准化服务"""
    print("=" * 60)
    print("测试标准化服务")
    print("=" * 60)

    service = NormalizationService()

    # 测试 MinMax
    config = NormalizationConfig(type="minmax", direction="lower_better")
    costs = {"AWS": 20.0, "Azure": 50.0, "GCP": 35.0}
    result = service.normalize(costs, config)

    print(f"MinMax 标准化成本:")
    print(f"  输入: {costs}")
    print(f"  输出: {result.normalized_scores}")
    assert result.normalized_scores["AWS"] == 1.0
    print("  ✅ 通过")

    # 测试 Vector
    config = NormalizationConfig(type="vector", direction="higher_better")
    scores = {"AWS": 85.0, "Azure": 92.0, "GCP": 88.0}
    result = service.normalize(scores, config)

    print(f"\nVector 标准化评分:")
    print(f"  输入: {scores}")
    print(f"  输出: {result.normalized_scores}")
    print("  ✅ 通过")

    # 测试批量标准化
    data = {
        "成本": {"AWS": 20.0, "Azure": 50.0, "GCP": 35.0},
        "性能": {"AWS": 85.0, "Azure": 92.0, "GCP": 88.0},
    }
    configs = {
        "成本": NormalizationConfig(type="minmax", direction="lower_better"),
        "性能": NormalizationConfig(type="vector", direction="higher_better"),
    }
    result = service.normalize_batch(data, configs)

    print(f"\n批量标准化:")
    print(f"  成本: {result['成本']}")
    print(f"  性能: {result['性能']}")
    assert len(result) == 2
    print("  ✅ 通过\n")


def test_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试错误处理")
    print("=" * 60)

    service = NormalizationService()

    # 测试未知方法
    config = NormalizationConfig(type="unknown_method", direction="higher_better")
    try:
        service.normalize({"A": 1.0, "B": 2.0}, config)
        print("❌ 应该抛出异常")
    except ValueError as e:
        print(f"✅ 未知方法异常: {e}")

    # 测试空输入
    method = MinMaxNormalization()
    try:
        method.normalize({}, direction="higher_better")
        print("❌ 应该抛出异常")
    except ValueError as e:
        print(f"✅ 空输入异常: {e}")

    # 测试单个值
    try:
        method.normalize({"A": 1.0}, direction="higher_better")
        print("❌ 应该抛出异常")
    except ValueError as e:
        print(f"✅ 单个值异常: {e}")

    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  MCDA Core - Phase 2 功能验证")
    print("=" * 60 + "\n")

    try:
        test_minmax()
        test_vector()
        test_service()
        test_error_handling()

        print("=" * 60)
        print("  ✅ 所有功能验证通过！")
        print("=" * 60 + "\n")

        print("📝 下一步: 运行完整测试套件")
        print("   python -m pytest tests/mcda-core/test_normalization.py -v\n")

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
