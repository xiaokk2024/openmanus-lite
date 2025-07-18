# 我们从文件顶部移除了 'from app.agent import ManusAgent'
from app.agent.base import BaseAgent
from app.llm import LLM
from app.config import AGENT_NAME, MAX_ITERATIONS


class AgentFactory:
    @staticmethod
    def create_agent(llm: LLM) -> BaseAgent:
        """
        根据配置创建并返回一个 Agent 实例。
        使用方法内部的局部导入来打破启动时的循环依赖。
        """
        # 将导入语句移动到方法内部
        from app.agent.manus import ManusAgent

        if AGENT_NAME == "ManusAgent":
            return ManusAgent(
                llm=llm,
                max_iterations=MAX_ITERATIONS,
            )
        else:
            raise ValueError(f"未知的 Agent 名称: {AGENT_NAME}")

