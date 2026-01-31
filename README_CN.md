# AI Core Skill

AI 驱动的开发框架，为 Claude Code 提供智能代理和技能。

## 项目概述

这是一个为个人开发者与 AI 协作优化的 AI 辅助开发框架。项目包含 22 个用户可调用命令、12 个专业 AI 代理，以及无缝的 MCP 服务器集成，旨在通过结构化的工作流提升开发效率。

## 核心特性

- **22 个用户命令** - 从规划到 TDD、代码审查到部署的完整工具链
- **12 个 AI 代理** - 架构、规划、测试等领域的专业自动化
- **MCP 集成** - GitHub、NPM、Memory、Context7、Web Search
- **Git Flow 工作流** - 为个人开发者优化的简化版 Git Flow
- **进度跟踪** - 实时任务进度文档记录
- **结构化文档** - 需求、计划、决策、报告完整体系

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/hunkwk/ai-core-skill.git
cd ai-core-skill

# 项目已配置完成，可直接与 Claude Code 配合使用
# 所有命令和代理均已预配置
```

## 项目结构

```
ai_core_skill/
├── .claude/                 # Claude Code 配置
│   ├── skills/            # 22 个用户命令
│   └── agents/            # 12 个专业代理
├── skills/                 # 技能开发（参考标准：skill-creator/）
│   └── skill-creator/     # 标准技能结构示例
├── docs/                   # 文档中心
│   ├── requirements/      # 需求分析（AI 输出）
│   ├── plans/             # 实施计划（按版本 v0.1, v0.2）
│   ├── active/            # ← 执行进度跟踪
│   ├── reports/           # 周报、审查、指标
│   └── decisions/         # 架构决策记录（ADR）
├── CLAUDE.md              # AI 协作指南和项目约定
├── README.md              # 本文件（英文）
└── README_CN.md           # 中文文档
```

## 开发工作流

项目遵循结构化的 AI 辅助开发流程：

1. **规划** - 复杂功能使用 `/plan`
2. **开发** - 使用 `/tdd` 进行测试驱动开发
3. **审查** - 使用 `/code-review` 质量保证
4. **学习** - 使用 `/learn` 提取模式供未来使用

## Git Flow 工作流

项目使用简化版 Git Flow 工作流：

- **main** - 生产分支（始终可部署）
- **develop** - 开发集成分支
- **feature/xxx** - 新功能（从 develop 分出）
- **fix/xxx** - Bug 修复（从 develop 分出）
- **hotfix/xxx** - 紧急修复（从 main 分出）

### Git 别名

```bash
git feature <name>     # 创建功能分支
git fix <name>         # 创建修复分支
git hotfix <name>      # 创建热修复分支
git finish             # 合并并清理
```

## 可用命令

### 核心开发
- `/plan` - 创建实施计划
- `/tdd` - 测试驱动开发（RED → GREEN → REFACTOR）
- `/code-review` - 安全和质量审查
- `/build-fix` - 修复构建错误
- `/e2e` - 端到端测试

### Go 语言
- `/go-test` - Go 项目 TDD
- `/go-review` - Go 代码模式审查
- `/go-build` - 修复 Go 构建错误

### 学习与演化
- `/learn` - 从会话中提取模式
- `/evolve` - 将模式聚类为技能/代理
- `/skill-create` - 从 git 历史创建技能

### 工具
- `/refactor-clean` - 清理死代码
- `/checkpoint` - 创建检查点
- `/verify` - 验证实现
- `/test-coverage` - 检查测试覆盖率

## 自动代理

Claude 会根据上下文自动调用专业代理：

- **architect** - 系统设计与可扩展性
- **planner** - 功能分解与风险评估
- **build-error-resolver** - TypeScript/JS 构建错误
- **code-reviewer** - 代码质量与安全
- **tdd-guide** - 强制 TDD（80%+ 覆盖率）
- **doc-updater** - 自动更新文档

## 文档

- **[CLAUDE.md](./CLAUDE.md)** - AI 协作指南和项目约定
- **[README.md](./README.md)** - English documentation
- **[docs/](./docs/)** - 详细文档中心
  - [需求分析](./docs/requirements/) - 需求文档
  - [实施计划](./docs/plans/) - 版本路线图
  - [活跃任务](./docs/active/) - 执行进度
  - [开发报告](./docs/reports/) - 周报、审查、指标

## 开发约定

项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 新功能
fix: Bug 修复
docs: 文档变更
refactor: 代码重构
test: 测试相关
chore: 构建/工具变更
```

## 版本规划

### v0.1（当前）- 项目基础 ✅
- Git Flow 配置
- 文档结构搭建
- 进度跟踪系统
- AI 命令集成

### v0.2（计划）- 首次实现
- 第一个生产级 skill
- 测试框架
- CI/CD 基础

### v1.0（未来）- 稳定发布
- 完整技能框架
- MCP 服务器集成
- 生产级工具

## 许可证

Apache License 2.0

## 联系方式

**作者**: hunkwk
**仓库**: https://github.com/hunkwk/ai-core-skill

---

**最后更新**: 2025-01-31
**插件版本**: everything-claude-code v1.2.0
