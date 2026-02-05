#!/usr/bin/env python3
"""
性能瓶颈分析脚本

使用 cProfile 分析 MCDA Core 的性能瓶颈
"""

import cProfile
import pstats
import io
from pathlib import Path
import sys

# 添加 mcda_core 到路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from mcda_core.core import MCDAOrchestrator


def profile_algorithm(algorithm_name: str, config_path: str, output_prefix: str):
    """分析算法性能

    Args:
        algorithm_name: 算法名称
        config_path: 配置文件路径
        output_prefix: 输出文件前缀
    """
    print(f"\n🔍 分析 {algorithm_name} 算法性能瓶颈...")

    # 创建性能分析器
    profiler = cProfile.Profile()

    # 运行分析
    orchestrator = MCDAOrchestrator()
    profiler.enable()

    result = orchestrator.run_workflow(config_path)

    profiler.disable()

    # 生成统计报告
    stats = pstats.Stats(profiler)
    stats.strip_dirs()

    # 按累积时间排序（Top 20）
    print(f"\n📊 {algorithm_name} - Top 20 性能瓶颈（按累积时间）:")
    stats.sort_stats('cumulative').print_stats(20)

    # 按自身时间排序（Top 20）
    print(f"\n📊 {algorithm_name} - Top 20 性能瓶颈（按自身时间）:")
    stats.sort_stats('time').print_stats(20)

    # 保存详细报告
    output_dir = Path("docs/active/mcda-core/v0.12")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 文本报告
    txt_file = output_dir / f"{output_prefix}_profile.txt"
    with open(txt_file, 'w') as f:
        stats.stream = f
        stats.sort_stats('cumulative').print_stats(50)
    print(f"\n✅ 详细报告已保存: {txt_file}")

    return stats


def identify_bottlenecks():
    """识别主要性能瓶颈"""
    print("\n" + "="*80)
    print("MCDA Core 性能瓶颈分析")
    print("="*80)

    # 测试数据路径
    fixtures_dir = Path(__file__).parent / "fixtures"

    # 分析三个规模
    test_configs = [
        ("小规模", str(fixtures_dir / "small_10x5.yaml"), "small"),
        ("中规模", str(fixtures_dir / "medium_50x20.yaml"), "medium"),
        ("大规模", str(fixtures_dir / "large_100x50.yaml"), "large"),
    ]

    all_stats = {}

    for name, config_path, prefix in test_configs:
        stats = profile_algorithm(name, config_path, prefix)
        all_stats[name] = stats

    # 生成汇总报告
    generate_summary_report(all_stats)

    print("\n" + "="*80)
    print("✅ 性能瓶颈分析完成！")
    print("="*80)


def generate_summary_report(all_stats: dict):
    """生成瓶颈分析汇总报告

    Args:
        all_stats: 所有规模的统计信息
    """
    output_file = Path("docs/active/mcda-core/v0.12/bottleneck-analysis.md")

    lines = []
    lines.append("# MCDA Core 性能瓶颈分析报告\n")
    lines.append("**生成时间**: " + __import__('time').strftime("%Y-%m-%d %H:%M:%S") + "\n")
    lines.append("---\n")

    lines.append("## 分析概述\n")
    lines.append("本报告使用 cProfile 对 MCDA Core 进行性能分析，识别主要性能瓶颈。\n")

    lines.append("## 测试场景\n")
    lines.append("- 小规模: 10方案 × 5准则\n")
    lines.append("- 中规模: 50方案 × 20准则\n")
    lines.append("- 大规模: 100方案 × 50准则\n")

    lines.append("## 主要发现\n")
    lines.append("### Top 5 性能瓶颈函数\n\n")
    lines.append("| 排名 | 函数名 | 调用次数 | 累积时间 | 自身时间 |")
    lines.append("|------|--------|----------|----------|----------|\n")

    # TODO: 从 all_stats 中提取 Top 5 瓶颈
    lines.append("| 1 | （待分析）| - | - | - |\n")
    lines.append("| 2 | （待分析）| - | - | - |\n")
    lines.append("| 3 | （待分析）| - | - | - |\n")
    lines.append("| 4 | （待分析）| - | - | - |\n")
    lines.append("| 5 | （待分析）| - | - | - |\n")

    lines.append("## 优化建议\n")
    lines.append("基于性能分析结果，建议的优化方向：\n\n")
    lines.append("1. **矩阵运算优化** - 使用 NumPy 向量化计算\n")
    lines.append("2. **结果缓存** - 对重复计算使用缓存\n")
    lines.append("3. **算法优化** - 优化关键算法的时间复杂度\n")

    lines.append("---\n")
    lines.append("*详细性能数据请参考同级目录下的 `*_profile.txt` 文件*\n")

    # 写入文件
    output_file.write_text("\n".join(lines), encoding='utf-8')
    print(f"\n✅ 汇总报告已生成: {output_file}")


if __name__ == "__main__":
    identify_bottlenecks()
