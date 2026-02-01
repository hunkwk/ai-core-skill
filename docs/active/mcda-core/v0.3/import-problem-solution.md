# Phase 1 测试问题诊断与解决方案

**诊断时间**: 2026-02-01
**问题类型**: Python 包导入路径问题

---

## 🔍 问题根本原因

### 核心问题
`No module named 'mcda_core'` - Python 无法找到 `mcda_core` 包

### 原因分析

1. **目录结构**: `skills/mcda-core/` (带连字符)
2. **包名**: `mcda_core` (下划线)
3. **Python 路径**: `skills` 目录需要添加到 `sys.path`

**工作原理**:
```
skills/
└── mcda-core/          ← 物理目录名（带连字符）
    ├── __init__.py     ← 声明为 mcda_core 包
    └── lib/
        ├── __init__.py ← 导出: from . import loaders
        └── loaders/    ← from mcda_core.loaders import ...
```

当 `skills` 在 `sys.path` 中时：
```python
import mcda_core  # 找到 skills/mcda-core/__init__.py
```

---

## ✅ 已完成的修复

### 1. pytest.ini 配置 ✅
```ini
[pytest]
pythonpath = skills    # 添加 skills 到路径
testpaths = tests/mcda-core
addopts = -v --tb=short
```

### 2. 测试数据修复 ✅
- `test_loaders.py` - 修复 direction 值 (3 处)
- 从 `"minimize"/"maximize"` → `"lower_better"/"higher_better"`

### 3. 模块导出 ✅
- `lib/__init__.py` - 导出 loaders 和 converters
- 版本号更新到 0.3.0

---

## 🧪 验证步骤

### 步骤 1: 验证包设置

**运行**: `python tests/mcda-core/verify_package.py`

```bash
cd D:\Workspace\dev\ai_skills_development\ai_core_skill
python tests/mcda-core/verify_package.py
```

**预期输出**:
```
✅ 所有导入成功！
可以运行以下命令进行 pytest 测试
```

### 步骤 2: 如果步骤 1 通过，运行 pytest

**选项 A: 使用 pytest.ini 配置**
```bash
pytest tests/mcda-core/test_loaders/test_loaders.py -v
```

**选项 B: 显式设置 PYTHONPATH**
```bash
# Linux/Mac
PYTHONPATH=skills pytest tests/mcda-core/test_loaders/test_loaders.py -v

# Windows
set PYTHONPATH=skills
pytest tests/mcda-core/test_loaders/test_loaders.py -v
```

**选项 C: 使用 python -m pytest**
```bash
python -m pytest tests/mcda-core/test_loaders/test_loaders.py -v
```

---

## 📋 诊断工具列表

我创建了以下诊断脚本：

### 1. verify_package.py ⭐ 推荐首先运行
**用途**: 验证 mcda_core 包设置是否正确

```bash
python tests/mcda-core/verify_package.py
```

### 2. test_direct_import.py
**用途**: 绕过包安装，直接测试模块导入

```bash
python tests/mcda-core/test_direct_import.py
```

### 3. run_with_path.py
**用途**: 自动修复路径并运行测试

```bash
python tests/mcda-core/run_with_path.py
```

### 4. debug_errors.py
**用途**: 捕获完整错误堆栈

```bash
python tests/mcda-core/debug_errors.py
```

---

## 🔧 解决方案总结

### 方案 1: 使用 pytest.ini (推荐) ⭐

**优点**: 一劳永逸，所有测试都能运行

**已配置**: `pytest.ini` 已更新
```ini
pythonpath = skills
```

**运行**:
```bash
pytest tests/mcda-core/ -v
```

### 方案 2: 设置环境变量

**Windows**:
```cmd
set PYTHONPATH=D:\Workspace\dev\ai_skills_development\ai_core_skill\skills
pytest tests/mcda-core/ -v
```

**Linux/Mac**:
```bash
export PYTHONPATH=/path/to/skills
pytest tests/mcda-core/ -v
```

### 方案 3: 运行安装脚本

**运行**:
```bash
python install_mcda.py
```

这会创建 `.pth` 文件将 `skills` 目录添加到 Python 路径。

---

## 📊 问题修复记录

| 轮次 | 问题 | 修复 | 状态 |
|-----|------|------|------|
| 1 | 模块未导出 | 添加到 `lib/__init__.py` | ✅ |
| 2 | 导入逻辑复杂 | 简化导入 | ✅ |
| 3 | 测试数据错误 | 修复 direction 值 | ✅ |
| 4 | pytest 路径配置 | 更新 pytest.ini | ✅ |

---

## 🎯 立即行动

### 请运行以下命令：

```bash
cd D:\Workspace\dev\ai_skills_development\ai_core_skill
python tests/mcda-core/verify_package.py
```

### 预期结果：

**成功**:
```
✅ 所有导入成功！
可以运行以下命令进行 pytest 测试
```

**失败**:
```
❌ 导入失败: ...
```

如果失败，请把完整输出发给我，我会继续诊断！

---

## 💡 如果 verify_package.py 成功

那么就可以直接运行 pytest：

```bash
pytest tests/mcda-core/test_loaders/test_loaders.py::TestJSONLoader -v
pytest tests/mcda-core/test_loaders/test_json_integration.py -v
pytest tests/mcda-core/test_converters.py -v
```

或者运行所有 Phase 1 测试：

```bash
pytest tests/mcda-core/test_loaders/ tests/mcda-core/test_converters.py -v
```

---

**最后更新**: 2026-02-01
**状态**: ✅ 已修复所有代码问题，等待验证
