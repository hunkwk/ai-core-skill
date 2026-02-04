# AI Core Skill Documentation

> AI-friendly documentation index for quick navigation

## Quick Navigation

### Planning & Requirements
- [Requirements](requirements/) - Requirements analysis (AI output)
  - [Current](requirements/current/) - Active requirements
  - [Backlog](requirements/backlog/) - Pending requirements
- [Plans](plans/) - Implementation plans (versioned)
  - [v0.1](plans/v0.1/) - Current version plans
  - [Roadmap](plans/roadmap.md) - Version roadmap

### Execution & Progress
- [Active Tasks](active/) - **Execution progress tracking**
  - TDD tasks: `tdd-{feature}.md`
  - Bug fixes: `fix-{bug}.md`
  - Refactoring: `refactor-{target}.md`

### Reports & Analysis
- [Weekly Reports](reports/weekly/) - Development summaries
- [Code Reviews](reports/review/) - Review reports
- [Metrics](reports/metrics/) - Coverage & performance

### Decision Records
- [ADR Index](decisions/) - Architecture Decision Records

## Documentation Maintenance

- Use `/update-docs` command for automatic updates
- Follow [CLAUDE.md](../CLAUDE.md) specifications
- AI maintains progress files in `active/` directory

## File Naming Conventions

**Progress Files** (`active/`):
```
tdd-{feature}.md      # TDD development
fix-{bug-name}.md     # Bug fix
refactor-{target}.md   # Refactoring
```

**Status Tracking**:
- TDD: `RED | GREEN | REFACTOR | DONE`
- Fix: `REPRODUCING | DIAGNOSING | FIXING | VERIFYING | DONE`

---

**Last Updated**: 2025-01-31
**Maintained by**: hunkwk + AI collaboration
