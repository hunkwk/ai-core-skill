"""
MCDA Core 评分规则应用器

支持从原始数据应用评分规则计算评分。
"""

from typing import Dict, Any

# 使用相对导入替代 sys.path.insert
from .. import models


class ScoringApplier:
    """评分规则应用器

    支持的评分规则类型:
    - threshold: 阈值分段评分
    - linear (MinMax): 线性评分
    """

    def apply_threshold(
        self,
        value: float,
        rule: models.ThresholdScoringRule,
        direction: models.Direction
    ) -> float:
        """应用阈值评分规则

        Args:
            value: 原始值
            rule: 阈值评分规则
            direction: 方向（higher_better 或 lower_better）

        Returns:
            评分（0-100）
        """
        # 遍历所有区间
        for range_rule in rule.ranges:
            min_val = range_rule.min
            max_val = range_rule.max

            # 判断是否在区间内
            in_range = True

            if min_val is not None and value < min_val:
                in_range = False
            if max_val is not None and value > max_val:
                in_range = False

            if in_range:
                return float(range_rule.score)

        # 没有匹配的区间，返回默认评分
        return float(rule.default_score)

    def apply_linear(
        self,
        value: float,
        rule: models.LinearScoringRule,
        direction: models.Direction
    ) -> float:
        """应用线性评分规则

        Args:
            value: 原始值
            rule: 线性评分规则
            direction: 方向（higher_better 或 lower_better）

        Returns:
            评分（0-100）
        """
        min_val, max_val = rule.min, rule.max
        scale = rule.scale

        # 限制在范围内
        clamped_value = max(min_val, min(max_val, value))

        # 线性映射
        if max_val == min_val:
            return 0.0

        if direction == "higher_better":
            # 越高越好
            score = scale * (clamped_value - min_val) / (max_val - min_val)
        else:
            # 越低越好
            score = scale * (max_val - clamped_value) / (max_val - min_val)

        return float(score)

    def apply_rule(
        self,
        value: float,
        rule: models.ScoringRule,
        direction: models.Direction
    ) -> float:
        """应用评分规则（统一入口）

        Args:
            value: 原始值
            rule: 评分规则（LinearScoringRule 或 ThresholdScoringRule）
            direction: 方向

        Returns:
            评分（0-100）
        """
        if rule.type == "linear":
            return self.apply_linear(value, rule, direction)
        elif rule.type == "threshold":
            return self.apply_threshold(value, rule, direction)
        else:
            raise ValueError(f"不支持的评分规则类型: {rule.type}")

    def calculate_scores(
        self,
        raw_data: Dict[str, Dict[str, float]],
        criteria: tuple[models.Criterion, ...]
    ) -> Dict[str, Dict[str, float]]:
        """批量计算评分

        Args:
            raw_data: 原始数据 {alternative: {column: value}}
            criteria: 准则列表

        Returns:
            评分矩阵 {alternative: {criterion: score}}

        Raises:
            ValueError: 缺少数据列或评分规则应用失败
        """
        scores = {}

        for alt_name, alt_data in raw_data.items():
            alt_scores = {}

            for criterion in criteria:
                # 获取列名
                column_name = criterion.column or criterion.name

                # 获取原始值
                if column_name not in alt_data:
                    raise ValueError(
                        f"备选方案 '{alt_name}' 缺少数据列 '{column_name}'"
                    )

                raw_value = alt_data[column_name]

                # 应用评分规则
                if criterion.scoring_rule:
                    score = self.apply_rule(
                        raw_value,
                        criterion.scoring_rule,
                        criterion.direction
                    )
                else:
                    # 没有评分规则，直接使用原始值
                    score = float(raw_value)

                alt_scores[criterion.name] = score

            scores[alt_name] = alt_scores

        return scores
