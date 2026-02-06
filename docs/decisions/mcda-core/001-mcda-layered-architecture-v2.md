# ADR-001: MCDA Core 分层架构设计 v2.0

## 状态
**已接受 (Accepted)** - **当前版本**

## 日期
- **初始版本**: 2026-01-31
- **v2.0 更新**: 2026-02-06
- **项目版本**: v0.13

## 变更历史

| 版本 | 日期 | 变更内容 | 理由 |
|------|------|----------|------|
| v1.0 | 2026-01-31 | 初始五层架构设计 | 奠定基础架构 |
| v2.0 | 2026-02-06 | 新增"功能扩展层" | 反映 v0.10-v0.13 的实际架构演进 |

---

## 上下文 (Context)

MCDA Core 需要支持多种决策分析算法（WSM、AHP、TOPSIS、ELECTRE、PROMETHEE 等），每种算法有：
- **不同的计算逻辑**: WSM 是线性加权，AHP 使用特征向量，TOPSIS 基于距离
- **不同的输入要求**: AHP 需要成对比较矩阵，WSM 只需直接评分
- **不同的输出格式**: 部分算法提供一致性指标、距离测度等

同时，核心功能（验证、报告、敏感性分析）应在所有算法间共享，避免代码重复。

**架构演进** (v0.1 → v0.13):
- v0.1-v0.6: 基础算法和赋权方法
- v0.7-v0.9: 区间数支持、排名计算
- v0.10-v0.13: 群决策、约束系统、可视化、报告生成

**挑战**:
1. 如何设计架构支持未来新增算法，无需修改核心代码？
2. 如何保证数据模型在各算法间一致性？
3. 如何平衡灵活性和复杂度？
4. **如何自然演进架构，容纳新增功能模块？** (v2.0 新增)

---

## 决策 (Decision)

采用**六层分层架构**，明确职责分离，支持算法可插拔和功能模块化扩展。

### 架构图 v2.0

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用层 (CLI)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   CLI 命令   │  │  配置解析   │  │   工作流编排            │ │
│  │  (cli.py)   │  │ (core.py)   │  │  (MCDAOrchestrator)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       核心服务层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   验证服务   │  │  报告服务   │  │   敏感性分析服务        │ │
│  │ (validation)│  │ (reporter) │  │   (sensitivity)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │ 标准化服务  │  │  赋权服务   │ ← ADR-002/003               │
│  │(normalization)│ │ (weighting) │                              │
│  └─────────────┘  └─────────────┘                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         ConstraintService (约束服务) ← ADR-014           │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         GroupDecisionService (群决策) ← ADR-008         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      算法抽象层                                  │
│                   ┌─────────────┐                               │
│                   │ MCDAAlgorithm│ (抽象基类)                    │
│                   │  - calculate()│                              │
│                   │  - validate() │                              │
│                   │  - get_metadata()│                          │
│                   └─────────────┘                               │
│                          △                                       │
│          ┌───────────────┼───────────────┐                     │
│          │               │               │                     │
│    ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐               │
│    │   WSM     │  │  TOPSIS   │  │   VIKOR   │  (可插拔)       │
│    │   WPM     │  │   TODIM   │  │ ELECTRE  │  (ADR-004)      │
│    │ PROMETHEE │  │           │  │           │                  │
│    └───────────┘  └───────────┘  └───────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据模型层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Criterion  │  │DecisionProblem│ │   DecisionResult        │ │
│  │(评价准则)   │  │ (决策问题)   │  │   (决策结果)            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │  Interval   │  │GroupDecision│ ← 群决策模型                │
│  │(区间数)     │  │  Problem    │                              │
│  └─────────────┘  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    功能扩展层 (v0.13 新增)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  aggregation│  │   group/   │  │   constraints/          │ │
│  │  (聚合方法) │  │  (群决策)   │  │   (约束/否决)           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  scoring/  │  │  ranking/  │  │   visualization/        │ │
│  │ (评分规则) │  │ (排名计算)  │  │   (可视化)              │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │  reports/  │  │   export/  │                              │
│  │ (报告生成) │  │  (数据导出) │                              │
│  └─────────────┘  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      基础设施层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ YAML I/O    │  │  工具函数   │  │   异常定义              │ │
│  │(loaders/)   │  │ (utils.py) │  │  (exceptions.py)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐                                           │
│  │converters.py│ (类型转换器)                              │
│  └─────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 各层职责详解

### 第 1 层：应用层 (Application Layer)
**职责**: CLI 接口和工作流编排

**核心组件**:
- `cli.py`: CLI 命令定义和解析
- `core.py`: MCDAOrchestrator 工作流编排器

**CLI 命令**:
```bash
mcda validate config.yaml
mcda calculate config.yaml
mcda report config.yaml --output report.md
mcda sensitivity config.yaml
mcda run config.yaml  # 一键执行
```

**工作流编排**:
```python
class MCDAOrchestrator:
    """MCDA 工作流编排器"""

    def run(self, config_path: str, options: RunOptions) -> DecisionResult:
        """执行完整工作流"""
        # 1. 加载配置 → 2. 验证 → 3. 计算 → 4. 报告
        ...
```

---

### 第 2 层：核心服务层 (Core Services)
**职责**: 提供跨算法的通用服务

**基础服务**:
- **ValidationService**: 数据完整性验证、权重归一化、评分范围检查
- **ReportService**: Markdown 报告生成、JSON 导出、自定义格式支持
- **SensitivityService**: 权重扰动测试、排名变化检测、关键因素识别

**标准化服务** (ADR-002):
- MinMax, Vector, Z-Score, Sum, Logarithmic, Sigmoid 标准化

**赋权服务** (ADR-003):
- AHP, 熵权法, CRITIC, CV, 博弈论组合, PCA 主成分分析

**扩展服务** (v0.10-v0.13 新增):
- **ConstraintService** (ADR-014): 约束和否决机制
- **GroupDecisionService** (ADR-008): 群决策聚合

---

### 第 3 层：算法抽象层 (Algorithm Abstraction)
**职责**: 定义统一的算法接口，支持可插拔

**核心抽象**:
```python
from abc import ABC, abstractmethod

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
```

**算法注册机制**:
```python
# lib/algorithms/__init__.py
_algorithms: dict[str, Type[MCDAAlgorithm]] = {}

def register_algorithm(name: str) -> Callable:
    """算法注册装饰器"""
    def decorator(cls: Type[MCDAAlgorithm]) -> Type[MCDAAlgorithm]:
        _algorithms[name] = cls
        return cls
    return decorator

# 使用示例
@register_algorithm("wsm")
class WSMAlgorithm(MCDAAlgorithm):
    ...
```

**扩展点**: 添加新算法只需
1. 继承 `MCDAAlgorithm`
2. 实现 `calculate()` 方法
3. 使用 `@register_algorithm()` 装饰器

**已实现算法** (v0.13):
1. TOPSIS - 优劣解距离法（含区间版）
2. TODIM - 前景理论决策（含区间版）
3. VIKOR - 折衷排序法
4. ELECTRE-I/II - 级别优于关系（ELECTRE-I 含区间版）
5. PROMETHEE - 偏好函数排序（含区间版）
6. WPM/WSM - 加权积/和法

---

### 第 4 层：数据模型层 (Data Models)
**职责**: 定义核心数据结构，作为全系统的契约

**核心类型**:
```python
@dataclass(frozen=True)
class Criterion:
    """评价准则"""
    name: str
    weight: float
    direction: Literal["higher_better", "lower_better"]
    description: str = ""
    # v0.10 新增：标准化配置
    normalization: NormalizationConfig | None = None
    # v0.10 新增：否决配置
    veto: VetoConfig | None = None
    # v0.11 新增：评分规则
    scoring_rule: ScoringRule | None = None

@dataclass(frozen=True)
class DecisionProblem:
    """决策问题（不可变，确保数据一致性）"""
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    scores: dict[str, dict[str, float]]
    algorithm: AlgorithmConfig
    # v0.2 新增：赋权配置
    weighting: WeightingConfig | None = None

@dataclass
class DecisionResult:
    """决策结果"""
    rankings: list[RankingItem]
    raw_scores: dict[str, float]
    sensitivity: SensitivityResult | None = None
    metadata: ResultMetadata
    # v0.10 新增：否决评估结果
    veto_results: dict[str, VetoResult] = field(default_factory=dict)
```

**设计原则**:
- 使用 `frozen=True` 确保不可变性
- 使用 `Literal` 类型约束方向值
- 数据验证在 `__post_init__` 中完成

**群决策模型** (v0.6 新增):
```python
@dataclass(frozen=True)
class DecisionMaker:
    """决策者"""
    id: str
    name: str
    weight: float = 1.0
    expertise: dict[str, float] | None = None

@dataclass(frozen=True)
class GroupDecisionProblem:
    """群决策问题"""
    base_problem: DecisionProblem
    decision_makers: list[DecisionMaker]
    individual_scores: dict[str, dict[str, dict[str, float]]]
    aggregation_config: AggregationConfig | None = None
```

**区间数模型** (v0.5 新增):
```python
@dataclass(frozen=True)
class Interval:
    """区间数"""
    lower: float
    upper: float

    def __post_init__(self):
        if self.lower > self.upper:
            raise ValueError(f"Invalid interval: [{self.lower}, {self.upper}]")
```

---

### 第 5 层：功能扩展层 (Feature Extension Layer) ⭐ v2.0 新增

**职责**: 提供模块化的功能扩展，支持高级决策分析场景

**设计理念**:
- **模块化**: 每个功能独立成包，职责清晰
- **可组合**: 功能模块可灵活组合使用
- **向后兼容**: 不影响基础算法的使用

**子模块详解**:

#### 1. `aggregation/` - 聚合方法
**功能**: 实现多种评分聚合和排名聚合方法

**核心类**:
- `BordaCountAggregator`: Borda 计数法
- `CopelandAggregator`: Copeland 方法
- `WeightedAverageAggregator`: 加权平均聚合
- `WeightedGeometricAggregator`: 加权几何平均聚合

**使用场景**: 群决策偏好聚合、多源数据融合

#### 2. `group/` - 群决策
**功能**: 支持多决策者参与决策分析

**核心类**:
- `DecisionMaker`: 决策者模型
- `GroupDecisionProblem`: 群决策问题
- `GroupDecisionService`: 群决策服务

**参考**: ADR-008 (群决策聚合策略)

#### 3. `constraints/` - 约束和否决
**功能**: 支持硬约束、软约束、分级约束、组合约束

**核心类**:
- `VetoConfig`: 否决配置
- `VetoEvaluator`: 否决评估器
- `ConstraintService`: 约束服务

**参考**: ADR-014 (否决机制)

#### 4. `scoring/` - 评分规则
**功能**: 支持自定义评分规则应用

**核心类**:
- `ScoringRule`: 评分规则模型
- `ScoringRuleApplier`: 评分规则应用器

**使用场景**: 将原始分数转换为决策评分

#### 5. `ranking/` - 排名计算
**功能**: 支持可能度计算和排名方法

**核心类**:
- `PossibilityCalculator`: 可能度计算器
- `RankingCalculator`: 排名计算器

**使用场景**: 区间数排序、模糊数排序

#### 6. `visualization/` - 可视化
**功能**: 生成决策分析图表

**核心类**:
- `ChartGenerator`: 图表生成器
- `ThemeManager`: 主题管理器
- `ReportTemplate`: 报告模板

**图表类型**: 条形图、雷达图、散点图、敏感性分析图

#### 7. `reports/` - 报告生成
**功能**: 生成结构化决策报告

**核心类**:
- `ReportBuilder`: 报告构建器
- `SectionGenerator`: 章节生成器

**输出格式**: Markdown, HTML, PDF

#### 8. `export/` - 数据导出
**功能**: 导出决策数据和结果

**核心类**:
- `DataExporter`: 数据导出器
- `ResultSerializer`: 结果序列化器

**支持格式**: CSV, Excel, JSON, YAML

---

### 第 6 层：基础设施层 (Infrastructure)
**职责**: 提供底层支持和工具函数

**核心组件**:
- **YAML I/O** (`loaders/`): 配置文件加载
  - `LoaderFactory`: 加载器工厂
  - `YAMLLoader`: YAML 加载器
  - `JSONLoader`: JSON 加载器
  - **参考**: ADR-005 (Loader 抽象层)

- **工具函数** (`utils.py`):
  - 数学工具函数
  - 统计计算函数
  - 类型转换函数

- **异常定义** (`exceptions.py`):
  - `MCDAError`: 基础异常类
  - `ValidationError`: 验证错误
  - `CalculationError`: 计算错误

- **类型转换器** (`converters.py`):
  - 数据类型转换
  - 格式转换

---

## 关键设计决策

### 决策 1: 使用 dataclass(frozen=True) 作为数据模型

**选项对比**:

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **dataclass (frozen)** | 不可变、类型安全、零依赖、性能好 | 继承受限、修改需新对象 | ✅ 采用 |
| **Pydantic Model** | 强验证、JSON 序列化、易用 | 额外依赖、性能开销 | ❌ 放弃 |
| **普通类** | 灵活、无限制 | 需手写 `__init__`、易出错 | ❌ 放弃 |

**理由**:
- 符合"最小依赖"原则
- 不可变性确保数据一致性
- Python 3.12 dataclass 性能优化（10-15% 提升）

---

### 决策 2: 算法注册使用装饰器模式

**选项对比**:

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **装饰器注册** | 声明式、解耦、支持动态加载 | 需确保模块导入 | ✅ 采用 |
| **手动注册表** | 显式、易追踪 | 每次添加需修改注册代码 | ❌ 放弃 |
| **插件发现** | 自动发现、零配置 | 依赖文件系统、复杂 | ❌ 放弃 |

**理由**:
- 代码简洁，易于使用
- 在 `__init__.py` 集中导入，避免遗漏
- 支持第三方插件注册

---

### 决策 3: 验证逻辑在模型层还是服务层

**混合模式**:
```python
# 模型层: 基础验证（数据完整性）
@dataclass(frozen=True)
class DecisionProblem:
    def __post_init__(self):
        if len(self.alternatives) < 2:
            raise ValueError("至少需要 2 个备选方案")

# 服务层: 复杂验证（业务规则）
class ValidationService:
    def validate_problem(self, problem: DecisionProblem) -> ValidationResult:
        # 权重归一化、评分范围等
        ...
```

**理由**:
- 基础验证在数据创建时立即生效
- 复杂验证支持多种策略和错误收集
- 避免模型层过度复杂

---

### 决策 4: 功能扩展层的设计 (v2.0 新增)

**选项对比**:

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **独立功能扩展层** | 职责清晰、模块化、易扩展 | 增加层级 | ✅ 采用 |
| **融合到服务层** | 层级少 | 职责混乱、耦合度高 | ❌ 放弃 |
| **每个功能独立服务** | 灵活 | 服务数量爆炸 | ❌ 放弃 |

**理由**:
- 功能扩展层专门处理高级功能，不影响核心服务层
- 模块化设计便于维护和测试
- 符合单一职责原则

---

## 权衡分析 (Trade-offs)

### 正面影响 ✅
1. **可扩展性**: 添加新算法无需修改核心代码
2. **可维护性**: 各层职责清晰，修改局部化
3. **可测试性**: 每层可独立测试，Mock 友好
4. **类型安全**: 100% 类型注解，mypy --strict 通过
5. **并发安全**: 无状态算法实例，支持多线程
6. **功能模块化** (v2.0): 功能扩展层支持独立开发和测试

### 负面影响 ⚠️
1. **复杂度**: 6 层架构对小型项目可能过度设计
2. **性能**: 接口抽象带来少量性能开销（< 5%）
3. **学习曲线**: 新开发者需要理解分层架构

### 缓解措施 🛡️
1. **MVP 验证**: 先实现 WSM，验证架构可行性
2. **性能优化**: 关键路径使用 NumPy 向量化
3. **文档完善**: 提供架构图、代码示例、最佳实践
4. **渐进式演进**: 架构随需求自然演进（v1.0 → v2.0）

---

## 后果 (Consequences)

### 对开发的影响
- **新增算法**: 继承 `MCDAAlgorithm`，实现 `calculate()`，约 80-100 行代码
- **新增服务**: 在 `services/` 添加新服务类，遵循单一职责
- **新增功能模块**: 在功能扩展层创建新目录，独立开发和测试
- **修改数据模型**: 需评估对所有算法的影响，谨慎修改

### 对测试的影响
- **单元测试**: 每层独立测试，覆盖率目标 80%+
- **集成测试**: 测试层间交互（算法 → 服务 → CLI）
- **性能测试**: 使用 pytest-benchmark 建立基准

### 对部署的影响
- **零外部依赖**: 仅依赖 Python 标准库 + pyyaml + numpy
- **纯 CLI 工具**: 无需 Web 服务器，部署简单
- **跨平台**: Windows/Linux/macOS 通用

### 对架构的影响（v0.13）
- **功能扩展层** (v2.0 新增): 8 个子模块，支持高级决策分析
- **群决策功能** (ADR-008): 完整实现，153 个测试，92% 覆盖率
- **约束系统** (ADR-014): 完整实现，支持 4 种否决类型
- **可视化**: 图表生成、主题管理、报告模板
- **报告和导出**: 多格式输出支持

---

## 架构演进历史

### v1.0 (2026-01-31) - 五层架构
- 应用层 → 核心服务层 → 算法抽象层 → 数据模型层 → 基础设施层
- 支持基础算法和赋权方法
- MVP 验证架构可行性

### v2.0 (2026-02-06) - 六层架构
- 新增**功能扩展层**
- 反映 v0.10-v0.13 的实际架构演进
- 支持群决策、约束系统、可视化、报告生成

### 未来演进 (v1.0+)
- **微服务架构**: 考虑将核心服务层拆分为独立服务
- **插件系统**: 增强算法可插拔性
- **Web API**: RESTful API 接口 (如果用户需求)
- **分布式计算**: 支持大规模决策问题

---

## 参考资料
- [SOLID 原则](https://en.wikipedia.org/wiki/SOLID)
- [分层架构模式](https://patterns.eecs.berkeley.edu/?page_id=457)
- [Python 3.12 dataclass 改进](https://peps.python.org/pep-0681/)
- [插件架构设计](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-01-31 (v1.0), 2026-02-06 (v2.0)
**最后更新**: 2026-02-06（架构审查后更新）
**状态**: 已接受，v0.13 生产验证
**下一审查**: v1.0 发布后
