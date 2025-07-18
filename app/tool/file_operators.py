from app.sandbox.client import SandboxClient
from app.tool.base import BaseTool, ToolSchema


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "列出指定路径下的文件和目录。"
    args_schema: ToolSchema = ToolSchema(
        type="object",
        properties={
            "path": ToolSchema(
                type="string",
                description="要列出内容的目录路径。",
            ),
        },
        required=["path"],
    )

    async def _execute(self, path: str) -> str:
        sandbox_client = await SandboxClient.get_instance()
        return await sandbox_client.run_command(f"ls -F {path}")


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "读取指定文件的内容。"
    args_schema: ToolSchema = ToolSchema(
        type="object",
        properties={
            "path": ToolSchema(
                type="string",
                description="要读取内容的文件路径。",
            ),
        },
        required=["path"],
    )

    async def _execute(self, path: str) -> str:
        sandbox_client = await SandboxClient.get_instance()
        try:
            return await sandbox_client.read_file(path)
        except FileNotFoundError as e:
            return f"错误: {e}"
        except Exception as e:
            return f"读取文件时发生未知错误: {e}"


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "将内容写入到指定文件。"
    args_schema: ToolSchema = ToolSchema(
        type="object",
        properties={
            "path": ToolSchema(
                type="string",
                description="要写入内容的文件路径。",
            ),
            "content": ToolSchema(
                type="string",
                description="要写入文件的内容。",
            ),
        },
        required=["path", "content"],
    )

    async def _execute(self, path: str, content: str) -> str:
        sandbox_client = await SandboxClient.get_instance()
        try:
            await sandbox_client.write_file(path, content)
            return f"文件 '{path}' 已成功写入。"
        except Exception as e:
            return f"写入文件时发生错误: {e}"
