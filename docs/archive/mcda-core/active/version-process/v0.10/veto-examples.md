# 一票否决机制使用示例

本文档展示如何使用 MCDA Core 的一票否决机制进行决策分析。

---

## 1. 供应商准入评估（硬否决 + 软否决）

### 场景描述

评估供应商是否满足准入条件：
- **硬否决**: 资质评分 ≥ 60（低于 60 直接拒绝）
- **软否决**: 财务风险 > 60（触发警告，扣 30 分）

### YAML 配置

```yaml
name: 供应商准入评估

alternatives:
  - 供应商A
  - 供应商B
  - 供应商C
  - 供应商D
  - 供应商E

criteria:
  - name: 资质评分
    weight: 0.6
    direction: higher_better
    veto:
      type: hard
      condition:
        operator: ">="
        value: 60
        action: reject
      reject_reason: "资质评分不足"

  - name: 财务风险
    weight: 0.4
    direction: lower_better
    veto:
      type: soft
      condition:
        operator: ">"
        value: 60
        action: warning
      penalty_score: -30
      reject_reason: "财务风险偏高"

scores:
  供应商A:
    资质评分: 80
    财务风险: 50  # 不触发软否决
  供应商B:
    资质评分: 40  # 触发硬否决拒绝
    财务风险: 70
  供应商C:
    资质评分: 70
    财务风险: 70  # 触发软否决警告
  供应商D:
    资质评分: 50  # 触发硬否决拒绝
    财务风险: 55
  供应商E:
    资质评分: 75
    财务风险: 40

algorithm:
  name: wsm
```

### 运行命令

```bash
# 应用一票否决约束
mcda analyze suppliers.yaml --apply-constraints -o report.md

# 不应用约束（所有方案参与排序）
mcda analyze suppliers.yaml -o report.md
```

### 预期结果

| 方案 | 资质评分 | 财务风险 | 硬否决 | 软否决 | 最终结果 |
|------|----------|----------|--------|--------|----------|
| 供应商A | 80 | 50 | ✅ 通过 | ✅ 无警告 | **参与排序** |
| 供应商B | 40 | 70 | ❌ 拒绝 | - | **被过滤** |
| 供应商C | 70 | 70 | ✅ 通过 | ⚠️ 警告 (-30) | **参与排序（扣分）** |
| 供应商D | 50 | 55 | ❌ 拒绝 | - | **被过滤** |
| 供应商E | 75 | 40 | ✅ 通过 | ✅ 无警告 | **参与排序** |

---

## 2. 项目风险评估（分级否决）

### 场景描述

评估项目风险等级，采用多档位管理：
- **低风险** (0-30): 接受
- **中风险** (30-60): 警告，扣 15 分
- **高风险** (60-100): 拒绝

### YAML 配置

```yaml
name: 项目风险评估

alternatives:
  - 项目A
  - 项目B
  - 项目C

criteria:
  - name: 技术风险
    weight: 0.5
    direction: lower_better
    veto:
      type: tiered
      tiers:
        - min: 0
          max: 30
          action: accept
        - min: 30
          max: 60
          action: warning
          penalty_score: -15
          label: "中等风险"
        - min: 60
          max: 100
          action: reject
          label: "高风险"

  - name: 资金风险
    weight: 0.5
    direction: lower_better
    veto:
      type: tiered
      tiers:
        - min: 0
          max: 40
          action: accept
        - min: 40
          max: 70
          action: warning
          penalty_score: -20
        - min: 70
          max: 100
          action: reject

scores:
  项目A:
    技术风险: 25  # 低风险
    资金风险: 35  # 低风险
  项目B:
    技术风险: 45  # 中风险（警告）
    资金风险: 50  # 中风险（警告）
  项目C:
    技术风险: 75  # 高风险（拒绝）
    资金风险: 30  # 低风险

algorithm:
  name: topsis
```

### 预期结果

| 方案 | 技术风险 | 资金风险 | 技术风险档位 | 资金风险档位 | 最终结果 |
|------|----------|----------|-------------|-------------|----------|
| 项目A | 25 | 35 | ✅ 低风险 | ✅ 低风险 | **参与排序** |
| 项目B | 45 | 50 | ⚠️ 中风险 (-15) | ⚠️ 中风险 (-20) | **参与排序（扣35分）** |
| 项目C | 75 | 30 | ❌ 高风险 | ✅ 低风险 | **被过滤** |

---

## 3. 合同风险评估（组合否决）

### 场景描述

评估合同风险，使用组合逻辑：
- **OR 逻辑**: 许可证过期或被吊销 → 拒绝
- **AND 逻辑**: 违约责任 **且** 付款条件苛刻 → 拒绝

### YAML 配置

```yaml
name: 合同风险评估

alternatives:
  - 合同A
  - 合同B
  - 合同C

criteria:
  - name: 许可证状态
    weight: 0.4
    direction: higher_better
    veto:
      type: composite
      conditions:
        - operator: "=="
          value: "expired"
          action: reject
        - operator: "in"
          value: ["revoked", "suspended"]
          action: reject
      logic: or

  - name: 违约责任
    weight: 0.3
    direction: lower_better
    veto:
      type: composite
      conditions:
        - operator: ">"
          value: 80
          action: reject
        - operator: ">"
          value: 50
          action: warning
      logic: or

  - name: 付款条件
    weight: 0.3
    direction: lower_better
    veto:
      type: soft
      condition:
        operator: ">"
        value: 60
        action: warning
      penalty_score: -20

scores:
  合同A:
    许可证状态: "valid"
    违约责任: 40
    付款条件: 50
  合同B:
    许可证状态: "expired"  # 触发 OR 拒绝
    违约责任: 30
    付款条件: 40
  合同C:
    许可证状态: "valid"
    违约责任: 85  # 触发 OR 拒绝
    付款条件: 70  # 触发软否决警告

algorithm:
  name: vikor
```

### 预期结果

| 方案 | 许可证状态 | 违约责任 | 付款条件 | 否决结果 | 最终结果 |
|------|-----------|----------|----------|----------|----------|
| 合同A | valid | 40 | 50 | ✅ 通过 | **参与排序** |
| 合同B | expired | 30 | 40 | ❌ 拒绝（许可证过期） | **被过滤** |
| 合同C | valid | 85 | 70 | ❌ 拒绝（违约责任过高）⚠️ 警告（付款条件） | **被过滤** |

---

## 4. Python API 使用

### 基础用法

```python
from mcda_core.core import MCDAOrchestrator

# 创建 orchestrator
orchestrator = MCDAOrchestrator()

# 运行工作流（应用约束）
result = orchestrator.run_workflow(
    file_path="suppliers.yaml",
    apply_constraints=True
)

# 查看否决结果
if hasattr(result, 'veto_results'):
    for alt_id, veto_result in result.veto_results.items():
        if veto_result.rejected:
            print(f"{alt_id}: 被拒绝 - {veto_result.reject_reasons}")
        elif veto_result.warnings:
            print(f"{alt_id}: 有警告 - {veto_result.warnings}")
            print(f"  总惩罚: {veto_result.total_penalty}")
        else:
            print(f"{alt_id}: 通过")
```

### 服务层直接使用

```python
from mcda_core.services.constraint_service import ConstraintService
from mcda_core.core import MCDAOrchestrator

# 加载问题
orchestrator = MCDAOrchestrator()
problem = orchestrator.load_from_yaml("suppliers.yaml")

# 创建约束服务
service = ConstraintService()

# 过滤问题
filtered_problem, veto_results = service.filter_problem(problem)

# 应用惩罚
adjusted_problem = service.apply_penalties(filtered_problem)

# 获取元数据
metadata = service.get_constraint_metadata(problem, veto_results)
print(f"总方案: {metadata.total_alternatives}")
print(f"拒绝: {metadata.rejected_count}")
print(f"警告: {metadata.warning_count}")
print(f"接受: {metadata.accept_count}")
```

---

## 5. 命令行使用

### 基础命令

```bash
# 分析决策问题（应用约束）
mcda analyze config.yaml --apply-constraints

# 指定输出文件
mcda analyze config.yaml --apply-constraints -o report.md

# 指定算法
mcda analyze config.yaml --apply-constraints --algorithm topsis

# 运行敏感性分析
mcda analyze config.yaml --apply-constraints --sensitivity

# 输出 JSON 格式
mcda analyze config.yaml --apply-constraints --format json -o result.json
```

### 对比分析

```bash
# 不应用约束（所有方案参与排序）
mcda analyze config.yaml -o report_all.md

# 应用约束（过滤后的方案参与排序）
mcda analyze config.yaml --apply-constraints -o report_filtered.md

# 对比两个报告，查看约束的影响
```

---

## 6. 配置技巧

### 硬否决配置

适用于合规性指标，不满足直接拒绝：

```yaml
veto:
  type: hard
  condition:
    operator: ">="  # 必须 >= 阈值
    value: 60
    action: reject
  reject_reason: "不满足准入条件"
```

### 软否决配置

适用于风险指标，不满足扣分但不拒绝：

```yaml
veto:
  type: soft
  condition:
    operator: ">"  # 超过阈值触发
    value: 60
    action: warning
  penalty_score: -30  # 扣 30 分
  reject_reason: "风险偏高"
```

### 分级否决配置

适用于风险等级评估：

```yaml
veto:
  type: tiered
  tiers:
    - min: 0
      max: 30
      action: accept
    - min: 30
      max: 60
      action: warning
      penalty_score: -15
      label: "中等风险"
    - min: 60
      max: 100
      action: reject
      label: "高风险"
```

### 组合否决配置

适用于复杂业务规则：

```yaml
# OR 逻辑：任一条件满足即触发
veto:
  type: composite
  conditions:
    - operator: "=="
      value: "expired"
      action: reject
    - operator: "in"
      value: ["revoked", "suspended"]
      action: reject
  logic: or

# AND 逻辑：所有条件满足才触发
veto:
  type: composite
  conditions:
    - operator: ">"
      value: 50
      action: warning
    - operator: "<"
      value: 80
      action: warning
  logic: and
```

---

## 7. 常见问题

### Q1: 如何选择否决类型？

- **hard**: 合规性指标（营业执照、资质证书）
- **soft**: 风险指标（财务风险、技术风险）
- **tiered**: 风险等级评估（低/中/高风险）
- **composite**: 复杂业务规则（多条件组合）

### Q2: 硬否决和软否决的区别？

- **硬否决**: 不满足条件直接拒绝，不参与排序
- **软否决**: 不满足条件扣分，但仍参与排序

### Q3: 如何调试否决结果？

1. 查看否决结果：`result.veto_results`
2. 检查拒绝原因：`veto_result.reject_reasons`
3. 查看警告信息：`veto_result.warnings`
4. 查看惩罚分数：`veto_result.total_penalty`

### Q4: 所有方案都被拒绝怎么办？

如果所有方案都被拒绝，ConstraintService 会返回原问题，并标记所有方案为拒绝。你可以：
1. 调整否决条件的阈值
2. 移除部分硬否决
3. 将硬否决改为软否决

---

**更多文档**:
- [ADR-014: 一票否决机制架构设计](../decisions/mcda-core/014-veto-mechanism.md)
- [v0.10 执行计划](../plans/mcda-core/v0.10/execution-plan.md)
- [TDD 进度文件](./active/mcda-core/v0.10/tdd-veto-constraints.md)
