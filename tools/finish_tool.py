# -*- coding: utf-8 -*-
from tools.base_tool import BaseTool

class FinishTool(BaseTool):
    name = "finish"
    description = "当您认为整个任务已完成时，调用此工具并提供最终摘要以结束流程。"

    def execute(self, summary: str, **kwargs) -> str:
        """
        标志着任务已完成。

        参数:
            summary (str): 对已完成任务的最终摘要或最终结果。

        返回:
            str: 确认任务已完成的消息。
        """
        if not summary:
            return "任务已完成，但未提供摘要。"
        return f"任务成功完成。最终摘要：{summary}"