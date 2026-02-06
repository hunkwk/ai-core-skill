"""
结果缓存装饰器

提供函数结果缓存功能，避免重复计算
"""

from functools import lru_cache
from typing import TypeVar, Callable

T = TypeVar('T')


def cached_result(maxsize: int = 128) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """缓存结果的装饰器

    Args:
        maxsize: 最大缓存大小（默认 128）
            - 设置为 None 表示无限制
            - 设置为 0 表示禁用缓存
            - 设置为正整数表示缓存最近 N 个结果

    Returns:
        装饰器函数

    Example:
        ```python
        @cached_result(maxsize=128)
        def expensive_function(x, y):
            return x + y

        # 第一次调用
        result1 = expensive_function(2, 3)

        # 第二次调用（从缓存读取）
        result2 = expensive_function(2, 3)
        ```

    Note:
        - 使用 LRU（最近最少使用）淘汰策略
        - 函数参数必须是可哈希的
        - 导出了 cache_info 和 cache_clear 方法
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # 使用 lru_cache 实现缓存
        cached_func = lru_cache(maxsize=maxsize)(func)

        # 包装函数，添加额外功能
        def wrapper(*args, **kwargs):
            return cached_func(*args, **kwargs)

        # 导出缓存信息方法
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear

        return wrapper

    return decorator


class CacheStats:
    """缓存统计工具"""

    @staticmethod
    def get_stats(func: Callable) -> dict[str, int]:
        """获取函数的缓存统计信息

        Args:
            func: 已缓存的函数

        Returns:
            dict: {
                'hits': 缓存命中次数,
                'misses': 缓存未命中次数,
                'maxsize': 最大缓存大小,
                'currsize': 当前缓存大小
            }

        Raises:
            AttributeError: 如果函数未使用缓存
        """
        if not hasattr(func, 'cache_info'):
            raise AttributeError("函数未使用缓存装饰器")

        info = func.cache_info()
        return {
            'hits': info.hits,
            'misses': info.misses,
            'maxsize': info.maxsize,
            'currsize': info.currsize
        }

    @staticmethod
    def print_stats(func: Callable, func_name: str = None):
        """打印缓存统计信息

        Args:
            func: 已缓存的函数
            func_name: 函数名称（可选）
        """
        stats = CacheStats.get_stats(func)
        name = func_name or func.__name__

        print(f"\n缓存统计: {name}")
        print(f"  命中次数: {stats['hits']}")
        print(f"  未命中次数: {stats['misses']}")
        print(f"  命中率: {stats['hits'] / (stats['hits'] + stats['misses']) * 100:.1f}%")
        print(f"  当前缓存大小: {stats['currsize']}")
        print(f"  最大缓存大小: {stats['maxsize']}")

    @staticmethod
    def clear_cache(func: Callable):
        """清除函数的缓存

        Args:
            func: 已缓存的函数
        """
        if hasattr(func, 'cache_clear'):
            func.cache_clear()


def enable_cache_for_weighting(weight_class) -> None:
    """为权重计算类启用缓存

    Args:
        weight_class: 权重计算类（如 EntropyWeightService）

    Example:
        ```python
        from services.entropy_weight_service import EntropyWeightService
        enable_cache_for_weighting(EntropyWeightService)
        ```
    """
    # 缓存 calculate 方法
    if hasattr(weight_class, 'calculate'):
        original_calculate = weight_class.calculate

        @cached_result(maxsize=256)
        def cached_calculate(self, problem, **kwargs):
            return original_calculate(self, problem, **kwargs)

        weight_class.calculate = cached_calculate
