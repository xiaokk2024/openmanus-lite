class AgentError(Exception):
    """Base exception for agent errors."""
    pass

# =================================================================
# [FIX] 添加 Terminate 异常类
# 这个异常类用于在任务完成或失败时，安全地终止代理的执行。
# The `terminate` tool raises this exception to signal that the agent's run should end.
# =================================================================
class Terminate(Exception):
    """
    Exception raised to terminate the agent's operation.
    This is used by the 'terminate' tool.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

