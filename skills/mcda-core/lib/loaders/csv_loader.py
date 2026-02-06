"""
CSV 配置文件加载器

支持从 CSV 文件加载决策数据，包括区间数格式。

CSV 格式约定：
- 第一行：备选方案名称（逗号分隔）
- 后续行：准则数据
- 列结构：[准则名称, 权重, 方向, 方案1得分, 方案2得分, ...]

示例：
```csv
方案A,方案B,方案C
性能,0.4,higher,85,90,88
成本,0.3,lower,50,60,55
```

区间数支持两种格式：
- 逗号分隔：80,90
- 方括号格式：[80,90]
"""

import csv
from pathlib import Path
from typing import Any, Union

from . import ConfigLoader


class CSVLoader(ConfigLoader):
    """CSV 配置文件加载器"""

    # 方向别名映射
    DIRECTION_ALIASES = {
        'higher': 'higher',
        'h': 'higher',
        'higher_is_better': 'higher',
        'lower': 'lower',
        'l': 'lower',
        'lower_is_better': 'lower',
    }

    def __init__(self):
        """初始化 CSV Loader"""
        super().__init__()
        self.alternatives: list[str] = []
        self.criteria: list[dict[str, Any]] = []
        self.matrix: list[list[Any]] = []

    def load(self, source: Union[str, Path]) -> dict[str, Any]:
        """
        加载 CSV 配置文件

        Args:
            source: CSV 文件路径

        Returns:
            解析后的配置字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式错误
        """
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"CSV 文件不存在: {source}")

        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'utf-8-sig']
        content = None
        used_encoding = None

        for encoding in encodings:
            try:
                with open(source_path, 'r', encoding=encoding, newline='') as f:
                    content = list(csv.reader(f))
                    used_encoding = encoding
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError(
                f"无法读取 CSV 文件，请确保文件编码为 UTF-8 或 GBK: {source}"
            )

        # 验证基本格式
        if len(content) < 2:
            raise ValueError(
                f"CSV 文件格式错误：至少需要 2 行数据（方案名称行 + 至少 1 个准则行）"
            )

        # 解析备选方案
        self.alternatives = content[0]
        if not self.alternatives:
            raise ValueError("CSV 文件格式错误：第一行必须包含备选方案名称")

        # 解析准则数据
        self.criteria = []
        self.matrix = []

        for row_idx, row in enumerate(content[1:], start=2):
            if len(row) < 4:
                raise ValueError(
                    f"CSV 文件格式错误：第 {row_idx} 行数据不完整，"
                    f"期望至少 4 列（准则名称, 权重, 方向, 得分），实际 {len(row)} 列"
                )

            criterion_name = row[0]
            weight_str = row[1]
            direction_str = row[2].lower()
            scores = row[3:]

            # 验证权重
            try:
                weight = float(weight_str)
                if weight < 0:
                    raise ValueError(f"权重不能为负数: {weight}")
            except ValueError as e:
                raise ValueError(
                    f"CSV 文件格式错误：第 {row_idx} 行权重值无效 '{weight_str}'"
                ) from e

            # 解析方向
            if direction_str not in self.DIRECTION_ALIASES:
                raise ValueError(
                    f"CSV 文件格式错误：第 {row_idx} 行方向值无效 '{row[2]}'，"
                    f"支持的值：higher, lower (或 h, l)"
                )
            direction = self.DIRECTION_ALIASES[direction_str]

            # 验证得分数量
            if len(scores) != len(self.alternatives):
                raise ValueError(
                    f"CSV 文件格式错误：第 {row_idx} 行得分数量与备选方案数量不匹配，"
                    f"期望 {len(self.alternatives)} 个得分，实际 {len(scores)} 个"
                )

            # 解析得分（支持区间数）
            parsed_scores = []
            for alt_idx, score in enumerate(scores, start=1):
                try:
                    parsed_score = self._parse_score(score, row_idx, alt_idx)
                    parsed_scores.append(parsed_score)
                except ValueError as e:
                    raise ValueError(
                        f"CSV 文件格式错误：第 {row_idx} 行第 {alt_idx} 个得分值无效 '{score}'"
                    ) from e

            # 添加到结果
            self.criteria.append({
                'name': criterion_name,
                'weight': weight,
                'direction': direction,
            })
            self.matrix.append(parsed_scores)

        # 构建配置字典
        config = {
            'alternatives': self.alternatives,
            'criteria': self.criteria,
            'matrix': self.matrix,
            'metadata': {
                'source': str(source_path),
                'format': 'csv',
                'encoding': used_encoding,
            }
        }

        return config

    def _parse_score(self, score_str: str, row_idx: int, col_idx: int) -> Any:
        """
        解析得分值（支持区间数）

        Args:
            score_str: 得分字符串
            row_idx: 行索引（用于错误提示）
            col_idx: 列索引（用于错误提示）

        Returns:
            解析后的得分（数值或区间数）
        """
        score_str = score_str.strip()

        # CSV 注入防护：检查危险字符（排除负号，因为负数是合法的）
        # 只检查以危险字符开头的情况（防止公式注入）
        dangerous_start_chars = {'$', '=', '+', '*', '/', '(', ')', '{', '}'}
        if score_str and score_str[0] in dangerous_start_chars:
            raise ValueError(
                f"得分值可能包含公式注入: '{score_str}'。"
                f"不允许以以下字符开头: {', '.join(sorted(dangerous_start_chars))}"
            )

        # 尝试解析为区间数
        if ',' in score_str:
            parts = score_str.split(',')
            if len(parts) != 2:
                raise ValueError(f"区间数格式错误，应为 'a,b' 或 '[a,b]'")

            lower = float(parts[0].strip().strip('[]').strip())
            upper = float(parts[1].strip().strip('[]').strip())

            # 导入 Interval 类
            from ..interval import Interval
            return Interval(lower, upper)

        # 尝试解析为单个数值
        try:
            return float(score_str)
        except ValueError as e:
            raise ValueError(
                f"无法解析得分值 '{score_str}'，"
                f"支持格式：数值（如 85）或区间数（如 80,90 或 [80,90]）"
            ) from e

    def validate(self, data: dict[str, Any]) -> bool:
        """验证 CSV 配置数据

        Args:
            data: 配置数据字典

        Returns:
            True（基本验证通过）
        """
        # 基本验证
        if not isinstance(data, dict):
            return False

        required_keys = ['alternatives', 'criteria', 'matrix']
        return all(key in data for key in required_keys)
