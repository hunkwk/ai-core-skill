# MCDA Core - 测试运行指南

## 🚀 快速开始

### 方法 1: Python 脚本（推荐）
```bash
# 在项目根目录执行
python tests/mcda-core/run_tests.py
```

### 方法 2: PowerShell 脚本
```powershell
# 在项目根目录执行
powershell -ExecutionPolicy Bypass -File tests/mcda-core/run_tests.ps1
```

### 方法 3: 批处理脚本
```cmd
# 双击运行或命令行执行
tests\mcda-core\run_tests.bat
```

### 方法 4: 直接使用 pytest
```bash
# 运行所有测试
python -m pytest tests/mcda-core/ -v

# 运行特定测试文件
python -m pytest tests/mcda-core/test_models.py -v
python -m pytest tests/mcda-core/test_exceptions.py -v

# 运行单个测试
python -m pytest tests/mcda-core/test_models.py::TestCriterion::test_create_valid_criterion -v

# 显示测试覆盖率
python -m pytest tests/mcda-core/ --cov=skills/mcda-core/lib --cov-report=term-missing
```

---

## 📦 依赖安装

首次运行前，需要安装测试依赖：

```bash
# 安装核心依赖
pip install pytest pyyaml numpy

# 可选：安装覆盖率工具
pip install pytest-cov
```

---

## ✅ 预期结果

所有测试应该通过，输出类似：

```
========================================
  MCDA Core - 运行单元测试
========================================

[1/4] Python 环境
  版本: 3.12.x
  路径: /path/to/python

[2/4] 安装依赖
========================================
  安装依赖包
✅ 安装依赖包 成功！

[3/4] 运行数据模型测试
========================================
tests/mcda-core/test_models.py::TestCriterion::test_create_valid_criterion PASSED
tests/mcda-core/test_models.py::TestCriterion::test_criterion_with_scoring_rule PASSED
...
✅ 数据模型测试 成功！

[4/4] 运行异常测试
========================================
tests/mcda-core/test_exceptions.py::TestMCDAError::test_create_basic_error PASSED
...
✅ 异常测试 成功！

========================================
  ✅ 所有测试通过！
========================================
```

---

## 🔧 常见问题

### Q1: 找不到 pytest 命令
**A**: 使用 `python -m pytest` 代替 `pytest`

### Q2: 权限错误
**A**: 以管理员身份运行命令提示符或 PowerShell

### Q3: 模块导入错误
**A**: 确保在项目根目录（`D:\Workspace\dev\ai_skills_development\ai_core_skill`）执行命令

### Q4: 测试失败
**A**: 查看详细错误信息，使用 `-v` 和 `--tb=long` 参数

---

## 📊 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| models.py | >= 80% | 待测试 |
| exceptions.py | >= 80% | 待测试 |

---

## 🎯 下一步

测试通过后：

1. ✅ **GREEN 阶段**：所有测试通过
2. 🔄 **REFACTOR 阶段**：代码重构优化
3. ✅ **DONE**：标记 Phase 1 完成
4. 🚀 开始 Phase 2：标准化服务

---

**需要帮助？** 查看 `docs/active/tdd-mcda-core.md` 了解详细进度
