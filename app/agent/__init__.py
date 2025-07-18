from app.agent.base import BaseAgent

# 下面这行代码是导致循环导入的根源，我们将其移除。
# Agent 的具体实现（如 ManusAgent）应该由 AgentFactory 在需要时动态导入，
# 而不应该在包的初始化阶段就被加载。
# from app.agent.manus import ManusAgent
