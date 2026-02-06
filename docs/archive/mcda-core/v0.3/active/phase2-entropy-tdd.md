# MCDA Core v0.3 Phase 2.2 - 熵权法 TDD 开发

**开始时间**: 2026-02-01
**状态**: 🔴 RED
**阶段**: Phase 2.2 - 熵权法实现

---

## 🎯 熵权法目标

### 核心功能
1. **数据标准化**
   - 归一化处理（消除量纲影响）
   - 处理不同方向准则（higher_better / lower_better）

2. **信息熵计算**
   - 计算每个准则的信息熵
   - 熵值越小，差异性越大，权重越大

3. **客观权重确定**
   - 计算差异系数
   - 归一化得到客观权重

4. **主客观权重组合**
   - 支持与主观权重（AHP）组合
   - 提供多种组合方法（加权平均、乘法合成）

---

## 📚 熵权法原理

### 信息熵

对于准则 j，信息熵计算公式：

```
E_j = - (1 / ln(n)) * Σ(p_ij * ln(p_ij))

其中:
- n: 备选方案数量
- p_ij: 第 i 个方案在准则 j 下的比重
- p_ij = x_ij / Σ(x_ij)
```

### 差异系数

```
D_j = 1 - E_j
```

### 客观权重

```
w_j = D_j / Σ(D_j)
```

---

## 🧪 测试计划

### 单元测试
1. **数据标准化测试**
   - test_normalize_higher_better - 越大越好准则
   - test_normalize_lower_better - 越小越好准则
   - test_handle_zero_values - 零值处理

2. **信息熵计算测试**
   - test_calculate_entropy_uniform - 均匀分布（最大熵）
   - test_calculate_entropy_extreme - 极端分布（最小熵）
   - test_entropy_formula - 熵公式正确性

3. **权重计算测试**
   - test_calculate_weights_standard - 标准案例
   - test_weights_sum_to_one - 权重和为1
   - test_identical_criteria_zero_weight - 完全相同准则权重为0

4. **主客观组合测试**
   - test_combine_weights_linear - 线性加权组合
   - test_combine_weights_multiplicative - 乘法合成

### 集成测试
1. **完整工作流测试**
   - test_entropy_weight_full_workflow - 从评分到权重
   - test_with_decision_problem - 集成到决策问题

---

## 📁 文件结构

```
skills/mcda-core/lib/
└── services/
    └── entropy_weight_service.py  # 熵权法服务

tests/mcda-core/test_services/
    └── test_entropy_weight_service.py  # 熵权法测试
```

---

## 🔬 TDD 循环

### 🔴 RED - 编写测试
- [ ] 创建测试文件 `test_entropy_weight_service.py`
- [ ] 编写所有测试用例（预期失败）

### 🟢 GREEN - 最小实现
- [ ] 实现 `EntropyWeightService` 类
- [ ] 实现数据标准化
- [ ] 实现信息熵计算
- [ ] 实现权重计算
- [ ] 实现主客观权重组合

### 🔵 REFACTOR - 重构优化
- [ ] 优化数值稳定性
- [ ] 改进错误消息
- [ ] 添加类型提示

### ✅ DONE - 验收
- [ ] 所有测试通过
- [ ] 测试覆盖率 ≥ 90%
- [ ] 文档更新

---

## 📊 进度追踪

| 任务 | 状态 | 时间 |
|-----|------|------|
| RED 阶段 | 🔴 进行中 | - |
| GREEN 阶段 | ⏳ 待开始 | - |
| REFACTOR 阶段 | ⏳ 待开始 | - |
| DONE 阶段 | ⏳ 待开始 | - |

---

## 📝 更新日志

### 2026-02-01
- 🔴 开始 RED 阶段 - 编写测试用例

---

**当前状态**: 🔴 RED - 编写测试
**下一步**: 创建 `test_entropy_weight_service.py` 并编写所有测试用例
