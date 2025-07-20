# -*- coding: utf-8 -*-
from tools.base_tool import BaseTool

class FinishTool(BaseTool):
    name = "finish"
    description = "Call this tool with a final summary when you believe the entire task is complete to end the process."

    def execute(self, summary: str, **kwargs) -> str:
        """
        Signals that the task is complete.

        Args:
            summary (str): A final summary of the completed task or the final result.

        Returns:
            str: A confirmation message that the task is finished.
        """
        if not summary:
            return "Task finished, but no summary was provided."
        return f"Task finished successfully. Final summary: {summary}"
