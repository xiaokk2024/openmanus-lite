from app.agent.react import ReActAgent
from app.prompt.manus import SYSTEM_PROMPT

class ManusAgent(ReActAgent):
    """
    ManusAgent 是一个通用的自主代理，使用 ReAct 框架来完成各种任务。
    """
    def __init__(self, **kwargs):
        super().__init__(system_prompt=SYSTEM_PROMPT, **kwargs)