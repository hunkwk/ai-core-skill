"""
MCDA Core - Phase 3 测试最终修复脚本

修复测试文件中的准则名称和数据错误。
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


def fix_file(filepath: Path) -> int:
    """修复单个文件

    Returns:
        修改的行数
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # 修复 test_wsm_all_higher_better 中的准则名称重复
    content = content.replace(
        'Criterion(name="性能", weight=0.5, direction="higher_better"),\n            Criterion(name="性能", weight=0.5, direction="higher_better"),',
        'Criterion(name="性能", weight=0.5, direction="higher_better"),\n            Criterion(name="可靠性", weight=0.5, direction="higher_better"),'
    )

    # 修复 test_wsm_equal_weights 的计算期望值
    # A: 0.25*80 + 0.25*(100-60) + 0.25*70 + 0.25*75 = 20 + 10 + 17.5 + 18.75 = 66.25
    # B: 0.25*85 + 0.25*(100-55) + 0.25*75 + 0.25*70 = 21.25 + 11.25 + 18.75 + 17.5 = 68.75
    # 但是由于 test 中使用了 criteria 而不是 sample_criteria，所以权重是 0.25

    # 检查是否有修改
    changes = content != original_content

    if changes:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return 1
    return 0


def main():
    """主函数"""
    print("="*60)
    print("  MCDA Core - Phase 3 测试最终修复")
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
        print("  pytest tests/mcda-core/test_wsm.py tests/mcda-core/test_wpm.py -v")


if __name__ == "__main__":
    main()
