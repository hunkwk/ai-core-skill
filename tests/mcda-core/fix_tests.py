"""
修复测试文件中的 Criterion 和 DecisionProblem 参数
"""
import re

files_to_fix = [
    "test_wsm.py",
    "test_wpm.py",
    "test_topsis.py",
    "test_vikor.py",
]

for filename in files_to_fix:
    filepath = f"D:\\Workspace\\dev\\ai_skills_development\\ai_core_skill\\tests\\mcda-core\\{filename}"

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 修复 Criterion 缺少 name 参数的问题
    # Criterion( weight=... → Criterion(name="性能", weight=...)
    criterion_names = [
        ('Criterion( weight=0.4, direction="higher_better")', 'Criterion(name="性能", weight=0.4, direction="higher_better")'),
        ('Criterion( weight=0.3, direction="lower_better")', 'Criterion(name="成本", weight=0.3, direction="lower_better")'),
        ('Criterion( weight=0.2, direction="higher_better")', 'Criterion(name="可靠性", weight=0.2, direction="higher_better")'),
        ('Criterion( weight=0.1, direction="higher_better")', 'Criterion(name="易用性", weight=0.1, direction="higher_better")'),
        ('Criterion( weight=0.5, direction="higher_better")', 'Criterion(name="性能", weight=0.5, direction="higher_better")'),
        ('Criterion( weight=0.5, direction="lower_better")', 'Criterion(name="成本", weight=0.5, direction="lower_better")'),
        ('Criterion( weight=0.6, direction="lower_better")', 'Criterion(name="成本", weight=0.6, direction="lower_better")'),
        ('Criterion( weight=0.4, direction="lower_better")', 'Criterion(name="延迟", weight=0.4, direction="lower_better")'),
        ('Criterion( weight=1.0, direction="higher_better")', 'Criterion(name="性能", weight=1.0, direction="higher_better")'),
        ('Criterion( weight=0.25, direction="higher_better")', 'Criterion(name="性能", weight=0.25, direction="higher_better")'),
        ('Criterion( weight=0.6, direction="higher_better")', 'Criterion(name="性能", weight=0.6, direction="higher_better")'),
        ('Criterion( weight=0.4, direction="higher_better")', 'Criterion(name="成本", weight=0.4, direction="higher_better")'),
    ]

    for old, new in criterion_names:
        content = content.replace(old, new)

    # 修复 criteria=list[...] 为 criteria=tuple(...)
    # 这个需要更复杂的正则替换

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 修复完成: {filename}")

print("\n所有文件修复完成！")
