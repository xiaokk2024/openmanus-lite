from app.agent.base import BaseAgent
from app.agent.manus import ManusAgent
from app.exceptions import AgentError

# Agent 名称到类的映射
AGENT_MAP = {
    "ManusAgent": ManusAgent,
    # 在这里可以添加其他 Agent
}

def create_agent(agent_name: str, **kwargs) -> BaseAgent:
    """
    根据给定的名称创建 Agent 实例。

    Args:
        agent_name: 要创建的 Agent 的名称。
        **kwargs: 传递给 Agent 构造函数的参数。

    Returns:
        一个 BaseAgent 的实例。

    Raises:
        AgentError: 如果找不到指定的 Agent。
    """
    if agent_name not in AGENT_MAP:
        raise AgentError(f"未知的 Agent: {agent_name}. 可用选项: {list(AGENT_MAP.keys())}")

    agent_class = AGENT_MAP[agent_name]
    return agent_class(**kwargs)