# ADR-002: MCDA 评分标准化方法架构设计

## 状态
**已批准**

## 日期
2026-01-31

## 上下文

### 问题陈述
MCDA Core v0.2 设计中，评分计算层需要支持多种标准化方法，将原始数据映射到统一的评分空间（0-100）。

**当前已确定的方法**:
1. **Linear** - 线性映射 (Min-Max 标准化)
2. **Inverse** - 反向线性映射
3. **Threshold** - 阶梯函数 (Step Function)

**文献研究发现的其他方法**:

| 方法 | 描述 | 公式 | 适用场景 | 引用量 |
|------|------|------|----------|--------|
| **Min-Max** | 线性缩放到 [0,1] | `(x - min) / (max - min)` | 连续数值，已知边界 | 342+ |
| **Vector** | 向量归一化 | `x / sqrt(Σx²)` | TOPSIS 等距离算法 | 200+ |
| **Z-Score** | 标准分数 | `(x - μ) / σ` | 正态分布数据 | 178+ |
| **Sum** | 总和归一化 | `x / Σx` | 比例型数据 | 150+ |
| **Max** | 最大值归一化 | `x / max(x)` | 简单缩放 | 100+ |
| **Logarithmic** | 对数变换 | `log(x) / log(max)` | 偏态分布 | 62+ |
| **Sigmoid** | S 型曲线 | `1 / (1 + exp(-k(x-x0)))` | 平滑过渡 | 31+ |

---

## 决策

### 1. 标准化方法抽象层架构

采用**策略模式 + 注册机制**：

```
评分计算层 (ScoringEngine)
    │
    └── 标准化服务层 (NormalizationService)
        ├── 方法注册表
        └── 标准化方法抽象层
            ├── 基础方法: MinMax, Inverse, Max, Sum
            ├── 统计方法: Vector, Z-Score, Logarithmic
            └── 高级方法: Sigmoid, Threshold, Custom
```

### 2. 核心接口设计

#### 2.1 标准化方法抽象基类

```python
# lib/normalization/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Any

Direction = Literal["higher_better", "lower_better"]

@dataclass(frozen=True)
class NormalizationResult:
    """标准化结果"""
    normalized_scores: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

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
```

#### 2.2 方法注册机制

```python
# lib/normalization/registry.py
from typing import Dict, Type, Callable
from .base import NormalizationMethod

_normalization_methods: Dict[str, Type[NormalizationMethod]] = {}

def register_normalization_method(name: str) -> Callable:
    """标准化方法注册装饰器"""
    def decorator(cls: Type[NormalizationMethod]) -> Type[NormalizationMethod]:
        _normalization_methods[name] = cls
        return cls
    return decorator

def get_normalization_method(name: str) -> NormalizationMethod:
    """获取标准化方法实例"""
    if name not in _normalization_methods:
        available = ", ".join(_normalization_methods.keys())
        raise ValueError(f"未知的标准化方法: '{name}'. 可用: {available}")
    return _normalization_methods[name]()
```

#### 2.3 标准化服务

```python
# lib/normalization/service.py
from typing import Dict
from .base import NormalizationResult, NormalizationConfig, Direction
from .registry import get_normalization_method

class NormalizationService:
    """标准化服务"""

    def normalize(
        self,
        values: dict[str, float],
        config: NormalizationConfig
    ) -> NormalizationResult:
        """根据配置执行标准化"""
        method = get_normalization_method(config.type)
        return method.normalize(values, config.direction)

    def normalize_batch(
        self,
        data: dict[str, dict[str, float]],
        configs: dict[str, NormalizationConfig]
    ) -> dict[str, dict[str, float]]:
        """批量标准化（多准则）"""
        result = {}
        for criterion, values in data.items():
            config = configs.get(criterion, NormalizationConfig(
                type="minmax",
                direction="higher_better"
            ))
            norm_result = self.normalize(values, config)
            result[criterion] = norm_result.normalized_scores
        return result
```

### 3. 方法实现优先级

#### 3.1 评分维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **应用热度** | 35% | 文献引用量 |
| **实现难度** | 30% | 5=最简单，1=最复杂 |
| **用户价值** | 25% | 解决问题能力 |
| **架构兼容性** | 10% | 与 ScoringEngine 适配度 |

#### 3.2 综合评分结果

| 排名 | 方法 | 热度 | 难度 | 价值 | 兼容 | **总分** | 类别 | 阶段 |
|------|------|------|------|------|------|----------|------|------|
| 🥇 1 | **MinMax** | 5.0 | 5.0 | 5.0 | 5.0 | **5.00** | 基础 | v0.2 |
| 🥈 2 | **Vector** | 4.5 | 5.0 | 4.5 | 5.0 | **4.70** | 统计 | v0.2 |
| 🥉 3 | **Z-Score** | 4.0 | 4.5 | 4.5 | 5.0 | **4.30** | 统计 | v0.3 |
| 4 | **Sum** | 4.0 | 5.0 | 4.0 | 5.0 | **4.25** | 基础 | v0.3 |
| 5 | **Max** | 3.0 | 5.0 | 3.5 | 5.0 | **3.80** | 基础 | v0.3 |
| 6 | **Logarithmic** | 3.0 | 4.0 | 4.0 | 5.0 | **3.75** | 统计 | v0.4 |
| 7 | **Sigmoid** | 2.5 | 3.0 | 4.5 | 4.0 | **3.25** | 高级 | v0.4 |
| - | **Inverse** | - | 5.0 | 4.0 | 5.0 | **4.50** | 基础 | v0.2 |
| - | **Threshold** | - | 4.0 | 4.5 | 5.0 | **4.25** | 高级 | v0.2 |

### 4. 分阶段实施路线图

#### v0.2: 基础标准化层（2 周，7.5 人日）

| 方法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **MinMax** | P0 | 0.5 人日 | 最常用，已有 Linear 基础 |
| **Inverse** | P0 | 0.5 人日 | MinMax 的反向版本 |
| **Threshold** | P1 | 1.5 人日 | 阶梯函数，已设计 |
| **Vector** | P1 | 1 人日 | TOPSIS 必需 |
| **测试与文档** | - | 4 人日 | 单元测试 + 使用文档 |

**总工作量**: **7.5 人日**

#### v0.3: 统计标准化层（2 周，9 人日）

| 方法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **Z-Score** | P0 | 2 人日 | 统计学标准，处理异常值 |
| **Sum** | P1 | 0.5 人日 | 简单实用 |
| **Max** | P1 | 0.5 人日 | 最简单的缩放 |
| **方法推荐引擎** | P1 | 2 人日 | 根据数据特征推荐方法 |
| **测试与文档** | - | 4 人日 | 单元测试 + 使用文档 |

**总工作量**: **9 人日**

#### v0.4: 高级标准化层（2-3 周，10.5 人日）

| 方法 | 优先级 | 工作量 | 说明 |
|------|--------|--------|------|
| **Logarithmic** | P1 | 1.5 人日 | 处理偏态分布 |
| **Sigmoid** | P2 | 2 人日 | 平滑过渡，抑制异常值 |
| **Custom** | P2 | 3 人日 | 用户自定义方法 |
| **测试与文档** | - | 4 人日 | 单元测试 + 使用文档 |

**总工作量**: **10.5 人日**

**标准化方法总计**: **27 人日** (约 7-8 周)

### 5. 核心方法实现示例

#### 5.1 MinMax 标准化

```python
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
            normalized[key] = max(0.0, min(1.0, norm))

        return NormalizationResult(
            normalized_scores=normalized,
            metadata={
                "method": self.name,
                "direction": direction,
                "min": min_val,
                "max": max_val
            }
        )
```

#### 5.2 Vector 标准化

```python
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
        vals = list(values.values())
        norm = sum(v ** 2 for v in vals) ** 0.5

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

        return NormalizationResult(
            normalized_scores=normalized,
            metadata={"method": self.name, "norm": norm}
        )
```

#### 5.3 Z-Score 标准化

```python
@register_normalization_method("zscore")
class ZScoreNormalization(NormalizationMethod):
    """Z-Score 标准化

    公式: (x - μ) / σ
    适用: 正态分布数据，自动处理异常值
    """

    def __init__(self, clip_range: tuple[float, float] = (-3.0, 3.0)):
        self.clip_range = clip_range

    @property
    def name(self) -> str:
        return "zscore"

    @property
    def description(self) -> str:
        return "Z-Score 标准化，适用于正态分布"

    def normalize(
        self,
        values: dict[str, float],
        direction: Direction = "higher_better"
    ) -> NormalizationResult:
        import statistics

        vals = list(values.values())
        mean = statistics.mean(vals)
        std = statistics.stdev(vals) if len(vals) >= 2 else 0

        # 处理常数情况
        if std == 0:
            return NormalizationResult(
                normalized_scores={k: 0.5 for k in values.keys()},
                metadata={"mean": mean, "std": std, "note": "constant"}
            )

        normalized = {}
        for key, value in values.items():
            z = (value - mean) / std
            # 裁剪到 [-3, 3]，抑制极端异常值
            z_clipped = max(self.clip_range[0], min(self.clip_range[1], z))
            # 映射到 [0, 1]
            norm = (z_clipped - self.clip_range[0]) / (
                self.clip_range[1] - self.clip_range[0]
            )
            if direction == "lower_better":
                norm = 1.0 - norm
            normalized[key] = max(0.0, min(1.0, norm))

        return NormalizationResult(
            normalized_scores=normalized,
            metadata={"method": self.name, "mean": mean, "std": std}
        )
```

### 6. 数据模型更新

```python
# lib/models.py
from dataclasses import dataclass, field
from typing import Literal, Union, Any

NormalizationType = Literal[
    "minmax", "inverse", "vector", "zscore",
    "sum", "max", "logarithmic", "sigmoid", "threshold"
]

Direction = Literal["higher_better", "lower_better"]

@dataclass(frozen=True)
class NormalizationConfig:
    """标准化配置"""
    type: NormalizationType
    direction: Direction = "higher_better"
    params: dict[str, Any] = field(default_factory=dict)
    # 示例 params:
    # - zscore: {"clip_range": [-3, 3]}
    # - sigmoid: {"k": 1.0, "x0": 0.5}
    # - logarithmic: {"base": 10}

@dataclass(frozen=True)
class NormalizationScoringRule:
    """通用标准化评分规则"""
    type: Literal["normalization"] = "normalization"
    normalization: NormalizationConfig
    scale: float = 100.0

# 联合类型（向后兼容）
ScoringRule = Union[
    LinearScoringRule,      # 保留 v1.0
    ThresholdScoringRule,   # 保留 v1.0
    NormalizationScoringRule,  # 新增 v2.0
]
```

### 7. YAML 配置示例

```yaml
criteria:
  # 方式 1: 原有 LinearScoringRule（向后兼容）
  - name: 成本
    weight: 0.3
    direction: lower_better
    scoring_rule:
      type: linear
      min: 0
      max: 100
      scale: 100

  # 方式 2: MinMax 标准化
  - name: 价格
    weight: 0.25
    direction: lower_better
    scoring_rule:
      type: normalization
      normalization:
        type: minmax
        direction: lower_better
      scale: 100

  # 方式 3: Vector 标准化（TOPSIS）
  - name: 性能
    weight: 0.25
    direction: higher_better
    scoring_rule:
      type: normalization
      normalization:
        type: vector
        direction: higher_better
      scale: 100

  # 方式 4: Z-Score 标准化
  - name: 评分
    weight: 0.2
    direction: higher_better
    scoring_rule:
      type: normalization
      normalization:
        type: zscore
        direction: higher_better
        params:
          clip_range: [-3, 3]
      scale: 100
```

### 8. 文件结构

```
lib/
└── normalization/              # 标准化模块
    ├── __init__.py
    ├── base.py                 # 抽象基类
    ├── registry.py             # 方法注册表
    ├── service.py              # 标准化服务
    └── methods/
        ├── __init__.py
        ├── basic.py            # MinMax, Inverse, Max, Sum
        ├── statistical.py      # Vector, Z-Score, Logarithmic
        └── advanced.py         # Sigmoid, Threshold, Custom

tests/normalization/
    ├── test_minmax.py
    ├── test_vector.py
    ├── test_zscore.py
    └── fixtures/
        └── normalization_data.yaml
```

---

## 权衡分析

### 决策 1: 标准化方法接口

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **统一接口** | 代码一致，可插拔 | 参数通过字典传递 | ✅ 采用 |
| **独立接口** | 类型安全 | 代码重复 | ❌ |

### 决策 2: 方向性处理

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **后处理反转** | 统一处理 | 部分方法语义不符 | ✅ 采用 |
| **方法内处理** | 灵活 | 代码重复 | ❌ |

### 决策 3: 输出范围

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **内部 [0,1]** | 数学简洁 | 用户不直观 | ✅ 内部使用 |
| **外部可配置** | 灵活 | 复杂度增加 | ✅ 接口支持 |

### 正面影响
1. **可扩展性**: 添加新方法约 30-50 行代码
2. **向后兼容**: 保留原有规则类型
3. **算法无关**: 标准化与算法解耦
4. **测试覆盖**: 单元测试 >= 85%

### 负面影响
1. **复杂度增加**: 需要理解多种方法的适用场景
2. **参数类型**: 通过字典传递，类型安全性稍弱

### 缓解措施
1. **完善文档**: 每种方法的使用场景和示例
2. **智能推荐**: 根据数据特征推荐合适的方法
3. **单元测试**: 确保每种方法 >= 85% 覆盖率
4. **CLI 提示**: 配置错误时给出友好提示

---

## 后果

### 对开发影响
- **v0.2** (2 周): 基础方法 (MinMax, Inverse, Threshold, Vector)
- **v0.3** (2 周): 统计方法 (Z-Score, Sum, Max) + 推荐引擎
- **v0.4** (2-3 周): 高级方法 (Logarithmic, Sigmoid, Custom)

### 对算法影响
- **WSM**: 推荐 MinMax
- **TOPSIS**: 必须 Vector
- **AHP**: 不需要标准化（成对比较）

### 对用户影响
- **灵活性**: 每个准则可选择不同的标准化方法
- **学习曲线**: 需要理解各种方法的适用场景
- **配置复杂度**: YAML 配置略微复杂

---

## 方法对比矩阵

| 方法 | 适用场景 | 优点 | 缺点 | 推荐算法 |
|------|----------|------|------|----------|
| **MinMax** | 通用，边界明确 | 简单直观 | 对异常值敏感 | WSM, AHP |
| **Vector** | 距离相关 | TOPSIS 标准 | 不保序 | TOPSIS |
| **Z-Score** | 正态分布 | 自动处理异常值 | 需要足够样本 | 统计类算法 |
| **Sum** | 比例型数据 | 简单 | 受总量影响 | WSM |
| **Max** | 快速缩放 | 最简单 | 丢失相对信息 | WSM |
| **Logarithmic** | 偏态分布 | 缩小极端值 | 零值问题 | 任意 |
| **Sigmoid** | 平滑过渡 | 抑制异常值 | 参数调优复杂 | 高级场景 |
| **Threshold** | 等级划分 | 简单粗暴 | 丢失精度 | 任意 |

---

## 未来演进

### 短期 (v0.2)
- MinMax, Inverse, Threshold, Vector
- 基础推荐引擎

### 中期 (v0.3)
- Z-Score, Sum, Max
- 智能方法推荐

### 长期 (v0.4)
- Logarithmic, Sigmoid, Custom
- 自适应标准化

---

## 使用示例

### Python API

```python
from lib.normalization import NormalizationService, NormalizationConfig

# 创建服务
service = NormalizationService()

# 示例 1: MinMax 标准化
costs = {"AWS": 20, "Azure": 50, "GCP": 35}
config = NormalizationConfig(type="minmax", direction="lower_better")
result = service.normalize(costs, config)
print(result.normalized_scores)
# 输出: {'AWS': 1.0, 'Azure': 0.0, 'GCP': 0.5}

# 示例 2: 批量标准化
data = {
    "成本": {"AWS": 20, "Azure": 50, "GCP": 35},
    "性能": {"AWS": 85, "Azure": 92, "GCP": 88}
}
configs = {
    "成本": NormalizationConfig(type="minmax", direction="lower_better"),
    "性能": NormalizationConfig(type="vector", direction="higher_better")
}
normalized = service.normalize_batch(data, configs)
```

### YAML 配置

```yaml
# decision.yaml
problem: "选择最佳云服务供应商"

alternatives:
  - AWS
  - Azure
  - GCP

criteria:
  - name: 成本
    weight: 0.3
    direction: lower_better
    scoring_rule:
      type: normalization
      normalization:
        type: minmax
      scale: 100

  - name: 性能
    weight: 0.7
    direction: higher_better
    scoring_rule:
      type: normalization
      normalization:
        type: vector
      scale: 100

raw_data:
  AWS:
    成本: 20
    性能: 85
  Azure:
    成本: 50
    性能: 92
  GCP:
    成本: 35
    性能: 88

algorithm:
  name: wsm
```

---

## 方法推荐引擎（v0.3 特性）

根据数据特征自动推荐标准化方法：

| 数据特征 | 推荐方法 | 理由 |
|----------|----------|------|
| 样本量 < 5 | MinMax | 简单稳定 |
| 样本量 >= 10，正态分布 | Z-Score | 统计最优 |
| 含极端异常值 | Z-Score (clipped) 或 Sigmoid | 自动抑制 |
| TOPSIS 算法 | Vector (必须) | 算法要求 |
| 比例型数据 | Sum | 保持比例关系 |
| 偏态分布 | Logarithmic | 拉伸低端 |

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-01-31
**状态**: ✅ 已批准
**总工作量**: 27 人日 (约 7-8 周)

**相关文档**:
- [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-003: 赋权方法路线图](./003-mcda-weighting-roadmap.md)
- [ADR-004: 汇总算法架构设计](./004-mcda-aggregation-algorithms.md)
- [需求文档: MCDA Core v2.0](../requirements/mcda-core.md)
