# ADR-006: 分离敏感性分析服务

**Status**: Proposed
**Type**: Refactoring
**Date**: 2026-02-01
**Project**: MCDA Core v0.3

---

## 📋 Context

### Current Situation
当前 `SensitivityService` 包含多个职责：

```python
class SensitivityService:
    def analyze(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        criterion_name: str,
        n_samples: int = 100
    ) -> SensitivityAnalysis | None:
        # 1. 生成权重扰动
        perturbations = self._generate_perturbations(...)

        # 2. 重新计算排名
        perturbed_rankings = []
        for perturbed_weights in perturbations:
            perturbed_result = self._reanalyze(problem, perturbed_weights)
            perturbed_rankings.append(perturbed_result.ranking)

        # 3. 评估排名稳定性
        stability_metrics = self._evaluate_stability(result.ranking, perturbed_rankings)

        return SensitivityAnalysis(...)
```

### Problems
1. **职责过重**：一个类负责生成扰动、重新分析、评估稳定性
2. **难以测试**：单个测试需要覆盖多个职责
3. **无法复用**：扰动生成逻辑无法被其他功能使用
4. **违反 SRP**：违反单一职责原则（Single Responsibility Principle）

### Requirements
- ✅ 职责分离，每个类专注单一职责
- ✅ 提升可测试性
- ✅ 支持功能复用
- ✅ 保持 API 向后兼容

---

## 🎯 Decision

将 `SensitivityService` 拆分为 **3个独立服务**：

```
SensitivityService (协调器)
    ├── PerturbationService (扰动生成)
    ├── RankingService (排名计算)
    └── StabilityService (稳定性评估)
```

### Design

#### 1. PerturbationService

```python
class PerturbationService:
    """权重扰动生成服务"""

    def __init__(self, random_seed: int | None = None):
        self.random_seed = random_seed

    def generate_perturbations(
        self,
        base_weights: dict[str, float],
        criterion_name: str,
        n_samples: int = 100,
        perturbation_range: tuple[float, float] = (-0.1, 0.1)
    ) -> list[dict[str, float]]:
        """
        为指定准则生成权重扰动

        Args:
            base_weights: 基础权重字典
            criterion_name: 要扰动的准则名称
            n_samples: 扰动样本数量
            perturbation_range: 扰动范围（相对变化）

        Returns:
            扰动后的权重列表（已归一化）
        """
        import random

        if self.random_seed is not None:
            random.seed(self.random_seed)

        perturbations = []

        for _ in range(n_samples):
            # 复制基础权重
            perturbed = base_weights.copy()

            # 扰动指定准则的权重
            original_weight = perturbed[criterion_name]
            delta = random.uniform(*perturbation_range)
            perturbed[criterion_name] *= (1 + delta)

            # 归一化
            total = sum(perturbed.values())
            perturbed = {k: v / total for k, v in perturbed.items()}

            perturbations.append(perturbed)

        return perturbations
```

#### 2. RankingService

```python
class RankingService:
    """排名计算服务"""

    def __init__(self, orchestrator: MCDAOrchestrator):
        self.orchestrator = orchestrator

    def compute_rankings_with_weights(
        self,
        problem: DecisionProblem,
        weights_list: list[dict[str, float]],
        algorithm: str = "topsis"
    ) -> list[list[RankingItem]]:
        """
        使用不同权重计算排名

        Args:
            problem: 决策问题
            weights_list: 权重列表
            algorithm: 算法名称

        Returns:
            排名列表
        """
        rankings = []

        for weights in weights_list:
            # 更新问题权重
            updated_problem = self._update_weights(problem, weights)

            # 重新分析
            result = self.orchestrator.analyze(
                updated_problem,
                algorithm=algorithm
            )

            rankings.append(result.ranking)

        return rankings

    def _update_weights(
        self,
        problem: DecisionProblem,
        new_weights: dict[str, float]
    ) -> DecisionProblem:
        """更新决策问题的权重"""
        # 使用 dataclass 替换创建新实例
        from dataclasses import replace

        updated_criteria = [
            replace(criterion, weight=new_weights[criterion.name])
            for criterion in problem.criteria
        ]

        return replace(problem, criteria=updated_criteria)
```

#### 3. StabilityService

```python
class StabilityService:
    """排名稳定性评估服务"""

    def evaluate_stability(
        self,
        base_ranking: list[RankingItem],
        perturbed_rankings: list[list[RankingItem]]
    ) -> StabilityMetrics:
        """
        评估排名稳定性

        Args:
            base_ranking: 基础排名
            perturbed_rankings: 扰动后的排名列表

        Returns:
            稳定性指标
        """
        # 计算排名变化
        rank_changes = self._compute_rank_changes(base_ranking, perturbed_rankings)

        # 计算统计指标
        mean_change = sum(rank_changes) / len(rank_changes)
        max_change = max(rank_changes)
        std_change = self._compute_std(rank_changes)

        # 计算稳定性得分（0-1，1表示完全稳定）
        stability_score = 1.0 / (1.0 + mean_change)

        return StabilityMetrics(
            mean_rank_change=mean_change,
            max_rank_change=max_change,
            std_rank_change=std_change,
            stability_score=stability_score
        )

    def _compute_rank_changes(
        self,
        base_ranking: list[RankingItem],
        perturbed_rankings: list[list[RankingItem]]
    ) -> list[float]:
        """计算每个备选方案的平均排名变化"""
        alternative_names = {item.alternative for item in base_ranking}
        base_ranks = {item.alternative: item.rank for item in base_ranking}

        all_changes = []

        for perturbed_ranking in perturbed_rankings:
            perturbed_ranks = {item.alternative: item.rank for item in perturbed_ranking}

            for alternative in alternative_names:
                change = abs(
                    base_ranks[alternative] - perturbed_ranks[alternative]
                )
                all_changes.append(change)

        return all_changes

    def _compute_std(self, values: list[float]) -> float:
        """计算标准差"""
        import statistics
        return statistics.stdev(values) if len(values) > 1 else 0.0
```

#### 4. Refactored SensitivityService

```python
class SensitivityService:
    """敏感性分析协调服务（重构版）"""

    def __init__(self, orchestrator: MCDAOrchestrator):
        self.perturbation = PerturbationService()
        self.ranking = RankingService(orchestrator)
        self.stability = StabilityService()

    def analyze(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        criterion_name: str,
        n_samples: int = 100
    ) -> SensitivityAnalysis | None:
        """
        执行敏感性分析（协调方法）

        Args:
            problem: 决策问题
            result: 原始分析结果
            criterion_name: 要分析的准则名称
            n_samples: 扰动样本数量

        Returns:
            敏感性分析结果
        """
        try:
            # 1. 提取基础权重
            base_weights = {
                criterion.name: criterion.weight
                for criterion in problem.criteria
            }

            # 2. 生成权重扰动
            perturbations = self.perturbation.generate_perturbations(
                base_weights=base_weights,
                criterion_name=criterion_name,
                n_samples=n_samples
            )

            # 3. 计算扰动后的排名
            perturbed_rankings = self.ranking.compute_rankings_with_weights(
                problem=problem,
                weights_list=perturbations,
                algorithm=result.algorithm_name
            )

            # 4. 评估稳定性
            stability_metrics = self.stability.evaluate_stability(
                base_ranking=result.ranking,
                perturbed_rankings=perturbed_rankings
            )

            return SensitivityAnalysis(
                criterion_name=criterion_name,
                base_ranking=result.ranking,
                perturbed_rankings=perturbed_rankings[:10],  # 只保存前10个
                stability_metrics=stability_metrics
            )

        except Exception as e:
            # 错误处理
            logger.error(f"Sensitivity analysis failed: {e}")
            return None
```

---

## ✅ Benefits

1. **单一职责**: 每个类专注单一功能
2. **易于测试**: 可以独立测试每个服务
3. **可复用性**: `PerturbationService` 可用于其他场景
4. **可扩展性**: 易于添加新的扰动策略或稳定性指标
5. **可维护性**: 代码结构清晰，易于理解和修改

---

## ⚠️ Consequences

### Positive
- ✅ 符合 SOLID 原则
- ✅ 提升代码质量
- ✅ 便于单元测试
- ✅ 支持功能扩展

### Negative
- ⚠️ 需要重构现有代码
- ⚠️ 增加了类的数量
- ⚠️ 需要更新相关测试

### Mitigation
- 保持 `SensitivityService.analyze()` API 不变
- 渐进式重构，保证功能等价
- 充分的测试覆盖

---

## 📊 Alternatives Considered

### Alternative 1: 保持现状

**拒绝原因**：
- 职责过重，难以维护
- 违反 SRP 原则
- 测试困难

### Alternative 2: 使用函数式编程

**拒绝原因**：
- 与现有 OOP 风格不一致
- 降低代码可读性
- 难以扩展

### Alternative 3: 合并到 Orchestrator

**拒绝原因**：
- `Orchestrator` 已经职责较多
- 增加耦合度
- 违反 SRP

---

## 🔗 Related Decisions

- ADR-001: 分层架构设计
- Plan-002: 算法扩展
- Plan-003: 轻量可视化

---

## 📅 Implementation Plan

### Phase 1: 创建新服务
1. 创建 `PerturbationService`
2. 创建 `RankingService`
3. 创建 `StabilityService`
4. 单元测试

### Phase 2: 重构 SensitivityService
1. 更新 `SensitivityService` 使用新服务
2. 保持 API 不变
3. 集成测试

### Phase 3: 文档和清理
1. 更新文档
2. 清理旧代码
3. 代码审查

---

## ✅ Acceptance Criteria

- [ ] 三个新服务独立可用
- [ ] `SensitivityService.analyze()` API 保持不变
- [ ] 所有现有测试通过
- [ ] 新增服务单元测试覆盖率 ≥ 90%
- [ ] 文档更新

---

**Created**: 2026-02-01
**Author**: hunkwk + AI Architect
**Status**: ✅ Proposed, Pending Implementation
