import logging
import xml.etree.ElementTree as ET
from app.agent.base import Agent
from app.exceptions import Terminate

logger = logging.getLogger(__name__)


class ReActAgent(Agent):
    """
    An agent that implements the ReAct (Reasoning and Acting) framework.
    """
    async def run(self, task: str):
        logger.info(f"Received task: {task}")
        messages = [{"role": "system", "content": self.prompt.format(task=task)}]

        for i in range(self.max_iterations):
            logger.info(f"Thinking... (iteration {i + 1}/{self.max_iterations})")

            try:
                response = await self.llm.chat(messages)
                logger.info(f"Assistant: {response}")

                messages.append({"role": "assistant", "content": response})

                thought, action_name, parameters = self._parse_response(response)
                logger.info(f"Thought: {thought}")
                logger.info(f"Action: {action_name}({parameters})")

                observation = await self.tools.run_tool(action_name, parameters)
                logger.info(f"Observation: {observation}")

                messages.append(
                    {
                        "role": "user",
                        "content": f"<observation>{observation}</observation>",
                    }
                )
            except Terminate as e:
                logger.info(f"Task finished: {e.message}")
                return
            except Exception as e:
                logger.error(f"Error during task execution: {e}", exc_info=True)
                error_message = f"Error: An unhandled exception occurred: {e}"
                messages.append(
                    {"role": "user", "content": f"<observation>{error_message}</observation>"}
                )
                continue

        logger.warning("Max iterations reached. Task may not be complete.")

    def _parse_response(self, response: str):
        try:
            root = ET.fromstring(response)
            thought = root.find("thought").text.strip()
            action_node = root.find("action")
            tool_name = action_node.find("tool_name").text.strip()
            parameters = {
                child.tag: child.text.strip()
                for child in action_node.find("parameters")
            }
            return thought, tool_name, parameters
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {e}\nResponse:\n{response}")

