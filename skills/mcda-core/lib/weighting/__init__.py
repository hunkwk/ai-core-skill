"""
赋权方法包

包含各种赋权方法的实现。
"""

from .critic_weighting import (
    critic_weighting,
    CRITICWeightingError
)
from .cv_weighting import (
    cv_weighting,
    CVWeightingError
)
from .game_theory_weighting import (
    GameTheoryWeighting,
    GameTheoryWeightingError
)

__all__ = [
    "critic_weighting",
    "CRITICWeightingError",
    "cv_weighting",
    "CVWeightingError",
    "GameTheoryWeighting",
    "GameTheoryWeightingError",
]
