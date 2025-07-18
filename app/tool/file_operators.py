from pydantic import BaseModel, Field
from typing import Type
from app.tool.base import BaseTool
from app.sandbox.client import SandboxClient
from app.exceptions import ToolError

class WriteFileArgs(BaseModel):
    path: str = Field(..., description="要写入的文件的相对路径（相对于工作区）。")
    content: str = Field(..., description="要写入文件的内容。")

class ReadFileArgs(BaseModel):
    path: str = Field(..., description="要读取的文件的相对路径。")

class ListFilesArgs(BaseModel):
    path: str = Field(default=".", description="要列出其内容的目录的相对路径。")

class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "将内容写入到沙箱工作区内的指定文件中。如果文件已存在，则会覆盖。"
    args_schema: Type[BaseModel] = WriteFileArgs

    def run(self, path: str, content: str) -> str:
        # 使用 echo 和重定向来写入文件，这比 put_archive 更可靠
        escaped_content = content.replace("\\", "\\\\").replace("'", "\\'")
        command = f"echo '{escaped_content}' > {path}"
        exit_code, output = SandboxClient().execute_command(command)
        if exit_code == 0:
            return f"文件已成功写入到沙箱中的: {path}"
        raise ToolError(f"写入文件 '{path}' 失败: {output}")

class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "读取沙箱工作区内指定文件的内容。"
    args_schema: Type[BaseModel] = ReadFileArgs

    def run(self, path: str) -> str:
        command = f"cat {path}"
        exit_code, output = SandboxClient().execute_command(command)
        if exit_code == 0:
            return output
        raise ToolError(f"从沙箱读取文件 '{path}' 失败: {output}")

class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "列出沙箱工作区内指定目录的文件和子目录。"
    args_schema: Type[BaseModel] = ListFilesArgs

    def run(self, path: str) -> str:
        # 'ls -F' 会在目录后附加 '/', 方便区分
        command = f"ls -F {path}"
        exit_code, output = SandboxClient().execute_command(command)
        if exit_code == 0:
            return output if output.strip() else "目录为空。"
        raise ToolError(f"执行 list_files 命令失败: {output}")