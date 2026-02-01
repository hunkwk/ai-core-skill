"""
MCDA Core v0.3 Phase 1 - 配置增强测试

测试 Loader 抽象层、JSON 配置支持、配置格式转换
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> dict:
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    # 打印输出
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    success = result.returncode == 0
    print(f"\n{'✅' if success else '❌'} {description}: {'通过' if success else '失败'}")

    return {
        "success": success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }


def main():
    """运行 Phase 1 测试"""
    print("="*60)
    print("  MCDA Core v0.3 Phase 1 - 配置增强测试")
    print("="*60)

    project_root = Path(__file__).parent.parent.parent
    import os
    os.chdir(project_root)

    results = []

    # 1. Loader 抽象层测试
    print("\n[1/4] Loader 抽象层测试")
    result = run_command(
        [sys.executable, "-m", "pytest",
         "tests/mcda-core/test_loaders/test_loaders.py",
         "-v", "--tb=short"],
        "Loader 抽象层"
    )
    results.append(("Loader 抽象层", result))

    # 2. JSON 配置加载测试
    print("\n[2/4] JSON 配置集成测试")
    result = run_command(
        [sys.executable, "-m", "pytest",
         "tests/mcda-core/test_integration.py",
         "-k", "json",
         "-v", "--tb=short"],
        "JSON 配置集成"
    )
    results.append(("JSON 配置集成", result))

    # 3. 配置验证测试
    print("\n[3/4] 配置验证测试")
    result = run_command(
        [sys.executable, "-m", "pytest",
         "tests/mcda-core/test_validation.py",
         "-v", "--tb=short"],
        "配置验证"
    )
    results.append(("配置验证", result))

    # 4. E2E 测试（JSON 相关）
    print("\n[4/4] E2E 测试")
    result = run_command(
        [sys.executable, "-m", "pytest",
         "tests/mcda-core/test_e2e.py",
         "-v", "--tb=short"],
        "E2E 测试"
    )
    results.append(("E2E 测试", result))

    # 汇总结果
    print("\n" + "="*60)
    print("  测试结果汇总")
    print("="*60)

    passed = sum(1 for _, r in results if r["success"])
    total = len(results)

    for name, r in results:
        status = "✅ 通过" if r["success"] else "❌ 失败"
        print(f"  {name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 Phase 1 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
