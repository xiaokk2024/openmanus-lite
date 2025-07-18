import logging
import sys

# 1. 获取一个名为 "openmanus-lite" 的 logger 实例
logger = logging.getLogger("openmanus-lite")

# 2. 设置该 logger 的最低日志级别为 INFO
# 这意味着它会处理 INFO, WARNING, ERROR, CRITICAL 级别的日志
logger.setLevel(logging.INFO)

# 3. 检查 logger 是否已经配置了处理器 (handler)
# 这是为了防止在代码被多次导入时重复添加处理器，导致日志输出多次
if not logger.handlers:
    # 4. 如果没有配置过，则创建一个新的处理器，将日志流式输出到标准输出（即您的控制台）
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # 5. 定义所有日志的输出格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # 6. 将配置好的处理器添加到 logger 中
    logger.addHandler(handler)
