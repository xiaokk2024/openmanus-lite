import sys
import logging
from core.orchestrator import Orchestrator
from config import AppConfig
from core.log_setup import setup_logging

def main():
    if not AppConfig:
        print("❌ 致命错误：无法加载配置。程序退出。")
        sys.exit(1)

    setup_logging()

    if not AppConfig.check_config():
        print("错误：无法加载大模型配置。程序退出。")
        sys.exit(1)

    task = "把周杰伦最热门的5首歌的歌词翻译成英文写入docx文档，放在tmp目录下"

    logging.info("🚀 智能体开始任务: %s", task)
    orchestrator = Orchestrator(task=task)
    final_result = orchestrator.run()

    logging.info("\n\n" + "#"*20 + " Task Final Result " + "#"*20)
    logging.info(final_result if final_result else "The task did not return a definitive final result.")
    logging.info("#"*58)


if __name__ == "__main__":
    main()