#!/usr/bin/env python
"""验证 Comparison Service 自动发现算法"""

import sys
sys.path.insert(0, 'lib')

from services.comparison_service import ComparisonService
from algorithms import list_algorithms

# 创建服务
service = ComparisonService()

# 检查支持的算法
print("=" * 60)
print("Comparison Service 算法发现验证")
print("=" * 60)
print()

# 从注册表获取所有算法
registered_algos = list_algorithms()
print(f"注册表中的算法 ({len(registered_algos)}):")
for algo in sorted(registered_algos):
    print(f"  - {algo}")
print()

# Comparison Service 支持的算法
supported_algos = service.supported_algorithms
print(f"Comparison Service 支持的算法 ({len(supported_algos)}):")
for algo in sorted(supported_algos):
    print(f"  - {algo}")
print()

# 验证一致性
if set(registered_algos) == set(supported_algos):
    print("✅ 验证通过：Comparison Service 自动支持所有已注册算法")
else:
    missing = set(registered_algos) - set(supported_algos)
    extra = set(supported_algos) - set(registered_algos)
    if missing:
        print(f"⚠️  缺少算法: {missing}")
    if extra:
        print(f"⚠️  多余算法: {extra}")

print()
print("=" * 60)
