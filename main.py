import argparse
import sys
from app.agent import create_agent
from app.config import config, load_config
from app.logger import get_logger
from app.sandbox.client import SandboxClient

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OpenManus - 自主 AI 代理")
    parser.add_argument(
        "-t", "--task", type=str, required=True, help="要让 Agent 执行的任务描述。"
    )
    parser.add_argument(
        "-a",
        "--agent",
        type=str,
        default="ManusAgent",
        help="要使用的 Agent 的名称。",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config/config.toml",
        help="配置文件的路径。",
    )
    args = parser.parse_args()

    # 加载配置和初始化日志
    try:
        load_config(args.config)
        logger = get_logger("main")
    except Exception as e:
        print(f"初始化失败: {e}", file=sys.stderr)
        sys.exit(1)

    logger.info("=" * 50)
    logger.info(f"OpenManus 正在启动...")
    logger.info(f"任务: {args.task}")
    logger.info(f"Agent: {args.agent}")
    logger.info(f"模型: {config.llm.model}")
    logger.info("=" * 50)

    try:
        # 创建 Agent 实例
        agent = create_agent(args.agent)

        # 运行 Agent
        final_result = agent.run(args.task)

        logger.info("=" * 50)
        logger.info("任务已完成！")
        logger.info(f"最终结果:\n{final_result}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"执行过程中发生严重错误: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # 清理沙箱
        logger.info("正在关闭沙箱...")
        SandboxClient().close()
        logger.info("程序已退出。")


if __name__ == "__main__":
    main()
