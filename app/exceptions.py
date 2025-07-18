# app/exceptions.py

class BaseError(Exception):
    """所有自定义异常的基类。"""
    pass


class AgentError(BaseError):
    """与 Agent 相关的错误。"""
    pass


class LLMError(BaseError):
    """与大语言模型 API 调用相关的错误。"""
    pass


class SandboxError(BaseError):
    """与沙箱执行相关的错误。"""
    pass

class SandboxTimeoutError(SandboxError):
    """沙箱命令执行超时错误。"""
    pass

