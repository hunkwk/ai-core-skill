"""MCDA Core 配置加载器模块

提供多种配置文件格式的加载支持：
- JSONLoader: JSON 配置文件
- YAMLLoader: YAML 配置文件
- LoaderFactory: 自动检测格式

设计遵循 ADR-005: 配置加载器抽象层
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Union

from ..exceptions import ConfigLoadError


# =============================================================================
# ConfigLoader - 抽象基类
# =============================================================================

class ConfigLoader(ABC):
    """配置加载器抽象基类

    定义配置加载器的统一接口，支持多种配置格式。
    """

    @abstractmethod
    def load(self, source: Union[str, Path]) -> dict[str, Any]:
        """加载配置文件

        Args:
            source: 配置文件路径

        Returns:
            解析后的配置字典

        Raises:
            FileNotFoundError: 文件不存在
            ConfigLoadError: 配置文件格式错误
        """
        pass

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> bool:
        """验证配置数据

        Args:
            data: 配置数据字典

        Returns:
            验证是否通过
        """
        pass


# =============================================================================
# JSONLoader - JSON 配置加载器
# =============================================================================

class JSONLoader(ConfigLoader):
    """JSON 配置文件加载器"""

    def load(self, source: Union[str, Path]) -> dict[str, Any]:
        """加载 JSON 配置文件

        Args:
            source: JSON 文件路径

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 文件不存在
            ConfigLoadError: JSON 格式错误
        """
        import json

        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {source_path}")

        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigLoadError(
                f"JSON 格式错误: {str(e)}",
                details={"file": str(source_path), "error": str(e)}
            ) from e
        except Exception as e:
            raise ConfigLoadError(
                f"加载 JSON 文件失败: {str(e)}",
                details={"file": str(source_path)}
            ) from e

        return data

    def validate(self, data: dict[str, Any]) -> bool:
        """验证 JSON 配置数据

        Args:
            data: 配置数据字典

        Returns:
            True（基本验证通过）
        """
        # 基本验证：确保是字典类型
        return isinstance(data, dict)


# =============================================================================
# YAMLLoader - YAML 配置加载器
# =============================================================================

class YAMLLoader(ConfigLoader):
    """YAML 配置文件加载器"""

    def load(self, source: Union[str, Path]) -> dict[str, Any]:
        """加载 YAML 配置文件

        Args:
            source: YAML 文件路径

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 文件不存在
            ConfigLoadError: YAML 格式错误
        """
        import yaml

        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {source_path}")

        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigLoadError(
                f"YAML 格式错误: {str(e)}",
                details={"file": str(source_path), "error": str(e)}
            ) from e
        except Exception as e:
            raise ConfigLoadError(
                f"加载 YAML 文件失败: {str(e)}",
                details={"file": str(source_path)}
            ) from e

        return data

    def validate(self, data: dict[str, Any]) -> bool:
        """验证 YAML 配置数据

        Args:
            data: 配置数据字典

        Returns:
            True（基本验证通过）
        """
        # 基本验证：确保是字典类型
        return isinstance(data, dict)


# =============================================================================
# LoaderFactory - 加载器工厂
# =============================================================================

class LoaderFactory:
    """配置加载器工厂

    根据文件扩展名自动选择合适的加载器。
    支持动态注册新的加载器。
    """

    # 默认支持的文件格式
    _loaders: dict[str, type[ConfigLoader]] = {
        '.json': JSONLoader,
        '.yaml': YAMLLoader,
        '.yml': YAMLLoader,
    }

    @classmethod
    def get_loader(cls, file_path: Union[str, Path]) -> ConfigLoader:
        """根据文件扩展名获取加载器

        Args:
            file_path: 配置文件路径

        Returns:
            配置加载器实例

        Raises:
            ValueError: 不支持的文件格式
        """
        ext = Path(file_path).suffix.lower()

        if ext not in cls._loaders:
            raise ValueError(
                f"不支持的文件格式: {ext}. "
                f"支持的格式: {', '.join(cls._loaders.keys())}"
            )

        loader_class = cls._loaders[ext]
        return loader_class()

    @classmethod
    def register_loader(cls, ext: str, loader: type[ConfigLoader]):
        """注册新的加载器

        Args:
            ext: 文件扩展名（必须以 '.' 开头）
            loader: 加载器类

        Raises:
            ValueError: 扩展名格式错误
        """
        if not ext.startswith('.'):
            raise ValueError("文件扩展名必须以 '.' 开头")

        if not issubclass(loader, ConfigLoader):
            raise ValueError("加载器必须继承自 ConfigLoader")

        cls._loaders[ext] = loader

    @classmethod
    def supported_formats(cls) -> list[str]:
        """获取支持的文件格式列表

        Returns:
            文件扩展名列表
        """
        return list(cls._loaders.keys())


__all__ = [
    'ConfigLoader',
    'JSONLoader',
    'YAMLLoader',
    'LoaderFactory',
]
