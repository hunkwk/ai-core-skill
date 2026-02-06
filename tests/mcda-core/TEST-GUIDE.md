# Phase 4 测试指南

## 🔧 修复说明

### 问题
测试文件导入 `mcda_core` 模块失败：
```
ModuleNotFoundError: No module named 'mcda_core'
```

### 解决方案
已修复以下文件：

#### 1. 测试文件（test_validation.py, test_reporter.py, test_sensitivity.py）
在每个测试文件开头添加路径设置：
```python
import sys
from pathlib import Path

# 添加 mcda_core 模块路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_core_path.resolve()))
```

#### 2. `tests/mcda-core/conftest.py`
添加了 `skills/mcda-core/lib` 到 Python 路径：
```python
# 添加 mcda-core/lib 到 Python 路径，这样可以直接导入 mcda_core
mcda_core_lib_path = project_root / "skills" / "mcda-core" / "lib"
sys.path.insert(0, str(mcda_core_lib_path.resolve()))
```

#### 3. `skills/mcda-core/lib/__init__.py`
导入了所有核心模块：
```python
from . import models
from . import exceptions
from . import normalization
from . import validation
from . import reporter
from . import sensitivity
```

---

## 🚀 运行测试

### 方法 1: 使用测试运行脚本（推荐）

```bash
python tests\mcda-core\run_phase4_tests.py
```

### 方法 2: 直接使用 pytest

```bash
# 运行单个测试文件
pytest tests\mcda-core\test_validation.py -v
pytest tests\mcda-core\test_reporter.py -v
pytest tests\mcda-core\test_sensitivity.py -v

# 运行所有 Phase 4 测试
pytest tests\mcda-core\test_validation.py tests\mcda-core\test_reporter.py tests\mcda-core\test_sensitivity.py -v

# 运行并查看详细输出
pytest tests\mcda-core\test_validation.py -v --tb=short
```

### 方法 3: 运行所有 mcda-core 测试

```bash
pytest tests\mcda-core\ -v
```

---

## 📊 测试覆盖

| 测试文件 | 行数 | 测试用例数 |
|---------|------|-----------|
| test_validation.py | ~350 | 30 |
| test_reporter.py | ~380 | 30 |
| test_sensitivity.py | ~370 | 28 |

**总计**: ~1100 行测试代码，88 个测试用例

---

## ✅ 预期结果

所有测试应该通过：
```
============================== 88 passed in 2.34s ==============================
```

---

## 🐛 如果测试失败

### 常见问题 1: 导入错误
**错误**:
```
ModuleNotFoundError: No module named 'mcda_core'
```

**解决**: 确保 `tests/mcda-core/conftest.py` 存在且内容正确。

### 常见问题 2: 缺少依赖
**错误**:
```
ImportError: cannot import name 'xxx' from 'mcda_core.models'
```

**解决**: 确保 `skills/mcda-core/lib/__init__.py` 导入了所有模块。

### 常见问题 3: Windows 路径问题
**错误**:
```
PermissionError: [WinError 5]
```

**解决**: 使用管理员权限运行或使用虚拟环境。

---

## 📝 测试状态

- ✅ RED: 88 个测试用例编写完成
- ✅ GREEN: 3 个服务实现完成
- ✅ 导入配置修复完成
- ⏸️ 待运行测试验证
- ⏸️ 待测试覆盖率检查（目标 >= 80%）

---

**创建时间**: 2026-02-01
**修复者**: hunkwk + Claude Sonnet 4.5
