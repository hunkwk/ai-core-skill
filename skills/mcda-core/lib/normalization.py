"""
MCDA Core - 标准化服务

提供 MinMax 和 Vector 标准化算法。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal, TYPE_CHECKING
import math

# 导入类型定义（避免重复）
from .models import Direction, MIN_NORMALIZED, MAX_NORMALIZED

# 类型注解导入（避免循环导入）
if TYPE_CHECKING:
    from .models import NormalizationConfig


# =============================================================================
# 类型别名
# =============================================================================

# Direction 已从 models.py 导入，避免重复定义


# =============================================================================
# 标准化结果
# =============================================================================

@dataclass(frozen=True)
class NormalizationResult:
    """标准化结果

    Attributes:
        normalized_scores: 标准化后的评分
        metadata: 元数据（方法、参数等）
    """
    normalized_scores: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 标准化方法抽象基类
# =============================================================================

class NormalizationMethod(ABC):
    """标准化方法抽象基类"""

    @abstractmethod
    def normalize(
        self,
        values: dict[str, float],
        direction: Direction = "higher_better"
    ) -> NormalizationResult:
        """标准化一组数值到 [0, 1]"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """方法名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """方法描述"""
        pass

    def validate_input(self, values: dict[str, float]) -> None:
        """验证输入数据"""
        if not values:
            raise ValueError("输入值不能为空")
        if len(values) < 2:
            raise ValueError("至少需要 2 个备选方案")


# =============================================================================
# 标准化方法注册表
# =============================================================================

_normalization_methods: dict[str, type[NormalizationMethod]] = {}


def register_normalization_method(name: str):
    """标准化方法注册装饰器

    Args:
        name: 方法名称

    Returns:
        装饰器函数
    """
    def decorator(cls: type[NormalizationMethod]) -> type[NormalizationMethod]:
        _normalization_methods[name] = cls
        return cls
    return decorator


def get_normalization_method(name: str) -> NormalizationMethod:
    """获取标准化方法实例

    Args:
        name: 方法名称

    Returns:
        标准化方法实例

    Raises:
        ValueError: 未知的标准化方法
    """
    if name not in _normalization_methods:
        available = ", ".join(_normalization_methods.keys())
        raise ValueError(f"未知的标准化方法: '{name}'. 可用: {available}")
    return _normalization_methods[name]()


# =============================================================================
# MinMax 标准化
# =============================================================================

@register_normalization_method("minmax")
class MinMaxNormalization(NormalizationMethod):
    """Min-Max 标准化

    公式: (x - min) / (max - min)
    适用: 连续数值，边界已知
    """

    @property
    def name(self) -> str:
        return "minmax"

    @property
    def description(self) -> str:
        return "线性映射到 [0, 1] 区间"

    def normalize(
        self,
        values: dict[str, float],
        direction: Direction = "higher_better"
    ) -> NormalizationResult:
        """MinMax 标准化"""
        self.validate_input(values)

        vals = list(values.values())
        min_val = min(vals)
        max_val = max(vals)

        # 处理常数情况
        if max_val == min_val:
            return NormalizationResult(
                normalized_scores={k: 1.0 for k in values.keys()},
                metadata={"min": min_val, "max": max_val, "note": "constant"}
            )

        range_val = max_val - min_val
        normalized = {}

        for key, value in values.items():
            if direction == "higher_better":
                norm = (value - min_val) / range_val
            else:
                norm = (max_val - value) / range_val
            # 裁剪到 [0, 1]
            normalized[key] = max(MIN_NORMALIZED, min(MAX_NORMALIZED, norm))

        return NormalizationResult(
            normalized_scores=normalized,
            metadata={
                "method": self.name,
                "direction": direction,
                "min": min_val,
                "max": max_val
            }
        )


# =============================================================================
# Vector 标准化
# =============================================================================

@register_normalization_method("vector")
class VectorNormalization(NormalizationMethod):
    """向量归一化（TOPSIS 标准）

    公式: x / sqrt(Σx²)
    适用: TOPSIS 等距离敏感算法
    """

    @property
    def name(self) -> str:
        return "vector"

    @property
    def description(self) -> str:
        return "向量归一化（欧几里得范数）"

    def normalize(
        self,
        values: dict[str, float],
        direction: Direction = "higher_better"
    ) -> NormalizationResult:
        """Vector 标准化"""
        self.validate_input(values)

        vals = list(values.values())
        norm = math.sqrt(sum(v ** 2 for v in vals))

        # 处理零向量
        if norm == 0:
            return NormalizationResult(
                normalized_scores={k: 0.0 for k in values.keys()},
                metadata={"note": "zero_norm"}
            )

        normalized = {
            k: v / norm
            for k, v in values.items()
        }

        # 注意：Vector 标准化通常不反转方向
        # 如需反转，建议在调用方处理

        return NormalizationResult(
            normalized_scores=normalized,
            metadata={"method": self.name, "norm": norm}
        )


# =============================================================================
# 标准化服务
# =============================================================================

class NormalizationService:
    """标准化服务

    提供统一的标准化接口。
    """

    def normalize(
        self,
        values: dict[str, float],
        config: "NormalizationConfig"
    ) -> NormalizationResult:
        """根据配置执行标准化

        Args:
            values: 待标准化的值
            config: 标准化配置

        Returns:
            标准化结果
        """
        method = get_normalization_method(config.type)
        return method.normalize(values, config.direction)

    def normalize_batch(
        self,
        data: dict[str, dict[str, float]],
        configs: dict[str, "NormalizationConfig"]
    ) -> dict[str, dict[str, float]]:
        """批量标准化（多准则）

        Args:
            data: 待标准化数据 {criterion: {alternative: value}}
            configs: 标准化配置 {criterion: NormalizationConfig}

        Returns:
            标准化后的数据
        """
        # 运行时导入（避免循环导入）
        from .models import NormalizationConfig

        result = {}
        for criterion, values in data.items():
            config = configs.get(criterion)
            if config is None:
                # 默认使用 MinMax
                config = NormalizationConfig(type="minmax", direction="higher_better")

            norm_result = self.normalize(values, config)
            result[criterion] = norm_result.normalized_scores
        return result


# =============================================================================
# 导出公共 API
# =============================================================================

__all__ = [
    # 类型
    "Direction",
    "NormalizationResult",
    # 基类
    "NormalizationMethod",
    # 注册
    "register_normalization_method",
    "get_normalization_method",
    # 方法
    "MinMaxNormalization",
    "VectorNormalization",
    # 服务
    "NormalizationService",
]
