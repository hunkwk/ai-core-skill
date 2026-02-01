# TDD: JSON 配置支持

**Type**: tdd
**Status**: RED
**Project**: mcda-core
**Version**: v0.3.0
**Branch**: feature/mcda-core
**Created**: 2026-02-01
**Updated**: 2026-02-01

---

## 📋 Overview

实现 JSON 配置文件支持，与 YAML 配置并存，提升配置灵活性。

**Key Features**:
- ✅ JSON 配置文件加载
- ✅ 自动格式检测（基于扩展名）
- ✅ 配置加载器抽象层
- ✅ 向后兼容（YAML 仍可用）

**Related Docs**:
- Plan: `docs/plans/mcda-core/v0.3/summary.md` (Plan-001)
- ADR: `docs/decisions/mcda-core/005-loader-abstract-layer.md`

---

## 🔄 Current Status: **RED**

**Phase**: Writing failing tests

### Progress
- [x] 创建 ADR-005（配置加载器抽象层）
- [x] 创建 v0.3 规划文档
- [ ] 设计测试用例
- [ ] 编写失败的测试（RED）
- [ ] 实现功能（GREEN）
- [ ] 重构代码（REFACTOR）
- [ ] 完成验收（DONE）

---

## 🎯 Implementation Plan

### Phase 1: RED - 编写失败的测试

**测试清单**:
1. **测试 JSON 加载基本功能**
   - [ ] 测试标准 JSON 配置加载
   - [ ] 测试备选方案解析
   - [ ] 测试准则解析
   - [ ] 测试评分矩阵解析

2. **测试 YAML/JSON 一致性**
   - [ ] 同一内容，不同格式，结果一致
   - [ ] 测试数据类型一致性

3. **测试错误处理**
   - [ ] 测试文件不存在错误
   - [ ] 测试格式错误（无效 JSON）
   - [ ] 测试缺失必需字段
   - [ ] 测试数据验证错误

4. **测试 LoaderFactory**
   - [ ] 测试自动格式检测（.json, .yaml, .yml）
   - [ ] 测试不支持的格式错误
   - [ ] 测试自定义加载器注册

### Phase 2: GREEN - 实现功能

**实现清单**:
1. [ ] 创建 `lib/loaders/` 目录
2. [ ] 实现 `ConfigLoader` 抽象基类
3. [ ] 实现 `JSONLoader`
4. [ ] 实现 `YAMLLoader`
5. [ ] 实现 `LoaderFactory`
6. [ ] 重构 `MCDAOrchestrator.load_from_yaml()`
7. [ ] 添加 `MCDAOrchestrator.load_from_json()`
8. [ ] 添加 `MCDAOrchestrator.load_from_file()`

### Phase 3: REFACTOR - 优化代码

**重构清单**:
1. [ ] 提取通用配置解析逻辑
2. [ ] 优化错误消息
3. [ ] 添加类型注解
4. [ ] 性能优化（如果需要）

---

## 🧪 Test Cases

### Test Case 1: 标准 JSON 配置

```python
def test_load_json_config():
    """测试加载标准 JSON 配置"""
    config = {
        "name": "Test Problem",
        "description": "Test description",
        "alternatives": ["A", "B", "C"],
        "criteria": [
            {"name": "Cost", "weight": 0.5, "direction": "minimize"},
            {"name": "Quality", "weight": 0.5, "direction": "maximize"}
        ],
        "scores": {
            "A": {"Cost": 100, "Quality": 80},
            "B": {"Cost": 150, "Quality": 90},
            "C": {"Cost": 120, "Quality": 85}
        }
    }

    # 应该成功加载
    problem = orchestrator.load_from_json("test.json")
    assert problem.name == "Test Problem"
    assert len(problem.alternatives) == 3
    assert len(problem.criteria) == 2
```

### Test Case 2: YAML/JSON 一致性

```python
def test_yaml_json_consistency():
    """测试 YAML 和 JSON 配置结果一致"""
    # 加载同一内容的 YAML 和 JSON
    problem_yaml = orchestrator.load_from_yaml("test.yaml")
    problem_json = orchestrator.load_from_json("test.json")

    # 应该产生相同的 DecisionProblem
    assert problem_yaml.name == problem_json.name
    assert len(problem_yaml.alternatives) == len(problem_json.alternatives)
    assert len(problem_yaml.criteria) == len(problem_json.criteria)
```

### Test Case 3: 自动格式检测

```python
def test_auto_format_detection():
    """测试自动检测配置格式"""
    # 应该根据扩展名自动选择加载器
    problem_json = orchestrator.load_from_file("test.json")
    problem_yaml = orchestrator.load_from_file("test.yaml")

    assert isinstance(problem_json, DecisionProblem)
    assert isinstance(problem_yaml, DecisionProblem)
```

### Test Case 4: 错误处理

```python
def test_invalid_json():
    """测试无效 JSON 错误处理"""
    with pytest.raises(ConfigLoadError):
        orchestrator.load_from_json("invalid.json")

def test_missing_required_field():
    """测试缺失必需字段"""
    with pytest.raises(ValidationError):
        orchestrator.load_from_json("missing_field.json")
```

---

## 📝 Decisions & Notes

### 2026-02-01: 项目初始化

**Decision**:
- 采用 ADR-005 的架构设计
- 使用 LoaderFactory 模式
- 保持向后兼容

**Next Steps**:
1. 设计测试用例（今天）
2. 编写失败的测试（明天）
3. 实现 JSONLoader（后天）

---

## 🧪 Test Results

**待执行测试**:
- [ ] test_load_json_config
- [ ] test_yaml_json_consistency
- [ ] test_auto_format_detection
- [ ] test_invalid_json
- [ ] test_missing_required_field
- [ ] test_loader_factory_registration

**当前测试通过率**: N/A (RED phase)

---

## 🚧 Known Issues

无

---

## 📦 Dependencies

**新增依赖**:
- 标准库 `json`（无需安装）

**现有依赖**:
- `pyyaml`（YAML 支持）

---

## ✅ Acceptance Criteria

- [ ] 可以加载 JSON 配置文件
- [ ] JSON 和 YAML 配置结果一致
- [ ] 自动检测格式（基于扩展名）
- [ ] 错误提示清晰友好
- [ ] 保持向后兼容（现有 YAML 配置仍可用）
- [ ] 单元测试覆盖率 ≥ 90%
- [ ] 所有测试通过

---

## 📚 Documentation Updates

- [ ] 更新 `skills/mcda-core/README.md`
  - 添加 JSON 配置示例
  - 更新 API 文档
- [ ] 更新 `skills/mcda-core/SKILL.md`
  - 添加 JSON 配置说明

---

## 🔗 Related Resources

- ADR-005: `docs/decisions/mcda-core/005-loader-abstract-layer.md`
- Plan v0.3: `docs/plans/mcda-core/v0.3/summary.md`
- JSON Schema: (待创建)

---

**Last Updated**: 2026-02-01
**Status**: 🔄 RED - Writing failing tests
