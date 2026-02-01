# Changelog

All notable changes to MCDA Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-02-01

### Added
- JSON 报告格式支持
- CLI JSON 输出支持（`-f json` 选项）
- 测试报告目录（`tests/mcda-core/reports/`）

### Fixed
- 修复 `core.py` 调用不存在的 `generate_json` 方法 → 改为 `export_json`
- 修复 CLI 未传递 `format` 参数给 `run_workflow`
- 恢复 3 个之前被跳过的 E2E 测试

### Changed
- 更新 SKILL.md：补充 4 种算法说明（WSM/WPM/TOPSIS/VIKOR）
- 添加完整的 README.md 用户指南
- 重构测试报告位置到 tests 目录

### Tests
- **313 个测试全部通过**（312 → 313，+1）
- **覆盖率 92%**（维持高覆盖率）
- **0 个跳过测试**（1 → 0）
- **执行时间 2.61 秒**

### Documentation
- 新增 `test-report-v0.2.1.md` 测试报告
- 新增 `tests/mcda-core/reports/README.md` 报告索引
- 更新 CLAUDE.md 添加测试报告规范

## [0.2.0] - 2026-01-31

### Added
- **MVP v0.2 完整实现**
- 4 种聚合算法：WSM、WPM、TOPSIS、VIKOR
- 核心编排器：`MCDAOrchestrator`
- CLI 接口：`analyze`、`validate` 命令
- YAML 配置文件支持
- 自动权重归一化
- Markdown 报告生成
- 敏感性分析服务
- 数据验证服务
- 5 种标准化方法（MinMax、Vector 等）
- 完整的异常体系（12+ 异常类型）

### Tests
- **312 个测试全部通过**
- **覆盖率 92%**
- **17 个 E2E 测试**
- **3 个 YAML fixtures**

### Code Statistics
- **~8000 行代码**（实现 + 测试）
- **开发时间**: 2 天
- **6 个 Phase 完成**

## [0.1.0] - Unreleased

### Planned
- 初始版本设计

---

## Versioning Scheme

- **MAJOR** (0.x → 1.0): 稳定发布，生产就绪
- **MINOR** (0.1 → 0.2): 新功能（算法、服务）
- **PATCH** (0.2.0 → 0.2.1): Bug 修复、小改进

---

## Links

- [Git Tags](https://github.com/user/repo/tags)
- [GitHub Releases](https://github.com/user/repo/releases)
- [Documentation](../README.md)
