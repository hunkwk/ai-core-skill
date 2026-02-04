# MCDA Core - Phase 3 测试修复说明

## 问题

测试文件中的 `Criterion` 和 `DecisionProblem` 参数格式不正确：

### 1. Criterion 缺少 `name` 参数
```python
# 错误
Criterion( weight=0.4, direction="higher_better")

# 正确
Criterion(name="性能", weight=0.4, direction="higher_better")
```

### 2. DecisionProblem 参数格式错误
```python
# 错误
DecisionProblem(
    name="测试",
    alternatives=list(...),
    criteria=[...],
)

# 正确
DecisionProblem(
    alternatives=tuple(...),
    criteria=tuple(...),
)
```

## 快速修复

运行以下命令修复所有测试文件：

```bash
cd tests/mcda-core

# 使用 fix_tests.py 脚本修复
python fix_tests.py
```

## 手动修复（如果脚本无法运行）

需要在每个测试文件中进行以下替换：

### test_wsm.py, test_wpm.py, test_topsis.py, test_vikor.py

```python
# sample_criteria fixture (第 20-28 行)
Criterion( weight=0.4, direction="higher_better") → Criterion(name="性能", weight=0.4, direction="higher_better")
Criterion( weight=0.3, direction="lower_better") → Criterion(name="成本", weight=0.3, direction="lower_better")
Criterion( weight=0.2, direction="higher_better") → Criterion(name="可靠性", weight=0.2, direction="higher_better")
Criterion( weight=0.1, direction="higher_better") → Criterion(name="易用性", weight=0.1, direction="higher_better")
```

## 运行测试

修复后运行测试：

```bash
# 运行单个测试文件
pytest tests/mcda-core/test_wsm.py -v

# 运行所有 Phase 3 测试
python tests/mcda-core/run_phase3_tests.py
```

## 预期结果

所有测试应该通过，输出类似：

```
tests/mcda-core/test_wsm.py::TestWSMAlgorithm::test_wsm_basic_calculation PASSED
tests/mcda-core/test_wsm.py::TestWSMAlgorithm::test_wsm_all_higher_better PASSED
...
============================== 40+ passed in 0.XXs ===============================
```
