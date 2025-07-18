from abc import ABC, abstractmethod
from app.schema import AgentState

class BaseAgent(ABC):
    """Agent 的抽象基类"""

    def __init__(self, **kwargs):
        """
        初始化 Agent。
        kwargs 用于接收来自工厂的额外参数。
        """
        pass

    @abstractmethod
    def run(self, task: str) -> str:
        """
        执行任务的入口点。

        Args:
            task: 要完成的任务描述。

        Returns:
            任务的最终结果。
        """
        pass