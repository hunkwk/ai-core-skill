"""
MCDA Core - 工具函数模块

提供 YAML 加载、权重归一化、方向反转等工具函数。
"""

from pathlib import Path
from typing import Any
import yaml

from .exceptions import YAMLParseError


# =============================================================================
# YAML 加载函数
# =============================================================================

def load_yaml(file_path: Path | str) -> dict[str, Any]:
    """加载 YAML 配置文件

    Args:
        file_path: YAML 文件路径

    Returns:
        解析后的字典数据

    Raises:
        YAMLParseError: 文件不存在或 YAML 语法错误
    """
    file_path = Path(file_path)

    # 检查文件是否存在
    if not file_path.exists():
        raise YAMLParseError(
            f"YAML 文件不存在: {file_path}",
            file=str(file_path),
            details={"error": "File not found"}
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        # 获取错误位置信息
        error_line = getattr(e, "problem_mark", None)
        line = error_line.line + 1 if error_line else None
        column = error_line.column + 1 if error_line else None

        raise YAMLParseError(
            f"YAML 语法错误: {str(e)}",
            file=str(file_path),
            line=line,
            column=column,
            error=str(e)
        ) from e
    except Exception as e:
        raise YAMLParseError(
            f"读取 YAML 文件失败: {str(e)}",
            file=str(file_path),
            details={"error": str(e)}
        ) from e

    # 确保返回字典
    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise YAMLParseError(
            f"YAML 文件根节点必须是字典，实际类型: {type(data).__name__}",
            file=str(file_path),
            details={"actual_type": type(data).__name__}
        )

    return data


# =============================================================================
# 权重归一化函数
# =============================================================================

def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """归一化权重，使权重总和为 1.0

    Args:
        weights: 权重字典 {criterion_name: weight}

    Returns:
        归一化后的权重字典

    Raises:
        ValueError: 权重总和为 0 或包含负权重
    """
    if not weights:
        raise ValueError("权重字典不能为空")

    # 检查负权重
    for name, weight in weights.items():
        if weight < 0:
            raise ValueError(f"权重不能为负数: {name} = {weight}")

    # 计算权重总和
    total = sum(weights.values())

    if total == 0:
        raise ValueError("权重总和不能为 0")

    # 如果总和已经是 1.0（允许浮点误差），直接返回
    if abs(total - 1.0) < 1e-6:
        return weights.copy()

    # 归一化
    normalized = {name: weight / total for name, weight in weights.items()}

    return normalized


# =============================================================================
# 方向反转函数
# =============================================================================

def reverse_direction(direction: str) -> str:
    """反转评价准则方向

    Args:
        direction: 原始方向 ("higher_better" 或 "lower_better")

    Returns:
        反转后的方向

    Raises:
        ValueError: 无效的方向值
    """
    valid_directions = {"higher_better", "lower_better"}

    if direction not in valid_directions:
        raise ValueError(
            f"无效的方向: '{direction}'，"
            f"有效值为: {', '.join(valid_directions)}"
        )

    return "lower_better" if direction == "higher_better" else "higher_better"
