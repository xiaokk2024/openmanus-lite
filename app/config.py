import os
import toml
from pydantic import BaseModel, Field
from typing import Optional

class SandboxSettings(BaseModel):
    """
    Settings for the sandbox environment.
    """
    workspace_dir: str = Field(default="workspace", description="The working directory for the sandbox.")


class LLMSettings(BaseModel):
    """
    Settings for the Large Language Model.
    """
    model: str = Field(default="gpt-4o", description="The model to use for the LLM.")
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"), description="The API key for the LLM.")
    base_url: Optional[str] = Field(default=None, description="The base URL for the LLM API.")


class AgentSettings(BaseModel):
    """
    Settings for the agent.
    """
    agent_name: str = Field(default="Manus", description="The name of the agent to use.")
    max_iterations: int = Field(default=10, description="The maximum number of iterations for the agent.")


class Settings(BaseModel):
    """
    Main settings class that aggregates all other settings.
    """
    llm: LLMSettings = Field(default_factory=LLMSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)


def load_config(path: str = "config/config.toml") -> Settings:
    """
    Loads the configuration from a TOML file.
    If the file is not found, it returns the default settings.
    """
    try:
        config_data = toml.load(path)
    except FileNotFoundError:
        # 如果配置文件不存在，返回默认设置
        # If the config file does not exist, return default settings
        return Settings()
    return Settings.parse_obj(config_data)


# 全局配置实例
# Global settings instance
settings = load_config()
