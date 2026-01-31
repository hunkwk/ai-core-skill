# ADR-003: MCDA 赋权方法实现优先级路线图

## 状态
**已接受 (Accepted)**

## 日期
2026-01-31

## 上下文 (Context)
MCDA Core 框架需要支持多种赋权方法（主观、客观、组合），以支持不同应用场景。现有文献中存在 8+ 种常用赋权方法，需要确定实现优先级和分阶段计划。

**候选方法列表**:

### 主观赋权法
1. **直接赋权法** (Direct Weighting) - 专家直接指定权重
2. **德尔菲法** (Delphi Method) - 多轮专家咨询
3. **AHP** (层次分析法) - 成对比较 + 一致性检验

### 客观赋权法
4. **熵权法** (Entropy Weight Method) - 基于信息熵
5. **变异系数法** (Coefficient of Variation) - 基于数据变异
6. **CRITIC 法** - 对比强度 + 冲突性
7. **离差最大化法** (Maximizing Deviation) - 最大化方案差异
8. **标准离差法** (Standard Deviation) - 基于离散程度
9. **主成分分析法** (PCA) - 降维 + 权重提取

### 组合赋权法
10. **简单加权组合** - 主客观线性加权
11. **博弈论组合** - 纳什均衡解

**挑战**:
- 如何平衡应用热度、实现难度、用户价值？
- 如何分阶段实施，确保每个版本都有可用功能？
- 如何设计统一的赋权方法接口？

---

## 决策 (Decision)

### 1. 优先级评分体系

采用**四维评分法**确定优先级：

| 维度 | 权重 | 评分标准 (1-5 分) |
|------|------|------------------|
| **应用热度** | 40% | 文献引用量、实际使用频率、社区活跃度 |
| **实现难度** | 30% | 算法复杂度 (5=最简单)、依赖库需求 (5=最少)、开发工作量 (5=最小) |
| **用户价值** | 20% | 解决实际问题的能力、适用场景广度 |
| **架构兼容性** | 10% | 与现有 WSM 框架的适配度、接口设计难度 |

### 2. 综合评分结果

| 排名 | 方法 | 热度 | 难度 | 价值 | 兼容 | **总分** | 类型 | 实施阶段 |
|------|------|------|------|------|------|----------|------|---------|
| **1** | **熵权法** | 5.0 | 4.0 | 4.5 | 5.0 | **4.65** | 客观 | **v0.2** |
| **2** | **AHP** | 5.0 | 3.0 | 5.0 | 4.0 | **4.30** | 主观 | **v0.4** |
| **3** | **变异系数法** | 3.5 | 5.0 | 4.0 | 5.0 | **4.20** | 客观 | **v0.2** |
| **4** | **CRITIC 法** | 4.5 | 3.0 | 4.5 | 5.0 | **4.05** | 客观 | **v0.3** |
| **5** | **离差最大化法** | 3.5 | 4.0 | 3.5 | 5.0 | **3.85** | 客观 | **v0.3** |
| **6** | **标准离差法** | 2.5 | 5.0 | 3.5 | 5.0 | **3.70** | 客观 | **v0.2** |
| **7** | **德尔菲法** | 3.0 | 3.5 | 4.0 | 3.0 | **3.30** | 主观 | **v0.4** |
| **8** | **PCA** | 4.0 | 2.0 | 4.0 | 3.0 | **3.10** | 客观 | **v0.3** |
| - | **组合赋权** | - | 4.0 | 5.0 | 5.0 | **4.50** | 组合 | **v0.4** |

**评分依据**:

#### 应用热度 (文献引用量)
- **AHP**: 694+ 引用（最热门主观方法）
- **熵权法 + CRITIC**: 394+ 引用（最热门客观方法）
- **PCA**: 200+ 引用
- **变异系数法 / 标准离差法**: 50-100 引用

#### 实现难度
- **⭐⭐⭐⭐⭐ 极简单** (1-2 人日): 标准离差法、变异系数法
- **⭐⭐⭐⭐ 简单** (2-3 人日): 熵权法、离差最大化法
- **⭐⭐⭐ 中等** (3-4 人日): CRITIC 法、德尔菲法、AHP
- **⭐⭐ 复杂** (4-5 人日): PCA（需矩阵运算库）

---

### 3. 分阶段实施计划

#### v0.2: 基础赋权层 (2-3 周)

**目标**: 实现最常用的客观赋权方法，支持数据驱动的权重计算

**实现方法**:
1. ✅ **熵权法** (2 人日)
   - 优先级: **P0** (最高)
   - 理由: 最高热度 + 简单实现 + 与 AHP 组合最常用

2. ✅ **变异系数法** (1 人日)
   - 优先级: **P1**
   - 理由: 极简实现 + 补充熵权法的不足

3. ✅ **标准离差法** (0.5 人日)
   - 优先级: **P1**
   - 理由: 最简单的客观方法 + 基准对比

4. ✅ **测试与文档** (2.5 人日)
   - 单元测试 (80%+ 覆盖率)
   - 集成测试
   - 参考文档编写

**总工作量**: **6 人日** (约 2 周)

**里程碑**:
- [ ] 用户可以从数据自动计算权重
- [ ] 支持 3 种客观赋权方法
- [ ] YAML 配置支持 `weighting.method` 字段

---

#### v0.3: 高级赋权层 (3-4 周)

**目标**: 实现更复杂的客观方法，提升权重计算质量

**实现方法**:
1. ✅ **CRITIC 法** (3 人日)
   - 优先级: **P0**
   - 理由: 综合对比强度和冲突性，优于单一熵权法

2. ✅ **离差最大化法** (2 人日)
   - 优先级: **P1**
   - 理由: 最大化方案间差异，适合排序场景

3. ✅ **主成分分析法 (PCA)** (4 人日)
   - 优先级: **P2**
   - 理由: 降维能力强，但实现复杂且需额外依赖 (scipy)

4. ✅ **测试与文档** (6 人日)
   - 单元测试
   - 性能测试（大数据集）
   - 算法对比文档

**总工作量**: **15 人日** (约 3-4 周)

**里程碑**:
- [ ] 支持 6 种客观赋权方法
- [ ] 可选依赖 scipy (用于 PCA)
- [ ] 赋权方法推荐引擎

---

#### v0.4: 主观与组合赋权层 (4-5 周)

**目标**: 实现主观赋权方法和组合策略，完整的赋权体系

**实现方法**:
1. ✅ **AHP (层次分析法)** (4 人日)
   - 优先级: **P0**
   - 理由: 最热门主观方法，与熵权法组合最佳实践

2. ✅ **德尔菲法** (3 人日)
   - 优先级: **P1**
   - 理由: 支持多专家咨询，适合团队决策

3. ✅ **组合赋权** (5 人日)
   - **简单加权组合**: `w = α·w_sub + (1-α)·w_obj`
   - **博弈论组合**: 纳什均衡解
   - **推荐配置**: AHP (0.5) + 熵权法 (0.5)

4. ✅ **测试与文档** (7 人日)
   - 单元测试
   - 案例研究（实际业务场景）
   - 最佳实践指南

**总工作量**: **19 人日** (约 4-5 周)

**里程碑**:
- [ ] 完整主客观赋权体系
- [ ] 支持 2 种主观赋权 + 2 种组合策略
- [ ] 实际案例验证

---

### 4. 核心架构设计

#### 4.1 赋权方法抽象基类

```python
# lib/weighting/base.py
from abc import ABC, abstractmethod
from ..models import DecisionProblem, Criterion

@dataclass
class WeightingResult:
    """赋权结果"""
    weights: dict[str, float]  # {criterion_name: weight}
    method: str  # 方法名称
    metadata: dict[str, Any]  # 方法特定元数据
    scores: dict[str, dict[str, float]] | None = None  # 可选: 评分矩阵

class WeightingMethod(ABC):
    """赋权方法基类"""

    @abstractmethod
    def calculate(self, problem: DecisionProblem, **kwargs) -> WeightingResult:
        """
        计算权重

        Args:
            problem: 决策问题（包含评分矩阵）
            **kwargs: 方法特定参数

        Returns:
            WeightingResult: 权重计算结果
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """方法名称"""
        pass

    @property
    def is_objective(self) -> bool:
        """是否为客观赋权方法"""
        return False

    def validate(self, problem: DecisionProblem) -> ValidationResult:
        """验证输入数据（可覆盖）"""
        return ValidationResult(is_valid=True)

    @property
    def metadata(self) -> WeightingMethodMetadata:
        """方法元数据"""
        return WeightingMethodMetadata(
            name=self.name,
            is_objective=self.is_objective,
            requires_scores=True,  # 是否需要评分矩阵
            min_criteria=2,  # 最少准则数
        )
```

#### 4.2 赋权服务

```python
# lib/weighting/service.py
class WeightingService:
    """赋权服务"""

    def __init__(self):
        self._methods: dict[str, WeightingMethod] = {}

    def register_method(self, method: WeightingMethod) -> None:
        """注册赋权方法"""
        self._methods[method.name] = method

    def calculate_weights(
        self,
        problem: DecisionProblem,
        method: str | None = None,
        **kwargs
    ) -> WeightingResult:
        """
        计算权重

        Args:
            problem: 决策问题
            method: 赋权方法名称（若为 None，自动推荐）
            **kwargs: 方法参数

        Returns:
            WeightingResult: 权重计算结果
        """
        if method is None:
            method = self.suggest_method(problem)

        weighting_method = self.get_method(method)
        return weighting_method.calculate(problem, **kwargs)

    def suggest_method(self, problem: DecisionProblem) -> str:
        """
        推荐赋权方法

        推荐策略:
        - 有评分数据 → 熵权法
        - 有成对比较 → AHP
        - 数据样本少 → 变异系数法
        - 需要降维 → PCA
        """
        if problem.scores:
            return "entropy"  # 默认推荐熵权法
        raise ValueError("无法推荐赋权方法：缺少必要数据")

    def get_method(self, name: str) -> WeightingMethod:
        """获取赋权方法实例"""
        if name not in self._methods:
            available = ", ".join(self._methods.keys())
            raise ValueError(f"未知的赋权方法: {name}. 可用方法: {available}")
        return self._methods[name]()
```

#### 4.3 方法注册机制

```python
# lib/weighting/__init__.py
from typing import Callable, Type

_methods: dict[str, Type[WeightingMethod]] = {}

def register_weighting_method(name: str) -> Callable:
    """赋权方法注册装饰器"""
    def decorator(cls: Type[WeightingMethod]) -> Type[WeightingMethod]:
        _methods[name] = cls
        return cls
    return decorator

def get_weighting_method(name: str) -> WeightingMethod:
    """获取赋权方法实例"""
    if name not in _methods:
        available = ", ".join(_methods.keys())
        raise ValueError(f"未知的赋权方法: {name}. 可用方法: {available}")
    return _methods[name]()

# 使用示例
@register_weighting_method("entropy")
class EntropyWeightMethod(WeightingMethod):
    ...
```

---

### 5. 各方法实现要点

#### 5.1 熵权法 (v0.2)

**算法步骤**:
1. 数据标准化（归一化到 0-1）
2. 计算每个准则的信息熵: `E_j = -Σ(p_ij * ln(p_ij))`
3. 计算差异系数: `d_j = 1 - E_j`
4. 计算权重: `w_j = d_j / Σ(d_k)`

**核心代码**:
```python
@register_weighting_method("entropy")
class EntropyWeightMethod(WeightingMethod):
    """熵权法"""

    @property
    def name(self) -> str:
        return "entropy"

    @property
    def is_objective(self) -> bool:
        return True

    def calculate(self, problem: DecisionProblem, **kwargs) -> WeightingResult:
        epsilon = kwargs.get("epsilon", 1e-10)  # 防止 log(0)

        # 1. 标准化
        normalized = self._normalize(problem.scores)

        # 2. 计算熵值
        entropies = {}
        for crit in problem.criteria:
            values = [normalized[alt][crit.name] for alt in problem.alternatives]
            p_ij = np.array(values) / np.sum(values)
            entropy = -np.sum(p_ij * np.log(p_ij + epsilon))
            entropies[crit.name] = entropy

        # 3. 计算差异系数
        max_entropy = np.log(len(problem.alternatives))
        diversities = {name: max_entropy - e for name, e in entropies.items()}

        # 4. 计算权重
        total_diversity = sum(diversities.values())
        weights = {name: d / total_diversity for name, d in diversities.items()}

        return WeightingResult(
            weights=weights,
            method=self.name,
            metadata={"entropies": entropies, "diversities": diversities},
        )
```

**依赖**: `numpy`
**工作量**: 2 人日

---

#### 5.2 变异系数法 (v0.2)

**算法步骤**:
1. 计算每个准则的均值: `μ_j`
2. 计算每个准则的标准差: `σ_j`
3. 计算变异系数: `CV_j = σ_j / μ_j`
4. 归一化得到权重: `w_j = CV_j / Σ(CV_k)`

**核心代码**:
```python
@register_weighting_method("cv")
class CoefficientOfVariationMethod(WeightingMethod):
    """变异系数法"""

    def calculate(self, problem: DecisionProblem, **kwargs) -> WeightingResult:
        cvs = {}
        for crit in problem.criteria:
            values = [problem.scores[alt][crit.name] for alt in problem.alternatives]
            mean = np.mean(values)
            std = np.std(values)
            cv = std / mean if mean != 0 else 0
            cvs[crit.name] = cv

        total_cv = sum(cvs.values())
        weights = {name: cv / total_cv for name, cv in cvs.items()}

        return WeightingResult(
            weights=weights,
            method=self.name,
            metadata={"coefficients_of_variation": cvs},
        )
```

**依赖**: `numpy`
**工作量**: 1 人日

---

#### 5.3 CRITIC 法 (v0.3)

**算法步骤**:
1. 数据标准化（无量纲化）
2. 计算对比强度（标准差）: `σ_j`
3. 计算冲突性（相关系数）: `Σ(1 - r_jk)`
4. 计算信息量: `C_j = σ_j * Σ(1 - r_jk)`
5. 归一化得到权重: `w_j = C_j / Σ(C_k)`

**依赖**: `numpy`
**工作量**: 3 人日

---

#### 5.4 AHP (v0.4)

**算法步骤**:
1. 构建成对比较矩阵: `A = [a_ij]`
2. 计算权重向量（特征向量法）: `A · w = λ_max · w`
3. 计算最大特征值: `λ_max`
4. 一致性检验: `CI = (λ_max - n) / (n - 1)`
5. 计算一致性比率: `CR = CI / RI`
6. 若 `CR < 0.1`，通过检验

**依赖**: `numpy`（可选 `scipy.linalg` 用于特征值计算）
**工作量**: 4 人日

**特殊输入格式**:
```yaml
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

---

### 6. 组合赋权策略

#### 6.1 简单加权组合

```python
@register_weighting_method("combination_simple")
class SimpleCombinationMethod(WeightingMethod):
    """简单加权组合"""

    def calculate(
        self,
        problem: DecisionProblem,
        subjective_method: str = "ahp",
        objective_method: str = "entropy",
        alpha: float = 0.5,
        **kwargs
    ) -> WeightingResult:
        """
        Args:
            alpha: 主观权重占比（0-1）
        """
        service = WeightingService()

        # 计算主客观权重
        w_sub = service.calculate_weights(problem, subjective_method).weights
        w_obj = service.calculate_weights(problem, objective_method).weights

        # 加权组合
        weights = {
            name: alpha * w_sub[name] + (1 - alpha) * w_obj[name]
            for name in w_sub.keys()
        }

        return WeightingResult(
            weights=weights,
            method=f"combination_{subjective_method}_{objective_method}",
            metadata={
                "subjective_weights": w_sub,
                "objective_weights": w_obj,
                "alpha": alpha,
            },
        )
```

#### 6.2 博弈论组合（纳什均衡）

```python
@register_weighting_method("combination_game")
class GameTheoryCombinationMethod(WeightingMethod):
    """博弈论组合（纳什均衡解）"""

    def calculate(
        self,
        problem: DecisionProblem,
        methods: list[str],
        **kwargs
    ) -> WeightingResult:
        """
        寻找纳什均衡解: 最小化各权重向量与组合权重的偏差

        优化问题:
        min Σ||w - w_i||^2
        s.t. Σw_j = 1, w_j >= 0
        """
        service = WeightingService()

        # 计算各方法权重
        weight_vectors = [
            np.array(list(service.calculate_weights(problem, m).weights.values()))
            for m in methods
        ]

        # 使用拉格朗日乘数法求解
        W = np.vstack(weight_vectors)  # (m, n) 矩阵
        # ... 求解过程略

        return WeightingResult(...)
```

---

### 7. YAML 配置接口

#### 7.1 自动计算权重

```yaml
# decision.yaml
alternatives:
  - 方案 A
  - 方案 B
  - 方案 C

# 方式 1: 使用评分矩阵
scores:
  方案 A:
    成本: 20
    功能: 80
    周期: 30
  方案 B:
    成本: 50
    功能: 95
    周期: 15
  方案 C:
    成本: 35
    功能: 85
    周期: 25

# 方式 2: 指定赋权方法（自动计算权重）
weighting:
  method: entropy  # 赋权方法
  config:
    epsilon: 1e-10  # 方法参数

# 方式 3: 直接指定权重（不计算）
criteria:
  - name: 成本
    weight: 0.3  # 手动指定权重
    direction: lower_better
  - name: 功能
    weight: 0.4
    direction: higher_better
  - name: 周期
    weight: 0.3
    direction: lower_better

algorithm:
  name: wsm
```

#### 7.2 组合赋权

```yaml
weighting:
  method: combination_simple
  config:
    subjective_method: ahp
    objective_method: entropy
    alpha: 0.5  # 主观权重占比

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

---

### 8. 文件结构

```
lib/weighting/
├── __init__.py               # 方法注册和公共 API
├── base.py                   # 抽象基类和接口
├── service.py                # 赋权服务（协调器）
├── models.py                 # 赋权相关数据模型
├── objective/                # 客观赋权法目录
│   ├── __init__.py
│   ├── entropy.py            # 熵权法 ⭐ v0.2
│   ├── cv.py                 # 变异系数法 ⭐ v0.2
│   ├── std.py                # 标准离差法 ⭐ v0.2
│   ├── critic.py             # CRITIC 法 ⭐ v0.3
│   ├── max_dev.py            # 离差最大化法 ⭐ v0.3
│   └── pca.py                # 主成分分析法 ⭐ v0.3 (可选依赖 scipy)
├── subjective/               # 主观赋权法目录
│   ├── __init__.py
│   ├── direct.py             # 直接赋权法
│   ├── ahp.py                # AHP ⭐ v0.4
│   └── delphi.py             # 德尔菲法 ⭐ v0.4
└── combination/              # 组合赋权法目录
    ├── __init__.py
    ├── simple.py             # 简单加权组合 ⭐ v0.4
    └── game_theory.py        # 博弈论组合 ⭐ v0.4

tests/weighting/
├── conftest.py
├── test_entropy.py
├── test_cv.py
├── test_critic.py
├── test_ahp.py
├── test_combination.py
└── fixtures/
    ├── sample_data.yaml
    └── ahp_comparison.yaml
```

---

### 9. 依赖库需求

| 方法 | 核心依赖 | 可选依赖 | 用途 |
|------|---------|---------|------|
| 熵权法 | numpy | - | 对数运算 |
| 变异系数法 | numpy | - | 统计计算 |
| 标准离差法 | numpy | - | 统计计算 |
| CRITIC 法 | numpy | - | 相关系数 |
| 离差最大化法 | numpy | - | 优化求解 |
| PCA | numpy | **scipy** | 特征值分解 |
| AHP | numpy | **scipy.linalg** | 特征值计算 |
| 组合赋权 | numpy | - | 线性组合 |

**最小依赖策略**:
- **必需依赖**: `numpy` (所有方法)
- **可选依赖**: `scipy` (仅 PCA 和 AHP 的高级功能)
- **提示**: 用户安装时，scipy 作为 extras: `pip install mcda-core[pca]`

---

## 权衡分析 (Trade-offs)

### 正面影响 ✅
1. **清晰路线图**: 分 3 个阶段，每个阶段都有明确交付目标
2. **优先级合理**: 平衡热度、难度、价值
3. **架构可扩展**: 统一接口，易于添加新方法
4. **向后兼容**: 不破坏现有 WSM 算法

### 负面影响 ⚠️
1. **开发周期长**: 完整实施需要 10-12 周
2. **依赖递增**: v0.3 起需要 scipy（可选）
3. **复杂度增加**: 主观方法需要特殊输入格式

### 缓解措施 🛡️
1. **MVP 优先**: v0.2 先交付核心功能（熵权法 + 变异系数法）
2. **可选依赖**: scipy 作为 extras，不强制安装
3. **渐进式文档**: 每个版本配套完整文档和示例

---

## 后果 (Consequences)

### 对开发的影响
- **v0.2** (2 周): 客观赋权基础，可满足 80% 用户需求
- **v0.3** (3-4 周): 高级客观方法，权重质量提升
- **v0.4** (4-5 周): 主观赋权 + 组合策略，完整体系

### 对用户的影响
- **早期用户** (v0.2): 可使用数据驱动的客观赋权
- **中期用户** (v0.3): 更多方法选择，推荐引擎
- **成熟用户** (v0.4): 主客观结合，专家知识融入

### 对架构的影响
- **新增模块**: `lib/weighting/` （赋权服务层）
- **模块依赖**: 算法层可依赖赋权服务
- **接口扩展**: `DecisionProblem` 增加 `weighting` 字段

---

## 未来演进路径

### 短期 (v0.2 - 2025年2月)
- ✅ 熵权法、变异系数法、标准离差法
- ✅ 赋权服务基础架构
- ✅ YAML 配置支持

### 中期 (v0.3 - 2025年3月)
- ⏳ CRITIC 法、离差最大化法
- ⏳ PCA (可选依赖)
- ⏳ 赋权方法推荐引擎

### 长期 (v0.4 - 2025年4月)
- ⏳ AHP、德尔菲法
- ⏳ 组合赋权策略
- ⏳ 案例研究和最佳实践

### 可选扩展 (v1.0+)
- ⏳ 模糊赋权方法
- ⏳ 神经网络赋权
- ⏳ 交互式赋权（Web UI）

---

## 参考资料
- [Comparison of Key Weighting Methods in MCDA](https://managementpapers.polsl.pl/wp-content/uploads/2025/06/223-Wolny.pdf)
- [Entropy, CRITIC, SD Methods Comparison](https://www.dmame-journal.socialspacejournal.eu/index.php/dmame/article/download/194/75)
- [Weighting Methods and Their Effects on MCDA](http://ndl.ethernet.et/bitstream/123456789/71623/1/2015_Book_WeightingMethodsAndTheirEffect.pdf)
- [AHP-EWM 组合赋权](https://ask.csdn.net/questions/8975014)

---

**决策者**: hunkwk + AI architect agent
**批准日期**: 2026-01-31
**状态**: 已批准，按路线图实施
**总工作量**: 40 人日 (约 10-12 周)

**相关文档**:
- [ADR-001: 分层架构设计](./001-mcda-layered-architecture.md)
- [ADR-002: 评分标准化方法](./002-mcda-normalization-methods.md)
- [ADR-004: 汇总算法架构设计](./004-mcda-aggregation-algorithms.md)

