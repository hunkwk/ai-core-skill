#!/usr/bin/env python3
"""
生成性能测试数据
"""

import yaml
from pathlib import Path


def generate_test_data(alternatives_count: int, criteria_count: int, output_file: Path):
    """生成性能测试数据

    Args:
        alternatives_count: 方案数量
        criteria_count: 准则数量
        output_file: 输出文件路径
    """
    # 生成方案
    alternatives = [f"方案{i:03d}" for i in range(1, alternatives_count + 1)]

    # 生成准则
    criteria = []
    for i in range(1, criteria_count + 1):
        direction = "higher_better" if i % 2 == 0 else "lower_better"
        criteria.append({
            "name": f"准则{i:02d}",
            "weight": round(1.0 / criteria_count, 4),  # 均匀权重
            "direction": direction,
            "description": f"测试准则{i}"
        })

    # 生成评分矩阵
    scores = {}
    import random
    random.seed(42)  # 固定种子以确保一致性

    for alt in alternatives:
        scores[alt] = {}
        for crit in criteria:
            # 生成 0-100 的随机分数
            scores[alt][crit["name"]] = random.randint(1, 100)

    # 组装数据
    data = {
        "name": f"性能测试数据 - {alternatives_count}方案 × {criteria_count}准则",
        "algorithm": {
            "name": "topsis"  # 使用 TOPSIS 算法进行性能测试
        },
        "alternatives": alternatives,
        "criteria": criteria,
        "scores": scores
    }

    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✅ 生成测试数据: {output_file}")
    print(f"   方案数: {alternatives_count}, 准则数: {criteria_count}")


if __name__ == "__main__":
    fixtures_dir = Path(__file__).parent / "fixtures"

    # 生成小规模测试数据
    generate_test_data(
        alternatives_count=10,
        criteria_count=5,
        output_file=fixtures_dir / "small_10x5.yaml"
    )

    # 生成中规模测试数据
    generate_test_data(
        alternatives_count=50,
        criteria_count=20,
        output_file=fixtures_dir / "medium_50x20.yaml"
    )

    # 生成大规模测试数据
    generate_test_data(
        alternatives_count=100,
        criteria_count=50,
        output_file=fixtures_dir / "large_100x50.yaml"
    )

    print("\n✅ 所有测试数据生成完成！")
