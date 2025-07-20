import os
import toml
from dotenv import load_dotenv
# 如果存在.env文件，则从中加载环境变量
load_dotenv()

# --- 配置类 ---
class Config:
    def __init__(self, config_path="config.toml"):
        """从TOML文件和系统环境变量加载配置"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")

        # 加载TOML配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            toml_config = toml.load(f)

        # --- LLM模型配置 ---
        llm_config = toml_config.get("llm", {})
        # 优先从环境变量获取API密钥
        self.LLM_API_KEY = os.getenv("LLM_API_KEY", llm_config.get("api_key"))
        self.LLM_BASE_URL = llm_config.get("base_url")
        self.LLM_MODEL = llm_config.get("model")
        self.LLM_MAX_TOKENS = llm_config.get("max_tokens", 4096)
        self.LLM_TEMPERATURE = llm_config.get("temperature", 0.1)

        # --- 工作空间配置 ---
        self.WORKSPACE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workspace")

    def check_config(self):
        """检查核心配置是否已设置"""
        if not self.LLM_API_KEY:
            print("❌ 错误：未配置LLM API密钥")
            print("请在config.toml中设置或通过LLM_API_KEY环境变量配置")
            return False
        if not self.LLM_BASE_URL:
            print("❌ 错误：config.toml中未配置LLM基础URL")
            return False
        if not self.LLM_MODEL:
            print("❌ 错误：config.toml中未配置LLM模型")
            return False

        # 确保工作空间目录存在
        if not os.path.exists(self.WORKSPACE_PATH):
            print(f"📂 工作空间目录未找到，正在创建: {self.WORKSPACE_PATH}")
            os.makedirs(self.WORKSPACE_PATH)

        return True

# 创建全局配置实例供整个应用程序使用
try:
    AppConfig = Config()
except FileNotFoundError as e:
    print(f"❌ {e}")
    AppConfig = None