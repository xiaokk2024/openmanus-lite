from pydantic import BaseModel, Field
from typing import Type
from app.tool.base import BaseTool

class TerminateArgs(BaseModel):
    message: str = Field(..., description="任务完成的最终消息或答案。")

class TerminateTool(BaseTool):
    name: str = "terminate"
    description: str = "当任务完成或无法继续时，调用此工具以终止执行并返回最终答案。"
    args_schema: Type[BaseModel] = TerminateArgs

    def run(self, message: str) -> str:
        # 这个工具的特殊之处在于它的调用会由 Agent 逻辑捕获并停止循环
        return message