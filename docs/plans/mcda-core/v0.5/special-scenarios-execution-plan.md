# MCDA Core v0.5 特殊场景执行计划

## 📋 基本信息

- **版本**: v0.5 (特殊场景)
- **目标**: 实现特殊赋权方法和高级扩展功能
- **工作量**: 20.5 人日（4 周）
- **创建时间**: 2026-01-31
- **状态**: 待执行
- **依赖**: v0.4 高级功能完成并验收通过

---

## 🎯 版本目标

### 核心目标
1. ✅ 实现特殊赋权方法（德尔菲法 + PCA）
2. ✅ 实现高级组合赋权（博弈论组合）
3. ✅ 性能优化和扩展性增强
4. ✅ 完整测试覆盖（>= 80%）
5. ✅ 生产环境部署准备

### 交付标准
- [ ] 2 种特殊赋权方法正确实现
- [ ] 1 种高级组合赋权正确实现
- [ ] 性能优化（大数据集支持）
- [ ] 测试覆盖率 >= 80%
- [ ] 文档完善
- [ ] 生产环境就绪

---

## 📊 功能范围

### 赋权方法（ADR-003）扩展
| 方法 | 中文名 | 类型 | 优先级 | 工作量 | 状态 |
|------|--------|------|--------|--------|------|
| **德尔菲法** | Delphi Method | 主观 | P1 | 3 人日 | ⏳ 待实现 |
| **PCA** | 主成分分析 | 客观 | P2 | 4 人日 | ⏳ 待实现 |
| **博弈论组合** | Game Theory Combination | 组合 | P0 | 5 人日 | ⏳ 待实现 |

**总计**: 12 人日（不含测试）

### 性能优化
| 任务 | 工作量 | 状态 |
|------|--------|------|
| 大数据集优化 | 1.5 人日 | ⏳ 待实现 |
| 缓存机制 | 1 人日 | ⏳ 待实现 |
| 并行计算 | 1 人日 | ⏳ 待实现 |

**总计**: 3.5 人日

### 测试与文档
| 任务 | 工作量 | 状态 |
|------|--------|------|
| 单元测试 | 2 人日 | ⏳ 待实现 |
| 集成测试 | 1 人日 | ⏳ 待实现 |
| 使用文档 | 1 人日 | ⏳ 待实现 |
| 部署文档 | 1 人日 | ⏳ 待实现 |

**总计**: 5 人日

### 工作量汇总
- 赋权方法扩展: 12 人日
- 性能优化: 3.5 人日
- 测试与文档: 5 人日
- **总计: 20.5 人日**

---

## 🗂️ 文件结构（新增）

```
skills/mcda-core/lib/
├── weighting/
│   ├── subjective/
│   │   └── delphi.py             # 德尔菲法 ⭐ NEW
│   ├── objective/
│   │   └── pca.py                # PCA ⭐ NEW
│   └── combination/
│       └── game_theory.py        # 博弈论组合 ⭐ NEW
├── optimization/                 # 性能优化模块 ⭐ NEW
│   ├── __init__.py
│   ├── cache.py                 # 缓存机制
│   ├── parallel.py              # 并行计算
│   └── large_scale.py           # 大数据集优化
└── deployment/                   # 部署相关 ⭐ NEW
    ├── __init__.py
    ├── config.py                # 配置管理
    └── logging.py               # 日志管理

tests/mcda-core/
├── test_weighting/
│   ├── test_delphi.py           # ⭐ NEW
│   ├── test_pca.py              # ⭐ NEW
│   └── test_game_theory.py      # ⭐ NEW
├── test_optimization/           # ⭐ NEW
│   ├── __init__.py
│   ├── test_cache.py
│   ├── test_parallel.py
│   └── test_large_scale.py
└── fixtures/
    ├── delphi_rounds.yaml       # 德尔菲法多轮案例 ⭐ NEW
    └── pca_dataset.yaml         # PCA 数据集案例 ⭐ NEW

deployment/                       # 部署配置 ⭐ NEW
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── kubernetes/
│   ├── deployment.yaml
│   └── service.yaml
└── config/
    ├── production.yaml
    └── development.yaml
```

---

## 📋 开发任务分解

### Phase 1: 德尔菲法（3 天，3 人日）

#### Task 1.1: 实现德尔菲法（`lib/weighting/subjective/delphi.py`）
```python
@register_weighting_method("delphi")
class DelphiMethod(WeightingMethod):
    """
    德尔菲法 (Delphi Method)

    多轮专家咨询，达成共识

    步骤:
    1. 第一轮: 专家独立给出权重
    2. 计算统计量（均值、标准差）
    3. 反馈结果给专家
    4. 第二轮: 专家根据反馈调整权重
    5. 重复 2-4，直到达成共识或达到最大轮数
    6. 计算最终权重（均值或中位数）

    共识判断:
    - 标准差 < threshold（默认 0.1）
    - 或达到最大轮数（默认 3 轮）

    输入格式（YAML）:
    delphi:
      rounds:
        - round: 1
          experts:
            - name: 专家1
              weights: {成本: 0.3, 功能: 0.4, 周期: 0.3}
            - name: 专家2
              weights: {成本: 0.25, 功能: 0.5, 周期: 0.25}
        - round: 2
          experts:
            - name: 专家1
              weights: {成本: 0.28, 功能: 0.45, 周期: 0.27}
            ...

    参数:
    - max_rounds: 最大轮数（默认 3）
    - convergence_threshold: 共识阈值（默认 0.1）
    - aggregation_method: 聚合方法（mean/median，默认 mean）
    """
```

**实现要点**:
- 多轮权重收集
- 统计量计算（均值、标准差、四分位数）
- 共识判断（标准差阈值）
- 最终权重聚合（均值或中位数）

#### Task 1.2: YAML 配置支持
```yaml
weighting:
  method: delphi
  config:
    max_rounds: 3
    convergence_threshold: 0.1
    aggregation_method: mean

delphi:
  rounds:
    - round: 1
      experts:
        - name: 专家1
          weights:
            成本: 0.3
            功能: 0.4
            周期: 0.3
        - name: 专家2
          weights:
            成本: 0.25
            功能: 0.5
            周期: 0.25
```

#### Task 1.3: 单元测试
- [ ] 测试单轮德尔菲法
- [ ] 测试多轮收敛
- [ ] 测试共识判断
- [ ] 测试边界情况（未达成共识）

**验收标准**:
- [ ] 多轮权重收集正确
- [ ] 共识判断准确
- [ ] 测试覆盖率 >= 80%

---

### Phase 2: PCA 主成分分析（4 天，4 人日）

#### Task 2.1: 实现 PCA（`lib/weighting/objective/pca.py`）
```python
@register_weighting_method("pca")
class PCAWeightMethod(WeightingMethod):
    """
    PCA (Principal Component Analysis) 赋权法

    步骤:
    1. 数据标准化（Z-Score）
    2. 计算协方差矩阵或相关系数矩阵
    3. 计算特征值和特征向量
    4. 选择主成分（累计贡献率 > 85%）
    5. 计算主成分载荷
    6. 根据载荷计算权重

    权重计算:
    w_j = Σ(|L_ij| * variance_i) / Σ_j Σ(|L_ij| * variance_i)

    其中:
    - L_ij: 第 i 个主成分对第 j 个准则的载荷
    - variance_i: 第 i 个主成分的方差（特征值）

    参数:
    - variance_threshold: 累计贡献率阈值（默认 0.85）
    - use_correlation: 使用相关系数矩阵（默认 True）
    """
```

**实现要点**:
- 标准化（Z-Score）
- 协方差矩阵/相关系数矩阵计算
- 特征值分解（`numpy.linalg.eig` 或 `scipy.linalg.eigh`）
- 主成分选择（累计贡献率）
- 主成分载荷计算
- 权重提取

**依赖**: `scipy`（可选，优先使用）

#### Task 2.2: 单元测试
- [ ] 测试特征值分解
- [ ] 测试主成分选择
- [ ] 测试载荷计算
- [ ] 测试权重提取
- [ ] 测试边界情况（准则数 > 方案数）

**验收标准**:
- [ ] 与 sklearn PCA 结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 3: 博弈论组合赋权（5 天，5 人日）

#### Task 3.1: 实现博弈论组合（`lib/weighting/combination/game_theory.py`）
```python
@register_weighting_method("combination_game_theory")
class GameTheoryCombinationMethod(WeightingMethod):
    """
    博弈论组合赋权（纳什均衡解）

    思想:
    寻找使各赋权方法偏差最小的组合权重

    优化问题:
    min Σ||w - w_i||²
    s.t. Σw_j = 1, w_j >= 0

    求解（拉格朗日乘数法）:
    1. 构建权重矩阵 W = [w_1, w_2, ..., w_m]^T (m x n)
    2. 计算 W^T * W
    3. 求解线性方程组: (W^T * W) * w^* = ones(n)
    4. 归一化: w = w^* / Σ(w^*_j)

    参数:
    - methods: 赋权方法列表（如 ["entropy", "ahp", "critic"]）
    - weights: 各方法权重（可选，默认等权重）

    特点:
    - 纳什均衡解
    - 最小化与各方法的偏差
    - 更客观的组合方式
    """
```

**实现要点**:
- 多个赋权方法调用
- 权重矩阵构建
- 线性方程组求解（`numpy.linalg.solve`）
- 归一化

#### Task 3.2: YAML 配置支持
```yaml
weighting:
  method: combination_game_theory
  config:
    methods:
      - name: entropy
        weight: 0.4
      - name: ahp
        weight: 0.3
      - name: critic
        weight: 0.3
```

#### Task 3.3: 单元测试
- [ ] 测试纳什均衡求解
- [ ] 测试多方法组合
- [ ] 测试等权重和不等权重
- [ ] 测试边界情况（单一方法）

**验收标准**:
- [ ] 纳什均衡解正确
- [ ] 与文献计算结果一致
- [ ] 测试覆盖率 >= 80%

---

### Phase 4: 缓存机制（1 天，1 人日）

#### Task 4.1: 实现缓存机制（`lib/optimization/cache.py`）
```python
class MCDCache:
    """
    MCDA 计算缓存

    缓存策略:
    - 标准化结果缓存
    - 赋权结果缓存
    - 算法中间结果缓存

    缓存键:
    hash(data + algorithm + parameters)

    实现:
    - LRU 缓存（functools.lru_cache）
    - 可选磁盘缓存（joblib.Memory）
    """
```

**实现要点**:
- LRU 内存缓存
- 可选磁盘缓存
- 缓存失效策略

**验收标准**:
- [ ] 缓存命中率 > 50%
- [ ] 性能提升 > 30%

---

### Phase 5: 并行计算（1 天，1 人日）

#### Task 5.1: 实现并行计算（`lib/optimization/parallel.py`）
```python
class ParallelExecutor:
    """
    并行执行器

    应用场景:
    - 多方案并行计算
    - 多算法并行运行
    - 敏感性分析并行

    实现:
    - multiprocessing.Pool
    - concurrent.futures
    """
```

**实现要点**:
- 方案级并行
- 算法级并行
- 敏感性分析并行

**验收标准**:
- [ ] 多核利用率 > 70%
- [ ] 性能提升 > 50%（4 核）

---

### Phase 6: 大数据集优化（1.5 天，1.5 人日）

#### Task 6.1: 实现大数据集优化（`lib/optimization/large_scale.py`）
```python
class LargeScaleOptimizer:
    """
    大数据集优化器

    优化策略:
    - 稀疏矩阵（scipy.sparse）
    - 分块计算
    - 增量计算
    - 采样近似
    """
```

**实现要点**:
- 稀疏矩阵支持
- 分块计算（1000 方案/块）
- 增量权重更新

**验收标准**:
- [ ] 支持 10000+ 方案
- [ ] 内存占用 < 4GB

---

### Phase 7: 单元测试（2 天，2 人日）

#### Task 7.1: 赋权测试
- [ ] `test_weighting/test_delphi.py`
- [ ] `test_weighting/test_pca.py`
- [ ] `test_weighting/test_game_theory.py`

#### Task 7.2: 性能测试
- [ ] `test_optimization/test_cache.py`
- [ ] `test_optimization/test_parallel.py`
- [ ] `test_optimization/test_large_scale.py`

**验收标准**:
- [ ] 所有测试通过
- [ ] 测试覆盖率 >= 80%

---

### Phase 8: 集成测试（1 天，1 人日）

#### Task 8.1: 端到端测试
- [ ] 德尔菲法 + 博弈论组合完整流程
- [ ] PCA + TOPSIS 完整流程
- [ ] 大数据集性能测试（10000 方案）

#### Task 8.2: 压力测试
- [ ] 100 准则 x 10000 方案
- [ ] 内存占用测试
- [ ] 并发请求测试

**验收标准**:
- [ ] 集成测试通过
- [ ] 性能满足要求（< 30 秒）

---

### Phase 9: 使用文档（1 天，1 人日）

#### Task 9.1: 更新参考文档
- [ ] `references/algorithms.md` - 新增德尔菲法和 PCA
- [ ] `references/yaml-schema.md` - 新增配置参数
- [ ] `references/examples.md` - 新增使用示例
- [ ] `references/performance.md` - 性能优化指南

#### Task 9.2: 示例配置
- [ ] `tests/fixtures/delphi_rounds.yaml`
- [ ] `tests/fixtures/pca_dataset.yaml`
- [ ] `tests/fixtures/large_scale.yaml`

**验收标准**:
- [ ] 文档清晰易懂
- [ ] 示例可运行

---

### Phase 10: 部署文档（1 天，1 人日）

#### Task 10.1: 创建部署配置
- [ ] `deployment/docker/Dockerfile`
- [ ] `deployment/docker/docker-compose.yml`
- [ ] `deployment/kubernetes/deployment.yaml`
- [ ] `deployment/kubernetes/service.yaml`
- [ ] `deployment/config/production.yaml`
- [ ] `deployment/config/development.yaml`

#### Task 10.2: 部署文档
- [ ] Docker 部署指南
- [ ] Kubernetes 部署指南
- [ ] 配置管理指南
- [ ] 监控和日志指南

**验收标准**:
- [ ] Docker 镜像构建成功
- [ ] Kubernetes 部署成功
- [ ] 配置管理清晰

---

### Phase 11: 代码审查和优化（1 天，1 人日）

#### Task 11.1: 代码质量
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过
- [ ] 代码格式化
- [ ] 性能分析（`cProfile`）

**验收标准**:
- [ ] 无类型错误
- [ ] 无 lint 警告
- [ ] 性能瓶颈优化

---

### Phase 12: E2E 验证（1 天，1 人日）

#### Task 12.1: 真实案例验证
- [ ] 大规模决策案例（100 准则 x 10000 方案）
- [ ] 德尔菲法 + 博弈论组合案例
- [ ] PCA + 高级算法案例

#### Task 12.2: 生产环境验证
- [ ] Docker 容器化验证
- [ ] Kubernetes 部署验证
- [ ] 监控和日志验证

**验收标准**:
- [ ] 所有案例通过
- [ ] 生产环境就绪
- [ ] 文档无错误

---

## 🔍 验收标准

### 功能验收
- [ ] 2 种特殊赋权方法（德尔菲法 + PCA）正确实现
- [ ] 1 种高级组合赋权（博弈论组合）正确实现
- [ ] 缓存机制正确工作
- [ ] 并行计算正确工作
- [ ] 大数据集优化正确工作
- [ ] YAML 配置支持（德尔菲法多轮 + 博弈论组合）

### 质量验收
- [ ] 测试覆盖率 >= 80%
- [ ] 所有 pytest 测试通过
- [ ] 文档完善
- [ ] `mypy --strict` 通过
- [ ] `ruff` lint 通过

### 流程验收
- [ ] Git Flow 规范遵循
- [ ] TDD 进度文件维护（`docs/active/tdd-mcda-core-v0.5.md`）
- [ ] Conventional Commits 规范

### 架构验收
- [ ] 代码复用性高
- [ ] 接口一致性
- [ ] 可扩展性
- [ ] 性能优化有效

### 性能验收
- [ ] 缓存命中率 > 50%
- [ ] 并行计算性能提升 > 50%（4 核）
- [ ] 支持 10000+ 方案
- [ ] 内存占用 < 4GB

### 部署验收
- [ ] Docker 镜像构建成功
- [ ] Kubernetes 部署成功
- [ ] 配置管理清晰
- [ ] 监控和日志完善

---

## ⚠️ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 德尔菲法多轮收敛困难 | Medium | Medium | 提供默认最大轮数，强制终止 |
| PCA 特征值分解数值不稳定 | Medium | Low | 使用 scipy.linalg.eigh（更稳定）|
| 博弈论组合求解失败 | Low | Medium | 降级到简单加权组合 |
| 并行计算进程管理复杂 | Medium | Low | 使用 concurrent.futures（更简单）|
| 大数据集内存不足 | Low | High | 分块计算，提供内存监控 |
| Docker 镜像体积过大 | Low | Low | 多阶段构建，减小体积 |

---

## 📅 时间线

| 周次 | 阶段 | 交付物 |
|------|------|--------|
| Week 1 | Phase 1-2 | 德尔菲法 + PCA 赋权 |
| Week 2 | Phase 3 | 博弈论组合赋权 |
| Week 3 | Phase 4-7 | 性能优化（缓存 + 并行 + 大数据集）+ 测试 |
| Week 4 | Phase 8-12 | 集成测试 + 文档 + 部署 + 验证 |

---

## 📝 参考资料

### 架构文档
- [ADR-003: 赋权方法路线图](../../decisions/003-mcda-weighting-roadmap.md)

### 需求文档
- [MCDA Core 需求分析](../../requirements/mcda-core.md)

### 前序版本计划
- [v0.2 MVP 执行计划](../v0.2/mvp-execution-plan.md)
- [v0.3 基础扩展执行计划](../v0.3/basic-extension-execution-plan.md)
- [v0.4 高级功能执行计划](../v0.4/advanced-features-execution-plan.md)

### 外部参考
- [Delphi Method](https://en.wikipedia.org/wiki/Delphi_method)
- [PCA](https://en.wikipedia.org/wiki/Principal_component_analysis)
- [Nash Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium)

---

## 🚀 后续演进

### v1.0 规划（未来）
- [ ] Web UI 可视化界面
- [ ] 实时协作决策支持
- [ ] 机器学习增强
- [ ] 云原生微服务架构
- [ ] 国际化支持

---

**创建者**: hunkwk + AI collaboration
**创建时间**: 2026-01-31
**最后更新**: 2026-01-31
**文档版本**: v1.0
**状态**: 待执行
**依赖**: v0.4 高级功能完成并验收通过
**下一步**: v0.4 高级功能验收通过后开始执行
