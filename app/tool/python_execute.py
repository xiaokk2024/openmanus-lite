from pydantic import BaseModel, Field
from typing import Type
from app.tool.base import BaseTool
from app.sandbox.client import SandboxClient
from app.logger import get_logger

logger = get_logger(__name__)

class PythonExecuteArgs(BaseModel):
    code: str = Field(..., description="要在沙箱中执行的 Python 代码字符串。")

class PythonExecuteTool(BaseTool):
    name: str = "python_execute"
    description: str = "在沙箱环境中执行给定的 Python 代码，并返回其标准输出和错误。"
    args_schema: Type[BaseModel] = PythonExecuteArgs

    def run(self, code: str) -> str:
        if not code:
            return "错误：代码不能为空。"
        # 在方法内部获取客户端实例
        exit_code, output = SandboxClient().execute_python(code)
        return f"Python 代码执行完成。\n退出码: {exit_code}\n输出:\n---\n{output}\n---"