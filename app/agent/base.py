from abc import ABC, abstractmethod
from app.llm import LLM


class BaseAgent(ABC):
    """
    所有 Agent 的抽象基类，定义了 Agent 的基本接口。
    """

    # ===============================================================================
    # 关键修正：添加 __init__ 方法。
    # 这个方法负责接收 llm 实例和最大迭代次数，并将它们存储为实例变量，
    # 以便 Agent 在其生命周期内使用。
    # ===============================================================================
    def __init__(self, llm: LLM, max_iterations: int):
        """
        初始化 BaseAgent。

        :param llm: 一个 LLM 类的实例，用于与大语言模型交互。
        :param max_iterations: Agent 执行任务的最大迭代次数。
        """
        self.llm = llm
        self.max_iterations = max_iterations

    @abstractmethod
    def get_prompt(self, task: str) -> str:
        """
        根据任务描述生成系统提示词。
        这是一个抽象方法，必须由子类实现。
        """
        ...

    @abstractmethod
    async def run(self, task: str):
        """
        运行 Agent 来完成指定的任务。
        这是一个抽象方法，必须由子类实现。
        """
        ...
