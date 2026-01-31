"""
MCDA Core - Python 测试运行脚本

使用方法:
    python tests/mcda-core/run_tests.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ {description} 失败！")
        return False

    print(f"\n✅ {description} 成功！")
    return True


def main():
    """主函数"""
    print("="*60)
    print("  MCDA Core - 运行单元测试")
    print("="*60)

    # 切换到项目根目录
    project_root = Path(__file__).parent.parent.parent
    import os
    os.chdir(project_root)

    # 检查 Python 版本
    print(f"\n[1/4] Python 环境")
    print(f"  版本: {sys.version}")
    print(f"  路径: {sys.executable}")

    # 安装依赖
    print(f"\n[2/4] 安装依赖")
    run_command(
        [sys.executable, "-m", "pip", "install", "pytest", "pyyaml", "numpy", "-q"],
        "安装依赖包"
    )

    # 运行数据模型测试
    print(f"\n[3/4] 运行数据模型测试")
    if not run_command(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_models.py", "-v", "--tb=short"],
        "数据模型测试"
    ):
        sys.exit(1)

    # 运行异常测试
    print(f"\n[4/4] 运行异常测试")
    if not run_command(
        [sys.executable, "-m", "pytest", "tests/mcda-core/test_exceptions.py", "-v", "--tb=short"],
        "异常测试"
    ):
        sys.exit(1)

    # 成功
    print(f"\n{'='*60}")
    print("  ✅ 所有测试通过！")
    print('='*60)

    # 尝试运行覆盖率测试
    print(f"\n测试覆盖率:")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/mcda-core/",
         "--cov=skills/mcda-core/lib", "--cov-report=term-missing", "-q"],
        capture_output=True
    )

    if result.returncode == 0:
        # 提取覆盖率信息
        output = result.stdout.decode()
        for line in output.split('\n'):
            if 'TOTAL' in line or '%' in line:
                print(f"  {line}")
    else:
        print("  提示: 安装 pytest-cov 可查看覆盖率 (pip install pytest-cov)")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
