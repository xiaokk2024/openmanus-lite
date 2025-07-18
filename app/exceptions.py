class AgentError(Exception):
    """当 Agent 执行出错时引发"""
    pass

class ToolError(Exception):
    """当工具执行出错时引发"""
    pass

class SandboxError(Exception):
    """当沙箱操作出错时引发"""
    pass

class SandboxTimeoutError(SandboxError):
    """当沙箱操作超时时引发"""
    pass