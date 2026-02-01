# Python 环境配置指南 - Claude Code

**目的**: 配置可在 Claude Code 中使用的 Python 环境
**适用**: Windows + Claude Code + Bash Tool

---

## 🚀 快速配置 (5 分钟)

### 步骤 1: 查找系统 Python

首先检查你的系统是否已安装完整版 Python:

```bash
# 在 Claude Code 中运行
where python
where python3
py --list
```

**预期结果**:
- 如果看到 `C:\Python39\python.exe` 或类似路径 → ✅ 已安装完整版
- 如果只看到 WindowsStore 路径 → ⚠️ 需要安装完整版或使用虚拟环境

### 步骤 2: 创建虚拟环境 (推荐)

```bash
# 进入项目目录
cd D:\Workspace\dev\ai_skills_development\ai_core_skill

# 创建虚拟环境 (使用系统的 python launcher)
py -m venv .venv

# 或者如果 python 命令可用
python -m venv .venv

# 或者使用 python3
python3 -m venv .venv
```

### 步骤 3: 激活虚拟环境

**在 Claude Code 的 Bash Tool 中**:

```bash
# Windows Git Bash
source .venv/Scripts/activate

# 或直接使用完整路径
export PATH="D:\Workspace\dev\ai_skills_development\ai_core_skill\.venv\Scripts:$PATH"
```

### 步骤 4: 验证环境

```bash
# 检查 Python 版本
python --version

# 检查 pip
pip --version

# 应该看到虚拟环境路径
```

### 步骤 5: 安装依赖

```bash
# 安装 pytest 和相关依赖
pip install pytest pytest-cov numpy

# 验证安装
pip list | grep -E "(pytest|numpy)"
```

### 步骤 6: 运行测试

```bash
# 运行 Phase 3 测试
pytest tests/mcda-core/test_algorithms/test_todim.py -v

# 运行 Phase 4 测试
pytest tests/mcda-core/test_algorithms/test_electre1.py -v

# 运行所有测试
pytest tests/mcda-core/test_algorithms/ -v
```

---

## 🎯 永久配置方案

### 选项 A: 修改项目启动脚本

创建 `tests/mcda-core/run_tests.sh`:

```bash
#!/bin/bash
# 测试运行脚本

# 激活虚拟环境
source .venv/Scripts/activate

# 运行测试
pytest tests/mcda-core/test_algorithms/ -v --tb=short "$@"
```

然后在 Claude Code 中运行:
```bash
bash tests/mcda-core/run_tests.sh
```

### 选项 B: 使用绝对路径

在 Claude Code 中始终使用完整路径:

```bash
# 使用虚拟环境中的 Python
D:\Workspace\dev\ai_skills_development\ai_core_skill\.venv\Scripts\python.exe -m pytest tests/mcda-core/test_algorithms/test_electre1.py -v

# 或使用正斜杠 (Git Bash 兼容)
D:/Workspace/dev/ai_skills_development/ai_core_skill/.venv/Scripts/python.exe -m pytest tests/mcda-core/test_algorithms/test_electre1.py -v
```

### 选项 C: 修改 PATH 环境变量

在每个会话开始时运行:

```bash
# 在 Claude Code 会话开始时运行一次
export PYTHON_BIN="D:\Workspace\dev\ai_skills_development\ai_core_skill\.venv\Scripts"
export PATH="$PYTHON_BIN:$PATH"

# 之后就可以直接使用
python -m pytest tests/mcda-core/test_algorithms/test_electre1.py -v
```

---

## 🛠️ 故障排除

### 问题 1: 虚拟环境创建失败

**错误**: `Error: Command '['...']' returned non-zero exit status`

**解决**:
```bash
# 尝试使用 python launcher
py -3 -m venv .venv

# 或指定 Python 版本
py -3.9 -m venv .venv
py -3.10 -m venv .venv
py -3.11 -m venv .venv
```

### 问题 2: 激活脚本找不到

**错误**: `.venv/Scripts/activate: No such file or directory`

**解决**:
```bash
# 检查虚拟环境是否创建成功
ls .venv/Scripts/

# 如果目录为空,重新创建
rm -rf .venv
py -m venv .venv
```

### 问题 3: 权限拒绝

**错误**: `Permission denied` when running activate

**解决**:
```bash
# 直接使用 Python 可执行文件,不使用 activate
.venv/Scripts/python.exe -m pytest tests/mcda-core/test_algorithms/test_electre1.py -v
```

### 问题 4: Python 版本不兼容

**错误**: `ModuleNotFoundError` or syntax errors

**解决**:
```bash
# 确保使用 Python 3.8+
python --version

# 如果版本过低,安装新版 Python
# 下载: https://www.python.org/downloads/
```

---

## 📝 快速参考命令

### 环境管理

```bash
# 创建虚拟环境
py -m venv .venv

# 激活虚拟环境
source .venv/Scripts/activate

# 退出虚拟环境
deactivate

# 删除虚拟环境
rm -rf .venv
```

### 依赖管理

```bash
# 安装依赖
pip install pytest pytest-cov numpy

# 导出依赖列表
pip freeze > requirements.txt

# 从 requirements.txt 安装
pip install -r requirements.txt

# 查看已安装包
pip list
```

### 测试执行

```bash
# 运行所有测试
pytest tests/mcda-core/test_algorithms/ -v

# 运行特定文件
pytest tests/mcda-core/test_algorithms/test_electre1.py -v

# 运行特定测试类
pytest tests/mcda-core/test_algorithms/test_electre1.py::TestConcordanceIndex -v

# 运行特定测试方法
pytest tests/mcda-core/test_algorithms/test_electre1.py::TestConcordanceIndex::test_concordance_basic -v

# 生成覆盖率报告
pytest tests/mcda-core/test_algorithms/test_electre1.py --cov=skills/mcda-core/lib/algorithms/electre1 --cov-report=html
```

---

## ✅ 验证配置成功

运行以下命令确认配置成功:

```bash
# 1. 检查 Python
python --version
# 预期: Python 3.8+

# 2. 检查 pytest
python -m pytest --version
# 预期: pytest 7.x+

# 3. 运行测试
python -m pytest tests/mcda-core/test_algorithms/test_electre1.py -v
# 预期: 37 个测试运行
```

如果所有命令都成功,配置完成! 🎉

---

## 🎯 给 Claude Code 的建议

### 在会话开始时

每次新会话开始时,运行:

```bash
cd D:\Workspace\dev\ai_skills_development\ai_core_skill
source .venv/Scripts/activate
python --version
```

### 创建别名

在项目根目录创建 `.bashrc` 或 `init.sh`:

```bash
# MCDA Core 开发环境初始化
export PROJECT_ROOT="D:\Workspace\dev\ai_skills_development\ai_core_skill"
export PATH="$PROJECT_ROOT/.venv/Scripts:$PATH"

cd $PROJECT_ROOT
```

然后在 Claude Code 中运行:
```bash
source init.sh
```

---

## 📚 额外资源

- [Python 虚拟环境文档](https://docs.python.org/3/library/venv.html)
- [pytest 文档](https://docs.pytest.org/)
- [Claude Code Bash Tool 使用](https://github.com/anthropics/claude-code)

---

**创建者**: AI (Claude Sonnet 4.5)
**最后更新**: 2026-02-01
**状态**: ✅ 完整指南
