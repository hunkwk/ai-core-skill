"""
MCDA Core - 群决策模块

提供群决策分析功能，包括多决策者评分聚合、共识度测量和德尔菲法。
"""

from .models import DecisionMaker, GroupDecisionProblem, AggregationConfig
from .service import GroupDecisionService
from .consensus import ConsensusMeasure, ConsensusResult
from .delphi import DelphiRound, DelphiProcess

__all__ = [
    "DecisionMaker",
    "GroupDecisionProblem",
    "AggregationConfig",
    "GroupDecisionService",
    "ConsensusMeasure",
    "ConsensusResult",
    "DelphiRound",
    "DelphiProcess",
]
