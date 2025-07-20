# -*- coding: utf-8 -*-
import subprocess
from tools.base_tool import BaseTool
from config import AppConfig # Corrected: Import the AppConfig instance

class ShellTool(BaseTool):
    name = "shell"
    description = (
        "Executes a shell command on the local system. "
        "⚠️ WARNING: This tool executes commands directly on the host machine with NO SANDBOX. Use with extreme caution. "
        "All commands are executed within the agent's workspace directory."
    )

    def execute(self, command: str, **kwargs) -> str:
        """
        Executes a shell command.

        Args:
            command (str): The shell command to execute.

        Returns:
            str: The output of the command (both stdout and stderr).
        """
        if not command:
            return "Error: command cannot be empty."

        # Corrected: Use AppConfig.WORKSPACE_PATH
        workspace = AppConfig.WORKSPACE_PATH
        print(f"Executing shell command: `{command}` in `{workspace}`")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=workspace, # Corrected: Use the workspace variable
                timeout=60
            )

            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout.strip()}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr.strip()}\n"

            if not output:
                return f"Command '{command}' executed successfully with no output."

            return output.strip()

        except subprocess.TimeoutExpired:
            return f"Error: Command '{command}' timed out after 60 seconds."
        except Exception as e:
            return f"Error executing command '{command}': {e}"
