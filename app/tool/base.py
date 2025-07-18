from abc import ABC, abstractmethod
from typing import Any, Dict

# 修正了 pydantic 的导入路径，以避免循环导入错误
from pydantic.main import create_model

from app.schema import ToolSchema


class BaseTool(ABC):
    """
    所有工具的基类。
    """

    name: str
    description: str
    args_schema: ToolSchema

    def get_definition(self) -> Dict[str, Any]:
        """
        获取工具的定义。

        :return: 工具定义的字典。
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_dump(),
            },
        }

    def get_description(self) -> str:
        """
        获取工具的描述。

        :return: 工具描述的字符串。
        """
        return f"- {self.name}: {self.description} 输入参数: {list(self.args_schema.properties.keys())}"

    async def execute(self, **kwargs) -> str:
        """
        异步执行工具。

        :param kwargs: 工具的参数。
        :return: 工具执行的结果。
        """
        # 验证参数
        validated_args = self._validate_args(kwargs)
        return await self._execute(**validated_args)

    def _validate_args(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证工具的参数。

        :param kwargs: 工具的参数。
        :return: 验证后的参数。
        """
        # 从 schema 创建 Pydantic 模型
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
        }

        fields = {
            name: (type_mapping.get(details.get("type", "string"), str), ...)
            for name, details in self.args_schema.properties.items()
        }
        ArgsModel = create_model(f"{self.name}Args", **fields)

        # 验证参数
        validated_model = ArgsModel(**kwargs)
        return validated_model.model_dump()

    @abstractmethod
    async def _execute(self, **kwargs) -> str:
        """
        工具的具体实现。

        :param kwargs: 工具的参数。
        :return: 工具执行的结果。
        """
        pass
