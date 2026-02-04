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

## Plugin Resources

- Commands: `.claude/skills/`
- Agents: `.claude/agents/`
- Settings: `.claude/settings.local.json`
