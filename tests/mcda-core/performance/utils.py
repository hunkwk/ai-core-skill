"""
性能测试工具函数

提供性能测量、验收标准和报告生成功能
"""

import time
import tracemalloc
from typing import Callable, Any
from pathlib import Path


def measure_execution_time(func: Callable, *args, **kwargs) -> dict[str, Any]:
    """测量函数执行时间和资源使用

    Args:
        func: 要测量的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        dict: {
            'execution_time': float,  # 执行时间（秒）
            'result': Any,             # 返回值
            'memory_mb': float,        # 内存使用增量（MB）
            'memory_peak_mb': float    # 峰值内存（MB）
        }
    """
    tracemalloc.start()
    process = None

    try:
        import psutil
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        # 如果 psutil 不可用，使用 tracemalloc 的内存跟踪
        start_memory = 0

    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()

    if process:
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
    else:
        end_memory = 0

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'execution_time': end_time - start_time,
        'result': result,
        'memory_mb': max(0, end_memory - start_memory),
        'memory_peak_mb': peak / 1024 / 1024,
    }


class PerformanceCriteria:
    """性能验收标准"""

    # 响应时间标准（秒）
    RESPONSE_TIME_LIMITS = {
        'small': (10, 5, 0.5),      # 10方案 x 5准则
        'medium': (50, 20, 2.0),    # 50方案 x 20准则
        'large': (100, 50, 10.0),   # 100方案 x 50准则
        'xlarge': (1000, 100, 60.0), # 1000方案 x 100准则
    }

    # 内存使用标准（MB）
    MEMORY_LIMITS = {
        'small': 50,
        'medium': 200,
        'large': 1024,
        'xlarge': 4096,
    }

    @classmethod
    def check_performance(cls, category: str, alternatives: int,
                          criteria: int, exec_time: float,
                          memory_mb: float) -> dict[str, Any]:
        """检查性能是否符合标准

        Args:
            category: 规模类别（small/medium/large/xlarge）
            alternatives: 方案数量
            criteria: 准则数量
            exec_time: 执行时间（秒）
            memory_mb: 内存使用（MB）

        Returns:
            dict: {
                'response_time_ok': bool,  # 响应时间是否达标
                'memory_ok': bool,          # 内存是否达标
                'category': str,            # 规模类别
                'time_limit': float,        # 时间限制
                'memory_limit': float       # 内存限制
            }
        """
        if category not in cls.RESPONSE_TIME_LIMITS:
            raise ValueError(f"未知的规模类别: {category}")

        time_limit = cls.RESPONSE_TIME_LIMITS[category]
        memory_limit = cls.MEMORY_LIMITS[category]

        return {
            'response_time_ok': exec_time < time_limit[2],
            'memory_ok': memory_mb < memory_limit,
            'category': category,
            'time_limit': time_limit[2],
            'memory_limit': memory_limit,
        }


def generate_performance_report(test_results: dict[str, dict], output_file: Path):
    """生成性能测试报告（Markdown 格式）

    Args:
        test_results: 测试结果字典
        output_file: 输出文件路径
    """
    lines = []
    lines.append("# MCDA Core 性能测试报告\n")
    lines.append("**生成时间**: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    lines.append("---\n")

    # 测试概览
    lines.append("## 测试概览\n")
    lines.append("| 规模 | 方案数 | 准则数 | 响应时间 | 内存使用 | 时间达标 | 内存达标 |")
    lines.append("|------|--------|--------|----------|----------|----------|----------|")

    for category, result in test_results.items():
        time_status = "✅" if result['response_time_ok'] else "❌"
        memory_status = "✅" if result['memory_ok'] else "❌"

        # 添加规模描述（用于测试验证）
        scale_desc = f"{result['alternatives']}方案 × {result['criteria']}准则"
        lines.append(f"### {category.upper()} - {scale_desc}\n")

        lines.append(
            f"| {category} | {result['alternatives']} | {result['criteria']} | "
            f"{result['execution_time']:.3f}s | {result['memory_mb']:.1f}MB | "
            f"{time_status} | {memory_status} |"
        )

    lines.append("\n---\n")

    # 性能标准
    lines.append("## 性能验收标准\n")
    lines.append("| 规模 | 方案数 | 准则数 | 时间限制 | 内存限制 |")
    lines.append("|------|--------|--------|----------|----------|")

    for category in ['small', 'medium', 'large']:
        time_limit = PerformanceCriteria.RESPONSE_TIME_LIMITS[category]
        memory_limit = PerformanceCriteria.MEMORY_LIMITS[category]
        lines.append(
            f"| {category} | {time_limit[0]} | {time_limit[1]} | "
            f"< {time_limit[2]}s | < {memory_limit}MB |"
        )

    lines.append("\n---\n")

    # 结论
    lines.append("## 测试结论\n")

    all_passed = all(
        result['response_time_ok'] and result['memory_ok']
        for result in test_results.values()
    )

    if all_passed:
        lines.append("✅ **所有测试通过** - 性能符合预期标准\n")
    else:
        failed_tests = [
            cat for cat, result in test_results.items()
            if not (result['response_time_ok'] and result['memory_ok'])
        ]
        lines.append(f"❌ **部分测试失败** - 失败的规模: {', '.join(failed_tests)}\n")

    # 写入文件
    output_file.write_text("\n".join(lines), encoding='utf-8')
