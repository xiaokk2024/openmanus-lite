import inspect
import pkgutil
from typing import Dict, Type, List, Any
from app.tool.base import BaseTool
from app.logger import get_logger

logger = get_logger(__name__)

class ToolCollection:
    """
    一个集合类，用于自动发现和管理项目中的所有工具。
    """

    def __init__(self, tool_packages: List[str] = None):
        if tool_packages is None:
            tool_packages = ['app.tool']
        self.tools: Dict[str, BaseTool] = self._discover_tools(tool_packages)
        logger.info(f"已加载 {len(self.tools)} 个工具: {list(self.tools.keys())}")

    def _discover_tools(self, packages: List[str]) -> Dict[str, BaseTool]:
        """从指定的包中发现所有 BaseTool 的子类"""
        tools = {}
        for package_name in packages:
            package = __import__(package_name, fromlist=["*"])
            for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                try:
                    module = __import__(module_name, fromlist=["*"])
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj is not BaseTool:
                            instance = obj()
                            if instance.name in tools:
                                logger.warning(f"发现重复的工具名称 '{instance.name}'。旧的将被覆盖。")
                            tools[instance.name] = instance
                except Exception as e:
                    logger.error(f"加载模块 {module_name} 时发现错误: {e}")
        return tools

    def get_tool(self, name: str) -> BaseTool:
        """根据名称获取工具实例"""
        if name not in self.tools:
            raise KeyError(f"未找到工具: {name}")
        return self.tools[name]

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具的 JSON Schema 定义列表"""
        return [tool.get_definition() for tool in self.tools.values()]

    def run_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """执行指定的工具"""
        tool = self.get_tool(tool_name)
        return tool.run(**parameters)

# 全局工具集合实例
tool_collection = ToolCollection()