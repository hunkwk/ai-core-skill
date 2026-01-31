# MCDA Core - 架构设计检查点

## 📅 检查点信息
- **创建时间**: 2026-01-31
- **分支**: `feature/mcda-core`
- **阶段**: 架构设计完成，待实施
- **状态**: ✅ 架构设计完成，待开发

---

## 🎯 本次会话成果

### 已完成的架构文档

#### 1. 需求与架构分析
- ✅ **docs/requirements/mcda-core.md**
  - 用户故事（供应商选择、产品决策、人才招聘、投资分析）
  - 功能需求（0-100分制、评分规则、数据源导入）
  - 架构需求（可扩展性、可插拔性、并发安全）
  - 技术约束（Python 3.12+、最小依赖）

#### 2. 架构决策记录（ADRs）
- ✅ **docs/decisions/001-mcda-layered-architecture.md** (ADR-001)
  - 五层分层架构（应用层→核心服务层→算法抽象层→数据模型层→基础设施层）
  - 各层职责详解
  - 关键设计决策：
    - 使用 `dataclass(frozen=True)` 作为数据模型
    - 算法注册使用装饰器模式
    - 混合验证模式（模型层 + 服务层）
  - 权衡分析（正面影响、负面影响、缓解措施）

- ✅ **docs/decisions/002-mcda-normalization-methods.md** (ADR-002) ⭐ 数据层
  - **评分标准化方法**（MinMax、Vector、Z-Score 等 9 种方法）
  - **分阶段实施计划**（v0.2 → v0.3 → v0.4）
  - 标准化服务架构设计
  - 方法推荐引擎

- ✅ **docs/decisions/003-mcda-weighting-roadmap.md** (ADR-003) ⭐ 服务层
  - **赋权方法优先级排序**（8种方法：熵权法、AHP、CRITIC 等）
  - **分阶段实施计划**（v0.2 → v0.3 → v0.4）
  - 赋权服务架构设计
  - 组合赋权策略（主客观结合）

- ✅ **docs/decisions/004-mcda-aggregation-algorithms.md** (ADR-004) ⭐ 算法层
  - **评分计算引擎**（0-100 分制、Linear/Threshold 规则）
  - **数据源支持**（CSV/Excel/YAML）
  - **汇总算法**（WSM 为 MVP，预留 TOPSIS/AHP）
  - 六层分层架构（新增评分计算层）

#### 3. 详细实施计划
- ✅ **docs/plans/v0.1/mcda-core-plan.md**
  - 完整文件结构（1140 行代码预估）
  - 核心数据模型定义（`Criterion`, `DecisionProblem`, `DecisionResult`）
  - 算法接口规范（`MCDAAlgorithm` 抽象基类）
  - WSM 算法详细设计（加权求和、方向性处理）
  - 未来算法接入路径（AHP、TOPSIS）

---

## 🏗️ 架构核心设计

### 五层分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用层 (CLI)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   CLI 命令   │  │  配置解析   │  │   工作流编排            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       核心服务层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   验证服务   │  │  报告服务   │  │   敏感性分析服务        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
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
│    │   WSM     │  │   AHP     │  │  TOPSIS   │  (可插拔)       │
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
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      基础设施层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ YAML I/O    │  │  工具函数   │  │   异常定义              │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 核心数据模型

```python
@dataclass(frozen=True)
class Criterion:
    """评价准则"""
    name: str
    weight: float
    direction: Literal["higher_better", "lower_better"]
    description: str = ""

@dataclass(frozen=True)
class DecisionProblem:
    """决策问题（不可变）"""
    alternatives: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    scores: ScoreMatrix
    algorithm: AlgorithmConfig

@dataclass
class DecisionResult:
    """决策结果"""
    rankings: list[RankingItem]
    raw_scores: dict[str, float]
    metadata: ResultMetadata
    sensitivity: SensitivityResult | None = None
```

### 算法可插拔机制

```python
# 算法注册装饰器
@register_algorithm("wsm")
class WSMAlgorithm(MCDAAlgorithm):
    def calculate(self, problem: DecisionProblem) -> DecisionResult:
        # WSM 实现
        pass

# 获取算法实例
algorithm = get_algorithm("wsm")
result = algorithm.calculate(problem)
```

---

## 📊 MCDA 数据流向与 ADR 依赖关系

### 数据流向（符合 MCDA 决策流程）

```
原始数据 (Excel/CSV/YAML)
    ↓
[ADR-002: 标准化方法] ← 数据层
    ├─ MinMax, Vector, Z-Score
    └─ 输出: 标准化数据 [0, 1]
    ↓
[ADR-003: 赋权方法] ← 服务层
    ├─ 客观: 熵权法, CRITIC (依赖标准化数据)
    ├─ 主观: AHP, 德尔菲法
    └─ 输出: 权重向量
    ↓
[ADR-004: 汇总算法] ← 算法层
    ├─ WSM (加权和)
    ├─ TOPSIS (距离法)
    └─ 输出: 最终排名
```

### 标准化方法优先级（ADR-002）

| 排名 | 方法 | 热度 | 难度 | 价值 | 兼容 | **总分** | 阶段 | 工作量 |
|------|------|------|------|------|------|----------|------|--------|
| 🥇 1 | **MinMax** | 5.0 | 5.0 | 5.0 | 5.0 | **5.00** | v0.2 | 0.5人日 |
| 🥈 2 | **Vector** | 4.5 | 5.0 | 4.5 | 5.0 | **4.70** | v0.2 | 1人日 |
| 🥉 3 | **Z-Score** | 4.0 | 4.5 | 4.5 | 5.0 | **4.30** | v0.3 | 2人日 |
| 4 | **Sum** | 4.0 | 5.0 | 4.0 | 5.0 | **4.25** | v0.3 | 0.5人日 |
| 5 | **Max** | 3.0 | 5.0 | 3.5 | 5.0 | **3.80** | v0.3 | 0.5人日 |

### 赋权方法优先级（ADR-003）

| 排名 | 方法 | 热度 | 难度 | 价值 | 兼容 | **总分** | 阶段 | 工作量 |
|------|------|------|------|------|------|----------|------|--------|
| 🥇 1 | **熵权法** | 5.0 | 4.0 | 4.5 | 5.0 | **4.65** | v0.2 | 2人日 |
| 🥈 2 | **AHP** | 5.0 | 3.0 | 5.0 | 4.0 | **4.30** | v0.4 | 4人日 |
| 🥉 3 | **变异系数法** | 3.5 | 5.0 | 4.0 | 5.0 | **4.20** | v0.2 | 1人日 |
| 4 | **CRITIC 法** | 4.5 | 3.0 | 4.5 | 5.0 | **4.05** | v0.3 | 3人日 |
| 5 | **离差最大化法** | 3.5 | 4.0 | 3.5 | 5.0 | **3.85** | v0.3 | 2人日 |
| 6 | **标准离差法** | 2.5 | 5.0 | 3.5 | 5.0 | **3.70** | v0.2 | 0.5人日 |
| 7 | **德尔菲法** | 3.0 | 3.5 | 4.0 | 3.0 | **3.30** | v0.4 | 3人日 |
| 8 | **PCA** | 4.0 | 2.0 | 4.0 | 3.0 | **3.10** | v0.3 | 4人日 |

### 分阶段实施时间线

```
v0.1 (当前): WSM 算法 + 核心框架
├── 五层架构实现
├── WSM 算法
├── 数据验证、报告、敏感性分析
└── 工作量: 10-13 人日 (已完成架构设计)

v0.2 (2-3周): 基础赋权层
├── 熵权法 ⭐ (最高优先级)
├── 变异系数法
├── 标准离差法
└── 工作量: 6 人日

v0.3 (3-4周): 高级赋权层
├── CRITIC 法
├── 离差最大化法
├── PCA (可选依赖 scipy)
└── 工作量: 15 人日

v0.4 (4-5周): 主观与组合赋权层
├── AHP
├── 德尔菲法
├── 组合赋权策略
└── 工作量: 19 人日
```

**总工作量**: 40 人日 (约 10-12 周)

---

## 📂 文件清单

### 新建的架构文档

```
docs/
├── requirements/
│   └── mcda-core.md                          ✅ 已更新（架构需求）
├── decisions/
│   ├── 001-mcda-layered-architecture.md      ✅ 已完成（分层架构）
│   ├── 002-mcda-normalization-methods.md     ✅ 已完成（标准化方法）← 按数据流向编号
│   ├── 003-mcda-weighting-roadmap.md         ✅ 已完成（赋权路线图）
│   └── 004-mcda-aggregation-algorithms.md    ✅ 已完成（汇总算法）
└── plans/
    └── v0.1/
        └── mcda-core-plan.md                 ✅ 已更新（详细计划）
```

### ADR 编号逻辑（按数据流向）

| 编号 | 文档 | 层次 | 依赖关系 |
|------|------|------|----------|
| ADR-001 | 分层架构 | 基础架构 | 无依赖 |
| ADR-002 | 标准化方法 | **数据层** | 仅依赖原始数据 |
| ADR-003 | 赋权路线图 | **服务层** | 依赖标准化数据 |
| ADR-004 | 汇总算法 | **算法层** | 依赖标准化+赋权 |

---

## 🔑 关键设计决策

### 1. ADR 编号按数据流向排序
**理由**:
- **ADR-002（标准化）** 是数据层，处理原始数据，无其他依赖
- **ADR-003（赋权）** 是服务层，客观赋权法需要基于标准化后的评分矩阵计算权重
- **ADR-004（汇总）** 是算法层，需要标准化数据 + 权重才能计算最终排名

这个顺序符合 MCDA 的实际决策流程：
```
原始数据 → 标准化 → 赋权 → 汇总 → 排名
```

### 2. 计划中的代码结构（未实施）

```
skills/mcda-core/
├── SKILL.md                     ⏳ 待创建
├── SKILL_CN.md                  ⏳ 待创建
├── README.md                    ⏳ 待创建
├── README_CN.md                 ⏳ 待创建
├── LICENSE.txt                  ⏳ 待创建
├── references/                  ⏳ 待创建
│   ├── algorithms.md
│   ├── yaml-schema.md
│   ├── examples.md
│   └── sensitivity.md
└── lib/                         ⏳ 待创建
    ├── __init__.py              (20 行)
    ├── models.py                (150 行)
    ├── utils.py                 (100 行)
    ├── exceptions.py            (30 行)
    ├── validation.py            (150 行)
    ├── reporter.py              (150 行)
    ├── sensitivity.py           (200 行)
    ├── core.py                  (150 行)
    └── algorithms/
        ├── __init__.py          (40 行)
        ├── base.py              (50 行)
        └── wsm.py               (100 行)

tests/mcda-core/                 ⏳ 待创建
├── conftest.py
├── test_models.py
├── test_validation.py
├── test_reporter.py
├── test_sensitivity.py
├── test_wsm.py
├── test_integration.py
└── fixtures/
    ├── vendor_selection.yaml
    ├── product_priority.yaml
    └── invalid_weights.yaml

docs/active/
└── tdd-mcda-core.md              ⏳ 待创建（TDD 进度跟踪）
```

---

## 🔑 关键设计决策

### 1. 使用 dataclass(frozen=True) 作为数据模型
**理由**:
- 不可变性确保数据一致性
- 类型安全，IDE 支持好
- Python 3.12 性能优化（10-15% 提升）
- 零外部依赖

**权衡**: 继承受限，修改需创建新对象

### 2. 算法注册使用装饰器模式
**理由**:
- 声明式，代码简洁
- 算法实现与注册逻辑解耦
- 支持动态加载和第三方插件

**权衡**: 需确保算法模块被导入

### 3. 混合验证模式
**模型层**: 基础验证（数据完整性）
**服务层**: 复杂验证（业务规则）

**理由**: 平衡数据安全性和灵活性

### 4. 赋权方法优先级
**第一优先级**: 熵权法
- 最高热度（394+ 文献引用）
- 实现简单（2 人日）
- 与 AHP 组合最常用

**第二优先级**: AHP（留到 v0.4）
- 最高主观方法热度（694+ 引用）
- 实现复杂（4 人日）
- 需要特殊输入格式（成对比较矩阵）

---

## 🎯 下一步行动

### 立即可执行的任务

1. **创建 Git 分支**
   ```bash
   git checkout develop && git pull
   git checkout -b feature/mcda-core
   ```

2. **创建 TDD 进度文件**
   ```bash
   touch docs/active/tdd-mcda-core.md
   ```

3. **创建目录结构**
   ```bash
   mkdir -p skills/mcda-core/{references,lib/algorithms}
   mkdir -p tests/mcda-core/fixtures
   ```

4. **开始 Phase 1: 项目初始化** (30 min)
   - 编写 SKILL.md 和 SKILL_CN.md
   - 编写 README.md 和 README_CN.md
   - 创建 LICENSE.txt

5. **开始 Phase 2: 核心框架实现** (3-4 hours)
   - 实现 `lib/models.py` (数据模型)
   - 实现 `lib/validation.py` (验证服务)
   - 实现 `lib/reporter.py` (报告服务)
   - 实现 `lib/sensitivity.py` (敏感性分析)

### 实施顺序建议

**推荐路径 1: 稳健型** (推荐)
```
Phase 1: 初始化 → Phase 2: 核心框架 → Phase 3: WSM 算法
→ Phase 4: 测试 → Phase 5: 文档 → Phase 6: E2E 验证
```

**推荐路径 2: 快速原型**
```
Phase 1: 初始化 → Phase 3: WSM 算法 (简化版)
→ Phase 2: 核心框架 (反向填充) → Phase 4-6
```

---

## 📝 技术栈确认

### 编程语言
- **Python 3.12+** (利用新特性)
  - 类型系统改进 (PEP 695)
  - dataclass 增强功能
  - f-string 调试改进
  - 性能优化（10-15% 提升）

### 核心依赖
```
pyyaml>=6.0          # YAML 配置解析
numpy>=1.24          # 数值计算
pytest>=8.0          # 测试框架（支持 3.12）
pytest-cov>=4.1      # 覆盖率
```

### 可选依赖
```
scipy>=1.10          # PCA 和 AHP 高级功能
openpyxl>=3.0        # Excel 支持（v2.0）
```

---

## ⚠️ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| YAML 解析错误处理复杂 | Medium | Medium | 早期实现详细错误提示 |
| 敏感性分析算法复杂度 | Low | Low | 简化算法，限制选项数 |
| 测试覆盖率不达标 | Low | Medium | 严格 TDD 流程 |
| 文档与实现不同步 | Medium | Low | 通过进度文件跟踪 |
| 中文字符编码问题 | Low | Low | 明确 UTF-8 编码 |
| 赋权方法实施周期长 | Medium | Medium | 分阶段交付，v0.2 先交付核心功能 |

---

## 🎖️ 成功标准

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

### 架构验收
- [ ] 五层分层架构清晰
- [ ] 算法可插拔（添加新算法无需修改核心代码）
- [ ] 数据模型不可变（frozen dataclass）
- [ ] 类型安全（mypy --strict 通过）

---

## 📚 参考资料

### 架构设计
- [ADR-001: 分层架构设计](../decisions/001-mcda-layered-architecture.md)
- [ADR-002: 赋权方法路线图](../decisions/002-mcda-weighting-roadmap.md)

### 需求文档
- [MCDA Core 需求分析](../requirements/mcda-core.md)

### 实施计划
- [v0.1 详细实施计划](../plans/v0.1/mcda-core-plan.md)

### 外部参考
- [SOLID 原则](https://en.wikipedia.org/wiki/SOLID)
- [Python 3.12 dataclass 改进](https://peps.python.org/pep-0681/)
- [Comparison of Weighting Methods](https://managementpapers.polsl.pl/wp-content/uploads/2025/06/223-Wolny.pdf)

---

## 🏷️ 元数据

- **创建者**: hunkwk + AI collaboration
- **创建时间**: 2026-01-31
- **最后更新**: 2026-01-31
- **文档版本**: v1.0
- **状态**: ✅ 架构设计完成，待实施
- **下一步**: 开始 Phase 1 - 项目初始化

---

## 💾 记忆快照

### 当前项目状态

**Git 状态**:
```
当前分支: feature/mcda-core
最新提交: fff1db6 feat(mcda-core): initialize skill structure and core documentation
```

**已完成**:
- ✅ 需求分析（用户故事、功能需求、架构需求）
- ✅ 分层架构设计（五层架构、数据模型、算法接口）
- ✅ 实施计划（文件结构、模块设计、测试策略）
- ✅ 赋权方法路线图（8种方法、3个阶段、优先级排序）

**待实施**:
- ⏳ Phase 1: 项目初始化（目录、SKILL.md、README）
- ⏳ Phase 2: 核心框架实现（数据模型、验证、报告、敏感性）
- ⏳ Phase 3: WSM 算法实现
- ⏳ Phase 4: 测试实现
- ⏳ Phase 5: 文档实现
- ⏳ Phase 6: E2E 验证

**预期工作量**:
- v0.1 (WSM + 核心框架): 10-13 人日
- v0.2 (基础赋权层): 6 人日
- v0.3 (高级赋权层): 15 人日
- v0.4 (主观与组合赋权): 19 人日

**总工作量**: 40 人日 (约 10-12 周)

---

*这个检查点记录了 MCDA Core 项目在架构设计阶段的完整状态。所有关键决策、设计文档和实施计划都已就绪，可以开始进入开发阶段。*
