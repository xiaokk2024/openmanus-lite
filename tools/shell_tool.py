# -*- coding: utf-8 -*-
import subprocess
from tools.base_tool import BaseTool
from config import AppConfig

class ShellTool(BaseTool):
    name = "shell"
    description = (
        "在本地系统上执行 shell 命令。"
        "⚠️ 警告：此工具直接在主机上执行命令，没有沙箱环境。请极其谨慎使用。"
        "所有命令都在代理的工作区目录中执行。"
    )

    def execute(self, command: str, **kwargs) -> str:
        """
        执行 shell 命令。

        参数:
            command (str): 要执行的 shell 命令。

        返回:
            str: 命令的输出（包括 stdout 和 stderr）。
        """
        if not command:
            return "错误：命令不能为空。"

        workspace = AppConfig.WORKSPACE_PATH
        print(f"正在执行 shell 命令: `{command}` (在 `{workspace}` 中)")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=workspace, # 已修正：使用 workspace 变量
                timeout=60
            )

            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout.strip()}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr.strip()}\n"

            if not output:
                return f"命令 '{command}' 成功执行，没有输出。"

            return output.strip()

        except subprocess.TimeoutExpired:
            return f"错误：命令 '{command}' 在 60 秒后超时。"
        except Exception as e:
            return f"执行命令 '{command}' 时出错：{e}"
