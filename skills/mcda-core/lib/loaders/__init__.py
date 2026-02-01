"""MCDA Core 配置加载器模块

提供多种配置文件格式的加载支持：
- JSONLoader: JSON 配置文件
- YAMLLoader: YAML 配置文件
- LoaderFactory: 自动检测格式

设计遵循 ADR-005: 配置加载器抽象层
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

# 相对导入异常
try:
    from ..exceptions import ConfigLoadError
except ImportError:
    # 测试环境下的导入
    import sys
    from pathlib import Path as PathLib
    lib_path = PathLib(__file__).parent.parent
    if str(lib_path) not in sys.path:
        sys.path.insert(0, str(lib_path))
    from exceptions import ConfigLoadError