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
├── checkpoints/                     # **Project milestone checkpoints**
│   ├── README.md                   # Checkpoints index
│   ├── checkpoint-complete.md      # Unified complete project checkpoint
│   ├── checkpoint-phase{N}.md      # Individual phase checkpoints
│   └── checkpoint-{feature}.md     # Feature-specific checkpoints
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

**Checkpoint Purpose**:
- **Project Milestones**: Record major project phase completions
- **Progress Tracking**: Centralized location for all milestone records
- **Knowledge Preservation**: Capture decisions, metrics, and lessons learned
- **Easy Review**: Single `checkpoint-complete.md` for entire project overview

**Checkpoint Content Requirements**:
1. **Executive Summary**: Brief overview of achievements
2. **Implementation Details**: Key features and deliverables
3. **Metrics**: Code statistics, test coverage, development time
4. **Git Commits**: Relevant commit hashes and messages
5. **Lessons Learned**: What went well and improvements
6. **Next Steps**: Future enhancements or follow-up work

**Checkpoint Creation Workflow**:
1. Complete a major milestone (phase/feature)
2. Run full test suite and record metrics
3. Create/update `checkpoint-complete.md` with summary
4. Optionally create individual `checkpoint-phase{N}.md` for detailed records
5. Save checkpoint to `docs/checkpoints/` directory
6. Git commit with descriptive message
7. Update memory knowledge graph with entities and relations

**IMPORTANT**:
- Always maintain `checkpoint-complete.md` as the **single source of truth** for entire project progress
- Individual phase checkpoints are optional detailed records
- Use `/everything-claude-code:checkpoint` command to extract and save progress
- All checkpoints MUST be in `docs/checkpoints/`, never in `docs/active/`

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
