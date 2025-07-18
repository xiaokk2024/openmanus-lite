import asyncio

import docker

from app.logger import logger


class AsyncDockerizedTerminal:
    """
    一个异步的 Docker 终端，用于在容器中执行命令。
    """
    def __init__(self, container_id: str, work_dir: str, env_vars: dict | None = None):
        self.client = docker.from_env().api
        self.container_id = container_id
        self.work_dir = work_dir
        self.env_vars = env_vars or {}

    async def run_command(self, cmd: str, timeout: int) -> tuple[int, str]:
        """
        异步执行命令并返回退出码和输出。

        :param cmd: 要执行的命令。
        :param timeout: 超时时间（秒）。
        :return: 一个元组 (exit_code, output_string)。
        """
        try:
            exec_instance = self.client.exec_create(
                self.container_id,
                cmd=f"/bin/sh -c '{cmd}'",
                workdir=self.work_dir,
                environment=self.env_vars,
                stdout=True,
                stderr=True,
                tty=True,
            )
            exec_id = exec_instance['Id']

            socket = self.client.exec_start(exec_id, detach=False, socket=True)
            socket_conn = socket._sock
            socket_conn.setblocking(False)

            output = ""
            loop = asyncio.get_event_loop()

            async def read_stream():
                nonlocal output
                while True:
                    try:
                        data = await loop.sock_recv(socket_conn, 4096)
                        if not data:
                            break
                        output += data.decode('utf-8', errors='ignore')
                    except BlockingIOError:
                        await asyncio.sleep(0.01)
                    except ConnectionAbortedError:
                        logger.warning("Socket connection aborted.")
                        break
                    except Exception as e:
                        logger.error(f"Error reading from socket: {e}")
                        break

            try:
                await asyncio.wait_for(read_stream(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Command timed out after {timeout} seconds.")
                # Even on timeout, we need to get the exit code.
            finally:
                try:
                    socket.close()
                except Exception:
                    pass

            inspect_result = self.client.exec_inspect(exec_id)
            exit_code = inspect_result.get('ExitCode')

            # When a command times out, exit code might be None.
            if exit_code is None:
                return -1, f"Command timed out and exit code could not be determined.\nOutput captured:\n{output}"

            return exit_code, output

        except Exception as e:
            logger.error(f"Failed to run command in terminal: {e}", exc_info=True)
            return -1, str(e)

    async def init(self):
        pass

    async def close(self):
        pass
