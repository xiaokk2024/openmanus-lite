from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Action(BaseModel):
    """定义 Agent 的行动"""
    tool_name: str = Field(..., description="要使用的工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="传递给工具的参数")

class ThoughtAction(BaseModel):
    """定义 Agent 的思考和行动对"""
    thought: str = Field(..., description="Agent 在决定行动之前的思考过程")
    action: Action = Field(..., description="Agent 决定执行的行动")

class Observation(BaseModel):
    """定义工具执行后返回的观察结果"""
    content: str
    is_error: bool = False
    tool_name: str

class Message(BaseModel):
    """定义 LLM 交互中的消息结构"""
    role: str # "user", "assistant", "system", "tool"
    content: Any
    tool_call_id: Optional[str] = None

class AgentState(BaseModel):
    """定义 Agent 的当前状态"""
    messages: List[Message] = []
    task: str