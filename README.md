# AI Core Skill

AI-powered development framework with intelligent agents and skills for Claude Code.

## Overview

This project provides a comprehensive AI-assisted development framework optimized for individual developers working with AI collaboration. It includes 22 user-invocable commands, 12 specialized AI agents, and seamless MCP server integrations.

## Key Features

- **22 User Commands** - From planning to TDD, code review to deployment
- **12 AI Agents** - Specialized automation for architecture, planning, testing, and more
- **MCP Integration** - GitHub, NPM, Memory, Context7, and Web Search
- **Git Flow Workflow** - Simplified Git Flow optimized for individual development
- **Progress Tracking** - Real-time task progress documentation
- **Structured Documentation** - Requirements, plans, decisions, and reports

## Quick Start

```bash
# Clone the repository
git clone https://github.com/hunkwk/ai-core-skill.git
cd ai-core-skill

# The project is ready to use with Claude Code
# All commands and agents are pre-configured
```

## Project Structure

```
ai_core_skill/
├── .claude/                 # Claude Code configuration
│   ├── skills/            # 22 user commands
│   └── agents/            # 12 specialized agents
├── skills/                 # Skill development (reference: skill-creator/)
│   └── skill-creator/     # Standard skill structure example
├── docs/                   # Documentation
│   ├── requirements/      # Requirements analysis (AI output)
│   ├── plans/             # Implementation plans (versioned)
│   ├── active/            # ← Execution progress tracking
│   ├── reports/           # Weekly reports, reviews, metrics
│   └── decisions/         # Architecture Decision Records
├── CLAUDE.md              # AI collaboration guidelines
├── README.md              # This file (English)
└── README_CN.md           # Chinese documentation
```

## Development Workflow

This project follows a structured AI-assisted workflow:

1. **Plan** - Use `/plan` for complex features
2. **Develop** - Use `/tdd` for test-driven development
3. **Review** - Use `/code-review` for quality assurance
4. **Learn** - Use `/learn` to extract patterns for future

## Git Flow

The project uses a simplified Git Flow workflow:

- **main** - Production branch (always deployable)
- **develop** - Development integration branch
- **feature/xxx** - New features (from develop)
- **fix/xxx** - Bug fixes (from develop)
- **hotfix/xxx** - Emergency fixes (from main)

### Git Aliases

```bash
git feature <name>     # Create feature branch
git fix <name>         # Create fix branch
git hotfix <name>      # Create hotfix branch
git finish             # Merge and cleanup
```

## Available Commands

### Core Development
- `/plan` - Create implementation plans
- `/tdd` - Test-driven development (RED → GREEN → REFACTOR)
- `/code-review` - Security and quality review
- `/build-fix` - Fix build errors
- `/e2e` - End-to-end tests

### Go Language
- `/go-test` - TDD for Go projects
- `/go-review` - Review Go idiomatic patterns
- `/go-build` - Fix Go build errors

### Learning & Evolution
- `/learn` - Extract patterns from sessions
- `/evolve` - Cluster patterns into skills/agents
- `/skill-create` - Create skills from git history

### Utility
- `/refactor-clean` - Remove dead code
- `/checkpoint` - Create checkpoints
- `/verify` - Verify implementations
- `/test-coverage` - Check test coverage

## Auto-Invoked Agents

Claude will automatically invoke specialized agents based on context:

- **architect** - System design & scalability
- **planner** - Feature breakdown & risk assessment
- **build-error-resolver** - TypeScript/JS build errors
- **code-reviewer** - Code quality & security
- **tdd-guide** - Enforce TDD with 80%+ coverage
- **doc-updater** - Auto-update documentation

## Documentation

- **[CLAUDE.md](./CLAUDE.md)** - AI collaboration guidelines and project conventions
- **[README_CN.md](./README_CN.md)** - 中文文档 (Chinese documentation)
- **[docs/](./docs/)** - Detailed documentation center
  - [Requirements](./docs/requirements/) - Requirements analysis
  - [Plans](./docs/plans/) - Implementation roadmap
  - [Active Tasks](./docs/active/) - Execution progress
  - [Reports](./docs/reports/) - Development reports

## Contributing

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: add new feature
fix: bug fix
docs: documentation changes
refactor: code refactoring
test: testing related
chore: build/tooling changes
```

## License

Apache License 2.0

## Contact

**Author**: hunkwk
**Repository**: https://github.com/hunkwk/ai-core-skill

---

**Last Updated**: 2025-01-31
**Plugin Version**: everything-claude-code v1.2.0
