"""
MCDA Core - Phase 3 测试运行脚本
"""

import subprocess
import sys
from pathlib import Path


def main():
    """主函数"""
    print("="*60)
    print("  MCDA Core - Phase 3 汇总算法测试")
    print("="*60)

    # 切换到项目根目录
    project_root = Path(__file__).parent.parent.parent
    import os
    os.chdir(project_root)

    # 运行所有汇总算法测试
    print("\n[1/4] 运行 WSM 算法测试")
    print("="*60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_wsm.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        print("\n❌ WSM 测试失败！")
        return False

    print("\n[2/4] 运行 WPM 算法测试")
    print("="*60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_wpm.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        print("\n❌ WPM 测试失败！")
        return False

    print("\n[3/4] 运行 TOPSIS 算法测试")
    print("="*60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_topsis.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        print("\n❌ TOPSIS 测试失败！")
        return False

    print("\n[4/4] 运行 VIKOR 算法测试")
    print("="*60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_vikor.py", "-v", "--tb=short"],
        capture_output=False
    )
    if result.returncode != 0:
        print("\n❌ VIKOR 测试失败！")
        return False

    print(f"\n{'='*60}")
    print("  ✅ 所有测试通过！")
    print('='*60)

    # 尝试运行覆盖率测试
    print(f"\n测试覆盖率:")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_wsm.py",
         "tests/mcda-core/test_wpm.py", "tests/mcda-core/test_topsis.py",
         "tests/mcda-core/test_vikor.py",
         "--cov=skills/mcda-core/lib/algorithms", "--cov-report=term-missing", "-q"],
        capture_output=True
    )

    if result.returncode == 0:
        output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
        for line in output.split('\n'):
            if 'TOTAL' in line or '%' in line or 'algorithms' in line:
                print(f"  {line}")
    else:
        print("  提示: 安装 pytest-cov 可查看覆盖率 (pip install pytest-cov)")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
