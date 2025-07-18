from app.sandbox.client import SandboxClient
from app.tool.base import BaseTool, ToolSchema

class PythonExecuteTool(BaseTool):
    name: str = "python_execute"
    description: str = "在沙箱中执行给定的 Python 代码。"
    args_schema: ToolSchema = ToolSchema(
        type="object",
        properties={
            "code": ToolSchema(
                type="string",
                description="要在沙箱中执行的 Python 代码。",
            ),
        },
        required=["code"],
    )

    async def _execute(self, code: str) -> str:
        sandbox_client = await SandboxClient.get_instance()
        # 将代码写入临时文件以执行
        script_path = "temp_script.py"
        await sandbox_client.write_file(script_path, code)
        # 执行脚本并返回输出
        return await sandbox_client.run_command(f"python {script_path}")
