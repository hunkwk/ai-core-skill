"""
MCDA Core - 算法抽象基类和注册机制

定义 MCDA 算法的统一接口和注册机制。
"""

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

# 类型注解导入（避免循环导入）
if TYPE_CHECKING:
    from mcda_core.models import DecisionProblem, DecisionResult


# =============================================================================
# 算法注册表
# =============================================================================

_algorithms: dict[str, type["MCDAAlgorithm"]] = {}


def register_algorithm(name: str):
    """算法注册装饰器

    Args:
        name: 算法名称

    Returns:
        装饰器函数

    Example:
        @register_algorithm("wsm")
        class WSMAlgorithm(MCDAAlgorithm):
            ...
    """
    def decorator(cls: type["MCDAAlgorithm"]) -> type["MCDAAlgorithm"]:
        _algorithms[name] = cls
        return cls
    return decorator


def get_algorithm(name: str) -> "MCDAAlgorithm":
    """获取算法实例

    Args:
        name: 算法名称

    Returns:
        算法实例

    Raises:
        ValueError: 未知的算法
    """
    if name not in _algorithms:
        available = ", ".join(_algorithms.keys())
        raise ValueError(f"未知的算法: '{name}'. 可用: {available}")
    return _algorithms[name]()


def list_algorithms() -> list[str]:
    """列出所有已注册的算法

    Returns:
        算法名称列表
    """
    return list(_algorithms.keys())


# =============================================================================
# 算法抽象基类
# =============================================================================

class MCDAAlgorithm(ABC):
    """MCDA 算法抽象基类

    所有 MCDA 汇总算法必须继承此类并实现 calculate 方法。
    """

    @abstractmethod
    def calculate(
        self,
        problem: "DecisionProblem",
        **kwargs: Any
    ) -> "DecisionResult":
        """执行计算，返回决策结果

        Args:
            problem: 决策问题
            **kwargs: 算法特定参数

        Returns:
            决策结果
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """算法名称"""
        pass

    @property
    def description(self) -> str:
        """算法描述（可选覆盖）"""
        return f"{self.name} 算法"

    def validate(self, problem: "DecisionProblem") -> None:
        """验证输入数据（可选覆盖）

        Args:
            problem: 决策问题

        Raises:
            ValueError: 数据验证失败
        """
        # 基本验证：至少有 2 个备选方案和 1 个准则
        if len(problem.alternatives) < 2:
            raise ValueError(f"至少需要 2 个备选方案，当前: {len(problem.alternatives)}")

        if len(problem.criteria) < 1:
            raise ValueError(f"至少需要 1 个准则，当前: {len(problem.criteria)}")

        # 验证评分完整性
        for alt in problem.alternatives:
            if alt not in problem.scores:
                raise ValueError(f"备选方案 '{alt}' 缺少评分数据")

            for crit in problem.criteria:
                if crit.name not in problem.scores[alt]:
                    raise ValueError(
                        f"备选方案 '{alt}' 缺少准则 '{crit.name}' 的评分"
                    )


# =============================================================================
# 导出公共 API
# =============================================================================

__all__ = [
    # 基类
    "MCDAAlgorithm",
    # 注册
    "register_algorithm",
    "get_algorithm",
    "list_algorithms",
]
