# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

---

## 🎯 Critical Guidelines

### Language & Documentation ⚠️

**Communication Rules:**
- **Conversation**: Chinese (中文)
- **Code Comments**: Chinese (中文)
- **Technical Terms**: English (variables, functions, technical nouns)

**Documentation Standards:**
- **Project Level**: `README.md` (English, concise) + `README_CN.md` (Chinese, detailed)
- **Skill Level**:
  - `README.md` / `README_CN.md` - Full documentation for developers
  - `SKILL.md` / `SKILL_CN.md` - AI execution instructions (minimal tokens, ruthless optimization)

**Core Principles:**
- SKILL files = Only essential AI instructions, ruthless optimization
- README files = Full explanations, examples, best practices
- Token budget is precious - every character must justify its existence

### System Environment
- **OS**: Windows (win32)
- **Shell**: Command Prompt / PowerShell
- **Commands**: Windows syntax (use Bash tool for compatibility)

**WSL2 Environment Notes**:
- 实际运行环境是 WSL2 (Linux)，使用 Linux 命令语法
- 双路径映射: `/mnt/d/...` (Windows) ↔ `/home/wangke/...` (WSL)
- Python 虚拟环境: `.venv_linux/` (WSL) 或 `.venv/` (Windows)
- 常用命令: `ls`, `grep`, `find`, `jq` (Linux 工具)

---

## 📁 Project Root Directory Structure

**根目录文件组织原则**: 保持简洁，只保留核心配置和文档

### Standard Layout

```
ai_core_skill/                       # 项目根目录
├── AGENTS.md                       # ✅ AI Agent 工作指南（项目级）
├── CHANGELOG.md                    # ✅ 变更日志
├── CLAUDE.md                       # ✅ 本文件（AI 指导）
├── LICENSE                         # ✅ 许可证
├── README.md / README_CN.md        # ✅ 项目说明（如有）
├── package.json                   # ✅ Node.js 配置
├── pytest.ini                      # ✅ pytest 配置
├── .gitignore / .coverage          # Git & 测试覆盖率
│
├── docs/                           # 📚 文档目录
│   ├── archive/                   # 归档旧文档（CHECKPOINT-PHASE3.md 等）
│   ├── checkpoints/               # ✅ 项目里程碑 checkpoints
│   ├── active/                    # ✅ 执行进度追踪
│   ├── plans/                     # 规划文档
│   └── decisions/                 # ADR 架构决策记录
│
├── skills/                        # 💡 技能模块目录
│   ├── mcda-core/                # MCDA Core 技能
│   │   ├── lib/                   # 核心代码
│   │   │   ├── algorithms/       # 排序算法
│   │   │   ├── services/         # 权重计算服务
│   │   │   └── visualization/   # 可视化
│   │   ├── tests/                # 测试文件
│   │   ├── reports/              # 测试报告
│   │   ├── README.md / README_CN.md
│   │   ├── SKILL.md / SKILL_CN.md
│   │   └── install_mcda.py       # 安装脚本
│   └── [other skills...]
│
└── tests/                         # 🧪 测试目录（如有全局测试）
    └── [test files...]
```

### File Placement Rules

**根目录应只包含**:
- ✅ **核心配置文件**: `.gitignore`, `package.json`, `pytest.ini`
- ✅ **项目级文档**: `AGENTS.md`, `CHANGELOG.md`, `CLAUDE.md`, `LICENSE`
- ✅ **项目说明**: `README.md` (如有)
- ❌ **不应该有**: 临时文件、旧文档、测试脚本、实现代码

**文档归档到 `docs/archive/`**:
- ✅ 旧阶段的 checkpoint 文件
- ✅ 旧阶段的总结文档
- ✅ 已完成阶段的临时文档

**测试脚本放到 `tests/{feature}/`**:
- ✅ `run_*.py` 测试运行脚本
- ✅ `test_*.py` 测试文件
- ✅ `fix_*.py` 修复脚本

**安装脚本放到 `skills/{skill}/`**:
- ✅ `install_*.py` 安装脚本

**IMPORTANT**:
- 根目录保持**简洁清晰** - 只包含配置和文档
- 所有实现代码在 `skills/` 下
- 所有测试在 `tests/` 下
- 旧文档归档到 `docs/archive/`

### 测试目录结构

**测试组织原则**: 按测试类型（单元测试/集成测试）和功能模块分层组织

```
tests/                             # 测试根目录
├── mcda-core/                    # MCDA Core 功能测试
│   ├── __init__.py              # 包初始化
│   ├── conftest.py              # pytest 全局配置和共享 fixtures
│   ├── fixtures/                # 测试数据文件
│   ├── reports/                 # 测试报告和覆盖率报告
│   ├── .archive/                # 已归档的旧测试文件（临时脚本等）
│   ├── README.md                # 测试目录说明文档
│   │
│   ├── unit/                    # 单元测试（28个文件）
│   │   ├── test_algorithms/     # 算法单元测试
│   │   │   ├── test_electre1.py
│   │   │   ├── test_promethee2_service.py
│   │   │   ├── test_todim.py
│   │   │   ├── test_topsis.py
│   │   │   ├── test_topsis_interval.py
│   │   │   ├── test_vikor.py
│   │   │   ├── test_wpm.py
│   │   │   └── test_wsm.py
│   │   │
│   │   ├── test_core/           # 核心模块单元测试
│   │   │   ├── test_converters.py
│   │   │   ├── test_exceptions.py
│   │   │   ├── test_interval.py
│   │   │   ├── test_models.py
│   │   │   ├── test_reporter.py
│   │   │   ├── test_sensitivity.py
│   │   │   ├── test_utils.py
│   │   │   └── test_validation.py
│   │   │
│   │   ├── test_loaders/        # 数据加载器测试
│   │   │   ├── test_json_integration.py
│   │   │   └── test_loaders.py
│   │   │
│   │   ├── test_normalization/  # 标准化方法测试
│   │   │   ├── test_logarithmic_normalizer.py
│   │   │   ├── test_sigmoid_normalizer.py
│   │   │   └── test_normalization.py
│   │   │
│   │   ├── test_scoring/        # 评分规则测试
│   │   │   └── test_scoring_models.py
│   │   │
│   │   ├── test_services/       # 服务层测试
│   │   │   ├── test_ahp_service.py
│   │   │   ├── test_comparison_service.py
│   │   │   └── test_entropy_weight_service.py
│   │   │
│   │   ├── test_visualization/  # 可视化测试
│   │   │   └── test_ascii_visualizer.py
│   │   │
│   │   └── test_weighting/      # 权重计算测试
│   │       ├── test_critic_weighting.py
│   │       ├── test_cv_weighting.py
│   │       └── test_game_theory_weighting.py
│   │
│   └── integration/             # 集成测试（8个文件）
│       ├── test_cli/            # CLI 集成测试
│       │   ├── test_cli.py
│       │   └── test_import.py
│       ├── test_e2e.py         # 端到端测试
│       ├── test_integration.py # 集成测试
│       └── test_customer_*.py  # 客户评分测试（2个）
│
└── [其他功能的测试目录...]
```

**测试运行命令**:
```bash
# 运行所有测试
pytest tests/mcda-core/

# 只运行单元测试
pytest tests/mcda-core/unit/

# 只运行集成测试
pytest tests/mcda-core/integration/

# 运行特定模块测试
pytest tests/mcda-core/unit/test_algorithms/

# 使用标记运行
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
pytest -m algorithms    # 算法测试
```

**测试文件放置规则**:
- ✅ **单元测试**: `tests/{feature}/unit/test_{module}/`
- ✅ **集成测试**: `tests/{feature}/integration/`
- ✅ **测试数据**: `tests/{feature}/fixtures/`
- ✅ **测试报告**: `tests/{feature}/reports/`
- ❌ **不应该有**: 临时调试脚本（移动到 `.archive/temp_scripts/`）

---

## 📚 Documentation Structure

Centralized documentation in `docs/` directory for AI-human collaboration.

### Directory Layout

```
docs/
├── README.md / README_CN.md        # Documentation index
│
├── requirements/                    # **Requirements analysis** (by feature)
│   ├── README.md
│   ├── README_CN.md
│   └── {feature}/                  # Feature-specific requirements
│       ├── requirements.md         # Feature requirements document
│       └── README.md               # Feature requirements index
│
├── decisions/                       # **Architecture Decision Records (ADR)** (by feature)
│   ├── README.md                   # ADR index
│   ├── template.md                 # ADR template
│   ├── README_CN.md
│   └── {feature}/                  # Feature-specific ADRs
│       ├── 001-design-decision.md
│       ├── 002-api-design.md
│       └── README.md
│
├── plans/                           # **Implementation plans** (by feature + version)
│   ├── README.md                   # Plans index
│   ├── roadmap.md                  # Version roadmap
│   └── {feature}/
│       ├── v0.1/
│       │   ├── execution-plan.md   # Version-specific plan
│       │   └── summary.md
│       ├── v0.2/
│       └── v0.3/
│
├── active/                          # **Execution progress tracking** (by feature + version)
│   ├── README.md
│   ├── README_CN.md
│   └── {feature}/
│       ├── v0.1/
│       │   ├── tdd-feature-x.md    # TDD progress tracking
│       │   ├── fix-bug-y.md        # Bug fix tracking
│       │   └── refactor-target.md  # Refactoring tracking
│       └── v0.2/
│
├── reports/                         # **Test reports & analysis** (by feature + version)
│   ├── README.md                   # Reports index
│   ├── README_CN.md
│   └── {feature}/
│       ├── v0.1/
│       │   └── test-report-v0.1.0.md
│       └── v0.2/
│           └── test-report-v0.2.0.md
│
├── checkpoints/                     # **Project milestone checkpoints** (by feature)
│   ├── README.md                   # Checkpoints index
│   └── {feature}/
│       ├── checkpoint-complete.md  # Unified complete feature checkpoint (REQUIRED)
│       ├── checkpoint-v0.3-phase2.md  # Version/phase checkpoint (OPTIONAL)
│       └── checkpoint-v0.3.md      # Version checkpoint (OPTIONAL)
│
└── archive/                         # **Archived documents** (by feature)
    └── {feature}/                  # Old documents moved here after completion
        ├── old-phase-docs/
        └── deprecated-plans/
```

### Documentation Architecture Principles

**核心原则**: 按文档特性选择分层策略

#### 类型 A: Feature 子目录（不包含版本号）

**适用场景**: 永久性、跨版本、积累型文档

| 目录 | 用途 | 示例 |
|------|------|------|
| `requirements/{feature}/` | 功能需求分析 | `mcda-core/requirements.md` |
| `decisions/{feature}/` | 架构决策记录（ADR） | `mcda-core/001-api-design.md` |
| `checkpoints/{feature}/` | 项目里程碑 | `mcda-core/checkpoint-complete.md` |
| `archive/{feature}/` | 归档旧文档 | `mcda-core/old-plans/` |

**特点**:
- ✅ 跨版本共享
- ✅ 随时间积累
- ✅ 不需要版本隔离

#### 类型 B: Feature + Version 子目录（包含版本号）

**适用场景**: 临时性、版本隔离、迭代型文档

| 目录 | 用途 | 示例 |
|------|------|------|
| `plans/{feature}/v{version}/` | 版本执行计划 | `mcda-core/v0.4/execution-plan.md` |
| `active/{feature}/v{version}/` | 版本开发进度 | `mcda-core/v0.4/tdd-todim.md` |
| `reports/{feature}/v{version}/` | 版本测试报告 | `mcda-core/v0.4/test-report.md` |

**特点**:
- ✅ 版本隔离清晰
- ✅ 完成后归档到 `archive/`
- ✅ 便于回溯历史版本

### File Naming Conventions

#### Progress Files (`active/`)
```
tdd-{feature-name}.md           # TDD development (RED → GREEN → REFACTOR → DONE)
fix-{bug-name}.md               # Bug fix (REPRODUCING → DIAGNOSING → FIXING → VERIFYING → DONE)
refactor-{target}.md            # Refactoring tasks
```

#### Test Reports (`reports/`)
```
test-report-v{version}.md       # Version-specific test report
test-report-{date}.md           # Date-specific test report
```

#### Checkpoints (`checkpoints/`)
```
checkpoint-complete.md          # Unified complete feature checkpoint (REQUIRED)
checkpoint-v{version}.md        # Version checkpoint (OPTIONAL)
checkpoint-v{version}-phase{N}.md  # Phase checkpoint (OPTIONAL)
```

#### ADR Files (`decisions/`)
```
{number}-{short-title}.md       # Architecture Decision Record
# Example: 002-mcda-algorithms-architecture.md
```

### Status Tracking

**Progress Status**:
- **TDD**: `RED | GREEN | REFACTOR | DONE`
- **Bug Fix**: `REPRODUCING | DIAGNOSING | FIXING | VERIFYING | DONE`
- **Refactoring**: `PLANNING | IN_PROGRESS | REVIEW | DONE`

**Document Status**:
- **Plans**: `DRAFT | APPROVED | IN_PROGRESS | COMPLETED | ARCHIVED`
- **Requirements**: `DRAFT | REVIEWED | APPROVED | IMPLEMENTED`
- **ADR**: `PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED`

### Test Reports (`tests/` directory)

**Test Report Location**:
- Test reports MUST be in `tests/{feature}/reports/` directory
- Report naming: `test-report-v{version}.md` or `test-report-{date}.md`

**Example Structure**:
```
tests/
├── mcda-core/
│   ├── test_*.py                    # Test files
│   ├── fixtures/                    # Test fixtures
│   └── reports/                     # **Test reports directory**
│       ├── README.md                # Reports index
│       └── test-report-v0.2.1.md   # Version-specific test report
```

**Test Report Content Requirements**:
1. **Test Summary**: Total tests, passed, failed, coverage
2. **Changes**: What's new in this version
3. **Bug Fixes**: List of bugs fixed
4. **Performance**: Execution time, benchmarks
5. **Comparison**: Metrics compared to previous version
6. **Known Issues**: Any warnings or limitations

**IMPORTANT**:
- Test reports are separate from project checkpoints
- Checkpoints (`docs/checkpoints/`) record project milestones
- Test reports (`tests/*/reports/`) record testing outcomes
- Use test reports for version releases and quality assurance

### Checkpoint Files

**Checkpoint Documentation** (`checkpoints/`):
```
checkpoint-complete.md      # Unified complete project checkpoint (REQUIRED)
checkpoint-v{version}.md    # Version checkpoint (OPTIONAL)
checkpoint-v{version}-phase{N}.md  # Phase checkpoint (OPTIONAL)
```

### Checkpoint Purpose

**项目里程碑**: 记录功能/项目阶段完成情况

- **Progress Tracking**: 所有关键里程碑的集中记录位置
- **Knowledge Preservation**: 捕获决策、指标和经验教训
- **Easy Review**: 单一 `checkpoint-complete.md` 查看整体进度
- **Team Alignment**: 统一的项目进度和成就视图

**Checkpoint Content Requirements**:

#### 必需内容 (Required)

1. **📊 Executive Summary**
   - 项目总览（名称、状态、最新版本）
   - 核心指标（测试数、覆盖率、代码行数）
   - 当前状态概述

2. **🎯 Version Milestones**
   - 所有版本的完成情况（v0.1 → v0.N）
   - 每个版本的功能清单
   - 测试统计和质量指标
   - Git 提交 hash

3. **📈 Cumulative Achievements**
   - 累计测试统计（所有版本汇总）
   - 算法库/功能清单
   - 代码量统计（实现、测试、文档）
   - 质量指标趋势

4. **🏆 Quality Metrics**
   - 代码质量评分
   - 测试覆盖率趋势
   - 性能指标
   - 开发效率

5. **🎓 Lessons Learned**
   - 成功经验（⭐⭐⭐⭐⭐ 评分）
   - 改进建议
   - 技术债务

6. **🚀 Git Commit History**
   - 关键提交记录
   - 当前分支状态
   - 总提交数

7. **🎯 Future Planning**
   - 下一版本规划
   - 长期目标
   - 技术路线图

#### 可选内容 (Optional)

8. **📂 Project Structure** - 项目结构图
9. **🔧 Tech Stack** - 技术栈清单
10. **📝 ADR References** - 架构决策链接
11. **🎉 Achievements** - 成就解锁清单
12. **📊 Project Health** - 项目健康度评分

**Checkpoint Creation Workflow**:

#### 标准流程 (MUST Follow)

```bash
# 1. 完成重要里程碑（版本/阶段完成）
# 例如：v0.6 所有 phase 完成并测试通过

# 2. 运行完整测试套件并记录指标
pytest tests/{feature}/ --cov=skills/{feature}/lib --cov-report=term-missing

# 3. 收集版本信息
git log --oneline -10                    # 最近提交
git log --oneline --all | grep -i "v0.6" # 版本相关提交
find tests/{feature}/ -name "test_*.py" | wc -l  # 测试数量

# 4. 更新 checkpoint-complete.md
# 添加新版本的内容到对应章节
# - 更新 "🎯 Version Milestones" 章节
# - 更新 "📈 Cumulative Achievements" 统计
# - 更新 "🚀 Git Commit History" 提交记录
# - 在 "🎯 Future Planning" 添加下一步计划

# 5. Git commit checkpoint
git add docs/checkpoints/{feature}/checkpoint-complete.md
git commit -m "docs({feature}): 更新 checkpoint-complete.md - v0.6 完成"

# 6. 更新 memory knowledge graph（可选）
# 使用 MCP memory 工具记录关键成就
```

#### 创建时机 (WHEN to Create)

✅ **必须创建 Checkpoint 的情况**:
- 版本完成（v0.1, v0.2, ... v0.N）
- 重大功能完成（如群决策功能）
- 项目阶段性总结（Phase 1-N 完成）
- 项目质量评估或报告

⏸️ **可以延迟创建的情况**:
- 小 bug 修复（不创建新 checkpoint，更新现有即可）
- 文档更新（无需 checkpoint）
- 代码重构（除非是重大重构）

#### Checkpoint 质量标准

**质量检查清单**:
- ✅ 包含所有必需章节（7 个必需内容）
- ✅ 版本信息完整（功能、测试、Git commit）
- ✅ 累计统计准确（测试总数、代码行数）
- ✅ Git 提交记录正确
- ✅ 格式统一（使用章节标题和表格）
- ✅ 中文叙述，技术术语保持英文
- ✅ 无拼写错误和格式错误

**IMPORTANT**:
- `checkpoint-complete.md` 始终作为整个功能的**单一真相来源**
- 各版本 checkpoint 是可选的详细记录，但推荐创建
- 每次完成版本后**必须更新** `checkpoint-complete.md`
- 所有 checkpoints 必须在 `docs/checkpoints/{feature}/` 中，绝不在 `docs/active/`
- Checkpoint 文件使用 **Markdown 格式**，便于版本控制和审查
- Checkpoint 是**项目文档**，不是进度文件（进度在 `docs/active/`）

### Archive Purpose

**归档旧文档**: 保存已完成的版本文档

**归档内容**:
- ✅ 旧版本的 `active/` 进度文件
- ✅ 旧版本的 `plans/` 执行计划
- ✅ 旧版本的 `reports/` 测试报告
- ✅ 过时的参考文档

**归档时机**:
- 版本发布并创建 checkpoint 后
- 文档内容被新版本替代后
- 临时文档不再需要引用后

**归档结构**:
```
archive/{feature}/
├── v0.1/                    # 版本归档
│   ├── active/             # 旧 active 文件
│   ├── plans/              # 旧 plans
│   └── reports/            # 旧 reports
└── deprecated/             # 废弃文档
    └── old-design.md
```

### Maintenance

- Use `/update-docs` command for automatic documentation updates
- AI maintains progress files in `active/{feature}/v{version}/` directory
- Archive completed versions to `archive/{feature}/v{version}/`
- Follow [CLAUDE.md](../CLAUDE.md) specifications

### Documentation Workflow

**新建版本开发流程**:
```
1. 创建 plans/{feature}/v{version}/execution-plan.md
2. 创建 active/{feature}/v{version}/ (空目录)
3. 开始开发，AI 在 active/ 下创建进度文件
4. 完成后创建 reports/{feature}/v{version}/test-report.md
5. 更新 checkpoints/{feature}/checkpoint-complete.md
6. 归档: mv active/{feature}/v{version}/ archive/{feature}/v{version}/active/
```

**文档生命周期**:
```
plans (draft) → active (in_progress) → reports (completed) → archive (historical)
                ↓
         checkpoints (milestones)
```

### Quick Reference

| 文档类型 | 目录位置 | 是否包含版本 | 归档时机 |
|---------|---------|-------------|---------|
| 需求文档 | `requirements/{feature}/` | ❌ | 不归档（持续更新） |
| 架构决策 | `decisions/{feature}/` | ❌ | 不归档（状态标记为 DEPRECATED） |
| 执行计划 | `plans/{feature}/v{version}/` | ✅ | 版本完成后 |
| 进度追踪 | `active/{feature}/v{version}/` | ✅ | 版本完成后 |
| 测试报告 | `reports/{feature}/v{version}/` | ✅ | 版本完成后 |
| 里程碑 | `checkpoints/{feature}/` | ❌ | 不归档（持续积累） |
| 旧文档 | `archive/{feature}/v{version}/` | ✅ | 永久归档 |

### Example: MCDA-Core Feature

**完整目录结构**:
```
docs/
├── requirements/
│   └── mcda-core/
│       ├── requirements.md
│       └── README.md
├── decisions/
│   └── mcda-core/
│       ├── 001-algorithms-architecture.md
│       ├── 002-normalization-methods.md
│       ├── 003-weighting-roadmap.md
│       └── README.md
├── plans/
│   └── mcda-core/
│       ├── v0.1/
│       ├── v0.2/
│       ├── v0.3/
│       └── v0.4/
│           └── advanced-features-execution-plan.md
├── active/
│   └── mcda-core/
│       └── v0.4/
│           ├── tdd-todim.md
│           └── fix-electre-kernel.md
├── reports/
│   └── mcda-core/
│       ├── v0.1/
│       ├── v0.2/
│       └── v0.3/
│           └── test-report-v0.3.md
├── checkpoints/
│   └── mcda-core/
│       ├── checkpoint-complete.md
│       ├── checkpoint-v0.3-phase2.md
│       └── checkpoint-v0.3-complete.md
└── archive/
    └── mcda-core/
        ├── v0.1/
        │   ├── active/
        │   ├── plans/
        │   └── reports/
        └── v0.2/
            ├── active/
            ├── plans/
            └── reports/
```

---

## 📁 Skills Directory Structure

Based on `skills/skill-creator/` reference.

### Standard Structure

```
skills/
├── skill-creator/
│   ├── README.md           # English overview (developers)
│   ├── README_CN.md        # Chinese detailed version
│   ├── SKILL.md            # AI instructions (minimal tokens)
│   ├── SKILL_CN.md         # Chinese AI instructions (minimal)
│   ├── LICENSE.txt         # Optional
│   ├── references/         # Optional: workflows, patterns
│   └── scripts/            # Optional: automation scripts
├── plan/
│   ├── README.md
│   ├── README_CN.md
│   ├── SKILL.md
│   └── SKILL_CN.md
└── ...                     # 22 skills total (flat structure)
```

### Required Files (per skill)

**README.md** - English overview for developers
- Brief introduction
- Quick examples
- Link to Chinese version

**README_CN.md** - Chinese detailed documentation
- Complete feature introduction
- Detailed usage examples
- Best practices

**SKILL.md** - AI execution instructions (English)
- Frontmatter: name, description, license
- Body: ONLY essential workflows
- Critical: Minimal tokens, no explanations

**SKILL_CN.md** - Chinese AI instructions
- Mirror of SKILL.md
- Equally minimalist

### Core Principles

1. **SKILL Files = AI Instructions Only**
   - Remove ALL explanations, examples, verbose content
   - ONLY operational instructions
   - Assume Claude knows programming concepts

2. **README Files = Human Documentation**
   - Full explanations, examples, best practices
   - Link README (human) ↔ SKILL (AI)

3. **Flat Structure**
   - All skills at first level under `skills/`
   - No nested subdirectories

---

## Available Commands (22 total)

### Core Development
- `/plan` - Create implementation plans
- `/tdd` - Test-driven development (RED → GREEN → REFACTOR)
- `/code-review` - Security and quality review
- `/build-fix` - Fix build errors
- `/e2e` - End-to-end tests with Playwright

### Go Language
- `/go-test` - TDD for Go projects
- `/go-review` - Review Go idiomatic patterns
- `/go-build` - Fix Go build errors

### Learning & Evolution
- `/learn` - Extract patterns from sessions
- `/evolve` - Cluster patterns into skills/agents
- `/skill-create` - Create skills from git history

### Instinct Management
- `/instinct-export` - Export instincts
- `/instinct-import` - Import instincts
- `/instinct-status` - Show learned instincts

### Utility
- `/refactor-clean` - Remove dead code
- `/checkpoint` - Create checkpoints
- `/verify` - Verify implementations
- `/eval` - Evaluation framework (EDD)
- `/test-coverage` - Check test coverage
- `/orchestrate` - Coordinate agents
- `/setup-pm` - Configure plan mode
- `/update-codemaps` - Update code maps
- `/update-docs` - Update documentation

---

## Auto-Invoked Agents (12 total)

- **architect** - System design & scalability
- **planner** - Feature breakdown & risk assessment
- **build-error-resolver** - TypeScript/JS build errors
- **go-build-resolver** - Go build errors
- **code-reviewer** - Code quality & security
- **go-reviewer** - Go idiomatic patterns
- **database-reviewer** - PostgreSQL optimization
- **security-reviewer** - OWASP Top 10 vulnerabilities
- **tdd-guide** - Enforce TDD with 80%+ coverage
- **e2e-runner** - E2E testing with Vercel Agent Browser
- **refactor-cleaner** - Dead code removal
- **doc-updater** - Auto-update documentation

---

---

## 🔧 Configuration Management

### 全局 vs 项目级配置

**配置层级**:
1. **全局配置** (`~/.claude/settings.json`) - 所有项目共享
2. **项目配置** (`.claude/settings.local.json`) - 项目特定
3. **MCP 配置** (`.mcp.json`) - 项目级 MCP 服务器

**配置合并策略**: 项目配置覆盖并扩展全局配置

**推荐原则**:
- **通用工具全局化**: ralph-loop, claude-md-management, github MCP
- **技术工具项目级**: pyright-lsp, typescript-lsp, frontend-design
- **最佳平衡**: 灵活性 + 一致性

### Git Configuration Files

**应该提交到 Git 的配置**:
- ✅ `.mcp.json` - 项目 MCP 服务器配置
- ✅ `.claude/settings.local.json` - 团队共享配置
- ✅ `.claude/permissions.json` - 权限管理配置

**不应该提交的配置**:
- ❌ `~/.claude/settings.json` - 全局个人配置
- ❌ GitHub Token - 已通过环境变量设置

### 配置迁移最佳实践

**何时迁移到全局**:
- ✅ 纯个人工具（ralph-loop, claude-md-management）
- ✅ 所有项目都需要（github MCP 如果主要用 GitHub）
- ✅ 轻量级插件（不影响性能）

**保留在项目级**:
- ⚠️ 语言特定工具（pyright-lsp, typescript-lsp）
- ⚠️ 框架特定工具（frontend-design）
- ⚠️ 项目特定 MCP（npm MCP）

**迁移流程**:
1. 备份现有配置
2. 更新 `~/.claude/settings.json`
3. 从项目配置移除重复项
4. 重启 Claude Code
5. 验证功能正常

### 配置示例

**全局配置** (`~/.claude/settings.json`):
```json
{
  "enabledPlugins": {
    "everything-claude-code": true,
    "ralph-loop": true,
    "claude-md-management": true
  },
  "mcpServers": {
    "memory": { ... },
    "github": { ... }
  }
}
```

**项目配置** (`.claude/settings.local.json`):
```json
{
  "enabledPlugins": {
    "pyright-lsp": true
  },
  "mcpServers": {
    "npm": { ... }
  }
}
```

### GitHub MCP 集成

**设置 GitHub Token**:
```bash
# 生成 Token: https://github.com/settings/tokens
# 权限: repo (完整仓库访问)
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**可用工具** (80+ 个):
- `mcp__github__search_code` - 搜索代码
- `mcp__github__search_issues` - 查询 Issues
- `mcp__github__create_issue` - 创建 Issue
- `mcp__github__create_pull_request` - 创建 PR
- `mcp__github__get_file_contents` - 获取文件
- `mcp__github__push_files` - 推送文件

**使用示例**:
```bash
# 搜索特定文件
mcp__github__search_code "q=pytest+language:python"

# 查询开放 Issues
mcp__github__search_issues "state=open"

# 获取仓库信息
mcp__github__get_repository_info
```

### 项目配置模板

**Python 项目** (`.claude/settings.local.json`):
```json
{
  "enabledPlugins": {
    "pyright-lsp@claude-plugins-official": true
  }
}
```

**Node.js/TypeScript 项目**:
```json
{
  "enabledPlugins": {
    "typescript-lsp@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true
  },
  "enabledMcpjsonServers": ["npm"],
  "mcpServers": {
    "npm": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-npm"]
    }
  }
}
```

**前端项目**:
```json
{
  "enabledPlugins": {
    "typescript-lsp@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true
  },
  "enabledSkills": {
    "plugin:claude-plugins-official:frontend-design:frontend-design": true
  }
}
```

### 故障排除

**配置不生效**:
- 重启 Claude Code 会话
- 检查 JSON 语法是否正确
- 运行验证脚本: `bash ~/.claude/verify_migration.sh`

**MCP 服务器连接失败**:
- 检查网络连接
- 验证 Token 是否正确: `echo $GITHUB_TOKEN`
- 查看 MCP 服务器日志

**Token 权限不足**:
- 确保 Token 有 `repo` 权限
- 重新生成 Token 并选择完整权限
- 更新 `~/.bashrc` 并执行 `source ~/.bashrc`

**恢复备份配置**:
```bash
# 恢复全局配置
cp ~/.claude/backup/settings.json.backup.* ~/.claude/settings.json

# 恢复项目配置
cp .claude/settings.local.json.backup.* .claude/settings.local.json
```

---

## 🔀 Git Flow Workflow

Simplified Git Flow optimized for individual developer + AI collaboration.

### Branch Strategy

```
main           → Production branch (always deployable)
develop        → Development integration branch
feature/xxx    → New features (from develop)
fix/xxx        → Bug fixes (from develop)
hotfix/xxx     → Emergency fixes (from main)
experiment/xxx → Experimental features (can be discarded)
```

### Branch Naming Convention

**重要原则**: 分支名称**不包含版本号**，版本号通过文档和标签管理

- `feature/<short-desc>` - 新功能开发（e.g., `feature/user-auth`, `feature/mcda-core`）
- `fix/<issue-desc>` - Bug修复（e.g., `fix/login-crash`）
- `hotfix/<urgent-desc>` - 紧急生产修复（e.g., `hotfix/payment-failure`）
- `experiment/<name>` - 实验性功能（e.g., `experiment/ai-suggestions`）

**规则**:
- 小写字母
- 连字符分隔
- 简洁描述（2-3个单词）
- **feature开发分支不加版本号**（❌ `feature/mcda-v0.3` → ✅ `feature/mcda-core`）

**版本管理**:
- 版本号通过 `docs/plans/{project}/v{version}/` 管理
- 版本进度通过 `docs/active/{project}/v{version}/` 追踪
- 发布时使用 Git Tag（如 `v0.3.0`）

### Conventional Commits

Format: `<type>(<scope>): <subject>`

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code formatting
- `refactor` - Code refactoring
- `perf` - Performance optimization
- `test` - Testing related
- `chore` - Build/tooling changes

**Example**:
```
feat(ai): add semantic search capability

- Implement vector-based pattern matching
- Add comprehensive tests (90% coverage)
- Update documentation
```

### Workflows

**Feature Development**:
```bash
git checkout develop && git pull
git checkout -b feature/your-feature
# /plan  # For complex features
# /tdd   # Test-driven development
# Run tests and lint before commit
git commit -m "feat: add xxx"
git push
git checkout develop && git merge feature/your-feature
```

**Bug Fix**:
```bash
git checkout develop
git checkout -b fix/bug-name
# /tdd  # Write failing test first
# ... fix ...
git commit -m "fix: resolve xxx issue"
```

**Emergency Fix**:
```bash
git checkout main
git checkout -b hotfix/critical-fix
# ... quick fix ...
git commit -m "hotfix: urgent fix for xxx"
git checkout main && git merge hotfix/critical-fix
git checkout develop && git merge hotfix/critical-fix
```

### Best Practices

1. **Keep branches short-lived** - Feature branches ≤ 3 days
2. **Atomic commits** - One change per commit
3. **Frequent integration** - Merge to develop regularly
4. **Clean up** - Delete merged branches
5. **Keep develop deployable** - Always in working state

---

## Development Workflow

1. `/plan` - Create implementation approach
2. AI creates progress file in `docs/active/{task-name}.md`
3. `/tdd` - Implement with tests (updates progress file)
4. `/code-review` - Review before commit
5. Agents auto-activate based on task
6. `/update-docs` - Update documentation after completion
7. `/learn` - Extract patterns for future

**Progress Tracking**:
- AI maintains `docs/active/{task-name}.md` during execution
- Updates status: RED → GREEN → REFACTOR → DONE (TDD)
- Documents decisions, blockers, and solutions
- Moves completed tasks to `docs/reports/` on completion

---

## Plugin Configuration

**Plugin**: `everything-claude-code` (v1.2.0)
- 22 commands in `.claude/skills/`
- 12 agents in `.claude/agents/`

Locally copied for immediate availability.
