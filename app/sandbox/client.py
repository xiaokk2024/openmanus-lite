from typing import Tuple, Optional
from app.sandbox.core.manager import get_sandbox, close_sandbox as close_global_sandbox
from app.logger import get_logger

logger = get_logger(__name__)

class SandboxClient:
    _instance: Optional['SandboxClient'] = None

    # 使用单例模式确保全局只有一个客户端实例
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SandboxClient, cls).__new__(cls)
            # 不要在这里初始化 sandbox，实现延迟加载
            cls._instance.sandbox = None
        return cls._instance

    def _ensure_sandbox(self):
        """如果沙箱未运行，则初始化它。"""
        if self.sandbox is None:
            logger.info("沙箱实例不存在，正在创建新的沙箱...")
            self.sandbox = get_sandbox()

    def execute_command(self, command: str) -> Tuple[int, str]:
        """执行 shell 命令。"""
        self._ensure_sandbox()
        return self.sandbox.execute(command)

    def execute_python(self, code: str) -> Tuple[int, str]:
        """执行 Python 代码。"""
        self._ensure_sandbox()
        # 使用 echo 和管道将代码安全地传递给 python 解释器
        escaped_code = code.replace("\\", "\\\\").replace("'", "\\'")
        command = f"echo '{escaped_code}' | python3"
        return self.execute_command(command)

    def close(self):
        """关闭沙箱并重置单例状态。"""
        logger.info("请求关闭沙箱...")
        close_global_sandbox()
        if SandboxClient._instance:
            SandboxClient._instance.sandbox = None