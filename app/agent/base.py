from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    所有 Agent 的基类。
    """

    @abstractmethod
    async def run(self, task: str) -> str:
        """
        异步运行 Agent 来完成给定的任务。

        :param task: 要完成的任务。
        :return: 任务的最终结果。
        """
        pass
