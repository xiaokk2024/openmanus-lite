# -*- coding: utf-8 -*-
import os
from tools.base_tool import BaseTool
from config import AppConfig # 已修正：导入 AppConfig 实例

def _secure_join(base: str, path: str) -> str:
    """
    将基础路径与相对路径连接起来，确保结果仍在基础目录内。
    这可以防止目录遍历攻击（例如，path = '../...'）。
    """
    abs_path = os.path.normpath(os.path.join(base, path))
    if os.path.commonprefix([abs_path, os.path.realpath(base)]) != os.path.realpath(base):
        raise ValueError("检测到路径遍历攻击。")
    return abs_path

class ListFilesTool(BaseTool):
    name = "list_files"
    description = "列出工作区目录中的所有文件和文件夹。"

    def execute(self, **kwargs) -> str:
        """列出工作区中的文件。"""
        try:
            # 已修正：使用 AppConfig.WORKSPACE_PATH
            files = os.listdir(AppConfig.WORKSPACE_PATH)
            if not files:
                return "工作区是空的。"
            return "工作区文件列表:\n- " + "\n- ".join(files)
        except Exception as e:
            return f"列出文件时出错：{e}"

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "从工作区读取指定文件的内容。"

    def execute(self, file_path: str, **kwargs) -> str:
        """读取文件的内容。"""
        try:
            # 已修正：使用 AppConfig.WORKSPACE_PATH
            secure_path = _secure_join(AppConfig.WORKSPACE_PATH, file_path)
            if not os.path.exists(secure_path):
                return f"错误：文件 '{file_path}' 未找到。"
            with open(secure_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"成功读取文件 '{file_path}':\n---\n{content}\n---"
        except ValueError as e:
            return f"错误：无效的文件路径。{e}"
        except Exception as e:
            return f"读取文件 '{file_path}' 时出错：{e}"

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "将内容写入工作区中的指定文件。如果文件已存在，则会覆盖它。"

    def execute(self, file_path: str, content: str, **kwargs) -> str:
        """将内容写入文件。"""
        try:
            # 已修正：使用 AppConfig.WORKSPACE_PATH
            secure_path = _secure_join(AppConfig.WORKSPACE_PATH, file_path)
            with open(secure_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"内容已成功写入文件 '{file_path}'。"
        except ValueError as e:
            return f"错误：无效的文件路径。{e}"
        except Exception as e:
            return f"写入文件 '{file_path}' 时出错：{e}"
