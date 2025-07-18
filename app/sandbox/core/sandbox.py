import os
import subprocess
import logging

# [FIX] 导入全局的 settings 对象，而不是 SandboxSettings 类
# Import the global settings object, not the SandboxSettings class
from app.config import settings

logger = logging.getLogger(__name__)

class Sandbox:
    """
    A sandboxed environment for executing code and commands.
    """
    def __init__(self):
        """
        Initializes the sandbox, creating the workspace directory if it doesn't exist.
        """
        # [FIX] 从全局 settings 对象中获取沙箱的工作目录
        # Get the sandbox working directory from the global settings object
        self.workspace_dir = settings.sandbox.workspace_dir
        if not os.path.exists(self.workspace_dir):
            logger.info(f"Creating workspace directory at: {self.workspace_dir}")
            os.makedirs(self.workspace_dir)

    async def run_command(self, command: str) -> str:
        """
        Runs a shell command in the sandbox's workspace directory.
        """
        logger.info(f"Executing command: {command}")
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
                check=True,
                timeout=30
            )
            output = f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        except subprocess.CalledProcessError as e:
            output = f"Error executing command: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except subprocess.TimeoutExpired as e:
            output = f"Command timed out: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except Exception as e:
            output = f"An unexpected error occurred: {e}"

        logger.info(f"Command output:\n{output}")
        return output

    async def read_file(self, path: str) -> str:
        """
        Reads the content of a file within the sandbox.
        """
        full_path = os.path.join(self.workspace_dir, path)
        logger.info(f"Reading file: {full_path}")
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found at '{path}'"
        except Exception as e:
            return f"Error reading file: {e}"

    async def write_file(self, path: str, content: str):
        """
        Writes content to a file within the sandbox.
        """
        full_path = os.path.join(self.workspace_dir, path)
        logger.info(f"Writing to file: {full_path}")
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Error writing file: {e}")

    async def list_files(self, path: str) -> str:
        """
        Lists all files and directories at a given path within the sandbox.
        """
        full_path = os.path.join(self.workspace_dir, path)
        logger.info(f"Listing files in: {full_path}")
        try:
            if not os.path.isdir(full_path):
                return f"Error: '{path}' is not a valid directory."
            files = os.listdir(full_path)
            return "\n".join(files)
        except FileNotFoundError:
            return f"Error: Directory not found at '{path}'"
        except Exception as e:
            return f"Error listing files: {e}"

