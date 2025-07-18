from typing import List, Literal, Optional

# 修正为 pydantic V2 的标准导入方式
from pydantic import BaseModel, Field


class ToolSchema(BaseModel):
    """
    工具参数的 schema 定义。
    """
    type: str = "object"
    properties: Dict[str, Dict[str, Any]]
    required: List[str] = []


class SandboxCommandOutput(BaseModel):
    """
    沙箱命令执行的输出。
    """

    exit_code: int
    stdout: str
    stderr: str


class FunctionCall(BaseModel):
    """
    函数调用的数据模型。
    """

    name: str
    arguments: str


class ToolCall(BaseModel):
    """
    工具调用的数据模型。
    """

    id: str
    function: FunctionCall
    type: str = "function"


class Message(BaseModel):
    """
    聊天消息的数据模型。
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class ModelResponse(BaseModel):
    """
    封装了从大语言模型返回的响应。
    """

    id: str
    role: str = "assistant"
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

    @classmethod
    def from_litellm_response(cls, response) -> "ModelResponse":
        """
        从 litellm 的响应对象创建 ModelResponse 实例。
        """
        if not response.choices:
            raise ValueError("LLM 响应不包含任何 'choices'。")

        choice = response.choices[0]
        message = choice.message

        tool_calls = (
            [ToolCall(**tc.model_dump()) for tc in message.tool_calls]
            if message.tool_calls
            else None
        )

        return cls(
            id=response.id,
            role=message.role,
            content=message.content,
            tool_calls=tool_calls,
        )
