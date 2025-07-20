# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import inspect

class BaseTool(ABC):
    """
    所有工具的抽象基类。
    它为所有工具强制执行一个通用结构，包括名称、描述和一个 execute 方法。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """工具的名称，LLM 使用它来调用工具。"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """关于工具功能的详细描述，以帮助 LLM 理解其用途。"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """工具的核心逻辑。"""
        pass

    def get_args_str(self) -> str:
        """
        自动检查 `execute` 方法的签名以获取其参数字符串。
        例如，如果 execute(file_path: str, content: str)，此方法将返回 "file_path, content"。
        这有助于为提示动态生成工具列表。
        """
        try:
            sig = inspect.signature(self.execute)
            # 筛选出位置或关键字参数，不包括 'self'、'args'、'kwargs'
            params = [
                p.name for p in sig.parameters.values()
                if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and p.name != 'self'
            ]
            return ", ".join(params)
        except Exception:
            return "" # 如果检查失败，则返回空字符串
