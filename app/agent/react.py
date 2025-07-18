import json
from typing import List, Dict, Any, Optional
from app.agent.base import BaseAgent
from app.llm import LLM
from app.schema import Message, Action, ThoughtAction, Observation
from app.tool.tool_collection import tool_collection
from app.exceptions import ToolError
from app.logger import get_logger

logger = get_logger(__name__)

class ReActAgent(BaseAgent):
    """
    一个实现了 ReAct (Reason+Act) 循环的 Agent。
    """
    def __init__(self, system_prompt: str, max_iterations: int = 15):
        super().__init__()
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.llm = LLM()
        self.messages: List[Message] = []

    def _initialize_messages(self, task: str):
        """初始化对话历史"""
        self.messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content=f"任务: {task}"),
        ]

    def _parse_llm_response(self, response_text: str) -> Optional[ThoughtAction]:
        """从 LLM 的文本响应中解析出 Thought 和 Action"""
        try:
            thought_part = ""
            action_part = ""

            if "Action:" in response_text:
                thought_part, action_part = response_text.split("Action:", 1)
            else:
                logger.warning("响应中未找到 'Action:'，将整个响应视为思考。")
                thought_part = response_text

            thought = thought_part.replace("Thought:", "").strip()

            if not action_part.strip():
                return ThoughtAction(thought=thought, action=Action(tool_name="terminate", parameters={"message": "Agent did not provide an action."}))

            action_json = json.loads(action_part.strip())
            action = Action(**action_json)

            return ThoughtAction(thought=thought, action=action)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"解析 LLM 响应失败: {e}\n响应文本: '{response_text}'")
            return ThoughtAction(thought="解析上一次的响应失败。", action=Action(tool_name="terminate", parameters={"message": f"Error parsing LLM response: {e}"}))
        except Exception as e:
            logger.error(f"解析过程中发生未知错误: {e}")
            return None

    def _execute_action(self, action: Action) -> Observation:
        """执行一个 Action 并返回 Observation"""
        try:
            logger.info(f"执行工具: {action.tool_name}，参数: {action.parameters}")
            output = tool_collection.run_tool(action.tool_name, action.parameters)
            return Observation(content=str(output), is_error=False, tool_name=action.tool_name)
        except ToolError as e:
            logger.error(f"工具 '{action.tool_name}' 执行出错: {e}")
            return Observation(content=f"错误: {e}", is_error=True, tool_name=action.tool_name)
        except Exception as e:
            logger.error(f"执行工具 '{action.tool_name}' 时发生未知错误: {e}")
            return Observation(content=f"未知错误: {e}", is_error=True, tool_name=action.tool_name)

    def run(self, task: str) -> str:
        """执行 ReAct 循环来完成任务"""
        self._initialize_messages(task)

        for i in range(self.max_iterations):
            logger.info(f"--- 第 {i + 1} 轮迭代 ---")

            # 1. 调用 LLM
            response = self.llm.chat(self.messages, tools=tool_collection.get_tool_definitions())

            # 检查是否有响应内容
            if not response.choices or not response.choices[0].message.content:
                logger.error("LLM 返回了空响应。")
                return "任务失败：LLM 返回空响应。"

            response_text = response.choices[0].message.content
            self.messages.append(Message(role="assistant", content=response_text))

            # 2. 解析 Thought 和 Action
            thought_action = self._parse_llm_response(response_text)
            if not thought_action:
                return "任务失败：无法解析 LLM 的响应。"

            logger.info(f"思考: {thought_action.thought}")

            # 3. 检查是否终止
            if thought_action.action.tool_name == "terminate":
                final_message = thought_action.action.parameters.get("message", "任务已完成。")
                logger.info(f"任务终止，最终消息: {final_message}")
                return final_message

            # 4. 执行 Action 并获取 Observation
            observation = self._execute_action(thought_action.action)
            logger.info(f"观察: {observation.content}")

            # 5. 将 Observation 添加到消息历史中
            self.messages.append(Message(role="user", content=f"观察结果:\n{observation.content}"))

        logger.warning("已达到最大迭代次数。")
        return "任务失败：已达到最大迭代次数。"