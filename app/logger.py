import logging
import sys
from app.config import config

def get_logger(name: str) -> logging.Logger:
    """获取一个配置好的日志记录器"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(config.log.level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger