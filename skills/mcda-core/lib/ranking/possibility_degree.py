"""
MCDA Core - 可能度排序 (Possibility Degree Ranking)

基于可能度的区间排序方法，比中点法更精确，保留了区间的不确定性信息。

数学模型:
    P(A ≥ B) 表示区间 A 大于等于区间 B 的可能度

计算公式:
    P(A ≥ B) = {
        1,                              if A^L ≥ B^U
        0,                              if A^U ≤ B^L
        (A^U - B^L) / ((A^U - A^L) + (B^U - B^L)),  otherwise
    }
"""

from dataclasses import dataclass
from mcda_core.interval import Interval


@dataclass
class PossibilityDegree:
    """可能度排序工具类

    提供基于可能度的区间排序方法，用于比较和排序多个区间数。

    Example:
        ```python
        # 创建区间
        a = Interval(2.0, 5.0)
        b = Interval(3.0, 6.0)

        # 计算可能度
        pd = PossibilityDegree()
        prob = pd.calculate(a, b)  # P(a ≥ b)

        # 排序多个区间
        intervals = {
            "A": Interval(2.0, 5.0),
            "B": Interval(3.0, 6.0),
            "C": Interval(1.0, 4.0)
        }
        rankings = pd.rank(intervals)
        ```
    """

    @staticmethod
    def calculate(a: Interval, b: Interval) -> float:
        """计算 P(a ≥ b) - 区间 a 大于等于区间 b 的可能度

        Args:
            a: 区间 a
            b: 区间 b

        Returns:
            可能度值，范围 [0, 1]
            - 1.0: a 完全大于等于 b
            - 0.0: a 完全小于 b
            - 0.5: a 和 b 相等（重合）
            - (0, 0.5): a 可能小于 b
            - (0.5, 1.0): a 可能大于 b

        Example:
            ```python
            a = Interval(2.0, 5.0)
            b = Interval(3.0, 6.0)
            pd = PossibilityDegree()
            prob = pd.calculate(a, b)  # 0.25 (a 有 25% 可能 ≥ b)
            ```

        数学公式:
            P(a ≥ b) = {
                1,                              if a.lower ≥ b.upper
                0,                              if a.upper ≤ b.lower
                0.5,                            if a = b (完全相等)
                (a.upper - b.lower) / ((a.upper - a.lower) + (b.upper - b.lower)),  otherwise
            }
        """
        # 特殊情况: 两个区间完全相等（包括零宽度区间）
        if a.lower == b.lower and a.upper == b.upper:
            return 0.5

        # 情况1: a 完全大于等于 b
        if a.lower >= b.upper:
            return 1.0

        # 情况2: a 完全小于 b
        if a.upper <= b.lower:
            return 0.0

        # 情况3: a 和 b 有重叠
        # 使用可能度公式
        numerator = a.upper - b.lower
        denominator = a.width + b.width

        # 避免除零（理论上不会发生，因为有重叠）
        if denominator == 0:
            return 0.5

        return numerator / denominator

    def rank(
        self,
        intervals: dict[str, Interval]
    ) -> list[tuple[str, float]]:
        """对多个区间进行排序

        使用综合可能度方法：计算每个区间相对于其他所有区间的
        综合可能度，然后按综合可能度降序排序。

        Args:
            intervals: 区间字典，key 为名称，value 为区间

        Returns:
            排序结果，列表中每个元素为 (名称, 综合可能度) 元组
            按综合可能度降序排列

        Example:
            ```python
            intervals = {
                "A": Interval(2.0, 5.0),
                "B": Interval(3.0, 6.0),
                "C": Interval(1.0, 4.0)
            }
            pd = PossibilityDegree()
            rankings = pd.rank(intervals)
            # [("B", 1.5), ("A", 1.0), ("C", 0.5)]
            ```

        算法步骤:
            1. 计算两两可能度矩阵 P = [P(Ai ≥ Aj)]
            2. 计算综合可能度: Si = Σ P(Ai ≥ Aj)
            3. 按 Si 降序排序
        """
        if not intervals:
            return []

        # 初始化综合可能度
        scores = {name: 0.0 for name in intervals}

        # 计算两两可能度
        for name_i, interval_i in intervals.items():
            for name_j, interval_j in intervals.items():
                if name_i != name_j:
                    # 累加 P(Ai ≥ Aj)
                    scores[name_i] += self.calculate(interval_i, interval_j)

        # 按综合可能度降序排序
        rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return rankings

    def compare(self, a: Interval, b: Interval) -> str:
        """比较两个区间的大小关系

        Args:
            a: 区间 a
            b: 区间 b

        Returns:
            比较结果:
            - "a > b": a 大于 b
            - "a < b": a 小于 b
            - "a = b": a 等于 b
            - "a ≈ b": a 和 b 有重叠，难以确定

        Example:
            ```python
            a = Interval(2.0, 5.0)
            b = Interval(6.0, 8.0)
            pd = PossibilityDegree()
            result = pd.compare(a, b)  # "a < b"
            ```
        """
        prob_a_ge_b = self.calculate(a, b)
        prob_b_ge_a = self.calculate(b, a)

        if prob_a_ge_b == 1.0:
            return "a > b"
        elif prob_b_ge_a == 1.0:
            return "a < b"
        elif prob_a_ge_b == 0.5 and prob_b_ge_a == 0.5:
            return "a = b"
        else:
            return "a ≈ b"
