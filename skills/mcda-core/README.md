# MCDA Core

**多准则决策分析（MCDA）核心库**

[![Version](https://img.shields.io/badge/version-v0.7-blue)](https://github.com/your-org/mcda-core)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE.txt)

---

## 📖 简介

MCDA Core 是一个功能强大的 Python 多准则决策分析库，提供多种经典和先进的决策算法，支持精确数、区间数和模糊数决策问题。

### 核心特性

- ✅ **10+ 决策算法**: WSM, WPM, TOPSIS, VIKOR, TODIM, ELECTRE-I, PROMETHEE II 等
- ✅ **区间数支持**: VIKOR 和 TODIM 支持区间数输入，处理不确定性
- ✅ **可能度排序**: 创新的区间数比较和排序方法
- ✅ **前景理论集成**: TODIM 算法支持损失厌恶建模
- ✅ **权重计算**: AHP, 熵权法, CRITIC, 博弈论组合赋权等
- ✅ **敏感性分析**: 完整的敏感性分析工具
- ✅ **CLI 支持**: 命令行工具，支持 YAML 配置
- ✅ **类型安全**: 完整的类型注解，支持 Pyright/MyPy
- ✅ **高测试覆盖**: 90%+ 测试覆盖率

---

## 🚀 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/your-org/mcda-core.git
cd mcda-core
pip install -e .

# 或使用安装脚本
python install_mcda.py
```

### 基础用法

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.algorithms import topsis

# 定义准则
criteria = [
    Criterion(name="性能", weight=0.4, direction="higher_better"),
    Criterion(name="成本", weight=0.3, direction="lower_better"),
    Criterion(name="可靠性", weight=0.2, direction="higher_better"),
    Criterion(name="易用性", weight=0.1, direction="higher_better"),
]

# 定义评分
scores = {
    "方案A": {"性能": 85, "成本": 50, "可靠性": 90, "易用性": 80},
    "方案B": {"性能": 90, "成本": 45, "可靠性": 85, "易用性": 75},
    "方案C": {"性能": 82, "成本": 55, "可靠性": 88, "易用性": 82},
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

# 运行 TOPSIS
result = topsis(problem)

# 查看结果
for ranking in result.rankings:
    print(f"第 {ranking.rank} 名: {ranking.alternative}")
```

---

## 🎯 v0.7 新特性

### 区间数决策支持

**VIKOR 区间版本** 和 **TODIM 区间版本** 现已支持！

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.interval import Interval
from mcda_core.algorithms.base import get_algorithm

# 定义区间评分
scores = {
    "方案A": {
        "性能": Interval(85, 92),  # 不确定性: [85, 92]
        "成本": Interval(40, 50),
    },
    "方案B": {
        "性能": Interval(90, 95),
        "成本": Interval(45, 55),
    },
}

# 创建决策问题
problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

# 运行 VIKOR 区间算法
algorithm = get_algorithm("vikor_interval")
result = algorithm.calculate(problem)
```

### 核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| **VIKOR 区间版本** | 折衷排序法，支持区间数 | ✅ 新增 |
| **TODIM 区间版本** | 基于前景理论，支持区间数 | ✅ 新增 |
| **可能度排序** | 区间数科学比较方法 | ✅ 新增 |
| **前景理论集成** | 损失厌恶建模 | ✅ 新增 |

### 性能提升

- 50×20 规模问题: < 5 秒 ✅
- 10×10 规模问题: < 0.5 秒 ✅

---

## 📚 算法列表

### 汇总算法

| 算法 | 描述 | 区间支持 |
|------|------|----------|
| **WSM** | 加权求和法 | ❌ |
| **WPM** | 加权乘积法 | ❌ |
| **TOPSIS** | 逼近理想解排序法 | ❌ |
| **VIKOR** | 折衷排序法 | ✅ v0.7 |
| **TODIM** | 前景理论决策法 | ✅ v0.7 |
| **ELECTRE-I** | 级别优先关系法 | ⏳ v1.0+ |
| **PROMETHEE II** | 偏好排序组织法 | ⏳ v1.0+ |

### 权重计算

| 方法 | 描述 |
|------|------|
| **AHP** | 层次分析法 |
| **熵权法** | 信息熵权重 |
| **CRITIC** | CRITIC 权重法 |
| **博弈论组合** | 博弈论组合赋权 |
| **变异系数** | CV 权重法 |

---

## 📖 使用文档

### 快速链接

- [使用示例](docs/active/mcda-core/v0.7/usage-examples.md) - 详细使用示例
- [API 文档](docs/api/) - 完整 API 参考
- [算法详解](docs/algorithms/) - 算法原理和实现
- [v0.7 完成报告](docs/active/mcda-core/v0.7/v0.7-completion-report.md) - 版本详情

### 常用场景

#### 1. 供应商选择

```python
from mcda_core.models import Criterion, DecisionProblem
from mcda_core.algorithms import topsis

criteria = [
    Criterion(name="质量", weight=0.35, direction="higher_better"),
    Criterion(name="价格", weight=0.25, direction="lower_better"),
    Criterion(name="交期", weight=0.20, direction="lower_better"),
    Criterion(name="服务", weight=0.12, direction="higher_better"),
    Criterion(name="信誉", weight=0.08, direction="higher_better"),
]

scores = {
    "供应商A": {"质量": 85, "价格": 50, "交期": 10, "服务": 80, "信誉": 85},
    "供应商B": {"质量": 88, "价格": 45, "交期": 14, "服务": 75, "信誉": 82},
    "供应商C": {"质量": 82, "价格": 55, "交期": 7, "服务": 85, "信誉": 88},
}

problem = DecisionProblem(
    alternatives=tuple(scores.keys()),
    criteria=criteria,
    scores=scores,
)

result = topsis(problem)
```

#### 2. 投资决策

```python
# 使用 VIKOR 区间版本处理不确定性
from mcda_core.interval import Interval

scores = {
    "项目A": {
        "投资成本": Interval(100, 120),
        "预期收益": Interval(150, 180),
        "风险水平": Interval(0.3, 0.5),
    },
    # ...
}
```

#### 3. 云服务选择

```python
# 使用 TODIM 区间版本建模风险态度
algorithm = get_algorithm("todim_interval")
result = algorithm.calculate(problem, theta=2.5)
```

---

## 🔧 CLI 使用

### 安装

```bash
pip install mcda-core
```

### 基本命令

```bash
# 验证配置文件
mcda validate config.yaml

# 运行分析
mcda analyze config.yaml

# 批量分析
mcda batch analyses/

# 生成报告
mcda report config.yaml --format json
```

### YAML 配置示例

```yaml
problem:
  name: "供应商选择"
  alternatives:
    - 供应商A
    - 供应商B
    - 供应商C

  criteria:
    - name: 质量
      weight: 0.35
      direction: higher_better
    - name: 价格
      weight: 0.25
      direction: lower_better

  scores:
    供应商A:
      质量: 85
      价格: 50
    供应商B:
      质量: 88
      价格: 45

algorithm:
  name: vikor_interval
  params:
    v: 0.5
```

---

## 📊 性能基准

| 规模 | 算法 | 时间 | 目标 |
|------|------|------|------|
| 10×10 | VIKOR | 0.3s | < 1s ✅ |
| 10×10 | TODIM | 0.4s | < 1s ✅ |
| 50×20 | VIKOR | 4.2s | < 5s ✅ |
| 50×20 | TODIM | 4.8s | < 5s ✅ |

测试环境: Intel i7, 16GB RAM, Python 3.12

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/mcda-core/

# 运行特定测试
pytest tests/mcda-core/unit/test_algorithms/test_vikor_interval.py

# 查看覆盖率
pytest tests/mcda-core/ --cov=skills/mcda-core/lib --cov-report=html
```

**测试覆盖率**: 90%+

---

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md)。

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/your-org/mcda-core.git

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black skills/mcda-core/lib/
isort skills/mcda-core/lib/
```

---

## 📝 更新日志

### v0.7 (2026-02-04)

**新增功能**:
- ✨ VIKOR 区间版本支持
- ✨ TODIM 区间版本支持
- ✨ 可能度排序方法
- ✨ 前景理论集成
- ✨ 11 个集成测试

**改进**:
- ⚡ 性能优化（50×20 < 5s）
- 📚 完整使用示例
- 🐛 Bug 修复（排名生成、区间运算）

**测试**:
- 82 个新测试（100% 通过率）
- 90%+ 代码覆盖率

**文档**:
- API 文档更新
- 使用示例文档
- v0.7 完成报告

### v0.6

- 添加 ELECTRE-I 和 PROMETHEE II
- CLI 工具支持
- YAML 配置文件

### v0.5

- 初始版本
- 基础算法实现（WSM, WPM, TOPSIS, VIKOR, TODIM）

---

## 📄 许可证

[MIT License](LICENSE.txt)

---

## 🙏 致谢

- 所有贡献者
- MCDA 算法原作者
- Python 科学计算社区

---

## 📮 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/your-org/mcda-core/issues)
- **功能建议**: [GitHub Discussions](https://github.com/your-org/mcda-core/discussions)
- **邮件**: your-email@example.com

---

**最后更新**: 2026-02-04
**版本**: v0.7
