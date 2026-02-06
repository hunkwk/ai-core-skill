# MCDA-Core 代码修复建议

本文档提供针对代码审查中发现问题的具体修复方案。

---

## 🔴 Critical Issues 修复方案

### 1. 修复 `lib/scoring/applier.py` 的导入问题

**当前代码** (第 9-13 行):
```python
import sys
from pathlib import Path
# 添加父目录到路径以导入 models
sys.path.insert(0, str(Path(__file__).parent.parent))
import models
```

**修复后代码**:
```python
# 删除 sys.path.insert 相关代码，使用相对导入
from .. import models
```

**完整修复**:
```python
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
    # ... 其余代码保持不变
```

---

### 2. 修复 `lib/interval.py` 的 `__eq__` 方法

**当前代码** (第 193-206 行):
```python
def __eq__(self, other: object) -> bool:
    """区间相等比较

    基于中点比较。

    Args:
        other: 另一个区间

    Returns:
        如果中点相等返回 True，否则返回 False
    """
    if not isinstance(other, Interval):
        return NotImplemented
    return self.midpoint == other.midpoint
```

**修复后代码**:
```python
def __eq__(self, other: object) -> bool:
    """区间相等比较

    基于区间端点比较。两个区间相等当且仅当
    它们的下界和上界都相等。

    Args:
        other: 另一个区间

    Returns:
        如果区间端点相等返回 True，否则返回 False
    """
    if not isinstance(other, Interval):
        return NotImplemented
    return self.lower == other.lower and self.upper == other.upper
```

**同时建议添加 `__hash__` 方法** (因为定义了 `__eq__`):
```python
def __hash__(self) -> int:
    """哈希值计算"""
    return hash((self.lower, self.upper))
```

---

### 3. 修复 `lib/loaders/csv_loader.py` 的负数处理问题

**当前代码** (第 186-192 行):
```python
dangerous_chars = {'$', '=', '+', '-', '*', '/', '(', ')', '{', '}'}
if any(char in score_str for char in dangerous_chars):
    raise ValueError(
        f"得分值包含非法字符: '{score_str}'。"
        f"为防止 CSV 注入攻击，不允许使用以下字符: {', '.join(sorted(dangerous_chars))}"
    )
```

**修复后代码**:
```python
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

    # CSV 注入防护：检查危险字符（排除负数符号）
    # 注意：'-' 被排除，因为负数是合法的数值
    dangerous_chars = {'$', '=', '+', '*', '/', '(', ')', '{', '}'}
    
    # 对于可能的公式注入，检查是否以危险字符开头
    if score_str and score_str[0] in dangerous_chars:
        raise ValueError(
            f"得分值可能包含公式注入: '{score_str}'。"
            f"不允许以以下字符开头: {', '.join(sorted(dangerous_chars))}"
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
            f"支持格式：数值（如 85 或 -10）或区间数（如 80,90 或 [80,90]）"
        ) from e
```

---

## 🟠 High Risk Issues 修复方案

### 4. 修复 `lib/core.py` 的代码重复问题

**提取公共方法**:

在 `MCDAOrchestrator` 类中添加：

```python
def _build_problem_from_data(
    self,
    data: dict[str, Any],
    auto_normalize_weights: bool
) -> DecisionProblem:
    """从解析后的数据构建决策问题

    Args:
        data: 解析后的配置数据
        auto_normalize_weights: 是否自动归一化权重

    Returns:
        决策问题对象
    """
    alternatives = self._parse_alternatives(data)
    criteria = self._parse_criteria(data, auto_normalize_weights)
    scores = self._parse_scores(data, alternatives, criteria)
    algorithm_config = self._parse_algorithm_config(data)

    try:
        problem = DecisionProblem(
            alternatives=tuple(alternatives),
            criteria=tuple(criteria),
            scores=scores,
            algorithm=algorithm_config
        )
    except Exception as e:
        raise MCDAValidationError(
            f"创建决策问题失败: {str(e)}",
            details={"error": str(e)}
        ) from e

    return problem
```

**然后简化三个加载方法**:

```python
def load_from_yaml(
    self,
    file_path: Path | str,
    auto_normalize_weights: bool = True
) -> DecisionProblem:
    """从 YAML 文件加载决策问题"""
    data = load_yaml(file_path)
    return self._build_problem_from_data(data, auto_normalize_weights)

def load_from_json(
    self,
    file_path: Path | str,
    auto_normalize_weights: bool = True
) -> DecisionProblem:
    """从 JSON 文件加载决策问题"""
    loader = JSONLoader()
    data = loader.load(file_path)
    return self._build_problem_from_data(data, auto_normalize_weights)

def load_from_file(
    self,
    file_path: Path | str,
    auto_normalize_weights: bool = True
) -> DecisionProblem:
    """自动检测格式并加载配置文件"""
    loader = LoaderFactory.get_loader(file_path)
    data = loader.load(file_path)
    return self._build_problem_from_data(data, auto_normalize_weights)
```

---

### 5. 修复 `lib/interval.py` 的浮点数比较问题

**添加模块级常量**:
```python
# 模块级常量
EPSILON = 1e-9
"""浮点数比较容差"""
```

**修改 `__post_init__`**:
```python
def __post_init__(self):
    """验证区间数"""
    if self.lower > self.upper + EPSILON:
        raise IntervalError(
            f"区间下界必须小于等于上界，当前: lower={self.lower}, upper={self.upper}"
        )
    # 规范化：如果 lower 略大于 upper，调整为相等
    if self.lower > self.upper:
        object.__setattr__(self, 'upper', self.lower)
```

---

### 6. 修复 `lib/core.py` 的未使用变量

**当前代码** (第 578-584 行):
```python
# 验证所有准则都有评分
for crit_name in criterion_names:
    if crit_name not in alt_scores:
        raise MCDAValidationError(...)

    score = float(alt_scores[crit_name])  # 这行未使用

# 转换评分
scores[alt] = {crit: float(alt_scores[crit]) for crit in criterion_names}
```

**修复后代码**:
```python
# 验证所有准则都有评分并转换
alt_scores_converted = {}
for crit_name in criterion_names:
    if crit_name not in alt_scores:
        raise MCDAValidationError(
            f"备选方案 '{alt}' 在准则 '{crit_name}' 缺少评分",
            field="scores",
            alternative=alt,
            criterion=crit_name
        )
    alt_scores_converted[crit_name] = float(alt_scores[crit_name])

scores[alt] = alt_scores_converted
```

---

### 7. 统一 `lib/core.py` 的类型注解

**将第 110 行的**:
```python
def load_from_json(
    self,
    file_path: Union[str, Path],  # 旧语法
    auto_normalize_weights: bool = True
) -> DecisionProblem:
```

**改为**:
```python
def load_from_json(
    self,
    file_path: Path | str,  # 新语法
    auto_normalize_weights: bool = True
) -> DecisionProblem:
```

**同时删除第 8 行的 `Union` 导入** (如果不再使用)。

---

### 8. 修复算法基类验证重复

**在 `lib/algorithms/base.py` 中添加验证方法**:

```python
def validate_problem_size(
    self,
    n_alternatives: int,
    n_criteria: int,
    min_alternatives: int = 2,
    min_criteria: int = 1
) -> None:
    """验证问题规模

    Args:
        n_alternatives: 备选方案数量
        n_criteria: 准则数量
        min_alternatives: 最小备选方案数
        min_criteria: 最小准则数

    Raises:
        ValueError: 验证失败
    """
    if n_alternatives < min_alternatives:
        raise ValueError(
            f"至少需要 {min_alternatives} 个备选方案，当前: {n_alternatives}"
        )
    if n_criteria < min_criteria:
        raise ValueError(
            f"至少需要 {min_criteria} 个准则，当前: {n_criteria}"
        )
```

**然后在算法中使用**:
```python
# 替代重复的验证代码
self.validate_problem_size(n_alt, n_crit)
```

---

## 🟡 Medium Issues 修复方案

### 9. 修复魔法数字问题

**在 `lib/algorithms/topsis_interval.py` 顶部添加**:
```python
# 模块级常量
EPSILON = 1e-10
"""除零保护容差"""
```

**然后替换第 196-197 行**:
```python
if norm < EPSILON:
    norm = 1.0
```

---

### 10. 添加 `lib/validation.py` 的 `__all__`

**在文件末尾添加**:
```python
__all__ = [
    "ValidationResult",
    "ValidationService",
    "WEIGHT_TOLERANCE",
]
```

---

### 11. 修复 `lib/services/constraint_service.py` 的深拷贝问题

**当前代码** (第 89-122 行):
```python
def apply_penalties(self, problem: DecisionProblem) -> DecisionProblem:
    # 深拷贝问题，避免修改原问题
    adjusted_problem = deepcopy(problem)  # 这行无用
    
    # ... 创建新的评分矩阵 ...
    
    # 创建新的决策问题对象
    adjusted_problem = DecisionProblem(...)  # 重新创建
    return adjusted_problem
```

**修复后代码**:
```python
def apply_penalties(self, problem: DecisionProblem) -> DecisionProblem:
    """
    应用惩罚分数到评分
    """
    # 创建新的评分矩阵
    new_scores = {}
    for alt_id in problem.alternatives:
        scores = problem.scores.get(alt_id, {}).copy()
        if not scores:
            new_scores[alt_id] = scores
            continue

        # 评估该方案
        result = self.evaluator.evaluate(alt_id, scores, problem.criteria)

        # 如果有惩罚，添加到评分中
        if result.total_penalty != 0:
            scores["penalty"] = result.total_penalty

        new_scores[alt_id] = scores

    # 创建新的决策问题对象（直接创建，无需深拷贝）
    adjusted_problem = DecisionProblem(
        alternatives=problem.alternatives,
        criteria=problem.criteria,
        scores=new_scores,
        algorithm=problem.algorithm if hasattr(problem, 'algorithm') else None,
        data_source=problem.data_source if hasattr(problem, 'data_source') else None,
        raw_data=problem.raw_data if hasattr(problem, 'raw_data') else None,
        score_range=problem.score_range if hasattr(problem, 'score_range') else (0.0, 100.0),
    )

    return adjusted_problem
```

---

### 12. 统一异常处理

**修改 `lib/algorithms/base.py`**:

```python
from ..exceptions import ValidationError as MCDAValidationError

def validate(self, problem: "DecisionProblem") -> None:
    """验证输入数据（可选覆盖）

    Raises:
        MCDAValidationError: 数据验证失败
    """
    # 基本验证：至少有 2 个备选方案和 1 个准则
    if len(problem.alternatives) < 2:
        raise MCDAValidationError(
            f"至少需要 2 个备选方案，当前: {len(problem.alternatives)}",
            details={"actual": len(problem.alternatives), "required": 2}
        )

    if len(problem.criteria) < 1:
        raise MCDAValidationError(
            f"至少需要 1 个准则，当前: {len(problem.criteria)}",
            details={"actual": len(problem.criteria), "required": 1}
        )

    # 验证评分完整性
    for alt in problem.alternatives:
        if alt not in problem.scores:
            raise MCDAValidationError(
                f"备选方案 '{alt}' 缺少评分数据",
                details={"alternative": alt}
            )

        for crit in problem.criteria:
            if crit.name not in problem.scores[alt]:
                raise MCDAValidationError(
                    f"备选方案 '{alt}' 缺少准则 '{crit.name}' 的评分",
                    details={"alternative": alt, "criterion": crit.name}
                )
```

---

## 🟢 Low Issues 修复方案

### 13. 修复文档字符串拼写错误

**修改 `lib/algorithms/promethee2_interval.py` 第 104 行**:
```python
# 从
preference_function: 偏差函数类型（可选，覆盖构造函数的值）
# 改为
preference_function: 偏好函数类型（可选，覆盖构造函数的值）
```

---

### 14. 统一 NumPy 导入位置

**建议**: 所有算法统一在模块顶部导入 NumPy：
```python
import numpy as np
```

---

### 15. 统一排名构建逻辑

**建议**: 在 `lib/models.py` 中添加辅助方法：

```python
@classmethod
def from_scores(
    cls,
    scores: dict[str, float],
    reverse: bool = True
) -> list["RankingItem"]:
    """从得分字典构建排名列表

    Args:
        scores: 得分字典 {alternative: score}
        reverse: 是否降序排列（默认 True）

    Returns:
        排名列表
    """
    sorted_items = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=reverse
    )
    
    return [
        cls(
            rank=i,
            alternative=alt,
            score=round(score, 4)
        )
        for i, (alt, score) in enumerate(sorted_items, 1)
    ]
```

---

## 附录：快速修复清单

### 立即执行（Critical）
- [ ] 修复 `lib/scoring/applier.py` 的导入
- [ ] 修复 `lib/interval.py` 的 `__eq__` 方法
- [ ] 修复 `lib/loaders/csv_loader.py` 的负数处理

### 本周完成（High）
- [ ] 重构 `lib/core.py` 消除重复
- [ ] 添加浮点数容差处理
- [ ] 统一类型注解
- [ ] 删除未使用变量

### 本月完成（Medium/Low）
- [ ] 添加 `__all__` 定义
- [ ] 修复深拷贝问题
- [ ] 统一异常处理
- [ ] 提取公共验证逻辑
- [ ] 修复文档拼写错误

---

*文档生成时间: 2026-02-06*
