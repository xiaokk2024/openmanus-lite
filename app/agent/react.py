from typing import Dict, List

from app.exceptions import AgentError
from app.logger import logger
from app.tool.base import BaseTool
from app.tool.bash import BashTool
from app.tool.file_operators import ListFilesTool, ReadFileTool, WriteFileTool
from app.tool.python_execute import PythonExecuteTool
from app.tool.terminate import TerminateTool


class ToolCollection:
    """
    ToolCollection 类用于管理和执行工具。
    """

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            "bash": BashTool(),
            "list_files": ListFilesTool(),
            "read_file": ReadFileTool(),
            "write_file": WriteFileTool(),
            "python_execute": PythonExecuteTool(),
            "terminate": TerminateTool(),
        }

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        获取指定名称的工具。

        :param tool_name: 工具的名称。
        :return: 工具实例。
        """
        if tool_name not in self.tools:
            raise AgentError(f"未知工具: {tool_name}")
        return self.tools[tool_name]

    def get_tool_definitions(self) -> List[Dict]:
        """
        获取所有工具的定义。

        :return: 工具定义的列表。
        """
        return [tool.get_definition() for tool in self.tools.values()]

    def get_tool_descriptions(self) -> str:
        """
        获取所有工具的描述。

        :return: 工具描述的字符串。
        """
        return "\n".join([tool.get_description() for tool in self.tools.values()])

    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """
        异步执行指定的工具。

        :param tool_name: 要执行的工具的名称。
        :param kwargs: 工具的参数。
        :return: 工具执行的结果。
        """
        try:
            tool = self.get_tool(tool_name)
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"执行工具 '{tool_name}' 时发生未知错误: {e}", exc_info=True)
            return f"未知错误: {e}"
