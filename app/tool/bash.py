from app.sandbox.client import SandboxClient
from app.tool.base import BaseTool, ToolSchema

class BashTool(BaseTool):
    name: str = "bash"
    description: str = "在沙箱中执行给定的 shell 命令。"
    args_schema: ToolSchema = ToolSchema(
        type="object",
        properties={
            "command": ToolSchema(
                type="string",
                description="要在沙箱中执行的 shell 命令。",
            ),
        },
        required=["command"],
    )

    async def _execute(self, command: str) -> str:
        sandbox_client = await SandboxClient.get_instance()
        return await sandbox_client.run_command(command)
