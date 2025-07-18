import asyncio
import io
import os
import tarfile
import tempfile
import uuid
from typing import Dict, Optional

import docker
from docker.errors import NotFound, APIError
from docker.models.containers import Container

from app.config import SandboxSettings
from app.exceptions import SandboxTimeoutError
from app.logger import logger
from app.sandbox.core.terminal import AsyncDockerizedTerminal


class DockerSandbox:
    """
    提供一个带资源限制、文件操作和命令执行能力的容器化执行环境。
    """

    def __init__(
            self,
            config: SandboxSettings,
            volume_bindings: Optional[Dict[str, str]] = None,
    ):
        self.config = config
        self.volume_bindings = volume_bindings or {}
        try:
            self.client = docker.from_env()
            self.api_client = docker.APIClient()
        except docker.errors.DockerException as e:
            logger.error(f"无法连接到 Docker。请确保 Docker 正在运行: {e}")
            raise RuntimeError(f"无法连接到 Docker。请确保 Docker 正在运行: {e}")

        self.container: Optional[Container] = None
        self.terminal: Optional[AsyncDockerizedTerminal] = None
        self._host_work_dir: Optional[str] = None

    async def create(self) -> "DockerSandbox":
        """创建并启动沙箱容器。"""
        try:
            # 准备容器配置
            self._host_work_dir = self._ensure_host_dir(self.config.working_directory)

            host_config = self.api_client.create_host_config(
                mem_limit=self.config.memory_limit,
                cpu_period=100000,
                cpu_quota=int(100000 * self.config.cpu_limit),
                network_mode="none" if not self.config.network_enabled else "bridge",
                binds={self._host_work_dir: {"bind": self.config.working_directory, "mode": "rw"}},
            )

            container_name = f"openmanus-sandbox_{uuid.uuid4().hex[:8]}"
            logger.info(f"正在创建容器 '{container_name}' 使用镜像 '{self.config.image}'...")

            # 创建容器
            container_info = await asyncio.to_thread(
                self.api_client.create_container,
                image=self.config.image,
                command="tail -f /dev/null",
                hostname="sandbox",
                working_dir=self.config.working_directory,
                host_config=host_config,
                name=container_name,
                tty=True,
                detach=True,
            )

            self.container = self.client.containers.get(container_info["Id"])
            await asyncio.to_thread(self.container.start)
            logger.info(f"容器 '{self.container.name}' 已启动。")

            self.terminal = AsyncDockerizedTerminal(
                container_info["Id"],
                self.config.working_directory,
                env_vars={"PYTHONUNBUFFERED": "1"}
            )
            await self.terminal.init()
            return self

        except APIError as e:
            logger.error(f"创建沙箱时发生 Docker API 错误: {e}")
            await self.cleanup()
            raise RuntimeError(f"创建沙箱失败: {e}") from e
        except Exception as e:
            logger.error(f"创建沙箱时发生未知错误: {e}", exc_info=True)
            await self.cleanup()
            raise RuntimeError(f"创建沙箱失败: {e}") from e

    @staticmethod
    def _ensure_host_dir(path: str) -> str:
        """确保主机上的目录存在。"""
        # 使用项目根目录下的 workspace 文件夹，而不是临时目录
        host_path = os.path.abspath(f"workspace_{os.urandom(4).hex()}")
        os.makedirs(host_path, exist_ok=True)
        logger.info(f"主机工作目录已映射: {host_path} -> {path}")
        return host_path

    async def run_command(self, cmd: str, timeout: Optional[int] = None) -> tuple[int, str]:
        """在沙箱中运行命令。"""
        if not self.terminal:
            raise RuntimeError("沙箱未初始化")
        try:
            timeout = timeout or self.config.timeout
            return await self.terminal.run_command(cmd, timeout=timeout)
        except asyncio.TimeoutError:
            raise SandboxTimeoutError(f"命令执行在 {timeout} 秒后超时")

    async def write_file(self, path: str, content: str) -> None:
        """将内容写入容器中的文件。"""
        if not self.container:
            raise RuntimeError("沙箱未初始化")

        resolved_path = os.path.join(self.config.working_directory, path)
        parent_dir = os.path.dirname(resolved_path)

        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=os.path.basename(path))
            content_bytes = content.encode('utf-8')
            tarinfo.size = len(content_bytes)
            tar.addfile(tarinfo, io.BytesIO(content_bytes))
        tar_stream.seek(0)

        await asyncio.to_thread(self.container.put_archive, parent_dir, tar_stream)

    async def read_file(self, path: str) -> str:
        """从容器中读取文件。"""
        if not self.container:
            raise RuntimeError("沙箱未初始化")

        resolved_path = os.path.join(self.config.working_directory, path)
        try:
            stream, _ = await asyncio.to_thread(self.container.get_archive, resolved_path)

            with tempfile.NamedTemporaryFile() as tmp:
                for chunk in stream:
                    tmp.write(chunk)
                tmp.seek(0)
                with tarfile.open(fileobj=tmp) as tar:
                    member = tar.next()
                    if not member:
                        raise FileNotFoundError(f"归档为空: {path}")
                    file_content = tar.extractfile(member)
                    if not file_content:
                        raise RuntimeError("无法从归档中提取文件")
                    return file_content.read().decode('utf-8')

        except NotFound:
            raise FileNotFoundError(f"文件未找到: {path}")

    async def cleanup(self) -> None:
        """清理沙箱资源。"""
        if self.terminal:
            await self.terminal.close()
        if self.container:
            logger.info(f"正在停止并移除容器 '{self.container.name}'...")
            try:
                await asyncio.to_thread(self.container.stop, timeout=5)
                await asyncio.to_thread(self.container.remove, force=True)
                logger.info("容器已清理。")
            except Exception as e:
                logger.warning(f"清理容器时出错: {e}")
        # 清理主机上的工作目录
        # if self._host_work_dir and os.path.exists(self._host_work_dir):
        #     shutil.rmtree(self._host_work_dir)
        #     logger.info(f"主机工作目录 '{self._host_work_dir}' 已清理。")


    async def __aenter__(self) -> "DockerSandbox":
        return await self.create()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.cleanup()
