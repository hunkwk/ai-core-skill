# TDD: TODIM 区间版本开发

**版本**: v0.7
**阶段**: Phase 3 - TODIM 区间版本
**开始日期**: 2026-02-04
**状态**: 🔴 RED (编写测试中)
**TDD 循环**: RED → GREEN → REFACTOR → DONE

---

## 📊 目标

实现 TODIM 算法的区间版本，支持前景理论和区间数。

### 核心功能

1. **IntervalTODIM 类**: 继承 MCDAAlgorithm，注册为 "todim_interval"
2. **区间前景价值函数**: v(d) = d^α (收益) 或 -θ·(-d)^β (损失)
3. **区间优势度计算**: Φ_i(A_j) = Σ (w_j / w_ref) · v(d_ij)
4. **区间全局优势度**: δ_i = Σ Φ_i(A_j)
5. **可能度排序**: 使用 PossibilityDegree 对区间 δ 值排序

### 验收标准

- [ ] 测试覆盖率 >= 85%
- [ ] 测试通过率 100% (28/28)
- [ ] 执行时间 < 0.5 秒
- [ ] 与精确数 TODIM 完全兼容

---

## 🔴 Step 1: RED - 编写失败的测试

### 测试计划 (28 个测试)

#### 1. 基础功能测试 (8 个)
- [ ] test_todim_interval_algorithm_registration
- [ ] test_todim_interval_basic_calculation
- [ ] test_todim_interval_with_three_alternatives
- [ ] test_todim_interval_with_parameters
- [ ] test_todim_interval_default_parameters
- [ ] test_todim_interval_custom_alpha_beta
- [ ] test_todim_interval_custom_theta
- [ ] test_todim_interval_empty_problem

#### 2. 前景价值函数测试 (8 个)
- [ ] test_prospect_value_gain_interval
- [ ] test_prospect_value_loss_interval
- [ ] test_prospect_value_zero_interval
- [ ] test_prospect_value_degenerate_interval
- [ ] test_prospect_value_power_alpha
- [ ] test_pro prospect_value_power_beta
- [ ] test_prospect_value_loss_aversion_theta
- [ ] test_prospect_value_interval_math

#### 3. 优势度计算测试 (6 个)
- [ ] test_dominance_calculation_interval
- [ ] test_reference_point_determination
- [ ] test_weight_normalization
- [ ] test_global_dominance_calculation
- [ ] test_dominance_with_intervals
- [ ] test_dominance_aggregation

#### 4. 可能度排序测试 (4 个)
- [ ] test_possibility_degree_ranking_todim
- [ ] test_ranking_with_interval_dominance
- [ ] test_ranking_stability_todim
- [ ] test_ranking_consistency

#### 5. 兼容性测试 (4 个)
- [ ] test_compatibility_with_crisp_todim
- [ ] test_degenerate_intervals_equal_crisp
- [ ] test_single_value_intervals_todim
- [ ] test_algorithm_name_and_description

---

## 🎯 数学模型（参考 P0-T4）

### 1. 区间前景价值函数

```
v(d) = {
    [d^α, d^α],                    if d ≥ 0  (区间收益)
    [-θ · (-d)^β, -θ · (-d)^β],    if d < 0  (区间损失)
}
```

其中:
- α, β: 风险态度参数 (通常 α = β = 0.88)
- θ: 损失厌恶系数 (通常 θ = 2.25)
- d: 区间收益/损失

### 2. 区间优势度计算

```
Φ_i(A_j) = Σ (w_j / w_ref) · v(d_ij)
```

### 3. 全局优势度

```
δ_i = Σ Φ_i(A_j)
```

### 4. 排序方法

使用可能度排序对区间 δ 值排序（δ 值越大越好）

---

## 🚀 执行记录

### 2026-02-04 - 启动 Phase 3 开发

**Action**: 开始 TODIM 区间版本 TDD 开发
**Status**: 🔴 RED 阶段开始
**Next**: 编写 28 个测试用例

---

## 🔗 相关链接

- [v0.7 执行计划](../../../plans/mcda-core/v0.7/execution-plan.md)
- [Phase 1 完成报告](./tdd-vikor-interval.md)
- [P0-T4 TODIM 设计文档](./p0-t4-todim-design.md)
- [ADR-007: 区间数/模糊数架构](../../../decisions/mcda-core/007-interval-fuzzy-mcda-architecture.md)
- [TODIM 精确数实现](../../../../../skills/mcda-core/lib/algorithms/todim.py)

---

**最后更新**: 2026-02-04
**更新者**: AI (Claude Sonnet 4.5)
**当前状态**: 🔴 RED - 编写测试中
