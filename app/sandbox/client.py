from app.sandbox.core.manager import SandboxManager
# 修正：直接从 app.config 导入所有需要的、大写的配置变量
from app.config import (
    SANDBOX_IMAGE,
    SANDBOX_TIMEOUT,
    SANDBOX_MEMORY_LIMIT,
    SANDBOX_CPU_LIMIT,
    SANDBOX_NETWORK_ENABLED,
    SANDBOX_WORKING_DIRECTORY,
)

# 使用导入的变量来初始化沙箱管理器
# 注意：manager 的参数名为 'working_dir'
sandbox_manager = SandboxManager(
    image=SANDBOX_IMAGE,
    timeout=SANDBOX_TIMEOUT,
    working_dir=SANDBOX_WORKING_DIRECTORY,
    memory_limit=SANDBOX_MEMORY_LIMIT,
    cpu_limit=SANDBOX_CPU_LIMIT,
    network_enabled=SANDBOX_NETWORK_ENABLED,
)


class SandboxClient:
    """
    一个用于与沙箱环境交互的客户端。
    此类为在隔离的沙箱中运行命令、管理文件和执行代码提供了高级 API。
    """
    async def run_command(self, command: str) -> str:
        """在沙箱中运行一个 shell 命令。"""
        return await sandbox_manager.run_command(command)

    async def run_python(self, code: str) -> str:
        """在沙箱中执行一个 Python 脚本。"""
        return await sandbox_manager.run_python(code)

    async def write_file(self, path: str, content: str) -> str:
        """向沙箱中的一个文件写入内容。"""
        return await sandbox_manager.write_file(path, content)

    async def read_file(self, path: str) -> str:
        """从沙箱中读取一个文件的内容。"""
        return await sandbox_manager.read_file(path)

    async def list_files(self, path: str) -> str:
        """列出沙箱中一个目录下的文件。"""
        return await sandbox_manager.list_files(path)


# 创建客户端的单例实例，供其他模块使用
sandbox_client = SandboxClient()
