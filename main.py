import sys
import logging
from core.orchestrator import Orchestrator
from config import AppConfig
from core.log_setup import setup_logging

def main():
    """
    应用程序的主入口函数。
    """
    if not AppConfig:
        print("❌ 致命错误：无法加载配置。程序退出。")
        sys.exit(1)

    setup_logging()

    if not AppConfig.check_config():
        print("错误：无法加载大模型配置。程序退出。")
        sys.exit(1)

    # ==========================================================================
    # 在此定义希望代理完成的任务
    # ==========================================================================
    task = "把周杰伦最热门的5首歌翻译成英文，放在tmp目录下"

    # 2. 初始化并运行编排器
    logging.info("🚀 智能体开始任务: %s", task)
    orchestrator = Orchestrator(task=task)
    final_result = orchestrator.run()

    # 3. 打印最终结果
    logging.info("\n\n" + "#"*20 + " Task Final Result " + "#"*20)
    logging.info(final_result if final_result else "The task did not return a definitive final result.")
    logging.info("#"*58)


if __name__ == "__main__":
    main()