# MCDA Core v0.3 Implementation Plan

**Status**: In Planning
**Version**: v0.3.0
**Target Release**: 2026-02-15
**Based on**: v0.2.1 (MVP Release)
**Planning Date**: 2026-02-01

---

## 📊 Executive Summary

MCDA Core v0.3 是在v0.2.1 MVP基础上的重要增强版本，专注于**配置灵活性**、**算法扩展**和**轻量可视化**三个核心方向。

**核心目标**：
- ✅ 支持多种配置格式（JSON + YAML）
- ✅ 新增3种核心算法（AHP、熵权法、PROMETHEE-II）
- ✅ 提供轻量级可视化（HTML报告）
- ✅ 保持最小依赖原则
- ✅ 提升开发者体验

---

## 🎯 Feature Overview

### Phase 1: 配置增强 (Configuration Enhancement)

**目标**: 提升配置灵活性，支持多种数据源

**功能列表**：
- [ ] JSON 配置文件支持
- [ ] 配置模板生成命令 (`mcda init --template`)
- [ ] 配置验证增强（详细错误提示）
- [ ] 配置文件格式转换工具 (`mcda convert --format json`)

**优先级**: 高
**估算时间**: 3-5天

### Phase 2: 算法扩展 (Algorithm Extension)

**目标**: 增强决策分析能力，支持更多算法

**功能列表**：
- [ ] AHP (Analytic Hierarchy Process) - 层次分析法
  - 成对比较矩阵
  - 一致性检验
  - 权重计算
- [ ] 熵权法 (Entropy Weight Method) - 客观赋权
  - 信息熵计算
  - 客观权重确定
- [ ] PROMETHEE-II - 偏好排序组织法
  - 偏好函数
  - 流量计算
  - 完全排序

**优先级**: 高
**估算时间**: 5-7天

### Phase 3: 轻量可视化 (Lightweight Visualization)

**目标**: 提供直观的结果展示，无需重型依赖

**功能列表**：
- [ ] HTML 报告模板（Jinja2）
  - 决策结果表格
  - 排名对比图表
  - 敏感性分析热力图
- [ ] ASCII 文本图表增强
  - 柱状图
  - 雷达图
- [ ] CSS 样式主题（浅色/深色）

**优先级**: 中
**估算时间**: 3-4天

---

## 📋 Implementation Plans

### 001: JSON 配置支持

**Status**: Pending
**Priority**: High
**Assigned To**: TBD

**Requirements**:
- 支持 JSON 格式配置文件（与 YAML 并存）
- 保持 API 兼容性
- 错误提示友好

**Implementation Approach**:
1. 引入 `ConfigLoader` 抽象接口
2. 实现 `JSONLoader` 和 `YAMLLoader`
3. 更新 `MCDAOrchestrator.load_from_*()` 方法
4. 添加 `load_from_json()` 和 `load_from_yaml()` 方法
5. 自动检测文件格式（基于扩展名）

**Testing Strategy**:
- 单元测试：JSON/YAML 加载一致性
- 集成测试：完整工作流
- 错误处理测试：格式错误、缺失字段

**Acceptance Criteria**:
- [ ] 可以加载 JSON 配置文件
- [ ] JSON 和 YAML 配置结果一致
- [ ] 错误提示清晰友好
- [ ] 文档完整（示例配置）

**Related ADR**: `docs/decisions/mcda-core/005-loader-abstract.md`

---

### 002: AHP 算法实现

**Status**: Pending
**Priority**: High
**Assigned To**: TBD

**Requirements**:
- 支持成对比较矩阵
- 一致性比率（CR）计算
- 特征向量法求权重
- CR > 0.1 时警告

**Implementation Approach**:
1. 创建 `algorithms/ahp.py`
2. 实现成对比较矩阵验证
3. 实现特征向量计算（幂法）
4. 实现一致性检验
5. 注册到算法注册表

**Testing Strategy**:
- 单元测试：标准Saaty矩阵
- 一致性检验测试
- 边界条件测试

**Acceptance Criteria**:
- [ ] 通过标准Saaty测试案例
- [ ] CR > 0.1 时发出警告
- [ ] 与文献结果一致

**Dependencies**:
- numpy（矩阵运算）

---

### 003: 熵权法实现

**Status**: Pending
**Priority**: High
**Assigned To**: TBD

**Requirements**:
- 计算信息熵
- 计算差异系数
- 确定客观权重
- 与主观权重集成

**Implementation Approach**:
1. 创建 `algorithms/entropy_weight.py`
2. 实现数据标准化
3. 计算信息熵
4. 计算客观权重
5. 提供主客观权重组合方法

**Testing Strategy**:
- 单元测试：标准数据集
- 边界条件测试（零权重）
- 与文献结果对比

**Acceptance Criteria**:
- [ ] 标准案例测试通过
- [ ] 权重和为1
- [ ] 处理零方差准则

**Dependencies**:
- numpy（数学运算）

---

### 004: PROMETHEE-II 算法实现

**Status**: Pending
**Priority**: High
**Assigned To**: TBD

**Requirements**:
- 支持6种偏好函数
- 计算离开流、进入流
- 计算净流量
- 完全排序

**Implementation Approach**:
1. 创建 `algorithms/promethee.py`
2. 实现6种偏好函数
3. 计算成对偏好度
4. 计算流量
5. 净流量排序

**Testing Strategy**:
- 标准案例测试
- 偏好函数测试
- 排序一致性测试

**Acceptance Criteria**:
- [ ] 标准案例测试通过
- [ ] 支持所有偏好函数
- [ ] 与文献结果一致

**Dependencies**:
- numpy（数学运算）

---

### 005: HTML 报告生成

**Status**: Pending
**Priority**: Medium
**Assigned To**: TBD

**Requirements**:
- 使用 Jinja2 模板
- 支持自定义 CSS 主题
- 响应式设计
- 包含决策结果、排名、敏感性分析

**Implementation Approach**:
1. 添加 Jinja2 依赖
2. 创建 HTML 模板（`reporter/templates/`）
3. 实现 `export_html()` 方法
4. CSS 样式主题
5. 静态资源嵌入

**Testing Strategy**:
- 模板渲染测试
- CSS 样式测试
- 跨浏览器测试（可选）

**Acceptance Criteria**:
- [ ] HTML 报告美观可读
- [ ] 支持浅色/深色主题
- [ ] 响应式设计
- [ ] 无外部依赖（内嵌CSS）

**Dependencies**:
- jinja2（模板引擎）

---

## 🏗️ Architecture Decisions

### ADR-005: 引入 Loader 抽象层

**Status**: Proposed
**Type**: Architectural

**Context**:
- 当前配置加载逻辑硬编码在 `core.py`
- 支持多种配置格式需要重构
- 未来可能支持更多数据源（Excel、数据库）

**Decision**:
引入 `ConfigLoader` 抽象接口，支持多种数据源：

```python
class ConfigLoader(ABC):
    @abstractmethod
    def load(self, source: str | Path) -> DecisionProblem:
        pass

class YAMLLoader(ConfigLoader):
    def load(self, source): ...

class JSONLoader(ConfigLoader):
    def load(self, source): ...
```

**Consequences**:
- ✅ 支持多种配置格式
- ✅ 易于扩展新数据源
- ✅ 降低耦合度
- ⚠️ 需要重构 `core.py`

**Related**: Plan 001

---

### ADR-006: 分离敏感性分析服务

**Status**: Proposed
**Type**: Refactoring

**Context**:
- 当前 `SensitivityService` 职责过重
- 包含扰动生成、排名计算、稳定性评估
- 违反单一职责原则

**Decision**:
拆分为独立服务：

```python
class PerturbationService:
    """生成权重扰动"""
    def generate_perturbations(self, weights, criterion, n_samples)

class RankingStabilityService:
    """评估排名稳定性"""
    def evaluate_stability(self, base_ranking, perturbed_rankings)
```

**Consequences**:
- ✅ 职责分离清晰
- ✅ 易于测试
- ✅ 可复用组件
- ⚠️ 需要更新测试

**Related**: Refactoring task

---

## 📅 Timeline

```
Week 1 (Feb 3-7): Phase 1 - 配置增强
  - Day 1-2: ADR-005 实现（Loader 抽象层）
  - Day 3-4: JSON 配置支持
  - Day 5: 配置模板生成和测试

Week 2 (Feb 10-14): Phase 2 - 算法扩展（上）
  - Day 1-3: AHP 算法
  - Day 4-5: 熵权法

Week 3 (Feb 17-21): Phase 2 - 算法扩展（下）
  - Day 1-3: PROMETHEE-II 算法
  - Day 4-5: 测试和文档

Week 4 (Feb 24-28): Phase 3 - 轻量可视化
  - Day 1-2: HTML 报告模板
  - Day 3: ASCII 图表增强
  - Day 4: 集成测试
  - Day 5: 文档和发布准备
```

**总估算**: 3-4周

---

## 🧪 Testing Strategy

### 单元测试
- 目标覆盖率：**90%+**
- 每个算法至少 10 个测试用例
- 边界条件和错误处理测试

### 集成测试
- 端到端工作流测试
- 多算法对比测试
- 配置格式兼容性测试

### 性能测试
- AHP 大规模矩阵测试（10x10+）
- PROMETHEE 性能基准
- HTML 报告生成性能

### E2E 测试
- 新增 5-10 个 E2E 测试场景
- 包括 JSON 配置、新算法、HTML 报告

---

## 📦 Dependencies

### 新增依赖

```python
# 现有依赖
numpy>=1.20.0           # TOPSIS 矩阵运算

# v0.3 新增
jinja2>=3.0.0           # HTML 报告模板（可选）
```

### 依赖策略
- **核心功能**：零依赖
- **算法层**：numpy 可选
- **报告层**：jinja2 可选

---

## 📚 Documentation Updates

### Required Updates
- [ ] `skills/mcda-core/README.md`
  - JSON 配置示例
  - 新算法使用指南
  - HTML 报告说明
- [ ] `skills/mcda-core/SKILL.md`
  - 算法总数更新（4 → 7）
  - 新算法简要说明
- [ ] `CHANGELOG.md`
  - v0.3.0 发布说明
- [ ] 测试报告
  - `tests/mcda-core/reports/test-report-v0.3.0.md`

---

## ✅ Success Criteria

- [ ] 所有3个Phase完成
- [ ] 7种算法（WSM、WPM、TOPSIS、VIKOR、AHP、熵权法、PROMETHEE-II）
- [ ] 3种配置格式支持（YAML、JSON、自动检测）
- [ ] HTML 报告生成功能
- [ ] 测试覆盖率 ≥ 90%
- [ ] 所有测试通过（350+ 测试）
- [ ] 文档完整更新
- [ ] 无破坏性变更

---

## 🚀 Next Steps

1. ✅ 创建 ADR-005 和 ADR-006
2. ✅ 创建进度文件 `docs/active/mcda-core/v0.3/tdd-json-config.md`
3. ✅ 切换到 `feature/mcda-core` 分支
4. ⏳ 开始 Phase 1 实施

---

**Plan Created**: 2026-02-01
**Last Updated**: 2026-02-01
**Status**: 📋 In Planning
