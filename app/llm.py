from litellm import completion

from app.exceptions import LLMError
from app.logger import logger
from app.schema import Message, ModelResponse


class LLM:
    """
    LLM 类封装了与大语言模型的交互。
    """

    def __init__(self, model: str, api_key: str, base_url: str):
        """
        初始化 LLM 客户端。

        :param model: 要使用的模型名称。
        :param api_key: API 密钥。
        :param base_url: API 的基础 URL。
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def chat(
            self, messages: list[Message], tools: list[dict] | None = None
    ) -> ModelResponse:
        """
        与大语言模型进行聊天。

        :param messages: 聊天消息列表。
        :param tools: 可用工具列表。
        :return: 模型的响应。
        """
        params = {
            "model": self.model,
            "messages": [message.model_dump() for message in messages],
            "api_key": self.api_key,
            "base_url": self.base_url,
        }
        if tools:
            params["tools"] = tools

        try:
            logger.info(f"正在使用模型 '{self.model}' 调用 LLM API...")
            response = completion(**params)
            logger.info("LLM API 调用成功。")
            return ModelResponse.from_litellm_response(response)
        except Exception as e:
            logger.error(f"调用 LLM API 时出错: {e}")
            raise LLMError(f"调用 LLM API 时出错: {e}") from e
