# ADR-005: 引入配置加载器抽象层

**Status**: Proposed
**Type**: Architectural
**Date**: 2026-02-01
**Project**: MCDA Core v0.3

---

## 📋 Context

### Current Situation
当前配置加载逻辑直接实现在 `MCDAOrchestrator` 中：

```python
class MCDAOrchestrator:
    def load_from_yaml(self, file_path: str | Path) -> DecisionProblem:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return self._parse_problem(data)
```

### Problems
1. **硬编码格式**：仅支持 YAML，不支持 JSON
2. **扩展困难**：添加新格式需要修改核心类
3. **职责混乱**：`MCDAOrchestrator` 既负责编排又负责加载
4. **测试困难**：加载逻辑与业务逻辑耦合

### Requirements
- ✅ 支持 JSON 和 YAML 配置
- ✅ 易于扩展（未来可能支持 Excel、数据库）
- ✅ 保持 API 向后兼容
- ✅ 提升可测试性

---

## 🎯 Decision

引入 **`ConfigLoader` 抽象接口**，实现配置加载的解耦和扩展。

### Design

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class ConfigLoader(ABC):
    """配置加载器抽象基类"""

    @abstractmethod
    def load(self, source: str | Path) -> dict[str, Any]:
        """加载配置文件并返回字典"""
        pass

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> bool:
        """验证配置数据格式"""
        pass


class YAMLLoader(ConfigLoader):
    """YAML 配置加载器"""

    def load(self, source: str | Path) -> dict[str, Any]:
        import yaml

        with open(source, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate(self, data: dict[str, Any]) -> bool:
        # YAML 特定验证
        return True


class JSONLoader(ConfigLoader):
    """JSON 配置加载器"""

    def load(self, source: str | Path) -> dict[str, Any]:
        import json

        with open(source, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate(self, data: dict[str, Any]) -> bool:
        # JSON 特定验证
        return True


class LoaderFactory:
    """加载器工厂"""

    _loaders: dict[str, type[ConfigLoader]] = {
        '.yaml': YAMLLoader,
        '.yml': YAMLLoader,
        '.json': JSONLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str | Path) -> ConfigLoader:
        """根据文件扩展名获取加载器"""
        ext = Path(file_path).suffix.lower()

        if ext not in cls._loaders:
            raise ValueError(f"Unsupported file format: {ext}")

        return cls._loaders[ext]()

    @classmethod
    def register_loader(cls, ext: str, loader: type[ConfigLoader]):
        """注册新的加载器"""
        cls._loaders[ext] = loader
```

### Updated Orchestrator

```python
class MCDAOrchestrator:
    def __init__(self):
        self.loader_factory = LoaderFactory()

    def load_from_file(self, file_path: str | Path) -> DecisionProblem:
        """自动检测格式并加载配置"""
        loader = self.loader_factory.get_loader(file_path)
        data = loader.load(file_path)
        return self._parse_problem(data)

    def load_from_yaml(self, file_path: str | Path) -> DecisionProblem:
        """加载 YAML 配置（向后兼容）"""
        loader = YAMLLoader()
        data = loader.load(file_path)
        return self._parse_problem(data)

    def load_from_json(self, file_path: str | Path) -> DecisionProblem:
        """加载 JSON 配置（新功能）"""
        loader = JSONLoader()
        data = loader.load(file_path)
        return self._parse_problem(data)

    def _parse_problem(self, data: dict) -> DecisionProblem:
        """解析配置数据（核心逻辑，保持不变）"""
        # 现有的解析逻辑
        pass
```

---

## ✅ Benefits

1. **解耦**: 加载逻辑与业务逻辑分离
2. **扩展**: 新增格式只需实现 `ConfigLoader` 接口
3. **测试**: 可以 mock `ConfigLoader` 进行单元测试
4. **兼容**: 保持现有 API（`load_from_yaml()`）不变
5. **灵活**: 支持自动检测和显式指定两种方式

---

## ⚠️ Consequences

### Positive
- ✅ 支持 JSON 配置（v0.3 核心功能）
- ✅ 未来易于扩展（Excel、数据库等）
- ✅ 代码更符合 SOLID 原则
- ✅ 提升可测试性

### Negative
- ⚠️ 需要重构 `core.py`
- ⚠️ 增加了少量抽象层
- ⚠️ 需要更新相关测试

### Mitigation
- 保持 `load_from_yaml()` 向后兼容
- 渐进式重构，先实现新接口再迁移
- 充分的单元测试保证功能不变

---

## 📊 Alternatives Considered

### Alternative 1: 单一加载器，if/else 判断

```python
def load(self, file_path):
    if file_path.endswith('.yaml'):
        # YAML 逻辑
    elif file_path.endswith('.json'):
        # JSON 逻辑
```

**拒绝原因**：
- 违反开闭原则
- 扩展时需修改核心代码
- 代码臃肿

### Alternative 2: 使用第三方库（如 `pydantic`）

**拒绝原因**：
- 增加依赖
- 过度设计
- 当前需求简单

### Alternative 3: 保持现状，复制 `load_from_yaml()` 为 `load_from_json()`

**拒绝原因**：
- 代码重复
- 不符合 DRY 原则
- 未来扩展困难

---

## 🔗 Related Decisions

- ADR-001: 分层架构设计
- Plan-001: JSON 配置支持
- Plan-003: 配置模板生成

---

## 📅 Implementation Plan

### Phase 1: 创建抽象层
1. 创建 `lib/loaders/` 目录
2. 实现 `ConfigLoader` 抽象基类
3. 实现 `YAMLLoader` 和 `JSONLoader`
4. 实现 `LoaderFactory`

### Phase 2: 重构 Orchestrator
1. 更新 `MCDAOrchestrator.load_from_yaml()` 使用新接口
2. 添加 `MCDAOrchestrator.load_from_json()`
3. 添加 `MCDAOrchestrator.load_from_file()`（自动检测）

### Phase 3: 测试
1. 单元测试：各加载器测试
2. 集成测试：完整工作流
3. 兼容性测试：YAML 配置仍可用

---

## ✅ Acceptance Criteria

- [ ] 可以加载 JSON 配置文件
- [ ] JSON 和 YAML 配置结果一致
- [ ] 自动检测格式（基于扩展名）
- [ ] 保持向后兼容（现有 YAML 配置仍可用）
- [ ] 单元测试覆盖率 ≥ 90%
- [ ] 文档更新（示例、API 说明）

---

**Created**: 2026-02-01
**Author**: hunkwk + AI Architect
**Status**: ✅ Proposed, Pending Implementation
