# 导入问题修复总结

## 问题根源

所有 `lib/` 下的模块使用了错误的导入路径：
```python
from skills.mcda_core.lib.models import ...
```

这个路径在正常情况下不会工作，因为：
1. `skills/mcda-core` 包名带连字符，无法直接作为 Python 模块名
2. 即使创建了 `mcda_core` 别名，`skills.mcda_core.lib` 这个路径也不存在

## 修复方案

### 1. 批量替换导入路径

**替换规则**：
```python
# 旧（错误）
from skills.mcda_core.lib.models import ...
from skills.mcda_core.lib.algorithms.base import ...

# 新（正确）
from mcda_core.models import ...
from mcda_core.algorithms.base import ...
```

### 2. 修复的文件（共 7 个）

**核心模块**：
- ✅ `lib/normalization.py` - 2 处
- ✅ `lib/__init__.py` - 添加 `algorithms` 导入

**算法模块**：
- ✅ `lib/algorithms/__init__.py` - 6 处
- ✅ `lib/algorithms/base.py` - 1 处
- ✅ `lib/algorithms/wsm.py` - 3 处
- ✅ `lib/algorithms/wpm.py` - 3 处
- ✅ `lib/algorithms/topsis.py` - 4 处
- ✅ `lib/algorithms/vikor.py` - 4 处

### 3. 导入配置

**conftest.py**：使用 `importlib.util` 创建 `mcda_core` 模块别名
```python
spec = importlib.util.spec_from_file_location("mcda_core", mcda_core_lib_path / "__init__.py")
mcda_core_module = importlib.util.module_from_spec(spec)
sys.modules["mcda_core"] = mcda_core_module
sys.modules["mcda_core"].__path__ = [str(mcda_core_lib_path)]
spec.loader.exec_module(mcda_core_module)
```

**pytest.ini**：添加模块搜索路径
```ini
[pytest]
pythonpath = skills/mcda-core
```

**lib/__init__.py**：导出所有子模块
```python
from . import models
from . import exceptions
from . import algorithms
from . import normalization
from . import validation
from . import reporter
from . import sensitivity
```

---

## 验证步骤

### 1. 运行导入测试
```bash
python tests\mcda-core\test_import.py
```

预期输出：
```
Testing imports...
✅ from mcda_core import models - SUCCESS
✅ from mcda_core import exceptions - SUCCESS
✅ from mcda_core import validation - SUCCESS
✅ from mcda_core.models import Criterion - SUCCESS

All imports tested!
```

### 2. 运行 pytest
```bash
pytest tests\mcda-core\test_validation.py -v
pytest tests\mcda-core\test_reporter.py -v
pytest tests\mcda-core\test_sensitivity.py -v
```

预期结果：88 个测试全部通过 ✅

---

## 关键要点

1. **永远不要使用绝对路径包含目录名** - Python 不支持带连字符的包名
2. **使用 `mcda_core.xxx` 而不是 `skills.mcda_core.lib.xxx`** - 简洁且正确
3. **conftest.py 中的模块别名是关键** - 让测试可以导入 `mcda_core`
4. **批量替换工具很有用** - `sed` 命令可以快速修复多个文件

---

**修复时间**: 2026-02-01
**修复者**: hunkwk + Claude Sonnet 4.5
**影响范围**: Phase 4 测试导入
