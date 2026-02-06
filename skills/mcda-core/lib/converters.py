"""
MCDA Core - 配置格式转换工具

支持 YAML 和 JSON 格式之间的相互转换。
"""

from pathlib import Path
from typing import Literal
import json

from .loaders import JSONLoader, YAMLLoader, LoaderFactory
from .exceptions import ConfigLoadError


FormatType = Literal["json", "yaml", "yml"]


class ConfigConverter:
    """配置格式转换器

    支持 YAML 和 JSON 格式之间的相互转换。
    保持数据完整性和注释（对于 JSON）。
    """

    def __init__(self):
        """初始化转换器"""
        self.json_loader = JSONLoader()
        self.yaml_loader = YAMLLoader()

    def convert(
        self,
        input_file: str | Path,
        output_file: str | Path,
        output_format: FormatType | None = None,
        indent: int = 2,
        ensure_ascii: bool = False
    ) -> None:
        """转换配置文件格式

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            output_format: 输出格式（json, yaml, yml），如果为 None 则根据 output_file 扩展名推断
            indent: 缩进空格数（默认 2）
            ensure_ascii: JSON 是否确保 ASCII 编码（默认 False）

        Raises:
            FileNotFoundError: 输入文件不存在
            ConfigLoadError: 配置文件格式错误
            ValueError: 不支持的格式

        Example:
            >>> converter = ConfigConverter()
            >>> converter.convert("config.yaml", "config.json")
            >>> converter.convert("config.json", "config.yaml", output_format="yaml")
        """
        input_path = Path(input_file)
        output_path = Path(output_file)

        # 1. 加载输入文件
        input_data = self._load_config(input_path)

        # 2. 确定输出格式
        if output_format is None:
            output_format = self._detect_format(output_path)

        # 3. 保存为输出格式
        self._save_config(input_data, output_path, output_format, indent, ensure_ascii)

    def convert_to_json(
        self,
        input_file: str | Path,
        output_file: str | Path | None = None,
        indent: int = 2,
        ensure_ascii: bool = False
    ) -> str:
        """转换为 JSON 格式

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            indent: 缩进空格数
            ensure_ascii: 是否确保 ASCII 编码

        Returns:
            JSON 字符串（如果 output_file 为 None）

        Raises:
            FileNotFoundError: 输入文件不存在
            ConfigLoadError: 配置文件格式错误
        """
        input_path = Path(input_file)

        # 加载配置
        data = self._load_config(input_path)

        # 转换为 JSON 字符串
        json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

        # 如果指定了输出文件，则保存
        if output_file is not None:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)

        return json_str

    def convert_to_yaml(
        self,
        input_file: str | Path,
        output_file: str | Path | None = None,
        default_flow_style: bool = False
    ) -> str:
        """转换为 YAML 格式

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            default_flow_style: YAML 默认流样式

        Returns:
            YAML 字符串（如果 output_file 为 None）

        Raises:
            FileNotFoundError: 输入文件不存在
            ConfigLoadError: 配置文件格式错误
        """
        import yaml

        input_path = Path(input_file)

        # 加载配置
        data = self._load_config(input_path)

        # 转换为 YAML 字符串
        yaml_str = yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=default_flow_style,
            sort_keys=False
        )

        # 如果指定了输出文件，则保存
        if output_file is not None:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(yaml_str)

        return yaml_str

    def _load_config(self, file_path: Path) -> dict:
        """加载配置文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")

        # 使用 LoaderFactory 自动检测格式
        loader = LoaderFactory.get_loader(file_path)
        data = loader.load(file_path)

        if not loader.validate(data):
            raise ConfigLoadError(
                f"配置数据验证失败: {file_path}",
                details={"file": str(file_path)}
            )

        return data

    def _detect_format(self, file_path: Path) -> FormatType:
        """根据文件扩展名检测格式"""
        ext = file_path.suffix.lower()

        if ext == ".json":
            return "json"
        elif ext == ".yaml" or ext == ".yml":
            return "yaml"  # 统一返回 "yaml"
        else:
            raise ValueError(
                f"无法从文件扩展名推断格式: {ext}. "
                f"请明确指定 output_format"
            )

    def _save_config(
        self,
        data: dict,
        output_path: Path,
        output_format: FormatType,
        indent: int,
        ensure_ascii: bool
    ) -> None:
        """保存配置文件"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        elif output_format in ["yaml", "yml"]:
            import yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=indent
                )
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")


__all__ = ['ConfigConverter', 'FormatType']
