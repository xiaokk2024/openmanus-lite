import json
from typing import Dict, List
from app.schema import ToolSchema
# 修正：直接导入已经配置好的 logger 实例，而不是一个不存在的 get_logger 函数
from app.logger import logger
from app.tool.base import BaseTool


class ToolCollection:
    """
    一个管理和执行工具集合的类。
    """
    def __init__(self, tools: List[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}

    def get_tool_schemas(self) -> str:
        """
        获取所有工具的 schema 描述，并格式化为 JSON 字符串。
        """
        schemas = [tool.get_schema() for tool in self.tools.values()]
        return json.dumps(schemas, indent=4, ensure_ascii=False)

    async def run_tool(self, tool_name: str, parameters: Dict) -> str:
        """
        根据名称和参数运行指定的工具。

        :param tool_name: 要运行的工具的名称。
        :param parameters: 传递给工具的参数。
        :return: 工具执行后的观察结果。
        """
        if tool_name not in self.tools:
            return f"错误: 未找到名为 '{tool_name}' 的工具。"
        try:
            tool = self.tools[tool_name]
            # 使用 **parameters 将字典解包为关键字参数
            observation = await tool(**parameters)
            return observation
        except Exception as e:
            logger.error(f"执行工具 '{tool_name}' 时出错: {e}", exc_info=True)
            return f"错误: 执行工具 '{tool_name}' 时发生异常: {e}"
