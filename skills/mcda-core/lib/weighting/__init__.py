"""
赋权方法包

包含各种赋权方法的实现。
"""

from .critic_weighting import (
    critic_weighting,
    CRITICWeightingError
)

__all__ = [
    "critic_weighting",
    "CRITICWeightingError",
]
