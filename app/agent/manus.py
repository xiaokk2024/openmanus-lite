from app.agent.react import ReActAgent
# 修正：将导入的变量名从 SYSTEM_PROMPT 改为 MANUS_PROMPT
from app.prompt.manus import MANUS_PROMPT


class ManusAgent(ReActAgent):
    """
    ManusAgent 是一个具体的 Agent 实现，它使用 ReAct 框架来完成任务。
    """
    def get_prompt(self, task: str) -> str:
        """
        构建并返回一个包含了任务描述和可用工具的系统提示词。

        :param task: 需要 Agent 完成的具体任务。
        :return: 格式化后的系统提示词字符串。
        """
        tool_schemas = self.tool_collection.get_tool_schemas()
        # 修正：使用正确的变量名 MANUS_PROMPT
        return MANUS_PROMPT.format(
            task=task,
            tool_schemas=tool_schemas
        )
