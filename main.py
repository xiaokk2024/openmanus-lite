import argparse
import asyncio

from app.agent.factory import AgentFactory
# 从配置模块导入所有需要的 LLM 参数
from app.config import LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, LLM_TEMPERATURE
from app.llm import LLM
from app.logger import logger


async def main():
    """
    程序的主入口函数。
    """
    parser = argparse.ArgumentParser(description="OpenManus-Lite: 一个轻量级的自主 AI 代理")
    parser.add_argument(
        "-t", "--task",
        type=str,
        required=True,
        help="需要 Agent 完成的具体任务描述。"
    )
    args = parser.parse_args()

    logger.info(f"接收到任务: {args.task}")

    try:
        # 初始化 LLM，并传入所有必要的配置参数
        llm = LLM(
            model=LLM_MODEL,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            temperature=LLM_TEMPERATURE
        )
        # 创建 Agent
        agent = AgentFactory.create_agent(llm)
        # 运行 Agent 来完成任务
        await agent.run(args.task)

    except Exception as e:
        logger.error(f"在任务执行过程中发生了一个无法处理的错误: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
