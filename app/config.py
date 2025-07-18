import toml
from pydantic import BaseModel, Field

# 定义大语言模型配置的数据模型
class LLMSettings(BaseModel):
    model: str = "deepseek/deepseek-v3-0324"
    api_key: str = "YOUR_API_KEY"
    base_url: str = "https://api.deepseek.com"

# 定义沙箱配置的数据模型
class SandboxSettings(BaseModel):
    image: str = "ubuntu:22.04"
    working_directory: str = Field("/workspace", alias="work_dir")
    timeout: int = 60
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    network_enabled: bool = False

# 定义 Agent 配置的数据模型
class AgentSettings(BaseModel):
    agent_name: str = "ManusAgent"
    max_iterations: int = 10

# 定义总的配置模型
class Config(BaseModel):
    llm: LLMSettings
    sandbox: SandboxSettings
    agent: AgentSettings

# 全局配置变量
_config: Config | None = None

def load_config(path: str = "config/config.toml") -> Config:
    """
    从 toml 文件加载配置。
    """
    global _config
    if _config is None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = toml.load(f)
            _config = Config(**data)
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"加载或解析配置文件 '{path}' 时出错: {e}") from e
    return _config

def get_config() -> Config:
    """
    获取已加载的配置。如果未加载则先加载。
    """
    if _config is None:
        return load_config()
    return _config

