from app.agent.base import BaseAgent
from app.agent.manus import ManusAgent
from app.agent.react import ReActAgent
from app.llm import LLM

class AgentFactory:
    """
    AgentFactory 类用于根据名称创建不同的 Agent 实例。
    """
    @staticmethod
    def create_agent(agent_name: str, llm: LLM, max_iterations: int) -> BaseAgent:
        """
        根据 agent_name 创建并返回一个 Agent 实例。

        :param agent_name: 要创建的 Agent 的名称。
        :param llm: 要传递给 Agent 的 LLM 实例。
        :param max_iterations: Agent 的最大迭代次数。
        :return: 一个 BaseAgent 的子类实例。
        :raises ValueError: 如果 agent_name 无效。
        """
        if agent_name == "ManusAgent":
            return ManusAgent(llm=llm, max_iterations=max_iterations)
        elif agent_name == "ReActAgent":
            # 虽然 ManusAgent 继承自 ReActAgent，但为了清晰起见，也保留这个选项
            return ReActAgent(llm=llm, max_iterations=max_iterations)
        else:
            raise ValueError(f"未知的 Agent 名称: {agent_name}")

