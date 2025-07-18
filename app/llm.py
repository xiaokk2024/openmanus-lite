import litellm
from app.logger import logger
from app.schema import Message, ModelResponse


class LLM:
    """
    一个封装了与大语言模型（通过 litellm）交互逻辑的类。
    """
    def __init__(self, model: str, api_key: str, base_url: str, temperature: float):
        """
        初始化 LLM 客户端。

        :param model: 要使用的模型名称 (e.g., "deepseek/deepseek-v3-0324")。
        :param api_key: API 密钥。
        :param base_url: API 的基础 URL。
        :param temperature: 生成文本时的温度参数，控制创造性。
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature

    async def chat(self, messages: list[Message]) -> ModelResponse:
        """
        向大语言模型发送聊天请求。

        :param messages: 一个包含对话历史的消息列表。
        :return: 来自模型的响应。
        """
        try:
            final_model_string = f"openai/{self.model}"

            logger.debug(f"向 LLM 发送请求: model='{final_model_string}', messages={messages}")
            response = await litellm.acompletion(
                model=final_model_string,
                messages=[message.dict() for message in messages],
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=self.temperature,
            )
            logger.debug(f"从 LLM 收到响应: {response}")

            # ===============================================================================
            # 最终修正：将 litellm 返回的 ModelResponse 对象转换为字典，
            # 然后再用它来创建我们自己的 Pydantic 模型实例。
            # ===============================================================================
            return ModelResponse(**response.dict())

        except Exception as e:
            logger.error(f"与 LLM 通信时出错: {e}")
            raise
