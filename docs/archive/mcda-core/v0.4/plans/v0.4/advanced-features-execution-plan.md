# MCDA Core v0.4 高级功能执行计划

## 📋 基本信息

- **版本**: v0.4 (高级功能)
- **目标**: 实现高级赋权方法、汇总算法和标准化方法
- **工作量**: 31 人日（6 周）
- **创建时间**: 2026-01-31
- **状态**: 待执行
- **依赖**: v0.3 基础扩展完成并验收通过

---

## 🎯 版本目标

### 核心目标
1. ✅ 实现高级赋权方法（CRITIC + 变异系数法 + 标准离差法 + 离差最大化）
2. ✅ 实现高级汇总算法（SAW + TODIM + ELECTRE-I + MACBETH + MOORA + ORESTE）
3. ✅ 扩展标准化方法（Max + Threshold + Logarithmic + Sigmoid）
4. ✅ 组合赋权策略
5. ✅ 完整测试覆盖（>= 80%）

### 交付标准
- [ ] 4 种赋权方法正确实现
- [ ] 6 种汇总算法正确实现
- [ ] 4 种标准化方法正确实现
- [ ] 组合赋权策略正确实现
- [ ] 测试覆盖率 >= 80%
- [ ] 文档完善

---

## 📊 功能范围

### 标准化方法（ADR-002）扩展
| 方法 | 中文名 | 优先级 | 工作量 | 状态 |
|------|--------|--------|--------|------|
| **Max** | 最大值标准化 | P1 | 0.5 人日 | ⏳ 待实现 |
| **Threshold** | 阈值标准化 | P1 | 1 人日 | ⏳ 待实现 |
| **Logarithmic** | 对数标准化 | P2 | 1.5 人日 | ⏳ 待实现 |
| **Sigmoid** | S 标准化 | P2 | 2 人日 | ⏳ 待实现 |

**总计**: 5 人日

### 赋权方法（ADR-003）扩展
| 方法 | 中文名 | 类型 | 优先级 | 工作量 | 状态 |
|------|--------|------|--------|--------|------|
| **CRITIC** | CRITIC 法 | 客观 | P0 | 3 人日 | ⏳ 待实现 |
| **变异系数法** | CV Method | 客观 | P1 | 1 人日 | ⏳ 待实现 |
| **标准离差法** | SD Method | 客观 | P1 | 0.5 人日 | ⏳ 待实现 |
| **离差最大化** | Max Deviation | 客观 | P1 | 2 人日 | ⏳ 待实现 |
| **简单组合** | Simple Combination | 组合 | P1 | 1.5 人日 | ⏳ 待实现 |

**总计**: 8 人日（不含测试）

### 汇总算法（ADR-004）扩展
| 算法 | 中文名 | 类型 | 优先级 | 工作量 | 状态 |
|------|--------|------|--------|--------|------|
| **SAW** | 简单加权法 | 线性 | P3 | 0.5 人日 | ⏳ 待实现 |
| **TODIM** | TODIM 法 | 前景理论 | P0 | 4 人日 | ⏳ 待实现 |
| **ELECTRE-I** | ELECTRE-I | 级别优于 | P0 | 5 人日 | ⏳ 待实现 |
| **MACBETH** | MACBETH | 交互式 | P1 | 3 人日 | ⏳ 待实现 |
| **MOORA** | MOORA 比率法 | 效用 | P1 | 2 人日 | ⏳ 待实现 |
| **ORESTE** | ORESTE 排序 | 距离 | P1 | 2.5 人日 | ⏳ 待实现 |

**总计**: 17 人日（不含测试）

### 测试与文档
| 任务 | 工作量 | 状态 |
|------|--------|------|
| 单元测试 | 2 人日 | ⏳ 待实现 |
| 集成测试 | 1 人日 | ⏳ 待实现 |
| 使用文档 | 1 人日 | ⏳ 待实现 |

**总计**: 4 人日

### 工作量汇总
- 标准化方法扩展: 5 人日
- 赋权方法扩展: 8 人日
- 汇总算法扩展: 17 人日
- 测试与文档: 4 人日
- 风险缓冲: 4 人日（TODIM + ELECTRE-I 复杂度高）
- **总计: 31 人日**

---

## 🗂️ 文件结构（新增）

```
skills/mcda-core/lib/
├── normalization/
│   ├── max.py                 # Max 标准化 ⭐ NEW
│   ├── threshold.py           # Threshold 标准化 ⭐ NEW
│   ├── logarithmic.py         # Logarithmic 标准化 ⭐ NEW
│   └── sigmoid.py             # Sigmoid 标准化 ⭐ NEW
├── weighting/
│   ├── objective/
│   │   ├── critic.py          # CRITIC 法 ⭐ NEW
│   │   ├── cv.py              # 变异系数法 ⭐ NEW
│   │   ├── std.py             # 标准离差法 ⭐ NEW
│   │   └── max_dev.py         # 离差最大化法 ⭐ NEW
│   └── combination/
│       ├── __init__.py        # ⭐ NEW
│       └── simple.py          # 简单加权组合 ⭐ NEW
└── algorithms/
    ├── saw.py                 # SAW ⭐ NEW
    ├── todim.py               # TODIM ⭐ NEW
    ├── electre_i.py           # ELECTRE-I ⭐ NEW
    ├── macbeth.py             # MACBETH ⭐ NEW
    ├── moora.py               # MOORA ⭐ NEW
    └── oreste.py              # ORESTE ⭐ NEW

tests/mcda-core/
├── test_normalization/
│   ├── test_max.py            # ⭐ NEW
│   ├── test_threshold.py      # ⭐ NEW
│   ├── test_logarithmic.py    # ⭐ NEW
│   └── test_sigmoid.py        # ⭐ NEW
├── test_weighting/
│   ├── test_critic.py         # ⭐ NEW
│   ├── test_cv.py             # ⭐ NEW
│   ├── test_std.py            # ⭐ NEW
│   ├── test_max_dev.py        # ⭐ NEW
│   └── test_combination.py    # ⭐ NEW
├── test_algorithms/
│   ├── test_saw.py            # ⭐ NEW
│   ├── test_todim.py          # ⭐ NEW
│   ├── test_electre_i.py      # ⭐ NEW
│   ├── test_macbeth.py        # ⭐ NEW
│   ├── test_moora.py          # ⭐ NEW
│   └── test_orest.py          # ⭐ NEW
└── fixtures/
    ├── todim_theta.yaml       # TODIM θ 参数案例 ⭐ NEW
    └── electre_thresholds.yaml # ELECTRE 阈值案例 ⭐ NEW
```

---

## 📋 开发任务分解

### Phase 1: Max 和 Threshold 标准化（1.5 天，1.5 人日）

#### Task 1.1: 实现 Max 标准化（0.5 人日）
```python
@register_normalization_method("max")
class MaxNormalization(NormalizationMethod):
    """
    Max 标准化

    公式:
    - higher_better: x / max(x)
    - lower_better: 1 - x / max(x)

    特点:
    - 保留最大值关系
    - 适合最大值明确的数据
    - 简单直观
    """
```

#### Task 1.2: 实现 Threshold 标准化（1 人日）
```python
@register_normalization_method("threshold")
class ThresholdNormalization(NormalizationMethod):
    """
    Threshold 标准化

    公式:
    - x < t1: 0
    - t1 <= x <= t2: (x - t1) / (t2 - t1)
    - x > t2: 1

    特点:
    - 支持双阈值（t1: 下限，t2: 上限）
    - 阈值外值截断
    - 适合有明确目标范围的场景

    参数:
    - lower_threshold: 下限阈值
    - upper_threshold: 上限阈值
    """
```

**验收标准**:
- [ ] Max 标准化保留最大值
- [ ] Threshold 支持双阈值
- [ ] 测试覆盖率 >= 80%

---

### Phase 2: Logarithmic 和 Sigmoid 标准化（3.5 天，3.5 人日）

#### Task 2.1: 实现 Logarithmic 标准化（1.5 人日）
```python
@register_normalization_method("logarithmic")
class LogarithmicNormalization(NormalizationMethod):
    """
    Logarithmic 标准化

    公式:
    1. 对数变换: y = log(x + 1)
    2. MinMax 标准化

    特点:
    - 压缩大值，扩展小值
    - 适合偏态分布（右偏）
    - 减少异常值影响
    """
```

#### Task 2.2: 实现 Sigmoid 标准化（2 人日）
```python
@register_normalization_method("sigmoid")
class SigmoidNormalization(NormalizationMethod):
    """
    Sigmoid 标准化

    公式:
    - higher_better: 1 / (1 + exp(-k * (x - μ)))
    - lower_better: 1 - 1 / (1 + exp(-k * (x - μ)))

    特点:
    - S 型曲线转换
    - 平滑过渡
    - 适合连续型数据
    - 参数 k 控制陡峭度

    参数:
    - k: 陡峭度参数（默认 1.0）
    - center: 中心点（默认均值）
    """
```

**实现要点**:
- `numpy.exp` 计算
- 参数 k 控制曲线形状
- 数值稳定性处理

**验收标准**:
- [ ] Logarithmic 正确处理 0 值（x + 1）
- [ ] Sigmoid 曲线形状正确
- [ ] 测试覆盖率 >= 80%

---

### Phase 3: CRITIC 法（3 天，3 人日）

#### Task 3.1: 实现 CRITIC 法（`lib/weighting/objective/critic.py`）
```python
@register_weighting_method("critic")
class CRITICWeightMethod(WeightingMethod):
    """
    CRITIC 法 (CRiteria Importance Through Intercriteria Correlation)

    步骤:
    1. 数据标准化（无量纲化）
    2. 计算对比强度（标准差）: σ_j
    3. 计算冲突性（相关系数）: Σ(1 - r_jk)
    4. 计算信息量: C_j = σ_j * Σ(1 - r_jk)
    5. 归一化得到权重: w_j = C_j / Σ(C_k)

    特点:
    - 同时考虑对比强度和冲突性
    - 准则间相关性低的准则权重更高
    - 适合准则间相关性强的场景
    """
```

**实现要点**:
- 相关系数矩阵计算（`numpy.corrcoef`）
- 对比强度（标准差）计算
- 冲突性度量（1 - 相关系数）
- 信息量 = 对比强度 × 冲突性

#### Task 3.2: 单元测试
- [ ] 测试相关系数矩阵计算
- [ ] 测试信息量计算
- [ ] 测试权重归一化
- [ ] 测试边界情况

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 4: 变异系数法 + 标准离差法（1.5 天，1.5 人日）

#### Task 4.1: 实现变异系数法（1 人日）
```python
@register_weighting_method("cv")
class CoefficientOfVariationMethod(WeightingMethod):
    """
    变异系数法 (Coefficient of Variation)

    步骤:
    1. 计算每个准则的均值: μ_j
    2. 计算每个准则的标准差: σ_j
    3. 计算变异系数: CV_j = σ_j / μ_j
    4. 归一化得到权重: w_j = CV_j / Σ(CV_k)

    特点:
    - 基于数据离散程度
    - 变异系数越大，权重越大
    - 适合量纲不同的数据
    """
```

#### Task 4.2: 实现标准离差法（0.5 人日）
```python
@register_weighting_method("std")
class StandardDeviationMethod(WeightingMethod):
    """
    标准离差法 (Standard Deviation)

    步骤:
    1. 计算每个准则的标准差: σ_j
    2. 归一化得到权重: w_j = σ_j / Σ(σ_k)

    特点:
    - 最简单的客观赋权法
    - 基于数据离散程度
    - 标准差越大，权重越大
    """
```

**验收标准**:
- [ ] 变异系数法正确处理均值 = 0
- [ ] 标准离差法与理论一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 5: 离差最大化法（2 天，2 人日）

#### Task 5.1: 实现离差最大化法（`lib/weighting/objective/max_dev.py`）
```python
@register_weighting_method("max_deviation")
class MaxDeviationMethod(WeightingMethod):
    """
    离差最大化法 (Maximizing Deviation)

    思想:
    权重应使各方案间的差异最大

    优化问题:
    max D(w) = Σ_j Σ_i Σ_k |z_ij - z_kj| * w_j
    s.t. Σw_j = 1, w_j >= 0

    求解:
    使用拉格朗日乘数法
    w_j = (Σ_i Σ_k |z_ij - z_kj|) / Σ_j(Σ_i Σ_k |z_ij - z_kj|)
    """
```

**实现要点**:
- 计算所有方案对的离差
- 拉格朗日乘数法求解
- 归一化权重

#### Task 5.2: 单元测试
- [ ] 测试离差计算
- [ ] 测试优化求解
- [ ] 测试边界情况

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 6: 简单加权组合（1.5 天，1.5 人日）

#### Task 6.1: 实现简单加权组合（`lib/weighting/combination/simple.py`）
```python
@register_weighting_method("combination_simple")
class SimpleCombinationMethod(WeightingMethod):
    """
    简单加权组合

    公式:
    w = α * w_subjective + (1 - α) * w_objective

    参数:
    - subjective_method: 主观赋权方法（如 AHP）
    - objective_method: 客观赋权方法（如熵权法）
    - alpha: 主观权重占比（默认 0.5）

    特点:
    - 主客观结合
    - 参数 α 控制主客观比例
    - 最常用的组合方式
    """
```

**实现要点**:
- 调用主客观赋权方法
- 加权组合
- 验证权重和为 1

#### Task 6.2: YAML 配置支持
```yaml
weighting:
  method: combination_simple
  config:
    subjective_method: ahp
    objective_method: entropy
    alpha: 0.5  # 主观权重占比
```

**验收标准**:
- [ ] 主客观权重正确组合
- [ ] YAML 配置解析正确
- [ ] 测试覆盖率 >= 80%

---

### Phase 7: SAW 算法（0.5 天，0.5 人日）

#### Task 7.1: 实现 SAW（`lib/algorithms/saw.py`）
```python
@register_algorithm("saw")
class SAWAlgorithm(MCDAAlgorithm):
    """
    SAW (Simple Additive Weighting)

    步骤:
    1. MinMax 标准化
    2. 计算加权和: S_i = Σ(w_j * z_ij)
    3. 根据 S_i 排序

    注意: 与 WSM 几乎相同，差异仅在标准化方法
    """
```

**验收标准**:
- [ ] 与 WSM 计算结果一致（MinMax 标准化）
- [ ] 测试覆盖率 >= 80%

---

### Phase 8: TODIM 算法（4 天，4 人日）

#### Task 8.1: 实现 TODIM（`lib/algorithms/todim.py`）
```python
@register_algorithm("todim")
class TODIMAlgorithm(MCDAAlgorithm):
    """
    TODIM (Tomada de Decisão Interativa e Multicritério)

    基于前景理论，考虑决策者心理行为

    步骤:
    1. 确定参考准则（权重最大的准则）
    2. 计算每一对方案的局部优势度
    3. 计算全局优势度
    4. 排序

    关键公式:
    Φ_c(A_i, A_k) = {
      sqrt(w_c / w_ref * (x_ic - x_kc) / d_c)  if x_ic > x_kc
      0                                         if x_ic = x_kc
      -sqrt((w_ref / w_c) * (x_kc - x_ic) / d_c) if x_ic < x_kc
    }

    参数:
    - theta: 损失厌恶系数（默认 1.0）
    """
```

**实现要点**:
- 参考准则选择（权重最大）
- 局部优势度计算（分段函数）
- 全局优势度求和
- 支持 θ 参数调整

#### Task 8.2: 单元测试
- [ ] 测试局部优势度计算
- [ ] 测试全局优势度计算
- [ ] 测试 θ 参数影响
- [ ] 测试边界情况

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 9: ELECTRE-I 算法（5 天，5 人日）

#### Task 9.1: 实现 ELECTRE-I（`lib/algorithms/electre_i.py`）
```python
@register_algorithm("electre_i")
class ELECTRE_IAlgorithm(MCDAAlgorithm):
    """
    ELECTRE-I (Elimination Et Choix Traduisant la REalité)

    级别优于关系方法

    步骤:
    1. 构建一致性矩阵（Concordance）
    2. 构建不一致性矩阵（Discordance）
    3. 确定一致性阈值和不一致性阈值
    4. 构建级别优于关系
    5. 核心选择（Kernel）

    一致性指数:
    C(A_k, A_l) = Σ_j(w_j * c_j(A_k, A_l)) / Σw_j
    c_j(A_k, A_l) = 1 if x_kj >= x_lj else (x_lj - x_kj) / d_j

    不一致性指数:
    D(A_k, A_l) = max_j ((x_lj - x_kj) / d_j) for x_kj < x_lj

    级别优于关系:
    A_k S A_l if C(A_k, A_l) >= c_bar and D(A_k, A_l) <= d_bar

    参数:
    - concordance_threshold: 一致性阈值（默认 0.7）
    - discordance_threshold: 不一致性阈值（默认 0.3）
    """
```

**实现要点**:
- 一致性矩阵计算（逐准则）
- 不一致性矩阵计算（最大差距）
- 级别优于关系判断
- 核心选择（Kernel 算法）
- 支持阈值调整

#### Task 9.2: YAML 配置支持
```yaml
electre:
  concordance_threshold: 0.7
  discordance_threshold: 0.3
```

#### Task 9.3: 单元测试
- [ ] 测试一致性矩阵计算
- [ ] 测试不一致性矩阵计算
- [ ] 测试级别优于关系
- [ ] 测试核心选择
- [ ] 测试阈值参数影响

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 10: MACBETH 算法（3 天，3 人日）

#### Task 10.1: 实现 MACBETH（`lib/algorithms/macbeth.py`）
```python
@register_algorithm("macbeth")
class MACBETHAlgorithm(MCDAAlgorithm):
    """
    MACBETH (Measuring Attractiveness by a Categorical Based Evaluation TecHnique)

    交互式多准则决策方法

    步骤:
    1. 成对比较（定性偏好）
    2. 转换为定量得分
    3. 一致性检验
    4. 线性规划求解权重

    偏好类别:
    0: 无差异
    1: 弱优势
    2: 优势
    3: 强优势
    4: 极强优势
    5: 绝对优势

    转换公式:
    得分差 = f(偏好类别)
    """
```

**实现要点**:
- 定性偏好到定量得分转换
- 线性规划求解（`scipy.optimize.linprog`）
- 一致性检验

#### Task 10.2: 单元测试
- [ ] 测试偏好转换
- [ ] 测试线性规划求解
- [ ] 测试一致性检验

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 11: MOORA 算法（2 天，2 人日）

#### Task 11.1: 实现 MOORA（`lib/algorithms/moora.py`）
```python
@register_algorithm("moora")
class MOORAAlgorithm(MCDAAlgorithm):
    """
    MOORA (Multi-Objective Optimization on the basis of Ratio Analysis)

    步骤:
    1. Vector 标准化
    2. 计算加权标准化矩阵
    3. 分离效益型和成本型准则
    4. 计算综合效用值:
       y_i = Σ_benefits(w_j * z_ij) - Σ_costs(w_j * z_ij)
    5. 排序

    特点:
    - 使用 Vector 标准化
    - 明确分离效益和成本
    - 综合效用值 = 效益 - 成本
    """
```

**实现要点**:
- Vector 标准化（必需）
- 分离效益型和成本型
- 综合效用值 = 效益和 - 成本和

#### Task 11.2: 单元测试
- [ ] 测试 Vector 标准化应用
- [ ] 测试综合效用值计算
- [ ] 测试排名正确性

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 12: ORESTE 算法（2.5 天，2.5 人日）

#### Task 12.1: 实现 ORESTE（`lib/algorithms/oreste.py`）
```python
@register_algorithm("oreste")
class ORESTEAlgorithm(MCDAAlgorithm):
    """
    ORESTE (Organisation, Rangement et Synthèse de Données Relacionnelles)

    基于距离的排序方法

    步骤:
    1. 计算平均排名（Borda 排名）
    2. 计算两两比较的距离
    3. 构建强关系图
    4. 确定最终排序

    距离度量:
    d(i, k) = α * |rank_i - rank_k| + β * |position_i - position_k|

    特点:
    - 综合考虑排名和位置
    - 基于距离度量
    - 适合部分排序场景
    """
```

**实现要点**:
- Borda 排名计算
- 距离度量（排名 + 位置）
- 强关系图构建
- 最终排序

#### Task 12.2: 单元测试
- [ ] 测试 Borda 排名
- [ ] 测试距离度量
- [ ] 测试强关系图
- [ ] 测试最终排序

**验收标准**:
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 13: 单元测试（2 天，2 人日）

#### Task 13.1: 标准化测试
- [ ] `test_normalization/test_max.py`
- [ ] `test_normalization/test_threshold.py`
- [ ] `test_normalization/test_logarithmic.py`
- [ ] `test_normalization/test_sigmoid.py`

#### Task 13.2: 赋权测试
- [ ] `test_weighting/test_critic.py`
- [ ] `test_weighting/test_cv.py`
- [ ] `test_weighting/test_std.py`
- [ ] `test_weighting/test_max_dev.py`
- [ ] `test_weighting/test_combination.py`

#### Task 13.3: 算法测试
- [ ] `test_algorithms/test_saw.py`
- [ ] `test_algorithms/test_todim.py`
- [ ] `test_algorithms/test_electre_i.py`
- [ ] `test_algorithms/test_macbeth.py`
- [ ] `test_algorithms/test_moora.py`
- [ ] `test_algorithms/test_oreste.py`

**验收标准**:
- [ ] 所有测试通过
- [ ] 测试覆盖率 >= 80%

---

### Phase 14: 集成测试（1 天，1 人日）

#### Task 14.1: 端到端测试
- [ ] CRITIC + TODIM 完整流程
- [ ] 简单组合 + ELECTRE-I 完整流程
- [ ] 变异系数法 + MOORA 完整流程

#### Task 14.2: 性能测试
- [ ] 20 个准则 x 200 个方案性能测试

**验收标准**:
- [ ] 集成测试通过
- [ ] 性能满足要求（< 5 秒）

---

### Phase 15: 使用文档（1 天，1 人日）

#### Task 15.1: 更新参考文档
- [ ] `references/algorithms.md` - 新增 TODIM/ELECTRE-I/MACBETH/MOORA/ORESTE
- [ ] `references/yaml-schema.md` - 新增配置参数
- [ ] `references/examples.md` - 新增使用示例

#### Task 15.2: 示例配置
- [ ] `tests/fixtures/todim_theta.yaml`
- [ ] `tests/fixtures/electre_thresholds.yaml`

**验收标准**:
- [ ] 文档清晰易懂
- [ ] 示例可运行

---

### Phase 16: 代码审查和优化（1 天，1 人日）

#### Task 16.1: 代码质量
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过
- [ ] 代码格式化

**验收标准**:
- [ ] 无类型错误
- [ ] 无 lint 警告

---

### Phase 17: E2E 验证（1 天，1 人日）

#### Task 17.1: 真实案例验证
- [ ] 复杂决策案例（20 准则 x 50 方案）
- [ ] 多算法对比验证

#### Task 17.2: 文档完整性检查
- [ ] README 更新
- [ ] 所有示例正确

**验收标准**:
- [ ] 所有案例通过
- [ ] 文档无错误

---

## 🔍 验收标准

### 功能验收
- [ ] 4 种标准化方法（Max + Threshold + Logarithmic + Sigmoid）正确实现
- [ ] 4 种赋权方法（CRITIC + 变异系数法 + 标准离差法 + 离差最大化）正确实现
- [ ] 1 种组合赋权（简单加权组合）正确实现
- [ ] 6 种汇总算法（SAW + TODIM + ELECTRE-I + MACBETH + MOORA + ORESTE）正确实现
- [ ] YAML 配置支持（TODIM θ 参数 + ELECTRE 阈值 + 组合赋权）

### 质量验收
- [ ] 测试覆盖率 >= 80%
- [ ] 所有 pytest 测试通过
- [ ] 文档完善
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过

### 流程验收
- [ ] Git Flow 规范遵循
- [ ] TDD 进度文件维护（`docs/active/tdd-mcda-core-v0.4.md`）
- [ ] Conventional Commits 规范

### 架构验收
- [ ] 代码复用性高（避免重复）
- [ ] 接口一致性（标准化/赋权/算法）
- [ ] 可扩展性（易于添加新方法）

---

## ⚠️ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| ELECTRE-I 核心选择算法复杂 | High | High | 参考文献，多案例测试 |
| TODIM 局部优势度计算偏差 | Medium | Medium | 分段函数仔细实现，测试 |
| MACBETH 线性规划依赖 scipy | Medium | Low | scipy 作为可选依赖 |
| Sigmoid 参数 k 调优困难 | Low | Low | 提供默认值，文档说明 |
| 测试覆盖率不达标 | Low | Medium | 严格 TDD，每个方法独立测试 |

---

## 📅 时间线

| 周次 | 阶段 | 交付物 |
|------|------|--------|
| Week 1 | Phase 1-2 | Max + Threshold + Logarithmic + Sigmoid 标准化 |
| Week 2 | Phase 3-5 | CRITIC + 变异系数法 + 标准离差法 + 离差最大化 |
| Week 3 | Phase 6-7 | 简单组合赋权 + SAW 算法 |
| Week 4 | Phase 8-9 | TODIM + ELECTRE-I 算法 |
| Week 5 | Phase 10-12 | MACBETH + MOORA + ORESTE 算法 |
| Week 6 | Phase 13-17 | 测试 + 文档 + 审查 + 验证 |

---

## 📝 参考资料

### 架构文档
- [ADR-002: 标准化方法](../../decisions/002-mcda-normalization-methods.md)
- [ADR-003: 赋权方法路线图](../../decisions/003-mcda-weighting-roadmap.md)
- [ADR-004: 汇总算法架构设计](../../decisions/004-mcda-aggregation-algorithms.md)

### 需求文档
- [MCDA Core 需求分析](../../requirements/mcda-core.md)

### 前序版本计划
- [v0.2 MVP 执行计划](../v0.2/mvp-execution-plan.md)
- [v0.3 基础扩展执行计划](../v0.3/basic-extension-execution-plan.md)

### 外部参考
- [TODIM Method](https://en.wikipedia.org/wiki/TODIM)
- [ELECTRE Method](https://en.wikipedia.org/wiki/ELECTRE)
- [MACBETH Method](https://en.wikipedia.org/wiki/MACBETH)
- [MOORA Method](https://en.wikipedia.org/wiki/MOORA)

---

**创建者**: hunkwk + AI collaboration
**创建时间**: 2026-01-31
**最后更新**: 2026-01-31
**文档版本**: v1.0
**状态**: 待执行
**依赖**: v0.3 基础扩展完成并验收通过
**下一步**: v0.3 基础扩展验收通过后开始执行
