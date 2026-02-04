# MCDA Core v0.2 MVP 执行计划

## 📋 基本信息

- **版本**: v0.2 (MVP)
- **目标**: 2 周内交付可用的 MCDA 决策分析工具
- **工作量**: 10 人日（2 周）
- **创建时间**: 2026-01-31
- **状态**: 待执行

---

## 🎯 MVP 目标

### 核心目标
1. ✅ 支持用户手动指定权重（80% 用户场景）
2. ✅ 实现基础汇总算法（WSM + WPM + TOPSIS + VIKOR）
3. ✅ 实现基础标准化方法（MinMax + Vector）
4. ✅ 完整测试覆盖（>= 80%）
5. ✅ CLI 可用性验证

### 交付标准
- [ ] YAML 配置加载和验证
- [ ] 4 种汇总算法正确计算
- [ ] 敏感性分析识别关键准则
- [ ] Markdown 报告生成
- [ ] CLI 命令正常工作
- [ ] 测试覆盖率 >= 80%

---

## 📊 功能范围

### 标准化方法（ADR-002）
| 方法 | 优先级 | 工作量 | 状态 |
|------|--------|--------|------|
| **MinMax** | P0 | 0.5 人日 | ⏳ 待实现 |
| **Vector** | P0 | 1 人日 | ⏳ 待实现 |

**总计**: 1.5 人日

### 赋权方法（ADR-003）
| 方法 | 优先级 | 工作量 | 状态 |
|------|--------|--------|------|
| **直接赋权** | P0 | 0.5 人日 | ⏳ 待实现 |

**总计**: 0.5 人日

### 汇总算法（ADR-004）
| 算法 | 中文名 | 优先级 | 工作量 | 状态 |
|------|--------|--------|--------|------|
| **WSM** | 加权算术平均 | P0 | 1 人日 | ✅ v0.1 已完成 |
| **WPM** | 加权几何平均 | P0 | 1 人日 | ✅ v0.1 已完成 |
| **TOPSIS** | 逼近理想解 | P0 | 2 人日 | ⏳ 待实现 |
| **VIKOR** | 折衷排序 | P0 | 2 人日 | ⏳ 待实现 |

**总计**: 2 人日（新增）

### 测试与文档
| 任务 | 工作量 | 状态 |
|------|--------|------|
| 单元测试 | 2 人日 | ⏳ 待实现 |
| 使用文档 | 1 人日 | ⏳ 待实现 |

**总计**: 3 人日

### 工作量汇总
- 标准化方法: 1.5 人日
- 赋权方法: 0.5 人日
- 汇总算法: 2 人日
- 测试与文档: 3 人日
- 风险缓冲: 3 人日
- **总计: 10 人日**

---

## 🗂️ 文件结构

```
skills/mcda-core/
├── SKILL.md                     # AI 执行指令（< 5000 tokens）
├── SKILL_CN.md                  # 中文 AI 执行指令
├── README.md                    # 英文开发者文档
├── README_CN.md                 # 中文开发者文档
├── LICENSE.txt                  # MIT 许可证
├── references/                  # 参考文档目录
│   ├── algorithms.md           # 算法原理说明
│   ├── yaml-schema.md          # YAML 配置模式
│   ├── examples.md             # 使用示例
│   └── sensitivity.md          # 敏感性分析说明
└── lib/                         # 核心库
    ├── __init__.py              # 公共 API 导出
    ├── models.py                # 数据模型（150 行）
    ├── utils.py                 # 工具函数（100 行）
    ├── exceptions.py            # 异常定义（30 行）
    ├── validation.py            # 验证服务（150 行）
    ├── reporter.py              # 报告服务（150 行）
    ├── sensitivity.py           # 敏感性分析（200 行）
    ├── core.py                  # 核心服务（150 行）
    ├── normalization/           # 标准化服务目录 ⭐ NEW
    │   ├── __init__.py          # 方法注册（40 行）
    │   ├── base.py              # 抽象基类（50 行）
    │   ├── minmax.py            # MinMax 标准化（60 行）
    │   └── vector.py            # Vector 标准化（80 行）
    ├── weighting/               # 赋权服务目录 ⭐ NEW
    │   ├── __init__.py          # 方法注册（30 行）
    │   ├── base.py              # 抽象基类（50 行）
    │   └── direct.py            # 直接赋权（50 行）
    └── algorithms/              # 算法实现目录
        ├── __init__.py          # 算法注册（40 行）
        ├── base.py              # 抽象基类（50 行）
        ├── wsm.py               # WSM 算法（100 行）✅
        ├── wpm.py               # WPM 算法（100 行）✅
        ├── topsis.py            # TOPSIS 算法（150 行）⭐ NEW
        └── vikor.py             # VIKOR 算法（150 行）⭐ NEW

tests/mcda-core/                 # 测试目录
├── conftest.py                  # pytest 配置和 fixtures
├── test_models.py               # 数据模型测试
├── test_validation.py           # 验证服务测试
├── test_reporter.py             # 报告服务测试
├── test_sensitivity.py          # 敏感性分析测试
├── test_normalization/          # 标准化测试 ⭐ NEW
│   ├── __init__.py
│   ├── test_minmax.py
│   └── test_vector.py
├── test_weighting/              # 赋权测试 ⭐ NEW
│   ├── __init__.py
│   └── test_direct.py
├── test_algorithms/             # 算法测试
│   ├── __init__.py
│   ├── test_wsm.py
│   ├── test_wpm.py
│   ├── test_topsis.py          # ⭐ NEW
│   └── test_vikor.py           # ⭐ NEW
└── fixtures/                    # 测试数据
    ├── vendor_selection.yaml
    ├── product_priority.yaml
    └── invalid_weights.yaml
```

**预计代码量**: 2200 行（不含测试）

---

## 📋 开发任务分解

### Phase 1: 项目初始化（0.5 天，0.5 人日）

#### Task 1.1: 创建目录结构
- [ ] 创建 `skills/mcda-core/` 及子目录
- [ ] 创建 `tests/mcda-core/` 及子目录
- [ ] 验证目录权限

#### Task 1.2: 编写基础文档
- [ ] 编写 `SKILL.md`（AI 执行指令，英文，< 5000 tokens）
- [ ] 编写 `SKILL_CN.md`（AI 执行指令，中文）
- [ ] 编写 `README.md`（英文概述）
- [ ] 编写 `README_CN.md`（中文详细说明）
- [ ] 添加 `LICENSE.txt`（MIT）

#### Task 1.3: 创建配置文件
- [ ] 创建 `pyproject.toml`（Python 3.12+，依赖管理）
- [ ] 创建 `.gitignore`

**验收标准**:
- [ ] 目录结构完整
- [ ] 所有文档符合 CLAUDE.md 规范
- [ ] SKILL.md token 数 < 5000

---

### Phase 2: 核心数据模型（0.5 天，0.5 人日）

#### Task 2.1: 实现数据模型（`lib/models.py`）
```python
# 待实现的核心模型
@dataclass(frozen=True)
class Criterion:
    """评价准则"""
    name: str
    weight: float
    direction: Literal["higher_better", "lower_better"]
    description: str = ""
    # ADR-002: 标准化配置
    normalization: NormalizationConfig | None = None

@dataclass(frozen=True)
class NormalizationConfig:
    """标准化配置"""
    method: str  # "minmax", "vector"
    params: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class WeightingConfig:
    """赋权配置"""
    method: Literal["direct"]  # MVP 只支持直接赋权
    params: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DecisionProblem:
    """决策问题（不可变）"""
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    scores: dict[str, dict[str, float]]
    algorithm: AlgorithmConfig
    weighting: WeightingConfig | None = None  # ADR-003

@dataclass
class DecisionResult:
    """决策结果"""
    rankings: list[RankingItem]
    raw_scores: dict[str, float]
    metadata: ResultMetadata
    sensitivity: SensitivityResult | None = None
```

#### Task 2.2: 实现工具函数（`lib/utils.py`）
- [ ] YAML 加载/保存函数
- [ ] 数据验证辅助函数
- [ ] 方向性处理函数

#### Task 2.3: 实现异常类（`lib/exceptions.py`）
- [ ] `MCDAValidationError` - 数据验证错误
- [ ] `MCDAAlgorithmError` - 算法执行错误
- [ ] `MCDAConfigError` - 配置错误

**验收标准**:
- [ ] 所有模型使用 `@dataclass(frozen=True)`
- [ ] 通过 `mypy --strict` 类型检查
- [ ] 单元测试覆盖所有字段

---

### Phase 3: 标准化服务（1.5 天，1.5 人日）

#### Task 3.1: 实现标准化基类（`lib/normalization/base.py`）
```python
class NormalizationMethod(ABC):
    """标准化方法基类"""

    @abstractmethod
    def normalize(
        self,
        scores: dict[str, dict[str, float]],
        criteria: tuple[Criterion, ...]
    ) -> dict[str, dict[str, float]]:
        """
        标准化评分矩阵

        Args:
            scores: {alternative: {criterion: score}}
            criteria: 评价准则列表

        Returns:
            标准化后的评分矩阵（0-1 范围）
        """
        pass
```

#### Task 3.2: 实现 MinMax 标准化（0.5 人日）
```python
@register_normalization_method("minmax")
class MinMaxNormalization(NormalizationMethod):
    """
    MinMax 标准化

    公式:
    - higher_better: (x - min) / (max - min)
    - lower_better: (max - x) / (max - min)
    """
```

**实现要点**:
- 处理 higher_better 和 lower_better
- 处理 max == min 的边界情况
- 保持精度（使用 float64）

#### Task 3.3: 实现 Vector 标准化（1 人日）
```python
@register_normalization_method("vector")
class VectorNormalization(NormalizationMethod):
    """
    Vector 标准化

    公式:
    - higher_better: x_ij / sqrt(Σ(x_ij²))
    - lower_better: 1 - x_ij / sqrt(Σ(x_ij²))

    注意: TOPSIS 必需
    """
```

**实现要点**:
- 每个准则独立归一化
- 处理全零向量
- 支持方向性反转

#### Task 3.4: 标准化服务（`lib/normalization/__init__.py`）
- [ ] 方法注册装饰器
- [ ] 方法获取函数
- [ ] 自动方法推荐

**验收标准**:
- [ ] MinMax 和 Vector 测试通过
- [ ] 边界情况处理正确
- [ ] 注册机制工作正常

---

### Phase 4: 赋权服务（0.5 天，0.5 人日）

#### Task 4.1: 实现赋权基类（`lib/weighting/base.py`）
```python
@dataclass
class WeightingResult:
    """赋权结果"""
    weights: dict[str, float]  # {criterion_name: weight}
    method: str
    metadata: dict[str, Any]

class WeightingMethod(ABC):
    """赋权方法基类"""

    @abstractmethod
    def calculate(
        self,
        problem: DecisionProblem,
        **kwargs
    ) -> WeightingResult:
        pass
```

#### Task 4.2: 实现直接赋权（`lib/weighting/direct.py`）
```python
@register_weighting_method("direct")
class DirectWeightingMethod(WeightingMethod):
    """
    直接赋权

    用户在 YAML 中直接指定 weight 字段
    """
    def calculate(self, problem: DecisionProblem, **kwargs) -> WeightingResult:
        # 从 criteria 中提取权重
        weights = {c.name: c.weight for c in problem.criteria}
        # 验证权重和为 1
        self._validate_weights_sum(weights)
        return WeightingResult(weights=weights, method="direct", metadata={})
```

**验收标准**:
- [ ] 从 Criteria 提取权重
- [ ] 验证权重和为 1（误差 < 1e-6）
- [ ] 抛出清晰错误信息

---

### Phase 5: TOPSIS 算法（2 天，2 人日）

#### Task 5.1: 实现 TOPSIS 核心算法（`lib/algorithms/topsis.py`）
```python
@register_algorithm("topsis")
class TOPSISAlgorithm(MCDAAlgorithm):
    """
    TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

    步骤:
    1. Vector 标准化（必需）
    2. 构建加权标准化矩阵
    3. 确定理想解和负理想解
    4. 计算距离（D+ 和 D-）
    5. 计算相对贴近度
    6. 排序
    """
```

**实现要点**:
- 依赖 Vector 标准化（自动应用）
- 支持方向性处理
- 欧氏距离计算
- 处理零权重

#### Task 5.2: 单元测试（`tests/test_algorithms/test_topsis.py`）
- [ ] 测试 Vector 标准化应用
- [ ] 测试理想解/负理想解计算
- [ ] 测试距离计算
- [ ] 测试排名正确性
- [ ] 测试边界情况

**验收标准**:
- [ ] 与文献中的计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 6: VIKOR 算法（2 天，2 人日）

#### Task 6.1: 实现 VIKOR 核心算法（`lib/algorithms/vikor.py`）
```python
@register_algorithm("vikor")
class VIKORAlgorithm(MCDAAlgorithm):
    """
    VIKOR (VIseKriterijumska Optimizacija I Kompromisno Resenje)

    步骤:
    1. 确定最佳和最差值（f* 和 f-）
    2. 计算 S（群体效用值）和 R（个别遗憾值）
    3. 计算 Q（折衷排序值）
    4. 排序

    参数:
    - v: 策略权重（默认 0.5，v > 0.5 强调最大效用）
    """
```

**实现要点**:
- 支持 MinMax 或 Vector 标准化
- 计算 S、R、Q 三个指标
- 支持策略权重参数 v
- 提供折衷解解释

#### Task 6.2: 单元测试（`tests/test_algorithms/test_vikor.py`）
- [ ] 测试 S/R/Q 计算
- [ ] 测试 v 参数影响
- [ ] 测试折衷解识别
- [ ] 测试排名稳定性

**验收标准**:
- [ ] 唯一折衷解算法
- [ ] 测试覆盖率 >= 80%

---

### Phase 7: 验证和报告服务（0.5 天，0.5 人日）

#### Task 7.1: 完善验证服务（`lib/validation.py`）
- [ ] YAML 配置验证
- [ ] 权重和验证（误差 < 1e-6）
- [ ] 评分完整性检查
- [ ] 算法参数验证

#### Task 7.2: 完善报告服务（`lib/reporter.py`）
- [ ] Markdown 报告生成
- [ ] 排名表格展示
- [ ] 敏感性分析结果展示
- [ ] 算法参数说明

**验收标准**:
- [ ] 验证错误信息清晰
- [ ] Markdown 报告可读性强

---

### Phase 8: 单元测试（2 天，2 人日）

#### Task 8.1: 核心功能测试
- [ ] `test_models.py` - 数据模型测试
- [ ] `test_validation.py` - 验证服务测试
- [ ] `test_reporter.py` - 报告服务测试

#### Task 8.2: 标准化测试
- [ ] `test_normalization/test_minmax.py`
- [ ] `test_normalization/test_vector.py`

#### Task 8.3: 赋权测试
- [ ] `test_weighting/test_direct.py`

#### Task 8.4: 算法测试
- [ ] `test_algorithms/test_topsis.py`
- [ ] `test_algorithms/test_vikor.py`

**验收标准**:
- [ ] 所有测试通过
- [ ] 测试覆盖率 >= 80%
- [ ] 无 skipped tests

---

### Phase 9: 集成测试（0.5 天，0.5 人日）

#### Task 9.1: 端到端测试
- [ ] 完整决策流程测试（YAML → 结果）
- [ ] 多算法对比测试
- [ ] 错误处理测试

#### Task 9.2: 性能测试
- [ ] 10 个准则 x 50 个方案性能测试
- [ ] 内存占用测试

**验收标准**:
- [ ] 集成测试通过
- [ ] 性能满足要求（< 1 秒）

---

### Phase 10: 使用文档（1 天，1 人日）

#### Task 10.1: 参考文档（`references/`）
- [ ] `algorithms.md` - 算法原理说明
- [ ] `yaml-schema.md` - YAML 配置模式
- [ ] `examples.md` - 使用示例
- [ ] `sensitivity.md` - 敏感性分析说明

#### Task 10.2: 示例配置（`tests/fixtures/`）
- [ ] `vendor_selection.yaml` - 供应商选择案例
- [ ] `product_priority.yaml` - 产品优先级案例
- [ ] `invalid_weights.yaml` - 错误配置案例

**验收标准**:
- [ ] 文档清晰易懂
- [ ] 示例可运行

---

### Phase 11: CLI 接口（0.5 天，0.5 人日）

#### Task 11.1: 实现 CLI（`lib/cli.py`）
```bash
# CLI 命令设计
mcda analyze <config.yaml>      # 分析决策问题
mcda validate <config.yaml>     # 验证配置
mcda sensitivity <config.yaml>  # 敏感性分析
mcda --help                     # 帮助信息
```

**验收标准**:
- [ ] CLI 命令正常工作
- [ ] 错误处理完善

---

### Phase 12: 代码审查和优化（0.5 天，0.5 人日）

#### Task 12.1: 代码质量
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过
- [ ] 代码格式化（`black`）

#### Task 12.2: 性能优化
- [ ] 瓶颈识别（`cProfile`）
- [ ] 关键路径优化

**验收标准**:
- [ ] 无类型错误
- [ ] 无 lint 警告

---

### Phase 13: E2E 验证（0.5 天，0.5 人日）

#### Task 13.1: 真实案例验证
- [ ] 供应商选择案例
- [ ] 产品优先级案例
- [ ] 人才招聘案例

#### Task 13.2: 文档完整性检查
- [ ] README 可运行
- [ ] 示例正确
- [ ] CLI 帮助信息完整

**验收标准**:
- [ ] 所有案例通过
- [ ] 文档无错误

---

## 🔍 验收标准

### 功能验收
- [ ] YAML 配置加载和验证
- [ ] 4 种汇总算法（WSM + WPM + TOPSIS + VIKOR）正确计算
- [ ] 2 种标准化方法（MinMax + Vector）正确实现
- [ ] 直接赋权方法正确工作
- [ ] 敏感性分析识别关键准则
- [ ] Markdown 报告生成
- [ ] CLI 命令正常工作

### 质量验收
- [ ] 测试覆盖率 >= 80%
- [ ] 所有 pytest 测试通过
- [ ] 文档符合 CLAUDE.md 规范
- [ ] SKILL.md token 数 < 5000
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过

### 流程验收
- [ ] Git Flow 规范遵循
- [ ] TDD 进度文件维护（`docs/active/tdd-mcda-core-mvp.md`）
- [ ] Conventional Commits 规范

### 架构验收
- [ ] 五层分层架构清晰
- [ ] 算法可插拔（添加新算法无需修改核心代码）
- [ ] 数据模型不可变（frozen dataclass）
- [ ] 标准化和赋权服务独立

---

## ⚠️ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| TOPSIS 算法实现复杂度超预期 | Medium | Medium | 预留 0.5 天缓冲，参考文献实现 |
| VIKOR 折衷解理解偏差 | Medium | Low | 文献验证，多个案例测试 |
| 测试覆盖率不达标 | Low | Medium | 严格 TDD，每个算法独立测试 |
| Vector 标准化边界情况 | Low | Low | 单元测试覆盖全零向量等边界 |
| 文档编写时间不足 | Low | Low | 复用架构文档，分阶段完善 |

---

## 📅 时间线

| 日期 | 阶段 | 交付物 |
|------|------|--------|
| Day 1 | Phase 1-2 | 项目初始化，数据模型 |
| Day 2 | Phase 3 | 标准化服务（MinMax + Vector）|
| Day 3 | Phase 4 | 赋权服务（直接赋权）|
| Day 4-5 | Phase 5 | TOPSIS 算法 |
| Day 6-7 | Phase 6 | VIKOR 算法 |
| Day 8 | Phase 7-9 | 验证/报告/集成测试 |
| Day 9 | Phase 10-11 | 文档和 CLI |
| Day 10 | Phase 12-13 | 代码审查和 E2E 验证 |

---

## 📝 参考资料

### 架构文档
- [ADR-001: 分层架构设计](../../decisions/001-mcda-layered-architecture.md)
- [ADR-002: 标准化方法](../../decisions/002-mcda-normalization-methods.md)
- [ADR-003: 赋权方法路线图](../../decisions/003-mcda-weighting-roadmap.md)
- [ADR-004: 汇总算法架构设计](../../decisions/004-mcda-aggregation-algorithms.md)

### 需求文档
- [MCDA Core 需求分析](../../requirements/mcda-core.md)

### 检查点文档
- [架构设计检查点](../../active/checkpoint-mcda-core-architecture.md)

### 外部参考
- [TOPSIS 算法原理](https://en.wikipedia.org/wiki/TOPSIS)
- [VIKOR 算法原理](https://en.wikipedia.org/wiki/VIKOR_method)

---

**创建者**: hunkwk + AI collaboration
**创建时间**: 2026-01-31
**最后更新**: 2026-01-31
**文档版本**: v1.0
**状态**: 待执行
**下一步**: 开始 Phase 1 - 项目初始化
