"""
MCDA Core - Phase 3 测试修复脚本

修复测试文件中的 Criterion 和 DecisionProblem 参数问题。
"""

import re
from pathlib import Path

# 定义要修复的文件
files_to_fix = [
    "test_wsm.py",
    "test_wpm.py",
    "test_topsis.py",
    "test_vikor.py",
]

# 定义 Criterion 参数的映射
criterion_mappings = {
    'Criterion( weight=0.4, direction="higher_better")':
        'Criterion(name="性能", weight=0.4, direction="higher_better")',
    'Criterion( weight=0.3, direction="lower_better")':
        'Criterion(name="成本", weight=0.3, direction="lower_better")',
    'Criterion( weight=0.2, direction="higher_better")':
        'Criterion(name="可靠性", weight=0.2, direction="higher_better")',
    'Criterion( weight=0.1, direction="higher_better")':
        'Criterion(name="易用性", weight=0.1, direction="higher_better")',
    'Criterion( weight=0.5, direction="higher_better")':
        'Criterion(name="性能", weight=0.5, direction="higher_better")',
    'Criterion( weight=0.5, direction="lower_better")':
        'Criterion(name="成本", weight=0.5, direction="lower_better")',
    'Criterion( weight=0.6, direction="lower_better")':
        'Criterion(name="成本", weight=0.6, direction="lower_better")',
    'Criterion( weight=0.4, direction="lower_better")':
        'Criterion(name="延迟", weight=0.4, direction="lower_better")',
    'Criterion( weight=1.0, direction="higher_better")':
        'Criterion(name="性能", weight=1.0, direction="higher_better")',
    'Criterion( weight=0.25, direction="higher_better")':
        'Criterion(name="性能", weight=0.25, direction="higher_better")',
    'Criterion( weight=0.25, direction="lower_better")':
        'Criterion(name="成本", weight=0.25, direction="lower_better")',
}


def fix_file(filepath: Path) -> int:
    """修复单个文件

    Returns:
        修改的行数
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # 应用所有映射
    for old, new in criterion_mappings.items():
        content = content.replace(old, new)

    # 计算修改的行数
    changes = content != original_content

    if changes:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return 1
    return 0


def main():
    """主函数"""
    print("="*60)
    print("  MCDA Core - Phase 3 测试修复")
    print("="*60)

    # 获取当前目录
    current_dir = Path(__file__).parent

    fixed_count = 0
    for filename in files_to_fix:
        filepath = current_dir / filename

        if not filepath.exists():
            print(f"⚠️  文件不存在: {filename}")
            continue

        changes = fix_file(filepath)
        if changes:
            print(f"✅ 已修复: {filename}")
            fixed_count += 1
        else:
            print(f"ℹ️  无需修复: {filename}")

    print("="*60)
    print(f"  完成！共修复 {fixed_count} 个文件")
    print("="*60)

    if fixed_count > 0:
        print("\n下一步: 运行测试验证")
        print("  python tests/mcda-core/run_phase3_tests.py")
        print("  或")
        print("  pytest tests/mcda-core/test_wsm.py -v")


if __name__ == "__main__":
    main()
