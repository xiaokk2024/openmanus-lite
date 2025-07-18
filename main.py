import argparse
import asyncio
import os
import platform

from app.agent.factory import AgentFactory

from app.config import load_config
from app.llm import LLM
from app.logger import logger
from app.sandbox.client import SandboxClient


async def main():
    """
    主函数，用于解析命令行参数并运行 Agent。
    """
    # 在 Windows 上，旧的 docker-py 版本可能会错误地设置 DOCKER_HOST。
    # 尝试通过删除它来解决 "Not supported URL scheme http+docker" 的问题。
    if platform.system() == "Windows" and "DOCKER_HOST" in os.environ:
        logger.info("检测到 Windows 环境，正在尝试取消设置 DOCKER_HOST 以避免连接问题。")
        del os.environ["DOCKER_HOST"]

    parser = argparse.ArgumentParser(description="OpenManus Lite - 一个由 LLM 驱动的自主代理")
    parser.add_argument(
        "-t",
        "--task",
        type=str,
        required=True,
        help="要由 Agent 执行的任务。",
    )
    args = parser.parse_args()

    # 加载配置
    config = load_config()

    # 初始化 LLM 和 Agent
    llm = LLM(
        model=config.llm.model,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url,
    )
    agent = AgentFactory.create_agent(
        agent_name=config.agent.agent_name,
        llm=llm,
        max_iterations=config.agent.max_iterations,
    )

    logger.info("=" * 50)
    logger.info("OpenManus 正在启动...")
    logger.info(f"任务: {args.task}")
    logger.info(f"Agent: {config.agent.agent_name}")
    logger.info(f"模型: {config.llm.model}")
    logger.info("=" * 50)

    final_result = ""
    sandbox_client = None
    try:
        # 获取沙箱客户端实例
        sandbox_client = await SandboxClient.get_instance()

        # 运行 agent
        final_result = await agent.run(args.task)

        logger.info("=" * 50)
        logger.info("任务已完成！")
        logger.info(f"最终结果:\n{final_result}")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"执行过程中发生严重错误: {e}", exc_info=True)
    finally:
        logger.info("正在关闭沙箱...")
        # 如果沙箱客户端已初始化，则关闭它
        if sandbox_client:
            try:
                await sandbox_client.close()
            except Exception as e:
                logger.error(f"关闭沙箱时出错: {e}", exc_info=True)

        logger.info("程序已退出。")


if __name__ == "__main__":
    # 在 Windows 上设置正确的事件循环策略以支持 asyncio 和 aiohttp
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
