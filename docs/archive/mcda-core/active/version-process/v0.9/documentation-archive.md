# v0.9 文档归档清单

**版本**: v0.9
**功能**: 文档归档
**开始日期**: 2026-02-05
**预计工期**: 0.5 人日
**状态**: 🔄 进行中

---

## 🎯 归档目标

整理和归档 v0.8 阶段的文档，保持项目目录整洁。

---

## 📋 归档清单

### 需要归档的文档

1. **v0.8 阶段文档** ✅
   - [ ] `docs/active/mcda-core/v0.8/` → `docs/archive/mcda-core/v0.8/`
   - [ ] `v0.8-completion-report.md`
   - [ ] `v0.8-test-summary.md`

2. **临时测试文档** ✅
   - [ ] `tests/mcda-core/.archive/` - 已有临时脚本

3. **规划文档** ✅
   - [ ] `docs/plans/mcda-core/v0.8/` → `docs/archive/mcda-core/plans/v0.8/`

### v0.9 当前文档

**工作目录**:
- `docs/active/mcda-core/v0.9/` - v0.9 开发进度

**关键文档**:
- ✅ `preparation-checklist.md` - 准备工作清单
- ✅ `tdd-csv-loader.md` - CSV Loader TDD 进度
- ✅ `tdd-excel-loader.md` - Excel Loader TDD 进度
- ✅ `tdd-visualization.md` - 可视化 TDD 进度
- ✅ `tdd-cli-optimization.md` - CLI 优化 TDD 进度
- ✅ `markdown-report-template.md` - 报告模板文档

**规划文档**:
- ✅ `docs/plans/mcda-core/v0.9/execution-plan.md`
- ✅ `docs/plans/mcda-core/v0.9/csv-excel-import-design.md`

---

## 🎯 执行步骤

1. **创建归档目录**
   ```bash
   mkdir -p docs/archive/mcda-core/v0.8
   mkdir -p docs/archive/mcda-core/plans
   ```

2. **移动 v0.8 文档**
   ```bash
   mv docs/active/mcda-core/v0.8 docs/archive/mcda-core/v0.8/
   ```

3. **移动 v0.8 规划**
   ```bash
   mv docs/plans/mcda-core/v0.8 docs/archive/mcda-core/plans/v0.8/
   ```

4. **验证归档**
   ```bash
   ls -la docs/archive/mcda-core/
   ```

---

## ✅ 归档验收标准

- [ ] v0.8 文档已归档到 `docs/archive/mcda-core/v0.8/`
- [ ] 项目目录保持整洁
- [ ] v0.9 工作目录清晰
- [ ] 归档文档可访问

---

**当前状态**: 🔄 准备执行归档

**最后更新**: 2026-02-05
