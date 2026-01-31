# ADR-004: MCDA 汇总算法架构设计

## 状态
**已接受 (Accepted)**

## 日期
2026-01-31

## 上下文 (Context)
MCDA Core v1.0 设计中，用户需要直接提供各准则的评分（1-5 分制），但存在以下问题：

1. **评分制不够直观**: 1-5 分制不够精细，难以反映细微差异
2. **缺少评分转换能力**: 用户需要手动将原始数据（成本 20 万、响应时间 300ms）转换为评分
3. **数据源单一**: 仅支持 YAML 配置，Excel/CSV 等常见格式无法直接使用

### 用户需求反馈
- "希望能用 0-100 分制，更符合百分制习惯"
- "希望能配置评分规则，自动从原始值计算评分"
- "希望能直接导入 Excel 数据，不用手动转 YAML"

## 决策 (Decision)

### 1. 六层分层架构（新增评分计算层）

在原有五层架构基础上，在核心服务层和算法抽象层之间插入**评分计算层**：

```
应用层 (CLI)
    ↓
核心服务层 (Validation, Reporter, Sensitivity, DataSource)
    ↓
评分计算层 (ScoringEngine) ← NEW
    ↓
算法抽象层 (MCDAAlgorithm 基类)
    ↓
数据模型层 (DecisionProblem, DecisionResult)
    ↓
基础设施层 (YAML/CSV/Excel I/O, Utils)
```

**理由**:
- 评分是算法的通用前置步骤（所有算法都需要评分）
- 保持算法层纯粹性（只负责权重聚合）
- 便于独立测试和复用

### 2. 评分范围改为 0-100 分制

**原**: 1-5 分制（Likert scale）
**新**: 0-100 分制（百分制）

**影响**:
- ✅ 更直观，符合日常习惯
- ✅ 精度更高，能区分细微差异
- ✅ 方便归一化处理
- ⚠️ 需要更新验证逻辑

**实施**:
```python
# 修改前
ScoreRange = tuple[int, int]  # (1, 5)

# 修改后
ScoreRange = tuple[float, float]  # (0.0, 100.0)
```

### 3. 支持评分规则配置

新增 `ScoringRule` 数据模型，支持多种评分规则类型：

#### 3.1 线性评分规则（LinearScoringRule）
```yaml
scoring_rule:
  type: linear
  min: 0          # 最小值
  max: 100        # 最大值
  scale: 100      # 满分值
```

**公式**:
- `higher_better`: `score = scale * (value - min) / (max - min)`
- `lower_better`: `score = scale * (1 - (value - min) / (max - min))`

**示例**: 成本 0-100 万元
```
成本 20 万 → score = 100 * (1 - 20/100) = 80 分
成本 50 万 → score = 100 * (1 - 50/100) = 50 分
```

#### 3.2 阈值评分规则（ThresholdScoringRule）
```yaml
scoring_rule:
  type: threshold
  ranges:
    - {max: 100, score: 100}        # < 100ms → 100 分
    - {min: 100, max: 500, score: 80}   # 100-500ms → 80 分
    - {min: 500, max: 1000, score: 60}  # 500-1000ms → 60 分
    - {min: 1000, score: 40}        # > 1000ms → 40 分
  default_score: 20
```

#### 3.3 数据模型定义
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

@dataclass(frozen=True)
class Criterion:
    """评价准则（v2.0）"""
    name: str
    weight: float
    direction: Direction
    scoring_rule: ScoringRule | None = None  # 新增
    column: str | None = None                # 新增：映射到数据源列名
```

### 4. 支持 Excel/CSV 数据导入

#### 4.1 数据源配置
```yaml
data_source:
  type: csv
  file: data/vendor_data.csv
  encoding: utf-8

# 或 Excel
data_source:
  type: excel
  file: data/vendor_data.xlsx
  sheet: 决策数据
```

#### 4.2 数据加载器接口
```python
class DataSourceLoader(ABC):
    """数据源加载器基类"""
    @abstractmethod
    def can_handle(self, source: DataSource) -> bool:
        pass

    @abstractmethod
    def load(self, source: DataSource) -> dict[str, dict[str, float | str]]:
        """返回原始数据矩阵 {alternative: {criterion: raw_value}}"""
        pass

class CSVDataSourceLoader(DataSourceLoader):
    """CSV 加载器（使用标准库 csv 模块）"""
    pass

class ExcelDataSourceLoader(DataSourceLoader):
    """Excel 加载器（使用 openpyxl，可选依赖）"""
    pass
```

#### 4.3 Excel 示例
```
| 方案   | 成本(万元) | 响应时间(ms) | 功能数 | 稳定性(%) |
|--------|-----------|-------------|--------|----------|
| AWS    | 20        | 150         | 10     | 99.9     |
| Azure  | 50        | 80          | 20     | 99.5     |
| GCP    | 35        | 120         | 15     | 99.7     |
```

#### 4.4 依赖决策
| 依赖 | 用途 | 是否必需 | 备注 |
|------|------|---------|------|
| **csv** (标准库) | CSV 解析 | 必需 | 零依赖 |
| **openpyxl** | Excel 支持 | 可选 | 按需安装 |
| **pandas** | 数据处理 | 不推荐 | 过重 |

**决策**:
- CSV 支持（必需）：使用 Python 标准库
- Excel 支持（可选）：使用 `openpyxl`，未安装时友好提示
- 不使用 pandas（违反最小依赖原则）

---

## 核心接口设计

### ScoringEngine（评分计算引擎）
```python
class ScoringEngine:
    """评分计算引擎"""

    def calculate(
        self,
        raw_value: float | str | int,
        criterion: Criterion
    ) -> float:
        """根据评分规则计算评分（0-100）"""
        if criterion.scoring_rule is None:
            raise ScoringError(f"准则 '{criterion.name}' 未配置评分规则")

        numeric_value = self._to_numeric(raw_value)
        rule = criterion.scoring_rule

        if isinstance(rule, LinearScoringRule):
            return rule.calculate(numeric_value, criterion.direction)
        elif isinstance(rule, ThresholdScoringRule):
            return rule.calculate(numeric_value, criterion.direction)
        else:
            raise ScoringError(f"不支持的评分规则类型: {type(rule)}")

    def calculate_batch(
        self,
        raw_data: dict[str, dict[str, float | str]],
        criteria: tuple[Criterion, ...]
    ) -> dict[str, dict[str, float]]:
        """批量计算评分"""
        scores = {}
        for alt, raw_values in raw_data.items():
            scores[alt] = {}
            for criterion in criteria:
                if criterion.name not in raw_values:
                    continue
                raw_value = raw_values[criterion.name]
                scores[alt][criterion.name] = self.calculate(raw_value, criterion)
        return scores
```

### ScoringService（评分服务）
```python
class ScoringService:
    """评分服务（对外接口）"""

    def apply_scoring_rules(
        self,
        problem: DecisionProblem
    ) -> dict[str, dict[str, float]]:
        """应用评分规则，生成评分矩阵

        工作流程：
        1. 如果有 raw_data，使用评分规则计算
        2. 如果已有 scores，验证 0-100 范围
        3. 返回标准化的评分矩阵
        """
        if problem.raw_data is not None:
            return self._engine.calculate_batch(
                problem.raw_data,
                problem.criteria
            )
        elif problem.scores is not None:
            return self._validate_score_range(problem.scores, problem.score_range)
        else:
            raise ScoringError("决策问题必须包含 raw_data 或 scores")
```

### DataSourceService（数据源服务）
```python
class DataSourceService:
    """数据源服务"""

    def load(self, source: DataSource) -> dict[str, dict[str, float | str]]:
        """加载数据源

        支持格式：
        - yaml: YAML 配置文件
        - csv: CSV 表格文件
        - excel: Excel 工作表（需 openpyxl）
        """
        for loader in self._loaders:
            if loader.can_handle(source):
                return loader.load(source)
        raise ValueError(f"不支持的数据源类型: {source.type}")
```

---

## 权衡分析 (Trade-offs)

### 决策 1: 评分计算层的位置

| 选项 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **核心服务层** | 复用好，所有算法共享 | 职责过重，违反单一职责 | ❌ |
| **独立层（推荐）** | 职责清晰，易测试和扩展 | 增加一层抽象 | ✅ 采用 |
| **算法抽象层** | 算法可自定义评分 | 代码重复，不一致 | ❌ |

**决策**: 独立层，理由：
1. 评分是算法的通用前置步骤
2. 保持算法层纯粹（只负责聚合）
3. 便于单元测试

### 决策 2: Excel 支持方式

| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| **标准库 csv + 可选 openpyxl** | 轻量、按需安装 | Excel 功能受限 | ✅ 采用 |
| **pandas** | 功能强大、统一接口 | 依赖重（100MB+） | ❌ 放弃 |
| **仅 CSV，不支持 Excel** | 最轻量 | 用户体验差 | ❌ 放弃 |

### 决策 3: 评分规则类型

| 类型 | 适用场景 | 复杂度 | 是否支持 |
|------|---------|--------|---------|
| **Linear** | 连续数值（成本、时间、百分比） | 低 | ✅ v0.1 |
| **Threshold** | 分段评分（等级划分） | 中 | ✅ v0.1 |
| **Inverse** | 反向映射（lower_better 专用） | 低 | ⏳ v0.2 |
| **Custom** | 自定义函数 | 高 | ⏳ v0.3 |

---

## 实施影响

### 数据模型变更
```python
# 修改前
@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float
    direction: Direction
    description: str = ""

# 修改后
@dataclass(frozen=True)
class Criterion:
    name: str
    weight: float
    direction: Direction
    description: str = ""
    scoring_rule: ScoringRule | None = None  # NEW
    column: str | None = None                # NEW
```

### YAML 配置示例（v2.0）
```yaml
data_source:
  type: excel
  file: data/vendor_data.xlsx
  sheet: 决策数据

alternatives:
  - AWS
  - Azure
  - GCP

criteria:
  - name: 成本
    weight: 0.35
    direction: lower_better
    column: 成本(万元)        # 映射到 Excel 列
    scoring_rule:
      type: linear
      min: 0
      max: 100
      scale: 100

  - name: 响应时间
    weight: 0.20
    direction: lower_better
    column: 响应时间
    scoring_rule:
      type: threshold
      ranges:
        - {max: 100, score: 100}
        - {min: 100, max: 500, score: 80}
        - {min: 500, max: 1000, score: 60}
        - {min: 1000, score: 40}

algorithm:
  name: wsm
```

### 新增文件
- `lib/scoring.py` - 评分计算引擎
- `lib/data_source.py` - 数据源服务
- `tests/test_scoring.py` - 评分引擎测试
- `tests/test_data_source.py` - 数据源测试

### 修改文件
- `lib/models.py` - 扩展数据模型
- `lib/validation.py` - 更新 0-100 验证
- `lib/algorithms/wsm.py` - 无需实质修改（WSM 算法与评分范围无关）

---

## 后果 (Consequences)

### 正面影响 ✅
1. **用户体验提升**: 0-100 分制更直观
2. **自动化程度提高**: 评分规则自动计算，无需手动转换
3. **数据来源灵活**: 支持 Excel/CSV，降低使用门槛
4. **扩展性增强**: 新增评分规则类型无需修改核心代码

### 负面影响 ⚠️
1. **复杂度增加**: 新增评分计算层，理解成本上升
2. **实施周期延长**: 预计增加 4-5 小时开发时间
3. **依赖管理**: Excel 支持需要处理可选依赖

### 缓解措施 🛡️
1. **渐进式披露**: 基础使用无需评分规则（直接提供 scores）
2. **文档完善**: 提供评分规则配置示例
3. **友好提示**: 未安装 openpyxl 时给出安装指引
4. **单元测试**: 确保评分引擎测试覆盖率 ≥ 85%

---

## 未来演进

### v0.1 (MVP)
- ✅ 0-100 分制
- ✅ LinearScoringRule
- ✅ ThresholdScoringRule
- ✅ CSV 支持（标准库）
- ✅ Excel 支持（可选 openpyxl）

### v0.2
- ⏳ InverseScoringRule
- ⏳ 更多阈值规则类型
- ⏳ Google Sheets 导入

### v0.3
- ⏳ CustomScoringRule（自定义函数）
- ⏳ 评分规则模板库
- ⏳ 数据验证增强（异常值检测）

---

## 参考资料
- [ADR-001: MCDA Core 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-002: 评分标准化方法](./002-mcda-normalization-methods.md)
- [ADR-003: 赋权方法路线图](./003-mcda-weighting-roadmap.md)
- [Python csv 模块文档](https://docs.python.org/3/library/csv.html)
- [openpyxl 文档](https://openpyxl.readthedocs.io/)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-01-31
**状态**: 已接受，v0.1 实施
