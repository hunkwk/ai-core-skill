"""
MCDA Core - 安装脚本

将 mcda_core 模块安装到 Python 环境中
"""

import sys
from pathlib import Path
import subprocess

print("="*70)
print("  MCDA Core - 安装脚本")
print("="*70)

# 获取项目根目录
project_root = Path(__file__).parent.parent.parent
print(f"\n项目根目录: {project_root}")

# 检查 setup.py 或 pyproject.toml 是否存在
setup_files = [
    project_root / "setup.py",
    project_root / "pyproject.toml"
]

has_setup = any(f.exists() for f in setup_files)
print(f"找到配置文件: {has_setup}")

# 方案 1: 如果有 setup.py，使用 pip install -e
if has_setup:
    print("\n[方案 1] 使用 pip 安装...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(project_root)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("✅ 安装成功！")
        else:
            print(f"⚠️  安装可能有问题: {result.stderr}")
    except Exception as e:
        print(f"❌ 安装失败: {e}")

# 方案 2: 直接添加到 Python 路径
print("\n[方案 2] 添加到 Python 路径...")

# 添加 skills 目录到 Python 路径
skills_dir = project_root / "skills"
if skills_dir.exists():
    print(f"添加目录: {skills_dir}")

    # 创建 .pth 文件
    import site
    site_packages = site.getsitepackages()[0]
    pth_file = Path(site_packages) / "mcda_core.pth"

    try:
        with open(pth_file, 'w') as f:
            f.write(str(skills_dir))

        print(f"✅ 创建 {pth_file}")
        print(f"✅ 添加路径: {skills_dir}")
    except Exception as e:
        print(f"❌ 创建 .pth 文件失败: {e}")
        print("\n尝试手动添加...")

        # 手动添加到 sys.path
        if str(skills_dir) not in sys.path:
            sys.path.insert(0, str(skills_dir))
            print(f"✅ 已添加到 sys.path")

# 方案 3: 创建 __init__.py 在 skills/mcda-core 目录
print("\n[方案 3] 确保 mcda_core 包结构正确...")

mcda_core_dir = skills_dir / "mcda-core"
if mcda_core_dir.exists():
    print(f"mcda_core 目录: {mcda_core_dir}")

    # 确保 lib 目录有 __init__.py
    lib_init = mcda_core_dir / "lib" / "__init__.py"
    if lib_init.exists():
        print(f"✅ lib/__init__.py 存在")
    else:
        print(f"❌ lib/__init__.py 缺失")

# 测试导入
print("\n" + "="*70)
print("  测试导入")
print("="*70)

try:
    # 添加 skills 目录到路径
    if str(skills_dir) not in sys.path:
        sys.path.insert(0, str(skills_dir))

    import mcda_core
    print(f"✅ 成功导入 mcda_core")
    print(f"   版本: {mcda_core.__version__}")
    print(f"   路径: {mcda_core.__file__}")

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n请尝试以下命令:")
    print(f"  export PYTHONPATH={skills_dir}:$PYTHONPATH")
    print(f"  或者在 Windows 上:")
    print(f"  set PYTHONPATH={skills_dir};%PYTHONPATH%")

print("\n" + "="*70)
