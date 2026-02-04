"""
Logarithmic 标准化方法

实现对数标准化，适用于比率型数据。
"""

from typing import Union
import numpy as np
from numpy.typing import NDArray


class LogarithmicNormalizerError(Exception):
    """Logarithmic 标准化错误"""
    pass


class LogarithmicNormalizer:
    """对数标准化器"""

    def __init__(self, offset: float = 1.0):
        """
        初始化对数标准化器

        Args:
            offset: 零值偏移量（默认 1.0），用于处理零值
        """
        self.offset = offset

    def normalize(
        self,
        data: Union[NDArray, list],
        maximize: bool = True
    ) -> NDArray:
        """
        对数标准化

        数学模型:
        - 效益型: x'_ij = log(x_ij + offset) / log(max(x_j) + offset)
        - 成本型: x'_ij = log(max(x_j) + offset) / log(x_ij + offset)

        Args:
            data: 待标准化数据（numpy array 或 list）
            maximize: True=效益型（越大越好），False=成本型（越小越好）

        Returns:
            标准化后的数据 (NDArray)

        Raises:
            LogarithmicNormalizerError: 如果数据无效
        """
        # 输入验证和转换
        data = self._validate_and_convert_input(data)

        # 应用偏移并计算
        data_offset = data + self.offset
        max_val = np.max(data_offset)

        # 根据类型标准化
        if maximize:
            # 效益型: log(x) / log(max)
            return np.log(data_offset) / np.log(max_val)
        else:
            # 成本型: log(max) / log(x)
            return np.log(max_val) / np.log(data_offset)

    def _validate_and_convert_input(self, data: Union[NDArray, list]) -> NDArray:
        """
        验证并转换输入数据

        Args:
            data: 输入数据

        Returns:
            转换后的 numpy array

        Raises:
            LogarithmicNormalizerError: 如果数据无效
        """
        # None 检查
        if data is None:
            raise LogarithmicNormalizerError("数据不能为 None")

        # 转换为 numpy array
        if not isinstance(data, np.ndarray):
            try:
                data = np.array(data, dtype=float)
            except (ValueError, TypeError) as e:
                raise LogarithmicNormalizerError(f"无法转换数据类型: {type(data)}") from e

        # 空数组检查
        if len(data) == 0:
            raise LogarithmicNormalizerError("数据不能为空")

        # NaN 检查
        if np.any(np.isnan(data)):
            raise LogarithmicNormalizerError("数据包含 NaN")

        # 负值检查
        if np.any(data < 0):
            raise LogarithmicNormalizerError(
                f"对数标准化不支持负值，最小值: {np.min(data)}"
            )

        # 全零检查
        if np.all(data == 0):
            raise LogarithmicNormalizerError("全零数据无法标准化")

        return data


# 默认实例
_default_normalizer = LogarithmicNormalizer()


def logarithmic_normalize(
    data: Union[NDArray, list],
    maximize: bool = True,
    offset: float = 1.0
) -> NDArray:
    """
    对数标准化（便捷函数）

    Args:
        data: 待标准化数据
        maximize: True=效益型，False=成本型
        offset: 零值偏移量

    Returns:
        标准化后的数据
    """
    normalizer = LogarithmicNormalizer(offset=offset)
    return normalizer.normalize(data, maximize=maximize)
