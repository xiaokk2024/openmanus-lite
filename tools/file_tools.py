# -*- coding: utf-8 -*-
import os
from tools.base_tool import BaseTool
from config import AppConfig # Corrected: Import the AppConfig instance

def _secure_join(base: str, path: str) -> str:
    """
    Joins the base path with a relative path, ensuring the result is still within the base directory.
    This prevents directory traversal attacks (e.g., path = '../...').
    """
    abs_path = os.path.normpath(os.path.join(base, path))
    if os.path.commonprefix([abs_path, os.path.realpath(base)]) != os.path.realpath(base):
        raise ValueError("Path traversal attempt detected.")
    return abs_path

class ListFilesTool(BaseTool):
    name = "list_files"
    description = "Lists all files and folders in the workspace directory."

    def execute(self, **kwargs) -> str:
        """Lists files in the workspace."""
        try:
            # Corrected: Use AppConfig.WORKSPACE_PATH
            files = os.listdir(AppConfig.WORKSPACE_PATH)
            if not files:
                return "The workspace is empty."
            return "Workspace file list:\n- " + "\n- ".join(files)
        except Exception as e:
            return f"Error listing files: {e}"

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads the content of a specified file from the workspace."

    def execute(self, file_path: str, **kwargs) -> str:
        """Reads the content of a file."""
        try:
            # Corrected: Use AppConfig.WORKSPACE_PATH
            secure_path = _secure_join(AppConfig.WORKSPACE_PATH, file_path)
            if not os.path.exists(secure_path):
                return f"Error: File '{file_path}' not found."
            with open(secure_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"Successfully read file '{file_path}':\n---\n{content}\n---"
        except ValueError as e:
            return f"Error: Invalid file path. {e}"
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes content to a specified file in the workspace. Overwrites the file if it already exists."

    def execute(self, file_path: str, content: str, **kwargs) -> str:
        """Writes content to a file."""
        try:
            # Corrected: Use AppConfig.WORKSPACE_PATH
            secure_path = _secure_join(AppConfig.WORKSPACE_PATH, file_path)
            with open(secure_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Content successfully written to file '{file_path}'."
        except ValueError as e:
            return f"Error: Invalid file path. {e}"
        except Exception as e:
            return f"Error writing to file '{file_path}': {e}"
