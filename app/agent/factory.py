from typing import Type
from app.agent.base import Agent
from app.agent.manus import ManusAgent
from app.config import settings
from app.llm import LLM
from app.prompt.manus import get_prompt
from app.tool.tool_collection import get_tools


class AgentFactory:
    AGENTS = {
        "Manus": ManusAgent,
    }

    @staticmethod
    def create_agent(agent_name: str = None) -> Agent:
        if agent_name is None:
            agent_name = settings.agent.agent_name

        if agent_name not in AgentFactory.AGENTS:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent_class = AgentFactory.AGENTS[agent_name]

        # [FIX] 在创建 LLM 实例时传入 LLM 的特定配置
        # Pass the specific LLM settings when creating the LLM instance
        llm = LLM(settings=settings.llm)

        tools = get_tools()
        prompt = get_prompt(tools)

        return agent_class(
            llm=llm,
            prompt=prompt,
            tools=tools,
            max_iterations=settings.agent.max_iterations,
        )
