# -*- coding: utf-8 -*-
import io
import contextlib
from tools.base_tool import BaseTool

class PythonTool(BaseTool):
    name = "python"
    description = (
        "Executes a snippet of Python code and returns its output. "
        "⚠️ WARNING: This tool executes code directly in the current process with NO SANDBOX. Use with extreme caution. "
        "You can use `print()` to output results. The code does not have access to external variables but can import standard libraries."
    )

    def execute(self, code: str, **kwargs) -> str:
        """
        Executes a string of Python code.

        Args:
            code (str): The Python code to execute.

        Returns:
            str: The captured stdout and stderr from the code execution.
        """
        if not code:
            return "Error: code cannot be empty."

        print(f"Executing python code:\n---\n{code}\n---")

        # Create a string stream to capture stdout and stderr
        output_stream = io.StringIO()

        try:
            # Use contextlib.redirect_stdout and redirect_stderr to capture all output
            with contextlib.redirect_stdout(output_stream), contextlib.redirect_stderr(output_stream):
                # Use exec to execute the code.
                # Provide empty globals and locals dicts to create a somewhat isolated scope,
                # though it's not a true sandbox.
                exec(code, {}, {})

            output = output_stream.getvalue()
            if not output:
                return "Code executed successfully with no output."
            return f"Code execution output:\n{output.strip()}"

        except Exception as e:
            # Also capture any output that occurred before the exception
            return f"An error occurred during code execution: {e}\nCaptured output:\n{output_stream.getvalue().strip()}"
