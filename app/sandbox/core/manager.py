import asyncio
from app.logger import logger
from app.sandbox.core.sandbox import Sandbox


class SandboxManager:
    """
    管理沙箱的生命周期。
    此类负责创建、获取和关闭沙箱实例。
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SandboxManager, cls).__new__(cls)
        return cls._instance

    def __init__(
            self,
            image: str,
            timeout: int,
            working_dir: str,
            memory_limit: str,
            cpu_limit: float,
            network_enabled: bool
    ):
        # 防止重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.image = image
        self.timeout = timeout
        self.working_dir = working_dir
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.network_enabled = network_enabled
        self.sandbox = None
        self._initialized = True
        logger.info("沙箱管理器已初始化。")

    async def get_sandbox(self) -> Sandbox:
        """获取一个正在运行的沙箱实例，如果不存在则创建一个。"""
        if self.sandbox is None:
            logger.info("未找到活动的沙箱，正在创建一个新的...")
            self.sandbox = Sandbox(
                image=self.image,
                timeout=self.timeout,
                working_dir=self.working_dir,
                memory_limit=self.memory_limit,
                cpu_limit=self.cpu_limit,
                network_enabled=self.network_enabled,
            )
            await self.sandbox.start()
        return self.sandbox

    async def close_sandbox(self):
        """关闭并清理活动的沙箱。"""
        if self.sandbox:
            await self.sandbox.close()
            self.sandbox = None

    # 为了简化，我们将所有沙箱操作代理到 get_sandbox() 获取的实例上
    async def run_command(self, command: str) -> str:
        sandbox = await self.get_sandbox()
        return await sandbox.run_command(command)

    async def run_python(self, code: str) -> str:
        sandbox = await self.get_sandbox()
        return await sandbox.run_python(code)

    async def write_file(self, path: str, content: str) -> str:
        sandbox = await self.get_sandbox()
        return await sandbox.write_file(path, content)

    async def read_file(self, path: str) -> str:
        sandbox = await self.get_sandbox()
        return await sandbox.read_file(path)

    async def list_files(self, path: str) -> str:
        sandbox = await self.get_sandbox()
        return await sandbox.list_files(path)

