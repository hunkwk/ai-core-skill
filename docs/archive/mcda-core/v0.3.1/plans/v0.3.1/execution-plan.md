# MCDA Core v0.3.1 执行计划

**版本类型**: 补丁版本 (Bug Fix)
**计划工期**: 1 周 (2-3 人日)
**创建日期**: 2026-02-01
**目标**: 修复 v0.3 架构债和遗留问题

---

## 📋 版本目标

### 核心目标

修复 v0.3 遗留的架构债和功能缺陷，为 v0.4 高级功能开发奠定基础。

### 范围界定

**包含**:
- ✅ Comparison Service 算法发现机制修复
- ✅ Comparison Service API 兼容性修复
- ✅ ASCII 可视化测试修复
- ✅ 数据验证增强

**不包含**:
- ❌ 新算法实现（留待 v0.4）
- ❌ 新标准化方法（留待 v0.4）
- ❌ 性能优化（留待 v0.5）

---

## 🎯 任务分解

### Phase 1: Comparison Service 修复 (1.5 人日)

#### Task 1.1: 算法发现机制修复 (0.5 人日)

**问题描述**:
当前 `ComparisonService` 使用硬编码的 `supported_algorithms` 列表，违反开闭原则。

**技术方案**:
```python
# 修复前 (硬编码)
self.supported_algorithms = [
    "wsm", "wpm", "topsis", "vikor"
]

# 修复后 (动态注册)
from mcda.core import get_algorithm
self._algorithm_registry = get_algorithm.__dict__
```

**实现步骤**:
1. 读取 `mcda/core.py` 中的 `_algorithms` 注册表
2. 修改 `ComparisonService.__init__()` 使用动态注册
3. 添加 `register_algorithm()` 方法支持运行时注册
4. 编写单元测试验证自动发现

**验收标准**:
- [ ] 新增算法（PROMETHEE-II）自动支持比较
- [ ] 无需修改代码即可支持未来算法
- [ ] 单元测试覆盖率 100%

#### Task 1.2: API 兼容性修复 (0.5 人日)

**问题描述**:
Checkpoint 提到 "DecisionProblem 参数不匹配"，需要统一 API。

**技术方案**:
```python
# 统一 DecisionProblem 参数
def compare_algorithms(
    self,
    algorithm_names: List[str],
    decision_problem: DecisionProblem,
    metrics: List[str] = None
) -> pd.DataFrame:
    """比较多个算法在同一问题上的表现"""
```

**实现步骤**:
1. 审查所有算法的 DecisionProblem 接口
2. 统一参数命名和顺序
3. 添加参数验证和错误提示
4. 更新所有调用代码

**验收标准**:
- [ ] 所有算法接受相同 DecisionProblem 格式
- [ ] 参数不匹配时有清晰错误提示
- [ ] 集成测试通过率 100%

#### Task 1.3: 测试用例补充 (0.5 人日)

**当前状态**: 11/19 测试通过

**缺失测试**:
- [ ] PROMETHEE-II 比较测试
- [ ] 跨算法类型比较测试
- [ ] 边界条件测试（空矩阵、单准则）
- [ ] 错误处理测试

**实现步骤**:
1. 编写 PROMETHEE-II 比较测试
2. 编写跨类型算法比较测试
3. 编写边界条件测试
4. 修复失败的测试

**验收标准**:
- [ ] 19/19 测试全部通过
- [ ] 测试覆盖率 ≥ 95%

---

### Phase 2: ASCII 可视化测试修复 (0.5 人日)

#### Task 2.1: 测试环境修复 (0.3 人日)

**问题描述**:
ASCII 可视化测试未运行，可能存在环境问题。

**实现步骤**:
1. 运行 `tests/test_visualization.py` 查看失败原因
2. 修复依赖问题（numpy/pandas 版本）
3. 修复输出格式问题（终端宽度）
4. 添加 CI/CD 自动化测试

**验收标准**:
- [ ] 所有可视化测试通过
- [ ] CI/CD 自动测试运行成功

#### Task 2.2: 边界条件测试 (0.2 人日)

**实现步骤**:
1. 添加大规模矩阵可视化测试
2. 添加超长准则名称测试
3. 添加中文/特殊字符测试

**验收标准**:
- [ ] 边界条件测试通过
- [ ] 输出格式正确无乱码

---

### Phase 3: 数据验证增强 (1 人日)

#### Task 3.1: 决策矩阵验证 (0.4 人日)

**增强内容**:
- [ ] 检查 NaN/Inf 值
- [ ] 检查负值（对于不允许负值的算法）
- [ ] 检查零方差列
- [ ] 检查维度一致性（准则数 vs 权重数）

**技术方案**:
```python
def validate_decision_matrix(matrix: np.ndarray) -> None:
    """验证决策矩阵有效性"""
    if np.isnan(matrix).any():
        raise ValueError("决策矩阵包含 NaN 值")
    if np.isinf(matrix).any():
        raise ValueError("决策矩阵包含无穷大值")
    # ... 更多验证
```

**验收标准**:
- [ ] 所有异常情况有明确错误提示
- [ ] 验证逻辑不覆盖有效数据

#### Task 3.2: 权重向量验证 (0.3 人日)

**增强内容**:
- [ ] 检查权重和为 1（允许浮点误差）
- [ ] 检查权重范围 [0, 1]
- [ ] 检查权重维度与准则数匹配

**验收标准**:
- [ ] 异常权重有清晰错误提示
- [ ] 允许合理浮点误差（1e-6）

#### Task 3.3: 准则方向验证 (0.3 人日)

**增强内容**:
- [ ] 检查准则方向枚举值有效性
- [ ] 检查效益型/成本型一致性
- [ ] 添加准则方向自动推断（可选）

**验收标准**:
- [ ] 无效准则方向有明确提示
- [ ] 准则方向验证测试通过

---

## 📊 工作量估算

| Phase | 任务 | 工作量 | 优先级 |
|-------|------|--------|--------|
| 1.1 | 算法发现机制修复 | 0.5 人日 | 🔴 P0 |
| 1.2 | API 兼容性修复 | 0.5 人日 | 🔴 P0 |
| 1.3 | 测试用例补充 | 0.5 人日 | 🔴 P0 |
| 2.1 | ASCII 测试修复 | 0.3 人日 | 🟡 P1 |
| 2.2 | 边界条件测试 | 0.2 人日 | 🟡 P1 |
| 3.1 | 决策矩阵验证 | 0.4 人日 | 🟡 P1 |
| 3.2 | 权重向量验证 | 0.3 人日 | 🟡 P1 |
| 3.3 | 准则方向验证 | 0.3 人日 | 🟡 P1 |
| **总计** | | **3.0 人日** | |

---

## 🚀 执行流程

### Day 1: Comparison Service 修复
- **上午**: Task 1.1 算法发现机制修复
- **下午**: Task 1.2 API 兼容性修复

### Day 2: 测试与可视化
- **上午**: Task 1.3 测试用例补充
- **下午**: Task 2.1-2.2 ASCII 可视化测试修复

### Day 3: 数据验证增强
- **上午**: Task 3.1-3.2 决策矩阵和权重验证
- **下午**: Task 3.3 准则方向验证 + 完整测试

### Day 4: 缓冲与文档
- **上午**: 回归测试，修复发现的问题
- **下午**: 更新文档，准备发布

---

## ✅ 验收标准

### 功能验收
- [ ] Comparison Service 支持所有已注册算法（自动发现）
- [ ] 所有算法 Comparison 测试通过（19/19）
- [ ] ASCII 可视化测试通过（包括边界条件）
- [ ] 数据验证覆盖所有异常情况

### 质量验收
- [ ] 单元测试覆盖率 ≥ 95%
- [ ] 所有测试通过（无 skip）
- [ ] 无 Lint 错误
- [ ] 代码通过 Code Review

### 文档验收
- [ ] 更新 README.md 说明新功能
- [ ] 更新 CHANGELOG.md 记录变更
- [ ] 创建 checkpoint-v0.3.1.md

---

## 📝 交付物

### 代码文件
- `lib/services/comparison_service.py` (修改)
- `lib/core.py` (修改，添加注册机制)
- `lib/validators.py` (新增，数据验证)
- `tests/test_comparison_service.py` (修改)
- `tests/test_visualization.py` (修改)
- `tests/test_validators.py` (新增)

### 文档文件
- `docs/checkpoints/mcda-core/checkpoint-v0.3.1.md` (新增)
- `skills/mcda-core/README_CN.md` (更新)
- `CHANGELOG.md` (更新)

---

## 🎯 成功标准

**核心指标**:
- Comparison Service 架构债清零
- 测试通过率 100% (19/19)
- 测试覆盖率 ≥ 95%
- 零已知 Bug

**次要指标**:
- 代码行数增加 < 200 行
- 开发时间 ≤ 3 人日
- 文档完整性 100%

---

## 📋 参考资料

### 相关文档
- [v0.3 Checkpoint](../checkpoints/mcda-core/checkpoint-mcda-core-v0.3-complete.md)
- [ADR-004: MCDA 算法架构设计](../decisions/mcda-core/004-mcda-algorithms-architecture.md)
- [Comparison Service 源码](../../skills/mcda-core/lib/services/comparison_service.py)

### 技术债务
- [ ] 硬编码算法列表（Task 1.1）
- [ ] DecisionProblem 参数不匹配（Task 1.2）
- [ ] 11/19 测试通过（Task 1.3）
- [ ] ASCII 测试未运行（Task 2.1）

---

**最后更新**: 2026-02-01
**计划状态**: ✅ APPROVED
**下一步**: 开始 Phase 1 - Comparison Service 修复
