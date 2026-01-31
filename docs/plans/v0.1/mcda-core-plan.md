# MCDA Core Skill - Implementation Plan

## Overview

开发一个通用的多准则决策分析核心技能框架，支持可插拔的算法模型。MVP 版本实现核心框架（数据验证、结果报告、敏感性分析）和 WSM（Weighted Sum Model）算法。Python 3.12+ 实现，测试覆盖率 >= 80%。

---

## 📋 版本路线图（architect agent 审查后调整）

### 总体工作量对比

| 版本 | 原工作量 | 新工作量 | 节省 | 关键变化 |
|------|---------|---------|------|----------|
| v0.2 (MVP) | 15.5 人日 | **10 人日** | 5.5 人日 | 赋权降级，VIKOR 升级 |
| v0.3 | 33 人日 | **19 人日** | 14 人日 | AHP 升级，PROMETHEE-II |
| v0.4 | 45.5 人日 | **31 人日** | 14.5 人日 | 高级方法延后 |
| v0.5 | - | **20.5 人日** | - | 特殊场景 |
| **总计** | **96.5 人日** | **80.5 人日** | **16 人日** | **优化 17%** |

---

### v0.2: MVP 最小可行产品（2 周，10 人日）⭐

**目标**: 2 周内交付可用的 MCDA 决策分析工具

#### 模块分解

| 模块 | 方法/算法 | 工作量 | 优先级 |
|------|----------|--------|--------|
| **标准化方法** | MinMax | 0.5 人日 | P0 |
| | Vector | 1 人日 | P0 |
| | 小计 | **1.5 人日** | |
| **赋权方法** | 直接赋权（手动指定）| 0.5 人日 | P0 |
| | 小计 | **0.5 人日** | |
| **汇总算法** | WSM（已完成）| - | P0 |
| | WPM（已完成）| - | P0 |
| | TOPSIS | 2 人日 | P0 |
| | VIKOR | 3 人日 | P0 ⭐ |
| | 小计 | **5 人日** | |
| **测试与文档** | 单元测试 + 使用文档 | 3 人日 | P0 |
| **总计** | | **10 人日** | |

#### MVP 数据流

```
用户输入（YAML）
    ↓
┌───────────────────────────────────────┐
│ 数据导入（CSV/Excel）                  │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 评分计算                               │
│  - MinMax: 线性映射                     │
│  - Vector: TOPSIS 专用                 │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 权重                                   │
│  - 直接赋权（用户手动指定）             │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 汇总算法                               │
│  - WSM: 通用决策                       │
│  - WPM: 短板效应                       │
│  - TOPSIS: 距离决策                    │
│  - VIKOR: 折衷决策 ⭐核心              │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 输出                                   │
│  - 替代方案排名                         │
│  - 敏感度分析                          │
│  - 可视化报告（Markdown）              │
└───────────────────────────────────────┘
```

#### 验收标准
- [ ] 用户可以导入数据源进行多准则决策分析
- [ ] 支持核心场景：产品选型决策、技术方案评估、投资组合优化
- [ ] 输出：替代方案排名、敏感度分析、可视化报告
- [ ] VIKOR 提供折衷解（核心价值）

---

### v0.3: 基础扩展（4 周，19 人日）

**目标**: 主客观赋权 + 偏好关系决策

#### 模块分解

| 模块 | 方法/算法 | 工作量 |
|------|----------|--------|
| **标准化方法** | Z-Score | 2 人日 |
| | Sum | 0.5 人日 |
| | Inverse | 0.5 人日 |
| | 小计 | **3 人日** |
| **赋权方法** | 熵权法 | 2 人日 |
| | AHP | 3 人日 |
| | 测试与文档 | 1 人日 |
| | 小计 | **6 人日** |
| **汇总算法** | PROMETHEE-II | 4 人日 |
| | COPRAS | 2 人日 |
| | 小计 | **6 人日** |
| **测试与文档** | 单元测试 + 使用文档 | 4 人日 |
| **总计** | | **19 人日** |

---

### v0.4: 高级功能（6 周，31 人日）

**目标**: 完整标准化 + 高级赋权 + 更多算法

#### 模块分解

| 模块 | 方法/算法 | 工作量 |
|------|----------|--------|
| **标准化方法** | Max, Threshold, Logarithmic, Sigmoid | 5 人日 |
| **赋权方法** | CRITIC, 变异系数法, 标准离差法, 离差最大化 | 10 人日 |
| **汇总算法** | SAW, TODIM, ELECTRE-I, MACBETH, MOORA, ORESTE | 10 人日 |
| **测试与文档** | 单元测试 + 使用文档 | 6 人日 |
| **总计** | | **31 人日** |

---

### v0.5: 特殊场景（4 周，20.5 人日）

**目标**: 德尔菲法 + PCA + 组合赋权

#### 模块分解

| 模块 | 方法/算法 | 工作量 |
|------|----------|--------|
| **赋权方法** | 德尔菲法, PCA, 组合赋权 | 10.5 人日 |
| **测试与文档** | 单元测试 + 使用文档 | 5.5 人日 |
| **总计** | | **20.5 人日** |

---

### 交付时间线

| 版本 | 工作量 | 交付周期 | 累计时间 |
|------|--------|---------|---------|
| **v0.2 (MVP)** | 10 人日 | **2 周** | 2 周 |
| v0.3 | 19 人日 | 4 周 | 6 周 |
| v0.4 | 31 人日 | 6 周 | 12 周 |
| v0.5 | 20.5 人日 | 4 周 | 16 周 |

**MVP 验证**: 2 周后即可获得用户反馈

---

### 关键里程碑

| 里程碑 | 内容 | 时间 |
|--------|------|------|
| M1 | MVP 发布（WSM + WPM + TOPSIS + VIKOR） | 2 周 |
| M2 | Z-Score + 熵权法 + AHP + PROMETHEE-II | 6 周 |
| M3 | 完整标准化 + 高级赋权 + COPRAS | 12 周 |
| M4 | 特殊场景算法 | 16 周 |

---

### 优先级调整总结（architect agent 建议）

| 原优先级 | 新优先级 | 变化 | 理由 |
|----------|----------|------|------|
| Threshold (v0.2, P1) | v0.4, P3 | 降级 | 丢失精度 |
| 变异系数法 (v0.2, P1) | v0.4, P3 | 降级 | 与标准离差法重复 |
| 标准离差法 (v0.2, P1) | v0.4, P3 | 降级 | 价值有限 |
| **VIKOR (v0.3, P0)** | **v0.2, P0** | **升级** | 折衷解核心价值 |
| **AHP (v0.4, P0)** | **v0.3, P2** | **升级** | 最热门主观方法 |
| **直接赋权 (-)** | **v0.2, P0** | **新增** | 用户最常用 |
| SAW (v0.2, P1) | v0.4, P3 | 降级 | 与 WSM 重复 |

---

## Requirements 重述

### 功能需求

#### 1. 通用核心框架
- **决策问题定义**（YAML 配置格式）
  - 备选方案列表（alternatives）
  - 评价准则列表（criteria）
  - 权重定义（weights，支持归一化）
  - 评分矩阵（scores，1-5 分制）

- **数据验证**
  - 权重总和检查（= 1.0 或自动归一化）
  - 评分范围检查（1-5）
  - 最小方案数检查（≥ 2）
  - 最小准则数检查（≥ 2）

- **结果报告**
  - Markdown 格式输出
  - 排名表格
  - 得分详情
  - 决策建议

- **敏感性分析**
  - 权重扰动测试（±10%）
  - 排名变化检测
  - 关键权重识别

#### 2. WSM 算法模型（MVP）
- **加权得分计算**: `Score = Σ(weight_i × score_i)`
- **方向性支持**: higher_better / lower_better
- **排序和排名**: 按得分降序排列

#### 3. 文档结构（按 CLAUDE.md 规范）
- `skills/mcda-core/SKILL.md`（AI 执行指令，极简 < 5000 tokens）
- `skills/mcda-core/SKILL_CN.md`（中文 AI 执行指令）
- `skills/mcda-core/README.md` + `README_CN.md`（开发者文档）
- `skills/mcda-core/references/`（参考文档，渐进式披露）
- `docs/active/tdd-mcda-core.md`（TDD 进度跟踪）

### 非功能需求
- **语言**: Python 3.12+
- **依赖**: pyyaml, numpy, pytest 8.0+
- **测试覆盖率**: >= 80%
- **工作流**: 遵循项目 Git Flow 规范

---

## Architecture Changes

### 五层分层架构设计

根据 [ADR-001](../../../decisions/001-mcda-layered-architecture.md)，MCDA Core 采用五层分层架构：

```
应用层 (CLI)
    ↓
核心服务层 (Validation, Reporter, Sensitivity)
    ↓
算法抽象层 (MCDAAlgorithm 基类)
    ↓
数据模型层 (DecisionProblem, DecisionResult)
    ↓
基础设施层 (YAML I/O, Utils)
```

### 模块依赖关系图

```
                    ┌──────────────┐
                    │   models.py  │
                    │  (无依赖)    │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ algorithms/ │ │ validation  │ │    utils    │
    │             │ │    .py      │ │    .py      │
    └──────┬──────┘ └──────┬──────┘ └─────────────┘
           │               │
           └───────┬───────┘
                   ▼
            ┌─────────────┐
            │ reporter.py │
            │sensitivity.py│
            └──────┬──────┘
                   ▼
            ┌─────────────┐
            │   core.py   │
            │(orchestrator)│
            └─────────────┘
```

### 新增文件结构

```
skills/mcda-core/
├── SKILL.md                      # AI 执行指令（极简，< 5000 tokens）
├── SKILL_CN.md                   # 中文 AI 执行指令
├── README.md                     # 英文开发者文档
├── README_CN.md                  # 中文开发者文档
├── LICENSE.txt                   # Apache-2.0
├── references/                   # 参考文档（渐进式披露）
│   ├── algorithms.md             # 算法参考（WSM, AHP, TOPSIS）
│   ├── yaml-schema.md            # YAML 配置模式
│   ├── examples.md               # 实际案例集
│   └── sensitivity.md            # 敏感性分析方法
└── lib/                          # 核心实现（Python 3.12+）
    ├── __init__.py               # 公共 API 导出
    ├── models.py                 # 数据模型（150 行）
    │   # Criterion, DecisionProblem, DecisionResult
    ├── utils.py                  # 工具函数（100 行）
    │   # YAML 加载、权重归一化、方向反转
    ├── exceptions.py             # 异常定义（30 行）
    │   # ValidationError, AlgorithmError
    ├── validation.py             # 验证服务（150 行）
    │   # ValidationService, ValidationResult
    ├── reporter.py               # 报告服务（150 行）
    │   # ReportService, Markdown/JSON 生成
    ├── sensitivity.py            # 敏感性分析服务（200 行）
    │   # SensitivityService, 扰动测试
    ├── core.py                   # CLI 和编排器（150 行）
    │   # MCDAOrchestrator, CLI 命令
    └── algorithms/
        ├── __init__.py           # 算法注册（40 行）
        │   # register_algorithm, get_algorithm
        ├── base.py               # 算法基类（50 行）
        │   # MCDAAlgorithm 抽象类
        └── wsm.py                # WSM 算法实现（100 行）
            # WSMAlgorithm 类

tests/mcda-core/
├── __init__.py
├── conftest.py                   # pytest 配置和 fixtures
├── test_models.py                # 数据模型测试
├── test_validation.py            # 验证服务测试
├── test_reporter.py              # 报告生成测试
├── test_sensitivity.py           # 敏感性分析测试
├── test_wsm.py                   # WSM 算法测试
├── test_integration.py           # 集成测试
└── fixtures/
    ├── vendor_selection.yaml     # 供应商选择场景
    ├── product_priority.yaml     # 产品优先级场景
    └── invalid_weights.yaml      # 无效权重（负向测试）

docs/active/
└── tdd-mcda-core.md              # TDD 进度跟踪（RED → GREEN → REFACTOR → DONE）

docs/requirements/
└── mcda-core.md                  # 需求文档（已创建）
```

### 文件清单与职责

| 文件路径 | 职责 | 代码行数(预估) | 依赖 |
|---------|------|--------------|------|
| `lib/__init__.py` | 包初始化，导出公共 API | 20 | models |
| `lib/models.py` | 数据模型定义（frozen dataclass） | 150 | 无 |
| `lib/utils.py` | 工具函数（YAML 加载等） | 100 | models |
| `lib/exceptions.py` | 异常定义 | 30 | 无 |
| `lib/validation.py` | 验证服务 | 150 | models, utils |
| `lib/algorithms/base.py` | 算法基类（ABC） | 50 | models |
| `lib/algorithms/wsm.py` | WSM 算法实现 | 100 | base, models |
| `lib/algorithms/__init__.py` | 算法注册表 | 40 | base, wsm |
| `lib/reporter.py` | 报告生成服务 | 150 | models |
| `lib/sensitivity.py` | 敏感性分析服务 | 200 | models, algorithms |
| `lib/core.py` | CLI 和编排器 | 150 | 所有模块 |
| **总计** | | **1140** | |

### 核心数据模型定义

```python
# lib/models.py
from dataclasses import dataclass, field
from typing import Literal, Required, NotRequired

# 类型别名
Direction = Literal["higher_better", "lower_better"]
ScoreMatrix = dict[str, dict[str, float]]  # {alternative: {criterion: score}}

@dataclass(frozen=True)
class Criterion:
    """评价准则"""
    name: str
    weight: float
    direction: Direction
    description: str = ""

@dataclass(frozen=True)
class AlgorithmConfig:
    """算法配置"""
    name: str
    params: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DecisionProblem:
    """决策问题（不可变）"""
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    scores: ScoreMatrix
    algorithm: AlgorithmConfig

    def __post_init__(self):
        # 数据一致性验证
        if len(self.alternatives) < 2:
            raise ValueError("至少需要 2 个备选方案")
        if len(self.criteria) < 2:
            raise ValueError("至少需要 2 个评价准则")

@dataclass
class RankingItem:
    """排名项"""
    rank: int
    alternative: str
    score: float
    details: dict[str, float] = field(default_factory=dict)

@dataclass
class ResultMetadata:
    """结果元数据"""
    algorithm_name: str
    algorithm_version: str = "1.0.0"
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    problem_size: tuple[int, int] = (0, 0)

@dataclass
class SensitivityResult:
    """敏感性分析结果"""
    perturbations: list[Perturbation]
    critical_criteria: list[str]
    robustness_score: float  # 0-1

@dataclass
class DecisionResult:
    """决策结果"""
    rankings: list[RankingItem]
    raw_scores: dict[str, float]
    metadata: ResultMetadata
    sensitivity: SensitivityResult | None = None
```

### 算法接口规范

```python
# lib/algorithms/base.py
from abc import ABC, abstractmethod
from ..models import DecisionProblem, DecisionResult, ValidationResult

class MCDAAlgorithm(ABC):
    """MCDA 算法基类"""

    @abstractmethod
    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        """执行计算，返回决策结果"""
        pass

    def validate(self, problem: DecisionProblem) -> ValidationResult:
        """验证输入数据（可覆盖）"""
        return ValidationResult(is_valid=True)

    @property
    @abstractmethod
    def name(self) -> str:
        """算法名称"""
        pass

    @property
    def metadata(self) -> AlgorithmMetadata:
        """算法元数据（默认实现）"""
        return AlgorithmMetadata(
            name=self.name,
            version="1.0.0",
            requires_normalized_weights=True,
            score_range=(0, 5),
        )
```

### WSM 算法详细设计

```python
# lib/algorithms/wsm.py
class WSMAlgorithm(MCDAAlgorithm):
    """加权求和模型算法

    公式: Score_i = Σ(weight_j × score_ij)

    对于 lower_better 准则，得分需要反转
    """

    @property
    def name(self) -> str:
        return "wsm"

    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        # 1. 标准化得分（处理 lower_better）
        normalized = self._normalize_scores(problem)

        # 2. 计算加权得分
        scores = {}
        for alt in problem.alternatives:
            weighted_sum = 0.0
            for crit in problem.criteria:
                weight = crit.weight
                score = normalized[alt][crit.name]
                weighted_sum += weight * score
            scores[alt] = weighted_sum

        # 3. 排序并构建结果
        sorted_alternatives = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        rankings = [
            RankingItem(rank=i, alt=alt, score=round(score, 4))
            for i, (alt, score) in enumerate(sorted_alternatives, 1)
        ]

        return DecisionResult(
            rankings=rankings,
            raw_scores=scores,
            metadata=ResultMetadata(
                algorithm_name=self.name,
                problem_size=(len(problem.alternatives), len(problem.criteria)),
            ),
        )
```

### 未来算法接入路径

**添加 AHP 算法（示例）**:

```python
# lib/algorithms/ahp.py
from .base import MCDAAlgorithm, register_algorithm

@register_algorithm("ahp")
class AHPAlgorithm(MCDAAlgorithm):
    """层次分析法算法"""

    @property
    def name(self) -> str:
        return "ahp"

    def validate(self, problem: DecisionProblem) -> ValidationResult:
        """AHP 特定验证（成对比较矩阵）"""
        # 检查成对比较矩阵
        # 检查一致性比率
        pass

    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        # 1. 构建成对比较矩阵
        # 2. 计算特征向量（权重）
        # 3. 计算一致性比率
        # 4. 计算各方案得分
        pass

# 无需修改其他代码，自动注册到算法注册表
```

**添加 TOPSIS 算法（示例）**:

```python
# lib/algorithms/topsis.py
@register_algorithm("topsis")
class TOPSISAlgorithm(MCDAAlgorithm):
    """TOPSIS 算法（基于理想解相似度的排序方法）"""

    @property
    def name(self) -> str:
        return "topsis"

    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        # 1. 标准化决策矩阵
        # 2. 构建加权标准化矩阵
        # 3. 确定正理想解和负理想解
        # 4. 计算距离
        # 5. 计算相对接近度
        pass
```

---

## Implementation Steps（v2.0 更新）

根据 [ADR-002](../../../decisions/002-mcda-scoring-engine.md)，新增评分计算引擎和数据源支持。

### Phase 1: 项目初始化（30 min，Low）

#### 1.1 创建 Git 分支
```bash
git checkout develop && git pull
git checkout -b feature/mcda-core
```

#### 1.2 创建 TDD 进度文件
- **File**: `docs/active/tdd-mcda-core.md`
- **Content**: 跟踪开发进度（RED → GREEN → REFACTOR → DONE）

#### 1.3 创建目录结构
```bash
mkdir -p skills/mcda-core/{references,lib/algorithms}
mkdir -p tests/mcda-core/fixtures
```

---

### Phase 2: 数据模型扩展（2 hours，Medium）⭐ NEW

#### 2.1 ScoringRule 数据模型
- **File**: `skills/mcda-core/lib/models.py`
- **新增类型**:
  ```python
  @dataclass(frozen=True)
  class LinearScoringRule:
      """线性评分规则"""
      type: Literal["linear"] = "linear"
      min: float
      max: float
      scale: float = 100.0

  @dataclass(frozen=True)
  class ThresholdRange:
      """阈值范围"""
      min: float | None = None
      max: float | None = None
      score: float = 100.0

  @dataclass(frozen=True)
  class ThresholdScoringRule:
      """阈值分段评分规则"""
      type: Literal["threshold"] = "threshold"
      ranges: tuple[ThresholdRange, ...]
      default_score: float = 0.0

  ScoringRule = LinearScoringRule | ThresholdScoringRule
  ```

#### 2.2 DataSource 数据模型
- **新增类型**:
  ```python
  @dataclass(frozen=True)
  class DataSource:
      """数据源配置"""
      type: Literal["yaml", "csv", "excel"]
      file: str
      sheet: str | None = None
      encoding: str = "utf-8"
  ```

#### 2.3 更新 Criterion 和 DecisionProblem
- **修改**: 添加 `scoring_rule` 和 `column` 字段
- **修改**: 评分范围改为 0-100
  ```python
  @dataclass(frozen=True)
  class Criterion:
      name: str
      weight: float
      direction: Direction
      description: str = ""
      scoring_rule: ScoringRule | None = None  # NEW
      column: str | None = None                # NEW

  @dataclass(frozen=True)
  class DecisionProblem:
      alternatives: tuple[str, ...]
      criteria: tuple[Criterion, ...]
      data_source: DataSource | None = None   # NEW
      raw_data: dict | None = None            # NEW
      scores: dict | None = None
      algorithm: AlgorithmConfig
      score_range: ScoreRange = (0.0, 100.0)  # CHANGED: (1, 5) → (0, 100)
  ```

---

### Phase 3: 评分计算引擎（3 hours，Medium）⭐ NEW

#### 3.1 ScoringEngine 实现
- **File**: `skills/mcda-core/lib/scoring.py`
- **职责**: 根据评分规则计算评分
- **核心方法**:
  ```python
  class ScoringEngine:
      def calculate(
          self,
          raw_value: float | str | int,
          criterion: Criterion
      ) -> float:
          """根据评分规则计算评分（0-100）"""

      def calculate_batch(
          self,
          raw_data: dict[str, dict[str, float | str]],
          criteria: tuple[Criterion, ...]
      ) -> dict[str, dict[str, float]]:
          """批量计算评分"""
  ```

#### 3.2 ScoringService 实现
- **File**: `skills/mcda-core/lib/scoring.py`
- **职责**: 对外接口，协调评分计算
- **核心方法**:
  ```python
  class ScoringService:
      def apply_scoring_rules(
          self,
          problem: DecisionProblem
      ) -> dict[str, dict[str, float]]:
          """应用评分规则，生成评分矩阵"""
  ```

#### 3.3 DataSourceLoader 实现
- **File**: `skills/mcda-core/lib/data_source.py`
- **实现类**:
  - `YAMLDataSourceLoader`（YAML 加载）
  - `CSVDataSourceLoader`（CSV 加载，使用标准库）
  - `ExcelDataSourceLoader`（Excel 加载，可选 openpyxl）

#### 3.4 DataSourceService 实现
- **File**: `skills/mcda-core/lib/data_source.py`
- **职责**: 统一数据源加载接口
- **核心方法**:
  ```python
  class DataSourceService:
      def load(self, source: DataSource) -> dict[str, dict[str, float | str]]:
          """加载数据源"""
  ```

---

### Phase 4: 核心框架实现（3 hours，Medium）← 原 Phase 2

#### 4.1 数据验证模块
- **File**: `skills/mcda-core/lib/models.py`
- **Content**:
  ```python
  @dataclass
  class Criterion:
      name: str
      weight: float
      direction: str  # "higher_better" or "lower_better"
      description: str = ""

  @dataclass
  class DecisionProblem:
      alternatives: List[str]
      criteria: List[Criterion]
      scores: Dict[str, Dict[str, int]]
      algorithm: AlgorithmConfig

  @dataclass
  class DecisionResult:
      rankings: List[Dict[str, Any]]
      sensitivity: Dict[str, Any]
      metadata: Dict[str, Any]
  ```

#### 2.2 数据验证模块
- **File**: `skills/mcda-core/lib/validation.py`
- **Functions**:
  - `validate_weights(weights)`: 权重归一化验证
  - `validate_scores(scores, criteria)`: 评分范围验证（1-5）
  - `validate_min_count(items, min_count)`: 最小数量检查
  - `validate_criteria_direction(direction)`: 方向性验证
- **Tests**: 90%+ coverage

#### 2.3 YAML 配置解析
- **File**: `skills/mcda-core/lib/core.py`
- **Content**:
  - `load_decision_problem(yaml_path)`: 从 YAML 加载决策问题
  - 支持 YAML 结构定义
  - 错误处理和友好提示
- **Tests**: 85%+ coverage

#### 2.4 报告生成模块
- **File**: `skills/mcda-core/lib/reporter.py`
- **Functions**:
  - `generate_markdown_report(result)`: 生成 Markdown 报告
  - `generate_table(rankings)`: 生成排名表格
  - `generate_summary(result)`: 生成决策摘要
- **Tests**: 75%+ coverage

#### 2.5 敏感性分析模块
- **File**: `skills/mcda-core/lib/sensitivity.py`
- **Functions**:
  - `weight_perturbation_analysis(problem, delta=0.1)`: 权重扰动分析
  - `detect_rank_changes(original, perturbed)`: 检测排名变化
  - `identify_critical_criteria(sensitivity_result)`: 识别关键准则
- **Tests**: 80%+ coverage

---

### Phase 3: WSM 算法实现（1-2 hours，Low）

#### 3.1 算法基类定义
- **File**: `skills/mcda-core/lib/algorithms/base.py`
- **Content**:
  ```python
  class MCDAAlgorithm(ABC):
      @abstractmethod
      def calculate(self, problem: DecisionProblem) -> DecisionResult:
          pass

      @property
      @abstractmethod
      def name(self) -> str:
          pass
  ```

#### 3.2 WSM 算法实现
- **File**: `skills/mcda-core/lib/algorithms/wsm.py`
- **Content**:
  - `WSMAlgorithm` 类继承 `MCDAAlgorithm`
  - 核心计算：`score = sum(weight_i * score_i)`
  - 支持 higher_better / lower_better
  - 返回排序结果
- **Tests**: 85%+ coverage

#### 3.3 算法注册机制
- **File**: `skills/mcda-core/lib/algorithms/__init__.py`
- **Content**:
  ```python
  _algorithms = {"wsm": WSMAlgorithm}

  def get_algorithm(name: str) -> MCDAAlgorithm:
      if name not in _algorithms:
          raise ValueError(f"Unknown algorithm: {name}")
      return _algorithms[name]()
  ```

---

### Phase 4: 测试实现（2-3 hours，Medium）

#### 4.1 测试配置和 Fixtures
- **File**: `tests/mcda-core/conftest.py`
- **Content**: 共享测试数据
  - `sample_problem_config`: 标准问题配置
  - `sample_weights`: 有效权重集
  - `sample_scores`: 有效评分集
  - `invalid_weights`: 无效权重（负向测试）

#### 4.2 验证模块测试
- **File**: `tests/mcda-core/test_validation.py`
- **Tests**:
  - `test_validate_weights_normalization`
  - `test_validate_weights_auto_normalize`
  - `test_validate_weights_invalid`
  - `test_validate_scores_range`
  - `test_validate_min_count`
  - `test_validate_criteria_direction`

#### 4.3 WSM 算法测试
- **File**: `tests/mcda-core/test_wsm.py`
- **Tests**:
  - `test_wsm_basic_calculation`
  - `test_wsm_higher_better`
  - `test_wsm_lower_better`
  - `test_wsm_mixed_directions`
  - `test_wsm_tie_handling`
  - `test_wsm_edge_cases`

#### 4.4 敏感性分析测试
- **File**: `tests/mcda-core/test_sensitivity.py`
- **Tests**:
  - `test_sensitivity_perturbation`
  - `test_sensitivity_rank_change`
  - `test_sensitivity_critical_criteria`
  - `test_sensitivity_edge_cases`

#### 4.5 报告生成测试
- **File**: `tests/mcda-core/test_reporter.py`
- **Tests**:
  - `test_report_markdown_format`
  - `test_report_completeness`
  - `test_report_chinese_support`

#### 4.6 集成测试
- **File**: `tests/mcda-core/test_integration.py`
- **Tests**:
  - `test_full_workflow`: YAML → 计算 → 报告
  - `test_vendor_selection_scenario`: 真实场景测试

---

### Phase 5: 文档实现（2 hours，Low）

#### 5.1 SKILL.md（极简）
- **File**: `skills/mcda-core/SKILL.md`
- **Content**:
  - Frontmatter: name, description（触发条件）
  - Body: 核心工作流（< 5000 tokens）
  - 引用 references/ 详细文档

#### 5.2 SKILL_CN.md
- **File**: `skills/mcda-core/SKILL_CN.md`
- **Content**: 中文版 AI 执行指令

#### 5.3 README.md
- **File**: `skills/mcda-core/README.md`
- **Content**:
  - 项目概述
  - 快速开始
  - YAML 配置示例
  - CLI 使用方法
  - 算法说明

#### 5.4 README_CN.md
- **File**: `skills/mcda-core/README_CN.md`
- **Content**: 中文详细开发者文档

#### 5.5 参考文档
- **File**: `skills/mcda-core/references/algorithms.md`
  - WSM 原理和公式
  - AHP 预留
  - TOPSIS 预留

- **File**: `skills/mcda-core/references/yaml-schema.md`
  - 完整 YAML 模式
  - 字段说明
  - 验证规则

- **File**: `skills/mcda-core/references/examples.md`
  - 供应商选择案例
  - 产品优先级案例
  - 人才招聘案例

- **File**: `skills/mcda-core/references/sensitivity.md`
  - 敏感性分析方法
  - 扰动测试说明
  - 结果解读

---

### Phase 6: E2E 验证（1 hour，Low）

#### 6.1 端到端测试
- **File**: `tests/mcda-core/test_e2e.py`
- **Scenarios**:
  - 完整 WSM 决策流程
  - 敏感性分析集成
  - 报告生成和导出

#### 6.2 示例配置验证
- **Files**: `tests/mcda-core/fixtures/*.yaml`
- **Content**:
  - `vendor_selection.yaml`: 供应商选择
  - `product_priority.yaml`: 产品优先级
  - `invalid_weights.yaml`: 无效权重（测试验证）

#### 6.3 运行完整测试套件
```bash
pytest tests/mcda-core/ -v --cov=skills/mcda-core/lib --cov-report=html
# Target: 80%+ coverage
```

---

## Testing Strategy

### 单元测试
- **Framework**: pytest 8.0+
- **Coverage Target**: >= 80%
- **Mocking**: pytest-mock（文件 I/O）

### 集成测试
- **Scope**: 完整工作流测试
- **Scenarios**: 真实决策场景

### 测试数据
- 有效数据集（正常流程）
- 无效数据集（边界条件）
- 真实场景数据集

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| YAML 解析错误处理复杂 | Medium | Medium | 早期实现详细错误提示 |
| 敏感性分析算法复杂度 | Low | Low | 简化算法，限制选项数 |
| 测试覆盖率不达标 | Low | Medium | 严格 TDD 流程 |
| 文档与实现不同步 | Medium | Low | 通过进度文件跟踪 |
| 中文字符编码问题 | Low | Low | 明确 UTF-8 编码 |

---

## Complexity Estimation

| Phase | Steps | Complexity | Time Estimate |
|-------|-------|-----------|---------------|
| Phase 1: 初始化 | 3 | Low | 30 min |
| Phase 2: 核心框架 | 5 | Medium | 3-4 hours |
| Phase 3: WSM 算法 | 3 | Low | 1-2 hours |
| Phase 4: 测试 | 6 | Medium | 2-3 hours |
| Phase 5: 文档 | 9 | Low | 2 hours |
| Phase 6: E2E | 3 | Low | 1 hour |
| **Total** | **29** | **Medium** | **10-13 hours** |

---

## Success Criteria

### 功能验收
- [ ] YAML 配置加载和验证
- [ ] WSM 算法正确计算加权和
- [ ] 敏感性分析识别关键准则
- [ ] Markdown 报告生成
- [ ] CLI 命令正常工作

### 质量验收
- [ ] 测试覆盖率 >= 80%
- [ ] 所有 pytest 测试通过
- [ ] 文档符合 CLAUDE.md 规范
- [ ] SKILL.md token 数 < 5000

### 流程验收
- [ ] Git Flow 规范遵循
- [ ] TDD 进度文件维护
- [ ] Code review 通过

---

## Dependencies

### 外部依赖
- Python 3.12+
- pyyaml（YAML 解析）
- numpy（数值计算）
- pytest 8.0+（测试框架）

### 内部依赖
- CLAUDE.md 规范
- docs/requirements/mcda-core.md（需求文档）

---

## Next Steps (After Approval)

1. 创建 feature/mcda-core 分支
2. 初始化 TDD 进度文件
3. 按 Phase 顺序实施（1 → 2 → 3 → 4 → 5 → 6）
4. 每个 Phase 完成后更新 tdd-mcda-core.md
5. 最终合并到 develop 分支

---

**文档版本**: v1.0
**创建日期**: 2025-01-31
**维护者**: hunkwk + AI collaboration
**状态**: 待审批
