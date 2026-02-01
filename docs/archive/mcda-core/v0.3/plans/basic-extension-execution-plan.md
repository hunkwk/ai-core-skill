# MCDA Core v0.3 基础扩展执行计划

## 📋 基本信息

- **版本**: v0.3 (基础扩展)
- **目标**: 在 MVP 基础上扩展主客观赋权和高级算法
- **工作量**: 19 人日（4 周）
- **创建时间**: 2026-01-31
- **状态**: 待执行
- **依赖**: v0.2 MVP 完成并验收通过

---

## 🎯 版本目标

### 核心目标
1. ✅ 实现主客观赋权方法（熵权法 + AHP）
2. ✅ 实现高级汇总算法（PROMETHEE-II + COPRAS）
3. ✅ 扩展标准化方法（Z-Score + Sum + Inverse）
4. ✅ 赋权方法推荐引擎
5. ✅ 完整测试覆盖（>= 80%）

### 交付标准
- [ ] 2 种赋权方法（熵权法 + AHP）正确实现
- [ ] 2 种汇总算法（PROMETHEE-II + COPRAS）正确实现
- [ ] 3 种标准化方法（Z-Score + Sum + Inverse）正确实现
- [ ] 赋权方法自动推荐
- [ ] 测试覆盖率 >= 80%
- [ ] 文档完善

---

## 📊 功能范围

### 标准化方法（ADR-002）扩展
| 方法 | 中文名 | 优先级 | 工作量 | 状态 |
|------|--------|--------|--------|------|
| **Z-Score** | Z分数标准化 | P0 | 2 人日 | ⏳ 待实现 |
| **Sum** | 总和标准化 | P1 | 0.5 人日 | ⏳ 待实现 |
| **Inverse** | 反向标准化 | P1 | 0.5 人日 | ⏳ 待实现 |

**总计**: 3 人日

### 赋权方法（ADR-003）扩展
| 方法 | 中文名 | 类型 | 优先级 | 工作量 | 状态 |
|------|--------|------|--------|--------|------|
| **熵权法** | Entropy Weight | 客观 | P0 | 2 人日 | ⏳ 待实现 |
| **AHP** | 层次分析法 | 主观 | P0 | 3 人日 | ⏳ 待实现 |

**总计**: 5 人日（不含测试）

### 汇总算法（ADR-004）扩展
| 算法 | 中文名 | 类型 | 优先级 | 工作量 | 状态 |
|------|--------|------|--------|--------|------|
| **PROMETHEE-II** | 优先排序法 | 偏好 | P0 | 4 人日 | ⏳ 待实现 |
| **COPRAS** | 复杂比例评估法 | 效用 | P0 | 2 人日 | ⏳ 待实现 |

**总计**: 6 人日（不含测试）

### 赋权推荐引擎
| 任务 | 工作量 | 状态 |
|------|--------|------|
| 推荐引擎实现 | 1 人日 | ⏳ 待实现 |

**总计**: 1 人日

### 测试与文档
| 任务 | 工作量 | 状态 |
|------|--------|------|
| 单元测试 | 2 人日 | ⏳ 待实现 |
| 集成测试 | 1 人日 | ⏳ 待实现 |
| 使用文档 | 1 人日 | ⏳ 待实现 |

**总计**: 4 人日

### 工作量汇总
- 标准化方法扩展: 3 人日
- 赋权方法扩展: 5 人日
- 汇总算法扩展: 6 人日
- 赋权推荐引擎: 1 人日
- 测试与文档: 4 人日
- **总计: 19 人日**

---

## 🗂️ 文件结构（新增）

```
skills/mcda-core/lib/
├── normalization/
│   ├── zscore.py              # Z-Score 标准化 ⭐ NEW
│   ├── sum.py                 # Sum 标准化 ⭐ NEW
│   └── inverse.py             # Inverse 标准化 ⭐ NEW
├── weighting/
│   ├── objective/             # 客观赋权目录 ⭐ NEW
│   │   ├── __init__.py
│   │   └── entropy.py         # 熵权法 ⭐ NEW
│   ├── subjective/            # 主观赋权目录 ⭐ NEW
│   │   ├── __init__.py
│   │   └── ahp.py             # AHP ⭐ NEW
│   └── recommender.py         # 赋权推荐引擎 ⭐ NEW
└── algorithms/
    ├── promethee.py           # PROMETHEE-II ⭐ NEW
    └── copras.py              # COPRAS ⭐ NEW

tests/mcda-core/
├── test_normalization/
│   ├── test_zscore.py         # ⭐ NEW
│   ├── test_sum.py            # ⭐ NEW
│   └── test_inverse.py        # ⭐ NEW
├── test_weighting/
│   ├── test_entropy.py        # ⭐ NEW
│   └── test_ahp.py            # ⭐ NEW
├── test_algorithms/
│   ├── test_promethee.py      # ⭐ NEW
│   └── test_copras.py         # ⭐ NEW
└── fixtures/
    ├── ahp_pairwise.yaml      # AHP 成对比较案例 ⭐ NEW
    └── promethee_preferences.yaml  # PROMETHEE 偏好函数案例 ⭐ NEW
```

---

## 📋 开发任务分解

### Phase 1: Z-Score 标准化（2 天，2 人日）

#### Task 1.1: 实现 Z-Score 标准化（`lib/normalization/zscore.py`）
```python
@register_normalization_method("zscore")
class ZScoreNormalization(NormalizationMethod):
    """
    Z-Score 标准化

    公式:
    z = (x - μ) / σ

    转换到 [0, 1]:
    - higher_better: Φ(z) (累计分布函数)
    - lower_better: 1 - Φ(z)

    特点:
    - 适合正态分布数据
    - 保留异常值信息
    - 均值为 0，标准差为 1
    """
```

**实现要点**:
- 计算均值和标准差
- 处理 σ = 0 的边界情况
- 使用 `scipy.stats.norm.cdf` 转换到 [0, 1]
- 支持方向性处理

**依赖**: `scipy`（可选，若不可用则使用线性变换）

#### Task 1.2: 单元测试
- [ ] 测试正态分布数据
- [ ] 测试边界情况（σ = 0）
- [ ] 测试方向性处理
- [ ] 测试与理论值一致性

**验收标准**:
- [ ] 与 scipy 计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 2: Sum 和 Inverse 标准化（1 天，1 人日）

#### Task 2.1: 实现 Sum 标准化（0.5 人日）
```python
@register_normalization_method("sum")
class SumNormalization(NormalizationMethod):
    """
    Sum 标准化

    公式:
    - higher_better: x_ij / Σ(x_ij)
    - lower_better: 1 - x_ij / Σ(x_ij)

    特点:
    - 适用于成分数据（composition data）
    - 保持相对关系
    - 和为 1
    """
```

#### Task 2.2: 实现 Inverse 标准化（0.5 人日）
```python
@register_normalization_method("inverse")
class InverseNormalization(NormalizationMethod):
    """
    Inverse 标准化

    公式:
    inv(x) = 1 / x

    通常与 MinMax 结合使用:
    - higher_better: inv(x) normalized
    - lower_better: x normalized

    注意: 可作为 MinMax 的 direction 参数实现
    """
```

**验收标准**:
- [ ] Sum 标准化和为 1
- [ ] Inverse 正确处理 0 值

---

### Phase 3: 熵权法（2 天，2 人日）

#### Task 3.1: 实现熵权法（`lib/weighting/objective/entropy.py`）
```python
@register_weighting_method("entropy")
class EntropyWeightMethod(WeightingMethod):
    """
    熵权法（客观赋权）

    步骤:
    1. 数据标准化（归一化到 0-1）
    2. 计算每个准则的信息熵: E_j = -Σ(p_ij * ln(p_ij))
    3. 计算差异系数: d_j = 1 - E_j
    4. 计算权重: w_j = d_j / Σ(d_k)

    特点:
    - 基于数据离散程度
    - 信息熵越小，权重越大
    - 适合客观数据驱动场景
    """
```

**实现要点**:
- 自动应用 MinMax 标准化
- 处理 log(0)（epsilon = 1e-10）
- 归一化权重（和为 1）

#### Task 3.2: 单元测试
- [ ] 测试信息熵计算
- [ ] 测试差异系数计算
- [ ] 测试权重归一化
- [ ] 测试边界情况

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 4: AHP 层次分析法（3 天，3 人日）

#### Task 4.1: 实现 AHP（`lib/weighting/subjective/ahp.py`）
```python
@register_weighting_method("ahp")
class AHPWeightMethod(WeightingMethod):
    """
    AHP (Analytic Hierarchy Process)

    步骤:
    1. 构建成对比较矩阵: A = [a_ij]
    2. 计算权重向量（特征向量法）: A · w = λ_max · w
    3. 计算最大特征值: λ_max
    4. 一致性检验: CI = (λ_max - n) / (n - 1)
    5. 计算一致性比率: CR = CI / RI
    6. 若 CR < 0.1，通过检验

    参数:
    - pairwise_comparison: 成对比较矩阵
    - ri_threshold: 一致性比率阈值（默认 0.1）
    """
```

**实现要点**:
- 特征值和特征向量计算（`numpy.linalg.eig`）
- 一致性检验（RI 查表）
- 支持不完整矩阵（Harker 方法）

#### Task 4.2: YAML 配置支持
```yaml
# AHP 成对比较矩阵格式
ahp:
  pairwise_comparison:
    成本:
      成本: 1
      功能: 3
      周期: 2
    功能:
      成本: 1/3
      功能: 1
      周期: 1/2
    周期:
      成本: 1/2
      功能: 2
      周期: 1
```

#### Task 4.3: 单元测试
- [ ] 测试特征值计算
- [ ] 测试一致性检验
- [ ] 测试不完整矩阵处理
- [ ] 测试 YAML 配置解析

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 一致性检验正确
- [ ] 测试覆盖率 >= 80%

---

### Phase 5: PROMETHEE-II（4 天，4 人日）

#### Task 5.1: 实现 PROMETHEE-II（`lib/algorithms/promethee.py`）
```python
@register_algorithm("promethee_2")
class PROMETHEE2Algorithm(MCDAAlgorithm):
    """
    PROMETHEE-II (Preference Ranking Organization METHod for Enrichment Evaluations)

    步骤:
    1. 计算每一对方案的偏好度（偏好函数）
    2. 计算流出流（正流）
    3. 计算流入流（负流）
    4. 计算净流
    5. 根据净流排序

    偏好函数类型:
    - Usual: 线性偏好
    - U-Shape: 阈值偏好
    - V-Shape: 线性间接偏好
    - Level: 多级偏好
    - Linear: 线性偏好
    - Gaussian: 高斯偏好
    """
```

**实现要点**:
- 支持 6 种偏好函数
- 净流计算（Φ = Φ⁺ - Φ⁻）
- 处理相等情况

#### Task 5.2: YAML 配置支持
```yaml
# PROMETHEE 偏好函数配置
promethee:
  preference_functions:
    成本:
      type: linear  # 线性偏好
      p: 0.3        # 阈值
      q: 0.1        # 无差异阈值
    功能:
      type: usual   # 通常偏好
    周期:
      type: v_shape # V 型偏好
      p: 0.5
```

#### Task 5.3: 单元测试
- [ ] 测试 6 种偏好函数
- [ ] 测试净流计算
- [ ] 测试排名正确性
- [ ] 测试边界情况

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 6: COPRAS（2 天，2 人日）

#### Task 6.1: 实现 COPRAS（`lib/algorithms/copras.py`）
```python
@register_algorithm("copras")
class COPRASAlgorithm(MCDAAlgorithm):
    """
    COPRAS (Complex Proportional Assessment)

    步骤:
    1. MinMax 标准化
    2. 计算加权标准化矩阵
    3. 分离效益型和成本型准则
    4. 计算 S+（效益型总和）和 S-（成本型总和）
    5. 计算相对效用值: U = S+ + (S- * min(S-) / Σ(S-))
    6. 排序

    特点:
    - 明确分离效益和成本
    - 适合混合准则场景
    """
```

**实现要点**:
- 分离效益型和成本型准则
- 计算 S+ 和 S-
- 相对效用值计算

#### Task 6.2: 单元测试
- [ ] 测试 S+/S- 计算
- [ ] 测试相对效用值计算
- [ ] 测试混合准则场景
- [ ] 测试排名正确性

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 7: 赋权推荐引擎（1 天，1 人日）

#### Task 7.1: 实现推荐引擎（`lib/weighting/recommender.py`）
```python
class WeightingRecommender:
    """
    赋权方法推荐引擎

    推荐策略:
    - 有评分数据 → 熵权法
    - 有成对比较 → AHP
    - 混合场景 → 组合赋权
    - 数据样本少 → 直接赋权
    - 需要降维 → PCA（v0.4）
    """
    def suggest(self, problem: DecisionProblem) -> str:
        """
        推荐赋权方法

        策略:
        1. 检查是否有成对比较矩阵 → AHP
        2. 检查评分数据完整性
           - 数据完整 → 熵权法
           - 数据缺失 → 直接赋权
        3. 检查准则数量
           - 准则多（> 7）→ 熵权法（AHP 矩阵太大）
        4. 检查方案数量
           - 方案少（< 5）→ 直接赋权（数据不足）
        """
        pass
```

**实现要点**:
- 基于规则的推荐
- 支持配置文件覆盖
- 提供推荐理由

**验收标准**:
- [ ] 推荐逻辑合理
- [ ] 推荐理由清晰

---

### Phase 8: 单元测试（2 天，2 人日）

#### Task 8.1: 标准化测试
- [ ] `test_normalization/test_zscore.py`
- [ ] `test_normalization/test_sum.py`
- [ ] `test_normalization/test_inverse.py`

#### Task 8.2: 赋权测试
- [ ] `test_weighting/test_entropy.py`
- [ ] `test_weighting/test_ahp.py`

#### Task 8.3: 算法测试
- [ ] `test_algorithms/test_promethee.py`
- [ ] `test_algorithms/test_copras.py`

**验收标准**:
- [ ] 所有测试通过
- [ ] 测试覆盖率 >= 80%

---

### Phase 9: 集成测试（1 天，1 人日）

#### Task 9.1: 端到端测试
- [ ] 熵权法 + PROMETHEE-II 完整流程
- [ ] AHP + COPRAS 完整流程
- [ ] 赋权方法自动推荐测试

#### Task 9.2: 性能测试
- [ ] 15 个准则 x 100 个方案性能测试

**验收标准**:
- [ ] 集成测试通过
- [ ] 性能满足要求（< 2 秒）

---

### Phase 10: 使用文档（1 天，1 人日）

#### Task 10.1: 更新参考文档
- [ ] `references/algorithms.md` - 新增 PROMETHEE-II 和 COPRAS
- [ ] `references/yaml-schema.md` - 新增 AHP 和 PROMETHEE 配置
- [ ] `references/examples.md` - 新增使用示例

#### Task 10.2: 示例配置
- [ ] `tests/fixtures/ahp_pairwise.yaml`
- [ ] `tests/fixtures/promethee_preferences.yaml`

**验收标准**:
- [ ] 文档清晰易懂
- [ ] 示例可运行

---

### Phase 11: 代码审查和优化（1 天，1 人日）

#### Task 11.1: 代码质量
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过
- [ ] 代码格式化

**验收标准**:
- [ ] 无类型错误
- [ ] 无 lint 警告

---

### Phase 12: E2E 验证（1 天，1 人日）

#### Task 12.1: 真实案例验证
- [ ] 供应商选择案例（AHP + PROMETHEE-II）
- [ ] 产品优先级案例（熵权法 + COPRAS）

#### Task 12.2: 文档完整性检查
- [ ] README 更新
- [ ] 所有示例正确

**验收标准**:
- [ ] 所有案例通过
- [ ] 文档无错误

---

## 🔍 验收标准

### 功能验收
- [ ] 3 种标准化方法（Z-Score + Sum + Inverse）正确实现
- [ ] 2 种赋权方法（熵权法 + AHP）正确实现
- [ ] 2 种汇总算法（PROMETHEE-II + COPRAS）正确实现
- [ ] 赋权方法自动推荐
- [ ] YAML 配置支持（AHP 成对比较 + PROMETHEE 偏好函数）

### 质量验收
- [ ] 测试覆盖率 >= 80%
- [ ] 所有 pytest 测试通过
- [ ] 文档完善
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过

### 流程验收
- [ ] Git Flow 规范遵循
- [ ] TDD 进度文件维护（`docs/active/tdd-mcda-core-v0.3.md`）
- [ ] Conventional Commits 规范

### 架构验收
- [ ] 代码复用性高（避免重复）
- [ ] 接口一致性（标准化/赋权/算法）
- [ ] 可扩展性（易于添加新方法）

---

## ⚠️ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| AHP 一致性检验理解偏差 | Medium | Medium | 文献验证，RI 查表准确 |
| PROMETHEE-II 偏好函数复杂 | Medium | Medium | 参考文献，逐个实现 |
| 熵权法标准化依赖 | Low | Low | 自动应用 MinMax 标准化 |
| 测试覆盖率不达标 | Low | Medium | 严格 TDD，每个方法独立测试 |
| 文档编写时间不足 | Low | Low | 复用 MVP 文档模板 |

---

## 📅 时间线

| 周次 | 阶段 | 交付物 |
|------|------|--------|
| Week 1 | Phase 1-2 | Z-Score + Sum + Inverse 标准化 |
| Week 2 | Phase 3-4 | 熵权法 + AHP 赋权 |
| Week 3 | Phase 5-6 | PROMETHEE-II + COPRAS 算法 |
| Week 4 | Phase 7-12 | 推荐引擎 + 测试 + 文档 + 验证 |

---

## 📝 参考资料

### 架构文档
- [ADR-002: 标准化方法](../../decisions/002-mcda-normalization-methods.md)
- [ADR-003: 赋权方法路线图](../../decisions/003-mcda-weighting-roadmap.md)
- [ADR-004: 汇总算法架构设计](../../decisions/004-mcda-aggregation-algorithms.md)

### 需求文档
- [MCDA Core 需求分析](../../requirements/mcda-core.md)

### MVP 执行计划
- [v0.2 MVP 执行计划](../v0.2/mvp-execution-plan.md)

### 外部参考
- [PROMETHEE Methods](https://en.wikipedia.org/wiki/PROMETHEE)
- [COPRAS Method](https://en.wikipedia.org/wiki/COPRAS)
- [AHP Method](https://en.wikipedia.org/wiki/Analytic_hierarchy_process)

---

**创建者**: hunkwk + AI collaboration
**创建时间**: 2026-01-31
**最后更新**: 2026-01-31
**文档版本**: v1.0
**状态**: 待执行
**依赖**: v0.2 MVP 完成并验收通过
**下一步**: v0.2 MVP 验收通过后开始执行
