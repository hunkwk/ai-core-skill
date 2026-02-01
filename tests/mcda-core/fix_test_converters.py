"""
修复 test_converters.py 中的编码问题
"""

import sys
from pathlib import Path

test_file = Path(__file__).parent / "test_converters.py"

# 读取文件
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复: 添加 encoding='utf-8'
content = content.replace(
    'with open(json_file, \'r\') as f:',
    'with open(json_file, \'r\', encoding=\'utf-8\') as f:'
)

# 修复其他可能的 open 调用
content = content.replace(
    'with open(yaml_file, \'r\') as f:',
    'with open(yaml_file, \'r\', encoding=\'utf-8\') as f:'
)

content = content.replace(
    'with open(original_yaml, \'r\') as f:',
    'with open(original_yaml, \'r\', encoding=\'utf-8\') as f:'
)

content = content.replace(
    'with open(final_yaml, \'r\') as f:',
    'with open(final_yaml, \'r\', encoding=\'utf-8\') as f:'
)

content = content.replace(
    'with open(original_json, \'r\') as f:',
    'with open(original_json, \'r\', encoding=\'utf-8\') as f:'
)

content = content.replace(
    'with open(final_json, \'r\') as f:',
    'with open(final_json, \'r\', encoding=\'utf-8\') as f:'
)

# 写回文件
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ test_converters.py 编码问题修复完成")
print("\n修复内容:")
print("  所有 open() 调用添加 encoding='utf-8'")
