"""
MCDA Core 约束系统模块

实现一票否决机制（Veto Mechanism），支持：
- hard: 硬否决（直接排除）
- soft: 软否决（扣分惩罚）
- tiered: 分级否决（多档位管理）
- composite: 组合否决（AND/OR 逻辑）
"""

from mcda_core.constraints.models import (
    VetoCondition,
    VetoConfig,
    VetoTier,
    VetoResult,
    ConstraintMetadata,
)

__all__ = [
    "VetoCondition",
    "VetoConfig",
    "VetoTier",
    "VetoResult",
    "ConstraintMetadata",
]
