# MCDA Core 测试目录结构

本目录包含 MCDA Core 项目的所有测试用例，按照测试类型和功能模块组织。

## 目录结构

```
tests/mcda-core/
├── __init__.py                 # 包初始化文件
├── conftest.py                 # pytest 全局配置和共享 fixtures
├── fixtures/                   # 测试数据文件
├── reports/                    # 测试报告和覆盖率报告
├── .archive/                   # 已归档的旧测试文件
│
├── unit/                       # 单元测试（28 个文件）
│   ├── test_algorithms/        # 算法单元测试
│   │   ├── test_electre1.py
│   │   ├── test_promethee2_service.py
│   │   ├── test_todim.py
│   │   ├── test_topsis.py
│   │   ├── test_topsis_interval.py
│   │   ├── test_vikor.py
│   │   ├── test_wpm.py
│   │   └── test_wsm.py
│   │
│   ├── test_core/              # 核心模块单元测试
│   │   ├── test_converters.py
│   │   ├── test_exceptions.py
│   │   ├── test_interval.py
│   │   ├── test_models.py
│   │   ├── test_reporter.py
│   │   ├── test_sensitivity.py
│   │   ├── test_utils.py
│   │   └── test_validation.py
│   │
│   ├── test_loaders/           # 数据加载器测试
│   │   ├── test_json_integration.py
│   │   └── test_loaders.py
│   │
│   ├── test_normalization/     # 标准化方法测试
│   │   ├── test_logarithmic_normalizer.py
│   │   ├── test_sigmoid_normalizer.py
│   │   └── test_normalization.py
│   │
│   ├── test_scoring/           # 评分规则测试
│   │   └── test_scoring_models.py
│   │
│   ├── test_services/          # 服务层测试
│   │   ├── test_ahp_service.py
│   │   ├── test_comparison_service.py
│   │   └── test_entropy_weight_service.py
│   │
│   ├── test_visualization/     # 可视化测试
│   │   └── test_ascii_visualizer.py
│   │
│   └── test_weighting/         # 权重计算测试
│       ├── test_critic_weighting.py
│       ├── test_cv_weighting.py
│       └── test_game_theory_weighting.py
│
└── integration/                # 集成测试（8 个文件）
    ├── test_cli/               # CLI 集成测试
    │   ├── test_cli.py
    │   └── test_import.py
    ├── test_customer_scoring.py
    ├── test_customer_scoring_simple.py
    ├── test_e2e.py
    └── test_integration.py
```

## 运行测试

### 运行所有测试
```bash
pytest tests/mcda-core/
```

### 只运行单元测试
```bash
pytest tests/mcda-core/unit/
```

### 只运行集成测试
```bash
pytest tests/mcda-core/integration/
```

### 运行特定模块的测试
```bash
# 算法测试
pytest tests/mcda-core/unit/test_algorithms/

# 标准化测试
pytest tests/mcda-core/unit/test_normalization/

# 权重计算测试
pytest tests/mcda-core/unit/test_weighting/
```

### 运行单个测试文件
```bash
pytest tests/mcda-core/unit/test_algorithms/test_topsis.py
```

### 运行特定测试用例
```bash
pytest tests/mcda-core/unit/test_algorithms/test_topsis.py::TestTOPSIS::test_basic_ranking
```

### 生成测试覆盖率报告
```bash
# 需要 pytest-cov
pytest tests/mcda-core/ --cov=mcda_core --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 使用标记运行测试
```bash
# 运行所有单元测试
pytest -m unit

# 运行所有集成测试
pytest -m integration

# 运行算法相关测试
pytest -m algorithms

# 运行慢速测试
pytest -m slow
```

## 测试统计

- **单元测试**: 28 个文件
- **集成测试**: 8 个文件
- **总测试用例**: 532+ 个

## 编写新测试

### 单元测试规范

1. **文件位置**: 根据被测试模块放入对应子目录
2. **命名规则**: `test_<模块名>.py`
3. **类命名**: `Test<功能名>`
4. **方法命名**: `test_<具体功能>`

```python
# 示例：tests/mcda-core/unit/test_algorithms/test_new_algorithm.py

import pytest
from mcda_core.algorithms.new_algorithm import NewAlgorithm

class TestNewAlgorithm:
    """新算法测试"""

    def test_basic_ranking(self):
        """测试基本排名功能"""
        # 测试代码
        pass
```

### 集成测试规范

1. **文件位置**: `integration/` 目录
2. **命名规则**: `test_<功能>_integration.py`
3. **测试完整工作流**

```python
# 示例：tests/mcda-core/integration/test_full_workflow.py

import pytest
from mcda_core import MCDAOrchestrator

class TestFullWorkflow:
    """完整工作流集成测试"""

    def test_yaml_to_ranking(self):
        """测试从 YAML 配置到排名的完整流程"""
        # 测试代码
        pass
```

## Fixtures

共享的测试 fixtures 定义在 `conftest.py` 中：

- `sample_problem`: 标准决策问题
- `sample_criteria`: 测试准则集
- `sample_alternatives`: 测试方案集
- `temp_config_file`: 临时配置文件

## 清理和维护

### 归档旧测试
不再需要的测试文件移动到 `.archive/` 目录。

### 临时调试脚本
临时脚本移动到 `.archive/temp_scripts/` 目录。

## 注意事项

1. **不要在测试目录创建 `__init__.py`**：这会阻止 pytest 发现测试
2. **使用相对导入**：测试文件中应使用 `from mcda_core.xxx import`
3. **隔离测试**：每个测试应该独立，不依赖其他测试的执行顺序
4. **清理资源**：使用 `teardown` 或 fixture 清理临时文件和资源

## 参考文档

- [pytest 官方文档](https://docs.pytest.org/)
- [MCDA Core 文档](../../skills/mcda-core/README.md)
