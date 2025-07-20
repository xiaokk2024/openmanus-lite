# -*- coding: utf-8 -*-
import io
import contextlib
from tools.base_tool import BaseTool

class PythonTool(BaseTool):
    name = "python"
    description = (
        "执行一段 Python 代码并返回其输出。"
        "⚠️ 警告：此工具在当前进程中直接执行代码，没有沙箱环境。请极其谨慎使用。"
        "您可以使用 `print()` 来输出结果。代码无法访问外部变量，但可以导入标准库。"
    )

    def execute(self, code: str, **kwargs) -> str:
        """
        执行一个 Python 代码字符串。

        参数:
            code (str): 要执行的 Python 代码。

        返回:
            str: 从代码执行中捕获的标准输出和标准错误。
        """
        if not code:
            return "错误：代码不能为空。"

        print(f"正在执行 python 代码:\n---\n{code}\n---")

        # 创建一个字符串流来捕获 stdout 和 stderr
        output_stream = io.StringIO()

        try:
            # 使用 contextlib.redirect_stdout 和 redirect_stderr 来捕获所有输出
            with contextlib.redirect_stdout(output_stream), contextlib.redirect_stderr(output_stream):
                # 使用 exec 来执行代码。
                # 提供空的 globals 和 locals 字典来创建一个某种程度上隔离的作用域，
                # 尽管它不是一个真正的沙箱。
                exec(code, {}, {})

            output = output_stream.getvalue()
            if not output:
                return "代码成功执行，没有输出。"
            return f"代码执行输出:\n{output.strip()}"

        except Exception as e:
            # 同时捕获异常发生前产生的任何输出
            return f"代码执行期间发生错误: {e}\n捕获的输出:\n{output_stream.getvalue().strip()}"
