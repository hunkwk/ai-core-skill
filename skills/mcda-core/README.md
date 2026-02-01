# MCDA Core

**Multi-Criteria Decision Analysis Core Framework**

通用多准则决策分析核心框架，支持 5 种排序算法、2 种权重服务、算法对比和可视化功能。

[![Python Version](https://img.shields.io/badge/python-3.8%2B+-blue.svg)]
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)]
[![Tests](https://img.shields.io/badge/tests-83%20passed-green.svg)]
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen.svg)]
[![Version](https://img.shields.io/badge/version-v0.3.0-blue.svg)]

---

## 🎯 功能特性

### 核心功能
- ✅ **5 种 MCDA 排序算法**: WSM、WPM、TOPSIS、VIKOR、PROMETHEE-II
- ✅ **2 种权重计算服务**: AHP 主观赋权、熵权法客观赋权
- ✅ **算法对比服务**: 多算法结果对比、Spearman 相关性分析
- ✅ **ASCII 可视化**: 柱状图、雷达图、排名对比图
- ✅ **可插拔架构**: 算法注册机制，易于扩展
- ✅ **数据验证**: 完整的输入验证和错误处理
- ✅ **多种标准化**: MinMax、Vector 标准化
- ✅ **CLI 工具**: 命令行接口，支持批量处理

### 算法支持

#### 排序算法

| 算法 | 全称 | 适用场景 |
|------|------|----------|
| **WSM** | Weighted Sum Model | 简单加权求和 |
| **WPM** | Weighted Product Model | 加权乘积 |
| **TOPSIS** | 逼近理想解排序法 | 多准则权衡 |
| **VIKOR** | 折衷排序法 | 折衷决策 |
| **PROMETHEE-II** | 偏好排序法 | 基于偏好函数的排序 |

#### 权重计算服务

| 服务 | 全称 | 类型 |
|------|------|------|
| **AHP** | Analytic Hierarchy Process | 主观赋权 |
| **熵权法** | Entropy Weight Method | 客观赋权 |

#### 高级功能

| 功能 | 描述 |
|------|------|
| **算法对比** | 多算法结果对比、排名相关性分析 |
| **ASCII 可视化** | 柱状图、雷达图、排名对比图 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd ai_core_skill

# （可选）创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装依赖（如果需要）
pip install -r requirements.txt
```

### 基本使用

#### 1. 创建决策配置文件

```yaml
# config.yaml
name: 供应商选择

alternatives:
  - 供应商A
  - 供应商B
  - 供应商C

criteria:
  - name: 成本
    weight: 0.35
    direction: lower_better
  - name: 质量
    weight: 0.30
    direction: higher_better
  - name: 交付期
    weight: 0.20
    direction: lower_better
  - name: 服务
    weight: 0.15
    direction: higher_better

scores:
  供应商A:
    成本: 50
    质量: 80
    交付期: 30
    服务: 70
  供应商B:
    成本: 70
    质量: 60
    交付期: 20
    服务: 80
  供应商C:
    成本: 60
    质量: 90
    交付期: 40
    服务: 60

algorithm:
  name: topsis
```

#### 2. 验证配置

```bash
python -m mcda_core.cli validate config.yaml
```

#### 3. 运行分析

```bash
# 基本分析（输出 Markdown 报告到 stdout）
python -m mcda_core.cli analyze config.yaml

# 保存报告到文件
python -m mcda_core.cli analyze config.yaml -o report.md

# 指定算法
python -m mcda_core.cli analyze config.yaml --algorithm vikor

# 生成 JSON 报告
python -m mcda_core.cli analyze config.yaml -o result.json -f json

# 带敏感性分析
python -m mcda_core.cli analyze config.yaml --sensitivity
```

---

## 📖 Python API 使用

```python
from mcda_core.core import MCDAOrchestrator

# 创建编排器
orchestrator = MCDAOrchestrator()

# 加载配置
problem = orchestrator.load_from_yaml("config.yaml")

# 验证数据
validation = orchestrator.validate(problem)
if not validation.is_valid:
    print(f"验证失败: {validation.errors}")

# 运行分析
result = orchestrator.analyze(problem, algorithm_name="topsis")

# 查看排名
for ranking in result.rankings:
    print(f"{ranking.rank}. {ranking.alternative}: {ranking.score:.4f}")

# 生成报告
report = orchestrator.generate_report(problem, result, format="markdown")
print(report)

# 保存报告
orchestrator.save_report(problem, result, "output.md", format="markdown")
```

---

## 🛠️ CLI 命令

### analyze - 分析决策问题

```bash
mcda analyze <config> [OPTIONS]

选项:
  -o, --output PATH    输出报告文件路径
  -a, --algorithm STR  算法名称（wsm|wpm|topsis|vikor）
  -f, --format STR    报告格式（markdown|json）
  -s, --sensitivity  运行敏感性分析
```

### validate - 验证配置文件

```bash
mcda validate <config>
```

### 其他命令

```bash
mcda --help          # 显示帮助信息
mcda --version       # 显示版本信息
```

---

## 📋 YAML 配置格式

### 完整示例

```yaml
name: 决策问题名称

alternatives:
  - 备选方案A
  - 备选方案B
  - 备选方案C

criteria:
  - name: 准则1
    weight: 0.4
    direction: higher_better  # higher_better 或 lower_better
  - name: 准则2
    weight: 0.3
    direction: lower_better
  - name: 准则3
    weight: 0.3
    direction: higher_better

scores:
  备选方案A:
    准则1: 80
    准则2: 60
    准则3: 90
  备选方案B:
    准则1: 70
    准则2: 85
    准则3: 75
  备选方案C:
    准则1: 90
    准则2: 75
    准则3: 80

algorithm:
  name: topsis           # 算法名称
  # 算法特定参数（可选）
  # v: 0.5               # VIKOR 参数
```

### 配置规则

1. **备选方案**（alternatives）
   - 至少 2 个
   - 名称列表

2. **评价准则**（criteria）
   - 至少 1 个
   - 权重总和自动归一化为 1.0
   - 方向：`higher_better`（越高越好）或 `lower_better`（越低越好）

3. **评分矩阵**（scores）
   - 所有方案在所有准则上都必须有评分
   - 评分范围：0-100

4. **算法配置**（algorithm）
   - `name`: 算法名称（wsm、wpm、topsis、vikor）
   - 算法特定参数（可选）

---

## 🔬 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/mcda-core/

# 运行特定测试
pytest tests/mcda-core/test_algorithms.py
pytest tests/mcda-core/test_e2e.py

# 生成覆盖率报告
pytest tests/mcda-core/ --cov=skills/mcda-core --cov-report=html
```

### 测试结果

- **总测试数**: 313
- **通过率**: 100%
- **覆盖率**: 92%

---

## 📚 更多文档

- [SKILL.md](skills/mcda-core/SKILL.md) - AI 执行指令
- [SKILL_CN.md](skills/mcda-core/SKILL_CN.md) - AI 执行指令（中文）
- [TDD 进度](docs/active/tdd-mcda-core.md) - 开发进度
- [项目检查点](docs/checkpoints/) - 版本里程碑

---

## 📝 开发计划

### v0.2.1（当前版本）
- ✅ MVP 基础功能（4 种算法）
- ✅ CLI 接口
- ✅ JSON 报告支持

### v0.3（计划中）
- 熵权法、AHP 赋权方法
- PROMETHEE-II 算法
- 更多标准化方法

---

## 📄 License

Apache License 2.0

---

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📧 联系

- **项目**: MCDA Core
- **版本**: v0.2.1
- **状态**: 稳定版本

---

**最后更新**: 2026-02-01
