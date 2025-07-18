from pydantic import BaseModel, Field
from typing import Type
from app.tool.base import BaseTool
from app.sandbox.client import SandboxClient
from app.logger import get_logger

logger = get_logger(__name__)

class BashArgs(BaseModel):
    command: str = Field(..., description="要在沙箱中执行的 shell 命令")

class BashTool(BaseTool):
    name: str = "bash"
    description: str = "在沙箱环境中执行给定的 shell 命令，并返回其标准输出和错误。"
    args_schema: Type[BaseModel] = BashArgs

    def run(self, command: str) -> str:
        if not command:
            return "错误：命令不能为空。"
        # 在方法内部获取客户端实例
        exit_code, output = SandboxClient().execute_command(command)
        return f"命令 '{command}' 执行完成。\n退出码: {exit_code}\n输出:\n---\n{output}\n---"