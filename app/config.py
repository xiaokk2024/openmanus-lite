import os
import toml
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 读取配置文件路径，默认为 config/config.toml
config_path = os.getenv("CONFIG_PATH", "config/config.toml")
config = toml.load(config_path)

# ===============================================================================
# LLM (大语言模型) 配置
# ===============================================================================
LLM_MODEL = config["llm"]["model"]
LLM_TEMPERATURE = config["llm"]["temperature"]
LLM_API_KEY = os.getenv("LLM_API_KEY", config["llm"]["api_key"])
LLM_BASE_URL = os.getenv("LLM_BASE_URL", config["llm"]["base_url"])

# ===============================================================================
# Sandbox (沙箱) 配置
# ===============================================================================
SANDBOX_IMAGE = config["sandbox"]["image"]
SANDBOX_WORKING_DIRECTORY = config["sandbox"]["working_directory"]
SANDBOX_TIMEOUT = config["sandbox"]["timeout"]
SANDBOX_MEMORY_LIMIT = config["sandbox"]["memory_limit"]
SANDBOX_CPU_LIMIT = config["sandbox"]["cpu_limit"]
SANDBOX_NETWORK_ENABLED = config["sandbox"]["network_enabled"]

# ===============================================================================
# 新增的 Agent (代理) 配置
# ===============================================================================
AGENT_NAME = config["agent"]["agent_name"]
MAX_ITERATIONS = config["agent"]["max_iterations"]
