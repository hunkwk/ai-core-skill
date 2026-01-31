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

## 📚 Documentation Structure

Centralized documentation in `docs/` directory for AI-human collaboration.

### Directory Layout

```
docs/
├── README.md / README_CN.md        # Documentation index
├── requirements/                    # Requirements analysis
│   ├── README.md
│   └── README_CN.md
├── plans/                          # Implementation plans (versioned)
│   ├── README.md
│   ├── roadmap.md                  # Version roadmap
│   └── v0.1/
│       └── summary.md
├── active/                         # **Execution progress tracking**
│   ├── README.md
│   └── README_CN.md
│   # Progress files created by AI during execution:
│   # - tdd-{feature}.md
│   # - fix-{bug-name}.md
│   # - refactor-{target}.md
├── reports/                        # Analysis & metrics
│   ├── README.md
│   └── README_CN.md
│   # Subdirectories: weekly/, review/, metrics/
└── decisions/                      # Architecture Decision Records (ADR)
    ├── README.md
    ├── template.md
    └── README_CN.md
```

### Progress Tracking Files

**File Naming Conventions** (`active/`):
```
tdd-{feature}.md      # TDD development (RED → GREEN → REFACTOR → DONE)
fix-{bug-name}.md     # Bug fix (REPRODUCING → DIAGNOSING → FIXING → VERIFYING → DONE)
refactor-{target}.md  # Refactoring tasks
```

**Status Tracking**:
- **TDD**: `RED | GREEN | REFACTOR | DONE`
- **Bug Fix**: `REPRODUCING | DIAGNOSING | FIXING | VERIFYING | DONE`

### Maintenance

- Use `/update-docs` command for automatic documentation updates
- AI maintains progress files in `active/` directory
- Follow [CLAUDE.md](../CLAUDE.md) specifications

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
