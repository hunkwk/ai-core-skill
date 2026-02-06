# AGENTS.md

Guidelines for agentic coding agents working in this repository.

## Project Overview

This is an AI development project with multi-language support (TypeScript/JavaScript and Go) using the everything-claude-code plugin v1.2.0.

## Communication & Documentation Standards

### Language Rules

- **Conversation**: Chinese (中文)
- **Code Comments**: Chinese (中文)
- **Technical Terms**: English (variables, functions, technical nouns)

### Documentation Standards

- **Project Level**: `README.md` (English, concise) + `README_CN.md` (Chinese, detailed)
- **Skill Level**:
  - `README.md` / `README_CN.md` - Full documentation for developers
  - `SKILL.md` / `SKILL_CN.md` - AI execution instructions (minimal tokens, ruthless optimization)

**Core Principles:**

- SKILL files = Only essential AI instructions, ruthless optimization
- README files = Full explanations, examples, best practices
- Token budget is precious - every character must justify its existence

## System Environment

- **OS**: Windows (win32)
- **Shell**: Command Prompt / PowerShell
- **Commands**: Windows syntax (use Bash tool for compatibility)

## Project Directory Structure

### Root Directory Organization

**根目录文件组织原则**: 保持简洁，只保留核心配置和文档

```
ai_core_skill/                       # 项目根目录
├── AGENTS.md                       # ✅ AI Agent 工作指南（项目级）
├── CHANGELOG.md                    # ✅ 变更日志
├── CLAUDE.md                       # ✅ AI 指导文件
├── LICENSE                         # ✅ 许可证
├── README.md / README_CN.md        # ✅ 项目说明
├── package.json                   # ✅ Node.js 配置
├── pytest.ini                      # ✅ pytest 配置
├── .gitignore / .coverage          # Git & 测试覆盖率
│
├── docs/                           # 📚 文档目录
│   ├── archive/                   # 归档旧文档
│   ├── checkpoints/               # ✅ 项目里程碑 checkpoints
│   ├── active/                    # ✅ 执行进度追踪
│   ├── plans/                     # 规划文档
│   ├── decisions/                 # ADR 架构决策记录
│   └── requirements/              # 需求分析文档
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

- ✅ 核心配置文件: `.gitignore`, `package.json`, `pytest.ini`
- ✅ 项目级文档: `AGENTS.md`, `CHANGELOG.md`, `CLAUDE.md`, `LICENSE`
- ✅ 项目说明: `README.md`
- ❌ 不应该有: 临时文件、旧文档、测试脚本、实现代码

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

## Test Directory Structure

### Test Organization Principles

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
│   ├── unit/                    # 单元测试
│   │   ├── test_algorithms/     # 算法单元测试
│   │   ├── test_core/           # 核心模块单元测试
│   │   ├── test_loaders/        # 数据加载器测试
│   │   ├── test_normalization/  # 标准化方法测试
│   │   ├── test_scoring/        # 评分规则测试
│   │   ├── test_services/       # 服务层测试
│   │   ├── test_visualization/  # 可视化测试
│   │   └── test_weighting/      # 权重计算测试
│   │
│   └── integration/             # 集成测试
│       ├── test_cli/            # CLI 集成测试
│       ├── test_e2e.py         # 端到端测试
│       └── test_integration.py # 集成测试
│
└── [其他功能的测试目录...]
```

### Test Execution Commands

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

### Test File Placement Rules

- ✅ 单元测试: `tests/{feature}/unit/test_{module}/`
- ✅ 集成测试: `tests/{feature}/integration/`
- ✅ 测试数据: `tests/{feature}/fixtures/`
- ✅ 测试报告: `tests/{feature}/reports/`
- ❌ 不应该有: 临时调试脚本（移动到 `.archive/temp_scripts/`）

## Skills Directory Structure

All skills located in `skills/` directory with flat structure (no nested subdirectories).

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

## Available Commands

Use these slash commands when appropriate:

- `/plan` - Create implementation plans for new features
- `/tdd` - Test-driven development workflow (RED → GREEN → REFACTOR)
- `/go-test` - TDD workflow specifically for Go code
- `/code-review` - Comprehensive code review for security and quality
- `/build-fix` - Fix TypeScript/JavaScript build errors
- `/go-build` - Fix Go build errors and vet issues
- `/e2e` - Generate and run end-to-end tests with Playwright
- `/test-coverage` - Check test coverage metrics
- `/verify` - Run full verification loop
- `/learn` - Extract patterns from completed work

## Build/Lint/Test Commands

### TypeScript/JavaScript

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run single test file
npm test <path/to/test.ts>

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Build project
npm run build

# Lint code
npm run lint

# Type check
npm run typecheck
```

### Go

```bash
# Run all tests
go test ./...

# Run tests for specific package
go test ./package/...

# Run single test
go test -run TestFunctionName ./package

# Run tests with coverage
go test -cover ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Build project
go build ./...

# Vet code
go vet ./...

# Format code
go fmt ./...

# Run with race detection
go test -race ./...
```

## Code Style Guidelines

### General

- Write tests FIRST (TDD workflow mandatory)
- Target 80%+ test coverage (100% for critical code)
- Run lint and typecheck after completing work
- Never commit secrets or API keys
- Follow existing patterns in the codebase

### TypeScript/JavaScript

**Formatting:**

- Use the project's Prettier configuration
- Use single quotes for strings
- Use 2 spaces for indentation
- Max line length: 100 characters

**Naming:**

- Functions: camelCase (`calculateScore`)
- Classes: PascalCase (`UserService`)
- Constants: UPPER_SNAKE_CASE for true constants
- Interfaces: PascalCase with `I` prefix optional (`IUserData` or `UserData`)
- Types: PascalCase (`MarketData`)
- Files: camelCase for utilities, PascalCase for components

**Imports:**

- Group imports: built-ins → external → internal
- Use absolute imports for cross-module references
- Prefer named exports over default exports

**Error Handling:**

- Use explicit error types, not generic `Error`
- Always handle Promise rejections
- Use early returns to reduce nesting
- Log errors with context before throwing

**Types:**

- Prefer `interface` over `type` for object shapes
- Use strict TypeScript settings
- Avoid `any`, use `unknown` when type is uncertain
- Define return types on public functions

### Go

**Formatting:**

- Use `gofmt` for all Go files
- Use `goimports` to manage imports
- Max line length: 100 characters

**Naming:**

- Packages: lowercase, single word (`validator`, not `emailValidator`)
- Functions: PascalCase for exported, camelCase for internal
- Variables: camelCase (short names in small scopes: `i`, `n`, `err`)
- Constants: camelCase or PascalCase depending on export
- Interfaces: end with `er` when appropriate (`Reader`, `Writer`)

**Imports:**

- Group: standard library → third-party → internal
- Use blank imports only when necessary (with comment)
- Avoid dot imports

**Error Handling:**

- Return errors as last value, check immediately
- Use sentinel errors for specific error types
- Wrap errors with context using `fmt.Errorf("...: %w", err)`
- Never ignore errors (at minimum log them)

**Testing:**

- Use table-driven tests
- Name tests: `TestFunctionName` or `TestType_Method`
- Use `t.Helper()` in test helpers
- Use `t.Parallel()` for independent tests
- Test files: `*_test.go` in same package

## Testing Requirements

### Coverage Targets

- Critical business logic: 100%
- Public APIs: 90%+
- General code: 80%+
- Generated code: Exclude from coverage

### Test Patterns

**TypeScript/JavaScript:**

```typescript
describe('functionName', () => {
  it('should handle edge case', () => {
    // Arrange
    const input = {...}
    // Act
    const result = functionName(input)
    // Assert
    expect(result).toBe(expected)
  })
})
```

**Go:**

```go
func TestFunctionName(t *testing.T) {
  tests := []struct {
    name    string
    input   Type
    want    Type
    wantErr bool
  }{
    {"case 1", input1, want1, false},
  }
  for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
      got, err := Function(tt.input)
      if (err != nil) != tt.wantErr {
        t.Errorf("error = %v, wantErr %v", err, tt.wantErr)
      }
      if got != tt.want {
        t.Errorf("got %v, want %v", got, tt.want)
      }
    })
  }
}
```

## Development Workflow

1. **Plan**: Use `/plan` for complex features
2. **TDD**: Write tests first, then implement
3. **Verify**: Run tests and coverage checks
4. **Review**: Use `/code-review` before committing
5. **Learn**: Use `/learn` to extract patterns

## Git Flow Workflow

This project follows a simplified Git Flow workflow optimized for individual developer + AI collaboration.

### Branch Strategy

```
main         → Production branch (always deployable)
develop      → Development integration branch
feature/xxx  → New features (from develop)
fix/xxx      → Bug fixes (from develop)
hotfix/xxx   → Emergency fixes (from main)
experiment/xxx → Experimental features (can be discarded)
```

### Branch Naming Convention

- `feature/<short-desc>` - New feature development (e.g., `feature/user-auth`)
- `fix/<issue-desc>` - Bug fixing (e.g., `fix/login-crash`)
- `hotfix/<urgent-desc>` - Emergency production fix (e.g., `hotfix/payment-failure`)
- `experiment/<name>` - Experimental features (e.g., `experiment/ai-suggestions`)

**Rules**: lowercase, hyphen-separated, concise (2-3 words)

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

### Git Aliases (Optional)

```bash
git config --global alias.feature '!f() { git checkout develop && git pull && git checkout -b "feature/$1"; }; f'
git config --global alias.fix '!f() { git checkout develop && git pull && git checkout -b "fix/$1"; }; f'
git config --global alias.hotfix '!f() { git checkout main && git pull && git checkout -b "hotfix/$1"; }; f'
git config --global alias.finish '!f() { git checkout develop && git merge @{-1} && git branch -d @{-1}; }; f'

# Usage: git feature user-auth
```

## Documentation Architecture

### Directory Layout

```
docs/
├── requirements/                    # Requirements analysis (by feature)
│   └── {feature}/                  # Feature-specific requirements
│       ├── requirements.md         # Feature requirements document
│       └── README.md               # Feature requirements index
│
├── decisions/                       # Architecture Decision Records (ADR) (by feature)
│   ├── template.md                 # ADR template
│   └── {feature}/                  # Feature-specific ADRs
│       ├── 001-design-decision.md
│       └── README.md
│
├── plans/                           # Implementation plans (by feature + version)
│   └── {feature}/
│       └── v{version}/
│           ├── execution-plan.md   # Version-specific plan
│           └── summary.md
│
├── active/                          # Execution progress tracking (by feature + version)
│   └── {feature}/
│       └── v{version}/
│           ├── tdd-feature-x.md    # TDD progress tracking
│           ├── fix-bug-y.md        # Bug fix tracking
│           └── refactor-target.md  # Refactoring tracking
│
├── reports/                         # Test reports & analysis (by feature + version)
│   └── {feature}/
│       └── v{version}/
│           └── test-report-v0.1.0.md
│
├── checkpoints/                     # Project milestone checkpoints (by feature)
│   └── {feature}/
│       ├── checkpoint-complete.md  # Unified complete feature checkpoint (REQUIRED)
│       └── checkpoint-v0.3.md      # Version checkpoint (OPTIONAL)
│
└── archive/                         # Archived documents (by feature)
    └── {feature}/                  # Old documents moved here after completion
```

### Documentation Architecture Principles

**核心原则**: 按文档特性选择分层策略

#### 类型 A: Feature 子目录（不包含版本号）

**适用场景**: 永久性、跨版本、积累型文档

| 目录                      | 用途                | 示例                               |
| ------------------------- | ------------------- | ---------------------------------- |
| `requirements/{feature}/` | 功能需求分析        | `mcda-core/requirements.md`        |
| `decisions/{feature}/`    | 架构决策记录（ADR） | `mcda-core/001-api-design.md`      |
| `checkpoints/{feature}/`  | 项目里程碑          | `mcda-core/checkpoint-complete.md` |
| `archive/{feature}/`      | 归档旧文档          | `mcda-core/old-plans/`             |

**特点**:

- ✅ 跨版本共享
- ✅ 随时间积累
- ✅ 不需要版本隔离

#### 类型 B: Feature + Version 子目录（包含版本号）

**适用场景**: 临时性、版本隔离、迭代型文档

| 目录                            | 用途         | 示例                               |
| ------------------------------- | ------------ | ---------------------------------- |
| `plans/{feature}/v{version}/`   | 版本执行计划 | `mcda-core/v0.4/execution-plan.md` |
| `active/{feature}/v{version}/`  | 版本开发进度 | `mcda-core/v0.4/tdd-todim.md`      |
| `reports/{feature}/v{version}/` | 版本测试报告 | `mcda-core/v0.4/test-report.md`    |

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

| 文档类型 | 目录位置                        | 是否包含版本 | 归档时机                        |
| -------- | ------------------------------- | ------------ | ------------------------------- |
| 需求文档 | `requirements/{feature}/`       | ❌           | 不归档（持续更新）              |
| 架构决策 | `decisions/{feature}/`          | ❌           | 不归档（状态标记为 DEPRECATED） |
| 执行计划 | `plans/{feature}/v{version}/`   | ✅           | 版本完成后                      |
| 进度追踪 | `active/{feature}/v{version}/`  | ✅           | 版本完成后                      |
| 测试报告 | `reports/{feature}/v{version}/` | ✅           | 版本完成后                      |
| 里程碑   | `checkpoints/{feature}/`        | ❌           | 不归档（持续积累）              |
| 旧文档   | `archive/{feature}/v{version}/` | ✅           | 永久归档                        |
