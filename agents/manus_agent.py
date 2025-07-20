# -*- coding: utf-8 -*-
import json
import re
from typing import List, Dict, Any, Tuple

from core.llm import call_llm
from agents.prompts import MANUS_INSTRUCTIONS, MANUS_PROMPT_TEMPLATE
from tools.base_tool import BaseTool

class ManusAgent:
    """
    The core execution agent (a ReAct Agent).
    It follows a plan and executes task steps through a cycle of thought and action.
    """
    def __init__(self, tools: List[BaseTool]):
        """
        Initializes the ManusAgent.

        Args:
            tools (List[BaseTool]): A list of all available tool instances.
        """
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.tools_description = self._get_tools_description()
        self.tools_list = self._get_tools_list()

    def _get_tools_description(self) -> str:
        """Generates a description string of all tools for the system prompt."""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])

    def _get_tools_list(self) -> str:
        """Generates a list of tools with names and arguments for the user prompt."""
        return "\n".join([
            f"  - {tool.name}({tool.get_args_str()}): {tool.description}"
            for tool in self.tools
        ])

    def _find_json_block(self, text: str) -> Dict[str, Any]:
        """Extracts the first valid JSON block from the LLM's response."""
        # Regex to find JSON block enclosed in ```json ... ```
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ Warning: Found a JSON markdown block, but it failed to parse. Error: {e}. Raw string: {json_str}")
                # Fall through to try parsing the whole text

        # If no markdown block is found, or if it fails, try to parse the entire string as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"❌ Could not parse JSON from LLM response: {text}")
            return None

    def run_step(self, task: str, plan: List[str], current_step_index: int, previous_steps_history: str) -> Tuple[str, bool, str]:
        """
        Executes a single step from the plan.

        Args:
            task (str): The original top-level task.
            plan (List[str]): The full list of plan steps.
            current_step_index (int): The index of the current step to execute (1-based).
            previous_steps_history (str): The execution history of all previous steps.

        Returns:
            A tuple containing:
            - step_history (str): The full execution history (thought, action, observation) for the current step.
            - finished (bool): A flag indicating if the `finish` tool was called.
            - final_summary (str): The final summary if the `finish` tool was called.
        """
        current_step = plan[current_step_index - 1]
        plan_str = "\n".join(f"{i}. {s}" for i, s in enumerate(plan, 1))

        local_history = ""
        max_loops = 10  # Prevents infinite loops for a single step

        for i in range(max_loops):
            print(f"\n🔄 ManusAgent thinking loop {i+1}/{max_loops} for step {current_step_index}...")

            prompt = MANUS_PROMPT_TEMPLATE.format(
                task=task,
                plan=plan_str,
                history=previous_steps_history + local_history,
                current_step=f"{current_step_index}. {current_step}",
                tools_list=self.tools_list
            )

            # Get the next action from the LLM
            llm_response = call_llm(prompt, instructions=MANUS_INSTRUCTIONS.format(tools_description=self.tools_description))

            if "Error:" in llm_response:
                observation = f"LLM call failed. Details: {llm_response}"
                local_history += f"\nObservation: {observation}"
                continue

            action_json = self._find_json_block(llm_response)

            if not action_json:
                observation = "Invalid action format. Please respond strictly in the specified JSON format, including `thought` and `action` keys."
                local_history += f"\nObservation: {observation}"
                continue

            thought = action_json.get("thought", "[No thought provided]")
            action = action_json.get("action", {})
            tool_name = action.get("name")
            tool_args = action.get("args", {})

            print(f"🤔 Thought: {thought}")
            print(f"🎬 Action: Calling tool `{tool_name}` with args: {tool_args}")

            local_history += f"\nThought: {thought}\nAction: {json.dumps(action_json, indent=2, ensure_ascii=False)}"

            if tool_name in self.tool_map:
                tool = self.tool_map[tool_name]
                try:
                    observation = tool.execute(**tool_args)
                    print(f"👀 Observation: {observation}")
                except Exception as e:
                    observation = f"Error executing tool '{tool_name}': {e}"
                    print(f"❌ {observation}")

                local_history += f"\nObservation: {observation}"

                if tool.name == "finish":
                    return local_history, True, tool_args.get("summary", "No summary was provided.")
            else:
                observation = f"Tool '{tool_name}' not found. Please choose from the available tools list."
                print(f"❌ {observation}")
                local_history += f"\nObservation: {observation}"

            # A simple heuristic to break the loop if the step seems complete.
            # A more advanced agent might let the LLM decide when the step is done.
            if "successfully" in observation.lower() or "done" in observation.lower() or "complete" in observation.lower():
                print(f"✅ Observation suggests the step is complete. Moving to the next step in the plan.")
                break

        return local_history, False, ""
