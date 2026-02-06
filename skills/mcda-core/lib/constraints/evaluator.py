"""
VetoEvaluator: 一票否决评估器

实现一票否决机制的核心评估逻辑：
- 硬否决（hard）
- 软否决（soft）
- 分级否决（tiered）
- 组合否决（composite）
"""

from typing import Any

from mcda_core.constraints.models import (
    VetoCondition,
    VetoConfig,
    VetoTier,
    VetoResult,
)


class VetoEvaluator:
    """
    一票否决评估器

    评估方案是否满足否决条件，返回评估结果

    Examples:
        >>> evaluator = VetoEvaluator()
        >>> result = evaluator.evaluate(alternative, problem)
        >>> if result.rejected:
        ...     print(f"方案被拒绝: {result.reject_reasons}")
    """

    def evaluate(
        self,
        alternative_id: str,
        scores: dict[str, float],
        criteria: list[Any]  # list of Criterion
    ) -> VetoResult:
        """
        评估单个方案

        Args:
            alternative_id: 方案 ID
            scores: 方案评分字典 {criterion_name: score}
            criteria: 准则列表

        Returns:
            VetoResult: 评估结果
        """
        reject_reasons = []
        warnings = []
        penalties = {}

        for criterion in criteria:
            # 检查是否有否决配置
            if not hasattr(criterion, 'veto') or criterion.veto is None:
                continue

            score = scores.get(criterion.name)
            if score is None:
                continue

            # 根据否决类型评估
            veto_result = self._evaluate_criterion(
                criterion.name,
                score,
                criterion.veto,
                criterion.direction if hasattr(criterion, 'direction') else 'higher_better'
            )

            if veto_result['rejected']:
                reject_reasons.append(veto_result['reason'])

            if veto_result['warning']:
                warnings.append(veto_result['warning'])

            if veto_result['penalty'] != 0:
                penalties[criterion.name] = veto_result['penalty']

        # 判断是否被拒绝
        rejected = len(reject_reasons) > 0

        return VetoResult(
            alternative_id=alternative_id,
            rejected=rejected,
            reject_reasons=reject_reasons,
            warnings=warnings,
            penalties=penalties,
        )

    def _evaluate_criterion(
        self,
        criterion_name: str,
        score: float,
        veto_config: VetoConfig,
        direction: str
    ) -> dict:
        """
        评估单个准则的否决条件

        Returns:
            dict: {
                'rejected': bool,
                'reason': str | None,
                'warning': str | None,
                'penalty': float
            }
        """
        if veto_config.type == 'hard':
            return self._evaluate_hard(criterion_name, score, veto_config)
        elif veto_config.type == 'soft':
            return self._evaluate_soft(criterion_name, score, veto_config)
        elif veto_config.type == 'tiered':
            return self._evaluate_tiered(criterion_name, score, veto_config)
        elif veto_config.type == 'composite':
            return self._evaluate_composite(criterion_name, score, veto_config)
        else:
            return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

    def _evaluate_hard(
        self,
        criterion_name: str,
        score: float,
        veto_config: VetoConfig
    ) -> dict:
        """评估硬否决

        硬否决逻辑：
        - 如果条件是 operator=">=", value=60, action="reject"
        - 含义：score >= 60 时通过，score < 60 时拒绝
        - 即：如果不满足条件，则拒绝
        """
        if veto_config.condition is None:
            return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

        condition_met = self._check_condition(score, veto_config.condition)

        # 硬否决：如果不满足条件，则拒绝
        if not condition_met:
            return {
                'rejected': True,
                'reason': veto_config.reject_reason or f"{criterion_name}: 不满足硬否决条件",
                'warning': None,
                'penalty': 0
            }

        return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

    def _evaluate_soft(
        self,
        criterion_name: str,
        score: float,
        veto_config: VetoConfig
    ) -> dict:
        """评估软否决

        软否决逻辑：
        - 如果条件是 operator=">", value=60, action="warning"
        - 含义：score > 60 时触发警告，score <= 60 时通过
        - 即：如果满足条件（超过阈值），则触发警告
        """
        if veto_config.condition is None:
            return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

        condition_met = self._check_condition(score, veto_config.condition)

        # 软否决：如果满足条件（超过阈值），则触发警告
        if condition_met:
            penalty = veto_config.penalty_score
            return {
                'rejected': False,
                'reason': None,
                'warning': f"{criterion_name}: 触发软否决警告",
                'penalty': penalty
            }

        return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

    def _evaluate_tiered(
        self,
        criterion_name: str,
        score: float,
        veto_config: VetoConfig
    ) -> dict:
        """评估分级否决"""
        if not veto_config.tiers:
            return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

        # 找到匹配的档位
        for tier in veto_config.tiers:
            if tier.min <= score < tier.max:
                if tier.action == 'reject':
                    return {
                        'rejected': True,
                        'reason': f"{criterion_name}: 落入拒绝档位 [{tier.min}, {tier.max})",
                        'warning': None,
                        'penalty': 0
                    }
                elif tier.action == 'warning':
                    return {
                        'rejected': False,
                        'reason': None,
                        'warning': f"{criterion_name}: 落入警告档位 [{tier.min}, {tier.max})",
                        'penalty': tier.penalty_score
                    }
                else:  # accept
                    return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

        # 默认接受
        return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

    def _evaluate_composite(
        self,
        criterion_name: str,
        score: float,
        veto_config: VetoConfig
    ) -> dict:
        """评估组合否决"""
        if not veto_config.conditions:
            return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

        results = []
        for condition in veto_config.conditions:
            condition_met = self._check_condition(score, condition)
            results.append({
                'met': condition_met,
                'action': condition.action,
                'penalty': condition.penalty_score
            })

        # 应用逻辑
        if veto_config.logic == 'or':
            # OR 逻辑：任一条件满足即触发
            for result in results:
                if result['met']:
                    if result['action'] == 'reject':
                        return {
                            'rejected': True,
                            'reason': f"{criterion_name}: 组合否决（OR）触发拒绝",
                            'warning': None,
                            'penalty': 0
                        }
                    elif result['action'] == 'warning':
                        return {
                            'rejected': False,
                            'reason': None,
                            'warning': f"{criterion_name}: 组合否决（OR）触发警告",
                            'penalty': result['penalty']
                        }
        else:  # AND 逻辑
            # AND 逻辑：所有条件满足才触发
            all_met = all(r['met'] for r in results)
            if all_met:
                # 取最严格的动作
                has_reject = any(r['action'] == 'reject' for r in results)
                if has_reject:
                    return {
                        'rejected': True,
                        'reason': f"{criterion_name}: 组合否决（AND）触发拒绝",
                        'warning': None,
                        'penalty': 0
                    }
                else:
                    total_penalty = sum(r['penalty'] for r in results)
                    return {
                        'rejected': False,
                        'reason': None,
                        'warning': f"{criterion_name}: 组合否决（AND）触发警告",
                        'penalty': total_penalty
                    }

        return {'rejected': False, 'reason': None, 'warning': None, 'penalty': 0}

    def _check_condition(self, score: float, condition: VetoCondition) -> bool:
        """
        检查条件是否满足

        Args:
            score: 实际评分
            condition: 否决条件

        Returns:
            bool: 条件是否满足
        """
        operator = condition.operator
        value = condition.value

        if operator == '==':
            return score == value
        elif operator == '!=':
            return score != value
        elif operator == '>':
            return score > value
        elif operator == '>=':
            return score >= value
        elif operator == '<':
            return score < value
        elif operator == '<=':
            return score <= value
        elif operator == 'in':
            return score in value if isinstance(value, (list, tuple)) else False
        elif operator == 'not_in':
            return score not in value if isinstance(value, (list, tuple)) else True
        else:
            return False
