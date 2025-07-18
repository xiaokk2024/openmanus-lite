from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Type
from pydantic import create_model, BaseModel, Field
from app.schema import ToolSchema


class BaseTool(ABC):
    """
    所有工具的抽象基类。

    它定义了工具的基本结构和契约：
    1. 必须有 name 和 description。
    2. 必须通过 get_args_schema() 定义其参数。
    3. 必须在 _execute() 中实现其核心逻辑。
    """
    name: str = ""
    description: str = ""

    @abstractmethod
    def get_args_schema(self) -> Dict[str, Tuple[Type, Any]]:
        """
        【契约】子类必须实现此方法来定义其参数。
        返回一个字典，用于 Pydantic 模型的动态创建。
        示例: {"path": (str, Field(..., description="文件路径"))}
        """
        ...

    @abstractmethod
    async def _execute(self, **kwargs):
        """
        【契约】子类必须实现此方法来包含工具的核心执行逻辑。
        """
        ...

    def get_schema(self) -> Dict[str, Any]:
        """
        根据 get_args_schema() 的定义，生成一个 JSON 兼容的 schema，用于向 LLM 展示。
        """
        pydantic_fields = self.get_args_schema()
        # 动态创建一个 Pydantic 模型以生成 schema
        temp_model = create_model(f'{self.name}Args', **pydantic_fields)
        model_schema = temp_model.schema()

        schema = ToolSchema(
            name=self.name,
            description=self.description,
            properties=model_schema.get("properties", {}),
            required=model_schema.get("required", [])
        )
        return schema.dict()

    async def __call__(self, **kwargs):
        """
        这是一个公共方法，用于验证参数并执行工具。
        它首先验证传入的参数是否符合 schema，然后调用 _execute 方法。
        """
        pydantic_fields = self.get_args_schema()
        args_model = create_model(f'{self.name}ArgsValidator', **pydantic_fields)

        try:
            # 验证参数
            validated_args = args_model(**kwargs)
            # 调用核心逻辑
            return await self._execute(**validated_args.dict())
        except Exception as e:
            # 重新抛出异常，以便上层可以捕获
            raise e
