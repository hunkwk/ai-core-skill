"""
MCDA Core - Phase 2 测试运行脚本
"""

import subprocess
import sys
from pathlib import Path


def main():
    """主函数"""
    print("="*60)
    print("  MCDA Core - Phase 2 标准化服务测试")
    print("="*60)

    # 切换到项目根目录
    project_root = Path(__file__).parent.parent.parent
    import os
    os.chdir(project_root)

    # 运行标准化测试
    print("\n[1/1] 运行标准化服务测试")
    print("="*60)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_normalization.py", "-v", "--tb=short"],
        capture_output=False
    )

    if result.returncode != 0:
        print("\n❌ 测试失败！")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  ✅ 所有测试通过！")
    print('='*60)

    # 尝试运行覆盖率测试
    print(f"\n测试覆盖率:")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_normalization.py",
         "--cov=skills/mcda-core/lib/normalization", "--cov-report=term-missing", "-q"],
        capture_output=True
    )

    if result.returncode == 0:
        output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
        for line in output.split('\n'):
            if 'TOTAL' in line or '%' in line or 'normalization' in line:
                print(f"  {line}")
    else:
        print("  提示: 安装 pytest-cov 可查看覆盖率 (pip install pytest-cov)")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
