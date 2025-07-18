import asyncio
from typing import Optional

from app.config import get_config
from app.exceptions import SandboxError
from app.logger import logger
from app.sandbox.core.sandbox import DockerSandbox


class SandboxClient:
    _instance: Optional['SandboxClient'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._sandbox: Optional[DockerSandbox] = None
            self._initialized = True

    @classmethod
    async def get_instance(cls) -> 'SandboxClient':
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
                await cls._instance._initialize_sandbox()
        return cls._instance

    async def _initialize_sandbox(self):
        if self._sandbox is None:
            logger.info("沙箱实例不存在，正在创建新的沙箱...")
            config = get_config()
            try:
                self._sandbox = DockerSandbox(config=config.sandbox)
                await self._sandbox.create()
            except Exception as e:
                logger.error(f"创建沙箱实例时出错: {e}", exc_info=True)
                self._sandbox = None
                raise SandboxError(f"创建沙箱实例时出错: {e}") from e

    async def run_command(self, command: str) -> str:
        if not self._sandbox:
            raise SandboxError("沙箱未初始化。")
        try:
            exit_code, output = await self._sandbox.run_command(command)
            if exit_code == 0:
                return output
            else:
                return f"命令执行失败，退出码: {exit_code}\n输出:\n{output}"
        except Exception as e:
            logger.error(f"执行沙箱命令时发生未知错误: {e}", exc_info=True)
            return f"执行沙箱命令时发生未知错误: {e}"

    async def write_file(self, path: str, content: str) -> None:
        if not self._sandbox:
            raise SandboxError("沙箱未初始化。")
        await self._sandbox.write_file(path, content)

    async def read_file(self, path: str) -> str:
        if not self._sandbox:
            raise SandboxError("沙箱未初始化。")
        return await self._sandbox.read_file(path)

    async def close(self):
        async with self._lock:
            if self._sandbox:
                logger.info("请求关闭沙箱...")
                await self._sandbox.cleanup()
                self._sandbox = None
            SandboxClient._instance = None
