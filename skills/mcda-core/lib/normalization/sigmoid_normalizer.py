"""
Sigmoid 标准化方法

实现 Sigmoid 标准化，适用于需要平滑转换的场景。
"""

from typing import Union
import numpy as np
from numpy.typing import NDArray


class SigmoidNormalizerError(Exception):
    """Sigmoid 标准化错误"""
    pass


class SigmoidNormalizer:
    """Sigmoid 标准化器"""

    def __init__(self):
        """初始化 Sigmoid 标准化器"""
        pass

    def normalize(
        self,
        data: Union[NDArray, list],
        k: float = 2.0,
        mu: float = None,
        sigma: float = None,
        auto_stats: bool = True
    ) -> NDArray:
        """
        Sigmoid 标准化

        数学模型: x'_ij = 1 / (1 + exp(-k * (x_ij - μ) / σ))

        Args:
            data: 待标准化数据
            k: 压缩系数 (推荐 2-5)，越大曲线越陡峭
            mu: 均值 (None=自动计算)
            sigma: 标准差 (None=自动计算)
            auto_stats: 是否自动计算 μ, σ

        Returns:
            标准化后的数据 (NDArray)

        Raises:
            SigmoidNormalizerError: 如果数据无效
        """
        # 输入验证
        data = self._validate_and_convert_input(data)

        # 自动计算统计量
        if auto_stats or mu is None:
            mu = np.mean(data)
        if auto_stats or sigma is None:
            sigma = np.std(data)
            # 避免 σ=0 (所有值相同)
            if sigma < 1e-10:
                sigma = 1.0

        # Sigmoid 标准化
        # x' = 1 / (1 + exp(-k * (x - μ) / σ))
        z = k * (data - mu) / sigma
        result = 1 / (1 + np.exp(-z))

        return result

    def _validate_and_convert_input(self, data: Union[NDArray, list]) -> NDArray:
        """验证并转换输入"""
        if data is None:
            raise SigmoidNormalizerError("数据不能为 None")

        if not isinstance(data, np.ndarray):
            try:
                data = np.array(data, dtype=float)
            except (ValueError, TypeError) as e:
                raise SigmoidNormalizerError(f"无法转换数据类型: {type(data)}") from e

        if len(data) == 0:
            raise SigmoidNormalizerError("数据不能为空")

        if np.any(np.isnan(data)):
            raise SigmoidNormalizerError("数据包含 NaN")

        if np.any(np.isinf(data)):
            raise SigmoidNormalizerError("数据包含无穷值")

        return data


def sigmoid_normalize(
    data: Union[NDArray, list],
    k: float = 2.0,
    auto_stats: bool = True
) -> NDArray:
    """
    Sigmoid 标准化（便捷函数）

    Args:
        data: 待标准化数据
        k: 压缩系数
        auto_stats: 是否自动计算统计量

    Returns:
        标准化后的数据
    """
    normalizer = SigmoidNormalizer()
    return normalizer.normalize(data, k=k, auto_stats=auto_stats)
