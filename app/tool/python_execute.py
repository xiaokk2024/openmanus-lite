from pydantic import Field
from app.tool.base import BaseTool


class PythonExecuteTool(BaseTool):
    name = "python_execute"
    description = "在沙箱中执行 Python 代码。代码必须是一个可以独立运行的脚本。"

    def get_args_schema(self) -> dict:
        return {
            "code": (str, Field(..., description="要在沙箱中执行的 Python 代码。"))
        }

    async def _execute(self, code: str, **kwargs):
        from app.sandbox.client import sandbox_client
        return await sandbox_client.run_python(code)
