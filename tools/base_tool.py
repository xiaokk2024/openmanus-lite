# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import inspect

class BaseTool(ABC):
    """
    The abstract base class for all tools.
    It enforces a common structure for all tools, including name, description,
    and an execute method.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool, used by the LLM to call it."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does, to help the LLM understand its use."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """The core logic of the tool."""
        pass

    def get_args_str(self) -> str:
        """
        Automatically inspects the `execute` method's signature to get its arguments string.
        For example, if execute(file_path: str, content: str), this returns "file_path, content".
        This helps in dynamically generating the tool list for the prompt.
        """
        try:
            sig = inspect.signature(self.execute)
            # Filter for positional or keyword arguments, excluding 'self', 'args', 'kwargs'
            params = [
                p.name for p in sig.parameters.values()
                if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and p.name != 'self'
            ]
            return ", ".join(params)
        except Exception:
            return "" # Return empty string if inspection fails

