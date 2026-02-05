"""
NumPy 数组操作单元测试
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# 添加路径
project_root = Path(__file__).parent.parent.parent.parent.parent  # 回到项目根目录
mcda_core_path = project_root / "skills" / "mcda-core" / "lib"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

# 直接导入 array_ops，避免 utils.__init__.py 的导入问题
import importlib.util
spec = importlib.util.spec_from_file_location(
    "array_ops",
    mcda_core_path / "utils" / "array_ops.py"
)
if spec and spec.loader:
    array_ops = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(array_ops)

    scores_to_numpy = array_ops.scores_to_numpy
    normalize_vector = array_ops.normalize_vector
    compute_distance_matrix = array_ops.compute_distance_matrix
else:
    raise ImportError("无法加载 array_ops 模块")


class TestScoresToNumpy:
    """测试评分矩阵转 NumPy 数组"""

    def test_basic_conversion(self):
        """测试基本转换功能"""
        # 创建测试数据
        from models import DecisionProblem, Criterion, AlgorithmConfig

        problem = DecisionProblem(
            alternatives=("方案A", "方案B"),
            criteria=(
                Criterion("准则1", weight=0.5, direction="higher_better"),
                Criterion("准则2", weight=0.5, direction="higher_better")
            ),
            scores={
                "方案A": {"准则1": 80, "准则2": 60},
                "方案B": {"准则1": 70, "准则2": 90}
            },
            algorithm=AlgorithmConfig(name="wsm")
        )

        # 转换为 NumPy 数组
        matrix = scores_to_numpy(problem)

        # 验证形状
        assert matrix.shape == (2, 2)  # 2 方案 × 2 准则

        # 验证数据类型
        assert matrix.dtype == np.float64

        # 验证数据正确性
        assert matrix[0, 0] == 80  # 方案A, 准则1
        assert matrix[0, 1] == 60  # 方案A, 准则2
        assert matrix[1, 0] == 70  # 方案B, 准则1
        assert matrix[1, 1] == 90  # 方案B, 准则2

    def test_large_scale_conversion(self):
        """测试大规模数据转换"""
        from models import DecisionProblem, Criterion, AlgorithmConfig

        # 创建大规模问题
        alternatives = tuple(f"方案{i:03d}" for i in range(100))
        criteria = tuple(
            Criterion(f"准则{i:02d}", weight=0.02, direction="higher_better")
            for i in range(50)
        )

        # 生成随机评分
        import random
        random.seed(42)
        scores = {}
        for alt in alternatives:
            scores[alt] = {
                crit.name: random.randint(1, 100)
                for crit in criteria
            }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores,
            algorithm=AlgorithmConfig(name="wsm")
        )

        # 转换为 NumPy 数组
        matrix = scores_to_numpy(problem)

        # 验证形状
        assert matrix.shape == (100, 50)  # 100 方案 × 50 准则

        # 验证数据完整性
        assert not np.isnan(matrix).any()
        assert not np.isinf(matrix).any()


class TestNormalizeVector:
    """测试向量标准化"""

    def test_normalize_basic(self):
        """测试基本标准化"""
        vector = np.array([3.0, 4.0])

        result = normalize_vector(vector)

        expected = np.array([0.6, 0.8])
        np.testing.assert_array_almost_equal(result, expected, decimal=5)

    def test_normalize_zero_vector(self):
        """测试零向量"""
        vector = np.array([0.0, 0.0, 0.0])

        result = normalize_vector(vector)

        np.testing.assert_array_equal(result, vector)

    def test_normalize_large_vector(self):
        """测试大规模向量"""
        vector = np.random.rand(1000)

        result = normalize_vector(vector)

        # 验证归一化后范数为 1
        norm = np.linalg.norm(result)
        assert abs(norm - 1.0) < 1e-10


class TestComputeDistanceMatrix:
    """测试距离矩阵计算"""

    def test_euclidean_distance(self):
        """测试欧氏距离矩阵"""
        # 创建简单测试数据
        matrix = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ])

        distances = compute_distance_matrix(matrix, metric='euclidean')

        # 验证形状
        assert distances.shape == (3, 3)

        # 验证对角线为 0（到自身的距离）
        np.testing.assert_array_almost_equal(np.diag(distances), np.zeros(3))

    def test_manhattan_distance(self):
        """测试曼哈顿距离矩阵"""
        matrix = np.array([
            [1.0, 2.0],
            [3.0, 4.0],
            [5.0, 6.0]
        ])

        distances = compute_distance_matrix(matrix, metric='manhattan')

        # 验证形状
        assert distances.shape == (3, 3)

        # 验证对称性
        np.testing.assert_array_almost_equal(distances, distances.T)


class TestPerformance:
    """性能测试"""

    def test_conversion_performance(self):
        """测试转换性能"""
        import time
        from models import DecisionProblem, Criterion, AlgorithmConfig

        # 创建大规模问题
        alternatives = tuple(f"方案{i:03d}" for i in range(1000))
        criteria = tuple(
            Criterion(f"准则{i:02d}", weight=0.01, direction="higher_better")
            for i in range(100)
        )

        # 生成随机评分
        import random
        random.seed(42)
        scores = {}
        for alt in alternatives:
            scores[alt] = {
                crit.name: random.randint(1, 100)
                for crit in criteria
            }

        problem = DecisionProblem(
            alternatives=alternatives,
            criteria=criteria,
            scores=scores,
            algorithm=AlgorithmConfig(name="wsm")
        )

        # 测试转换性能
        start_time = time.perf_counter()
        result = scores_to_numpy(problem)
        end_time = time.perf_counter()

        # 验证结果正确性
        assert result.shape == (1000, 100)

        # 验证性能（应该在 0.1 秒内完成）
        conversion_time = end_time - start_time
        assert conversion_time < 0.1, f"转换时间 {conversion_time:.3f}s 超过 0.1s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
