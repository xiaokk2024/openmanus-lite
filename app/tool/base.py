from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type, Dict, Any

class BaseTool(ABC):
    """工具的抽象基类"""
    name: str
    description: str
    args_schema: Type[BaseModel]

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """执行工具的核心逻辑"""
        pass

    def get_definition(self) -> Dict[str, Any]:
        """获取工具的 JSON Schema 定义，用于 LLM"""
        schema = self.args_schema.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            },
        }