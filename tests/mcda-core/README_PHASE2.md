# MCDA Core - Phase 2 测试指南

## 🎯 Phase 2: 标准化服务

### 功能实现

✅ **算法抽象基类** - `NormalizationMethod` 抽象基类
✅ **方法注册机制** - `register_normalization_method` 装饰器
✅ **MinMax 标准化** - 线性映射到 [0, 1]
✅ **Vector 标准化** - 向量归一化（欧几里得范数）
✅ **标准化服务** - `NormalizationService` 统一接口

---

## 🚀 运行测试

### 方法 1: Python 脚本（推荐）

```bash
# 在项目根目录执行
python tests/mcda-core/run_phase2_tests.py
```

### 方法 2: 直接使用 pytest

```bash
# 运行 Phase 2 测试
python -m pytest tests/mcda-core/test_normalization.py -v

# 显示测试覆盖率
python -m pytest tests/mcda-core/test_normalization.py --cov=skills/mcda-core/lib/normalization --cov-report=term-missing
```

---

## ✅ 预期结果

所有测试应该通过，输出类似：

```
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_higher_better PASSED
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_lower_better PASSED
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_constant_values PASSED
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_empty_input_raises_error PASSED
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_single_value_raises_error PASSED
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_property_name PASSED
tests/mcda-core/test_normalization.py::TestMinMaxNormalization::test_minmax_property_description PASSED
tests/mcda-core/test_normalization.py::TestVectorNormalization::test_vector_normalize PASSED
tests/mcda-core/test_normalization.py::TestVectorNormalization::test_vector_zero_values PASSED
tests/mcda-core/test_normalization.py::TestVectorNormalization::test_vector_empty_input_raises_error PASSED
tests/mcda-core/test_normalization.py::TestVectorNormalization::test_vector_single_value_raises_error PASSED
tests/mcda-core/test_normalization.py::TestVectorNormalization::test_vector_property_name PASSED
tests/mcda-core/test_normalization.py::TestVectorNormalization::test_vector_property_description PASSED
tests/mcda-core/test_normalization.py::TestNormalizationService::test_service_minmax_normalize PASSED
tests/mcda-core/test_normalization.py::TestNormalizationService::test_service_vector_normalize PASSED
tests/mcda-core/test_normalization.py::TestNormalizationService::test_service_unknown_method_raises_error PASSED
tests/mcda-core/test_normalization.py::TestNormalizationService::test_service_normalize_batch PASSED
tests/mcda-core/test_normalization.py::TestNormalizationEdgeCases::test_minmax_negative_values PASSED
tests/mcda-core/test_normalization.py::TestNormalizationEdgeCases::test_minmax_large_range PASSED
tests/mcda-core/test_normalization.py::TestNormalizationEdgeCases::test_vector_negative_values PASSED
```

---

## 📊 测试覆盖

| 模块 | 测试用例数 | 目标覆盖率 |
|------|-----------|-----------|
| normalization.py | 19 | >= 80% |

---

## 🔍 测试内容

### MinMax 标准化测试

- ✅ `higher_better` 方向标准化
- ✅ `lower_better` 方向标准化
- ✅ 常数值处理（所有值相同）
- ✅ 空输入异常
- ✅ 单个值异常
- ✅ 属性访问（name, description）

### Vector 标准化测试

- ✅ 向量归一化计算
- ✅ 零向量处理
- ✅ 空输入异常
- ✅ 单个值异常
- ✅ 属性访问（name, description）

### 服务层测试

- ✅ MinMax 标准化调用
- ✅ Vector 标准化调用
- ✅ 未知方法异常
- ✅ 批量标准化

### 边界情况测试

- ✅ 负值处理
- ✅ 大范围数值
- ✅ Vector 负值处理

---

## 📁 文件结构

```
skills/mcda-core/lib/
├── models.py              # 数据模型（含 NormalizationConfig）
└── normalization.py       # 标准化服务实现

tests/mcda-core/
├── conftest.py           # pytest 配置
├── test_normalization.py # 标准化服务测试
└── run_phase2_tests.py   # Phase 2 测试运行脚本
```

---

## 🎯 下一步

测试通过后：

1. ✅ **GREEN 阶段**：所有测试通过
2. 🔄 **REFACTOR 阶段**：代码重构优化
3. ✅ **DONE**：标记 Phase 2 完成
4. 🚀 开始 Phase 3：汇总算法（WSM + WPM + TOPSIS + VIKOR）

---

**需要帮助？** 查看 `docs/active/tdd-mcda-core.md` 了解详细进度
