from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# ===============================================================================
# 新增的模型定义，用于处理与 LLM 的交互
# ===============================================================================

class Message(BaseModel):
    """
    定义了与大语言模型交互时单条消息的结构。
    """
    role: str = Field(description="消息发送者的角色 (e.g., 'system', 'user', 'assistant')")
    content: str = Field(description="消息的具体内容")


class ModelResponse(BaseModel):
    """
    定义了从大语言模型接收到的响应的结构。
    """
    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: List[Dict[str, Any]] = []
    usage: Optional[Dict[str, int]] = None


# ===============================================================================
# 项目中原有的模型定义
# ===============================================================================

class Thought(BaseModel):
    thought: str = Field(description="The thought process of the agent")


class ToolSchema(BaseModel):
    name: str
    description: str
    properties: Dict[str, Dict[str, Any]]
    required: List[str] = []


class Action(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


class Observation(BaseModel):
    tool_name: str
    tool_input: str
    observation: str

