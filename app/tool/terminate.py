from pydantic import Field
from app.tool.base import BaseTool


class TerminateTool(BaseTool):
    name = "terminate"
    description = "当你认为任务已成功完成或无法继续时，调用此工具以终止任务。"

    def get_args_schema(self) -> dict:
        return {
            "message": (str, Field(..., description="任务终止的原因或成功信息。"))
        }

    async def _execute(self, message: str, **kwargs):
        from app.exceptions import Terminate
        raise Terminate(message)
