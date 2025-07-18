from abc import ABC, abstractmethod
from app.llm import LLM
from app.tool.tool_collection import ToolCollection


# [FIX] 确保基类的名称是 'Agent' (首字母大写)
# Ensure the base class name is 'Agent' (PascalCase)
class Agent(ABC):
    """
    The abstract base class for all agents.
    """
    def __init__(
            self,
            llm: LLM,
            prompt,
            tools: ToolCollection,
            max_iterations: int,
    ):
        self.llm = llm
        self.prompt = prompt
        self.tools = tools
        self.max_iterations = max_iterations

    @abstractmethod
    async def run(self, task: str):
        """
        The main entry point for the agent to run a task.
        """
        pass
