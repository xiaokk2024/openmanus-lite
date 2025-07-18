import os
import toml
from pydantic import BaseModel, Field
from typing import Optional

class LogConfig(BaseModel):
    level: str = "INFO"

class LLMConfig(BaseModel):
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None # <--- 在这里新增此行
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 4096

class SandboxConfig(BaseModel):
    image_name: str = "ubuntu:22.04"
    workspace_mount_path: str = "/workspace"
    timeout: int = 120
    network_enabled: bool = False
    memory_limit: str = "512m"
    cpu_limit: float = 1.0

class Config(BaseModel):
    workspace_dir: str = "workspace"
    log: LogConfig = LogConfig()
    llm: LLMConfig = LLMConfig()
    sandbox: SandboxConfig = SandboxConfig()

_config: Optional[Config] = None

def load_config(config_file: str = "config/config.toml") -> Config:
    """加载 TOML 配置文件并解析为 Pydantic 模型"""
    global _config
    if _config is None:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = toml.load(f)
            _config = Config.model_validate(config_data)

            # 优先从环境变量加载 API Key
            if "OPENAI_API_KEY" in os.environ:
                _config.llm.api_key = os.environ["OPENAI_API_KEY"]

        except FileNotFoundError:
            print(f"错误: 配置文件 '{config_file}' 未找到。")
            # 创建一个默认配置
            _config = Config()
        except Exception as e:
            print(f"加载配置时出错: {e}")
            raise

    # 确保工作区目录存在
    os.makedirs(_config.workspace_dir, exist_ok=True)

    return _config

# 在模块加载时自动加载配置
config = load_config()