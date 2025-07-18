from pydantic import Field
from app.tool.base import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "读取沙箱中指定路径的文件内容。"

    def get_args_schema(self) -> dict:
        return {
            "path": (str, Field(..., description="要读取的文件的路径。"))
        }

    async def _execute(self, path: str, **kwargs):
        from app.sandbox.client import sandbox_client
        return await sandbox_client.read_file(path)


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "向沙箱中指定路径的文件写入内容。如果文件不存在，则会创建它；如果文件已存在，则会覆盖它。"

    def get_args_schema(self) -> dict:
        return {
            "path": (str, Field(..., description="要写入的文件的路径。")),
            "content": (str, Field(..., description="要写入文件的内容。"))
        }

    async def _execute(self, path: str, content: str, **kwargs):
        from app.sandbox.client import sandbox_client
        return await sandbox_client.write_file(path, content)


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "列出沙箱中指定目录下的所有文件和子目录。"

    def get_args_schema(self) -> dict:
        return {
            "path": (str, Field(..., description="要列出其内容的目录的路径。"))
        }

    async def _execute(self, path: str, **kwargs):
        from app.sandbox.client import sandbox_client
        return await sandbox_client.list_files(path)
