from litellm import completion
from typing import List, Dict, Any
from app.config import config
from app.logger import get_logger
from app.schema import Message

logger = get_logger(__name__)

class LLM:
    """LLM 交互的封装类"""

    def __init__(self):
        self.model = config.llm.model
        self.api_key = config.llm.api_key
        self.base_url = config.llm.base_url
        self.temperature = config.llm.temperature
        self.top_p = config.llm.top_p
        self.max_tokens = config.llm.max_tokens

    def chat(self, messages: List[Message], tools: List[Dict[str, Any]] = None) -> Any:
        """
        与 LLM 进行一次对话 (已适配自定义 API 端点)。
        """
        messages_dict = [msg.model_dump(exclude_none=True) for msg in messages]
        logger.debug(f"向 LLM 发送请求: Model={self.model}, Messages={messages_dict}, Tools={tools}")

        # 准备 API 调用参数
        params = {
            "model": self.model,
            "messages": messages_dict,
            "tools": tools,
            "tool_choice": "auto" if tools else None,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }

        # --- 核心改动 ---
        # 如果用户提供了 base_url，则明确告知 litellm 将其作为 OpenAI 兼容端点处理
        if self.base_url:
            params["custom_llm_provider"] = "openai"
        # -----------------

        try:
            response = completion(**params)
            logger.debug(f"从 LLM 收到响应: {response}")
            return response
        except Exception as e:
            logger.error(f"调用 LLM API 时出错: {e}")
            raise