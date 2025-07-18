import re
import xml.etree.ElementTree as ET
from app.agent.base import BaseAgent
from app.llm import LLM
from app.logger import logger
from app.schema import Message, Thought, Action, Observation


class ReActAgent(BaseAgent):
    def __init__(self, llm: LLM, max_iterations: int):
        super().__init__(llm, max_iterations)
        from app.tool.bash import BashTool
        from app.tool.file_operators import ReadFileTool, WriteFileTool, ListFilesTool
        from app.tool.python_execute import PythonExecuteTool
        from app.tool.terminate import TerminateTool
        from app.tool.tool_collection import ToolCollection

        self.tool_collection = ToolCollection([
            BashTool(),
            ReadFileTool(),
            WriteFileTool(),
            ListFilesTool(),
            PythonExecuteTool(),
            TerminateTool(),
        ])

    def get_prompt(self, task: str) -> str:
        return ""

    def _clean_llm_response(self, response: str) -> str:
        """
        清理 LLM 可能返回的多余字符，例如 markdown 代码块。
        """
        # 使用正则表达式查找 ```xml ... ``` 或 ``` ... ``` 并提取其中的内容
        match = re.search(r"```(xml\n)?(.*)```", response, re.DOTALL)
        if match:
            return match.group(2).strip()
        return response.strip()

    async def run(self, task: str):
        system_prompt = self.get_prompt(task)
        messages = [Message(role="system", content=system_prompt)]
        logger.info(f"System prompt:\n{system_prompt}")

        for i in range(self.max_iterations):
            logger.info(f"Thinking... (iteration {i + 1}/{self.max_iterations})")
            response = await self.llm.chat(messages)
            message_content = response.choices[0]["message"]["content"]
            messages.append(Message(role="assistant", content=message_content))

            logger.info(f"Assistant: {message_content}")

            try:
                # ===============================================================================
                # 关键修正：使用 XML 解析器，而不是 JSON 解析器
                # ===============================================================================
                cleaned_content = self._clean_llm_response(message_content)
                root = ET.fromstring(cleaned_content)

                # 1. 解析 Thought
                thought_node = root.find('thought')
                if thought_node is None:
                    raise ValueError("在 LLM 的响应中未找到 <thought> 标签")
                thought = Thought(thought=thought_node.text.strip())
                logger.info(f"Thought: {thought.thought}")

                # 2. 解析 Action
                action_node = root.find('action')
                if action_node is None:
                    raise ValueError("在 LLM 的响应中未找到 <action> 标签")

                tool_name_node = action_node.find('tool_name')
                if tool_name_node is None:
                    raise ValueError("在 <action> 标签中未找到 <tool_name>")
                tool_name = tool_name_node.text.strip()

                parameters_node = action_node.find('parameters')
                parameters = {}
                if parameters_node is not None:
                    for param_node in parameters_node:
                        parameters[param_node.tag] = param_node.text.strip() if param_node.text else ""

                action = Action(tool_name=tool_name, parameters=parameters)
                logger.info(f"Action: {action.tool_name}({action.parameters})")

                # 3. 执行工具并获取观察结果
                observation_text = await self.tool_collection.run_tool(action.tool_name, action.parameters)
                observation = Observation(
                    tool_name=action.tool_name,
                    tool_input=str(action.parameters),
                    observation=observation_text
                )
                logger.info(f"Observation: {observation.observation}")

                messages.append(Message(role="user", content=observation.observation))

            except Exception as e:
                logger.error(f"解析或执行时出错: {e}", exc_info=True)
                error_message = f"在解析你的响应或执行工具时发生错误: {e}。请检查你的 XML 格式并重试。"
                messages.append(Message(role="user", content=error_message))
