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
checkpoint-phase{N}.md      # Individual phase checkpoints (OPTIONAL)
checkpoint-{feature}.md     # Feature-specific checkpoints (OPTIONAL)
```

### Checkpoint Purpose

**项目里程碑**: 记录功能/项目阶段完成情况

- **Progress Tracking**: 所有关键里程碑的集中记录位置
- **Knowledge Preservation**: 捕获决策、指标和经验教训
- **Easy Review**: 单一 `checkpoint-complete.md` 查看整体进度

**Checkpoint Content Requirements**:
1. **Executive Summary**: 成就概览
2. **Implementation Details**: 关键功能和交付物
3. **Metrics**: 代码统计、测试覆盖率、开发时间
4. **Git Commits**: 相关 commit hash 和消息
5. **Lessons Learned**: 进展顺利和改进点
6. **Next Steps**: 未来增强或后续工作

**Checkpoint Creation Workflow**:
1. 完成重要里程碑（阶段/功能）
2. 运行完整测试套件并记录指标
3. 更新 `checkpoint-complete.md` 添加摘要
4. 可选：创建独立的 `checkpoint-v{version}.md` 详细记录
5. 保存 checkpoint 到 `docs/checkpoints/{feature}/` 目录
6. Git commit 并附带描述性消息
7. 更新 memory knowledge graph

**IMPORTANT**:
- `checkpoint-complete.md` 始终作为整个功能的**单一真相来源**
- 各版本 checkpoint 是可选的详细记录
- 使用 `/everything-claude-code:checkpoint` 命令提取和保存进度
- 所有 checkpoints 必须在 `docs/checkpoints/{feature}/` 中，绝不在 `docs/active/`

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
