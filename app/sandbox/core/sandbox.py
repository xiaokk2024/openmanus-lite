import docker
from docker.models.containers import Container
from docker.errors import NotFound
import os
import platform  # <--- 在这里新增此行
import uuid
from typing import Tuple, Optional

from app.config import config
from app.logger import get_logger
from app.exceptions import SandboxError

logger = get_logger(__name__)

class Sandbox:
    """
    管理单个 Docker 容器作为执行环境的沙箱。
    此实现基于用户的参考代码，提供了更健壮的容器管理和文件操作。
    """

    def __init__(self, container_id: Optional[str] = None):
        try:
            # --- 最终修复：强制使用正确的 Windows 连接方式 ---
            if platform.system() == "Windows":
                logger.debug("检测到 Windows 系统，强制使用 npipe 连接 Docker。")
                # 此方法将绕过所有环境变量，直接连接到 Docker Desktop。
                self.docker_client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
            else:
                # 在 Linux/macOS 上，标准方法工作良好。
                logger.debug("检测到非 Windows 系统，使用标准方法连接。")
                self.docker_client = docker.from_env()
            # ----------------------------------------------------

            self.docker_client.ping()
            logger.info("成功连接到 Docker daemon。")
        except Exception as e:
            logger.error(f"无法连接到 Docker daemon。请确保 Docker 正在运行。错误: {e}")
            raise SandboxError(f"Docker 连接失败: {e}")

        self.container: Optional[Container] = None
        if container_id:
            try:
                self.container = self.docker_client.containers.get(container_id)
                logger.info(f"已连接到现有沙箱容器: {self.container.short_id}")
            except NotFound:
                logger.warning(f"找不到容器 ID {container_id}，将创建一个新容器。")
                self._create_container()
        else:
            self._create_container()

    def _create_container(self):
        """
        使用低级 API 创建并启动一个长期运行的沙箱容器。
        """
        container_name = f"openmanus-sandbox-{uuid.uuid4().hex[:8]}"
        logger.info(f"正在创建沙箱容器 '{container_name}'，镜像: {config.sandbox.image_name}...")
        try:
            host_config = self.docker_client.api.create_host_config(
                mem_limit=config.sandbox.memory_limit,
                cpu_period=100000,
                cpu_quota=int(100000 * config.sandbox.cpu_limit),
                network_mode="bridge" if config.sandbox.network_enabled else "none",
                binds={
                    os.path.abspath(config.workspace_dir): {
                        "bind": config.sandbox.workspace_mount_path,
                        "mode": "rw",
                    }
                },
            )

            container_info = self.docker_client.api.create_container(
                image=config.sandbox.image_name,
                command="tail -f /dev/null",  # 保持容器运行
                name=container_name,
                working_dir=config.sandbox.workspace_mount_path,
                host_config=host_config,
                tty=True,
                detach=True,
            )

            self.container = self.docker_client.containers.get(container_info["Id"])
            self.container.start()
            logger.info(f"沙箱容器已创建并启动，ID: {self.container.short_id}")
        except Exception as e:
            logger.error(f"创建沙箱容器失败: {e}")
            self.close()
            raise SandboxError(f"创建容器失败: {e}")

    def execute(self, command: str) -> Tuple[int, str]:
        """在沙箱容器中执行命令。"""
        if not self.container:
            raise SandboxError("沙箱未初始化。")

        logger.info(f"在沙箱 {self.container.short_id} 中执行命令: {command}")

        # exec_run 是推荐的执行命令方式
        exit_code, (stdout, stderr) = self.container.exec_run(
            ["/bin/bash", "-c", command],
            demux=True, # 分离 stdout 和 stderr
        )

        output = ""
        if stdout:
            output += stdout.decode("utf-8", errors="ignore")
        if stderr:
            output += stderr.decode("utf-8", errors="ignore")

        logger.info(f"命令执行完成，Exit Code: {exit_code}")
        logger.debug(f"命令输出:\n{output}")
        return exit_code, output

    def write_file(self, path: str, content: str):
        """使用 put_archive 将内容写入容器内的文件。"""
        if not self.container:
            raise SandboxError("沙箱未初始化。")

        full_path = os.path.join(config.sandbox.workspace_mount_path, path)
        parent_dir = os.path.dirname(full_path)
        file_name = os.path.basename(path)

        logger.info(f"正在向沙箱写入文件: {full_path}")

        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=file_name)
            content_bytes = content.encode('utf-8')
            tarinfo.size = len(content_bytes)
            tar.addfile(tarinfo, io.BytesIO(content_bytes))
        tar_stream.seek(0)

        try:
            # put_archive 需要一个目录作为目标
            self.container.put_archive(path=parent_dir, data=tar_stream)
        except Exception as e:
            raise SandboxError(f"写入文件 '{path}' 失败: {e}")

    def read_file(self, path: str) -> str:
        """使用 get_archive 从容器中读取文件内容。"""
        if not self.container:
            raise SandboxError("沙箱未初始化。")

        full_path = os.path.join(config.sandbox.workspace_mount_path, path)
        logger.info(f"正在从沙箱读取文件: {full_path}")

        try:
            stream, _ = self.container.get_archive(full_path)

            with tarfile.open(fileobj=io.BytesIO(b"".join(chunk for chunk in stream))) as tar:
                # 假设 tar 包里只有一个文件
                for member in tar.getmembers():
                    f = tar.extractfile(member)
                    if f:
                        return f.read().decode('utf-8')
            raise FileNotFoundError(f"在归档中找不到文件: {path}")
        except NotFound:
            raise FileNotFoundError(f"文件在沙箱中未找到: {path}")
        except Exception as e:
            raise SandboxError(f"读取文件 '{path}' 失败: {e}")

    def close(self):
        """停止并移除沙箱容器。"""
        if self.container:
            container_id = self.container.short_id
            try:
                logger.info(f"正在停止并移除沙箱容器: {container_id}")
                self.container.stop(timeout=5)
                self.container.remove(force=True)
                logger.info(f"沙箱 {container_id} 已关闭。")
            except Exception as e:
                logger.error(f"关闭沙箱 {container_id} 时出错: {e}")
            finally:
                self.container = None