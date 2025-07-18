import litellm
import logging
from typing import List

# [FIX] 导入 LLMSettings 以用于类型提示
# Import LLMSettings for type hinting
from app.config import LLMSettings

logger = logging.getLogger(__name__)

class LLM:
    """
    A wrapper around the litellm library to interact with Large Language Models.
    """
    def __init__(self, settings: LLMSettings):
        """
        Initializes the LLM wrapper with the given settings.

        Args:
            settings: An LLMSettings object containing model, api_key, etc.
        """
        # [FIX] 在初始化时存储配置，而不是依赖全局变量
        # Store the configuration at initialization instead of relying on a global variable
        self.settings = settings

    async def chat(self, messages: List[dict]) -> str:
        """
        Sends a chat request to the LLM and returns the response content.
        """
        logger.info(f"Sending request to LLM model: {self.settings.model}")
        try:
            # [FIX] 使用实例变量 self.settings 来获取配置
            # Use the instance variable self.settings to get the configuration
            response = await litellm.acompletion(
                model=self.settings.model,
                messages=messages,
                api_key=self.settings.api_key,
                base_url=self.settings.base_url,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM returned an empty response.")
            return content
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}")
            # 在向上抛出异常之前，可以考虑进行更详细的错误处理
            # Consider more detailed error handling before re-raising
            raise

