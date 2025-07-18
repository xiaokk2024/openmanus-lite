from pydantic import Field
from app.tool.base import BaseTool


class BashTool(BaseTool):
    name = "bash"
    description = "在沙箱中执行 shell 命令，并返回其标准输出和标准错误。"

    def get_args_schema(self) -> dict:
        return {
            "command": (str, Field(..., description="要在沙箱中执行的 shell 命令。"))
        }

    async def _execute(self, command: str, **kwargs):
        """
        实现了工具的核心逻辑。
        """
        from app.sandbox.client import sandbox_client
        return await sandbox_client.run_command(command)
