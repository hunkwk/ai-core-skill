"""
缓存装饰器单元测试
"""

import pytest
import time
from pathlib import Path
import sys

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent
mcda_core_path = project_root / "skills" / "mcda-core" / "lib"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

# 直接导入 cache 模块
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cache",
    mcda_core_path / "utils" / "cache.py"
)
if spec and spec.loader:
    cache = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cache)

    cached_result = cache.cached_result
else:
    raise ImportError("无法加载 cache 模块")


class TestCachedResult:
    """测试缓存装饰器"""

    def test_cache_basic_functionality(self):
        """测试基本缓存功能"""
        call_count = [0]  # 使用列表避免 nonlocal 问题

        @cached_result(maxsize=128)
        def expensive_function(x, y):
            call_count[0] += 1
            return x + y

        # 第一次调用
        result1 = expensive_function(2, 3)
        assert result1 == 5
        assert call_count[0] == 1

        # 第二次调用（应该从缓存读取）
        result2 = expensive_function(2, 3)
        assert result2 == 5
        assert call_count[0] == 1  # 调用次数不应增加

    def test_cache_with_different_args(self):
        """测试不同参数的缓存"""
        call_count = [0]

        @cached_result(maxsize=128)
        def compute(x):
            call_count[0] += 1
            return x * 2

        # 调用不同参数
        assert compute(1) == 2
        assert call_count[0] == 1

        assert compute(2) == 4
        assert call_count[0] == 2

        # 重复调用（应该命中缓存）
        assert compute(1) == 2
        assert call_count[0] == 2

    def test_cache_with_kwargs(self):
        """测试关键字参数的缓存"""
        call_count = [0]

        @cached_result(maxsize=128)
        def func(a, b=0):
            call_count[0] += 1
            return a + b

        # 不同调用方式
        assert func(1, 2) == 3
        assert call_count[0] == 1

        assert func(1, b=3) == 4
        assert call_count[0] == 2  # 新参数

        # 重复调用相同参数
        assert func(1, b=3) == 4
        assert call_count[0] == 2  # 应该命中缓存

        assert func(1, 2) == 3
        assert call_count[0] == 2  # (1, 2) 之前调用过，应该命中缓存

    def test_cache_maxsize_limit(self):
        """测试缓存大小限制"""
        call_count = [0]

        @cached_result(maxsize=2)
        def func(x):
            call_count[0] += 1
            return x * 2

        # 填满缓存
        func(1)
        func(2)
        assert call_count[0] == 2

        # 超过 maxsize，最早的应该被淘汰
        func(3)
        func(1)  # 应该重新计算，因为被淘汰了
        assert call_count[0] == 4

    def test_cache_info(self):
        """测试缓存信息"""
        @cached_result(maxsize=10)
        def func(x):
            return x * 2

        # 调用几次
        func(1)
        func(2)
        func(1)

        # 检查缓存信息
        info = func.cache_info()
        assert info.hits == 1  # 命中 1 次
        assert info.misses == 2  # 未命中 2 次

    def test_cache_clear(self):
        """测试缓存清除"""
        call_count = [0]

        @cached_result(maxsize=128)
        def func(x):
            call_count[0] += 1
            return x * 2

        func(1)
        func(2)
        assert call_count[0] == 2

        # 清除缓存
        func.cache_clear()

        # 再次调用应该重新计算
        func(1)
        assert call_count[0] == 3

    def test_cache_performance(self):
        """测试缓存性能提升"""
        import time

        @cached_result(maxsize=128)
        def slow_function(n):
            """模拟慢函数"""
            time.sleep(0.01)  # 模拟耗时操作
            return sum(range(n))

        # 第一次调用（慢）
        start = time.perf_counter()
        result1 = slow_function(1000)
        time1 = time.perf_counter() - start

        # 第二次调用（快，从缓存读取）
        start = time.perf_counter()
        result2 = slow_function(1000)
        time2 = time.perf_counter() - start

        assert result1 == result2
        assert time1 >= 0.01  # 第一次应该 >= 10ms
        assert time2 < 0.001   # 第二次应该 < 1ms


class TestCacheInWeighting:
    """测试在权重计算中的应用"""

    def test_entropy_weight_caching(self):
        """测试熵权法缓存"""
        from models import DecisionProblem, Criterion, AlgorithmConfig
        from services.entropy_weight_service import EntropyWeightService

        # 创建测试问题
        problem = DecisionProblem(
            alternatives=("A", "B", "C"),
            criteria=(
                Criterion("C1", weight=0.5, direction="higher_better"),
                Criterion("C2", weight=0.5, direction="higher_better")
            ),
            scores={
                "A": {"C1": 80, "C2": 60},
                "B": {"C1": 70, "C2": 90},
                "C": {"C1": 90, "C2": 70}
            },
            algorithm=AlgorithmConfig(name="wsm")
        )

        service = EntropyWeightService()

        # 导入 array_ops
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "array_ops",
            mcda_core_path / "utils" / "array_ops.py"
        )
        if spec and spec.loader:
            array_ops = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(array_ops)
            scores_to_numpy = array_ops.scores_to_numpy
        else:
            raise ImportError("无法加载 array_ops")

        # 获取评分矩阵
        decision_matrix = scores_to_numpy(problem)

        # 第一次调用
        weights1 = service.calculate_weights(decision_matrix)

        # 第二次调用（相同输入，如果有缓存应该更快）
        weights2 = service.calculate_weights(decision_matrix)

        # 结果应该一致
        import numpy as np
        np.testing.assert_array_almost_equal(weights1, weights2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
