# -*- coding: utf-8 -*-
import json
import re
from typing import List, Dict, Any, Tuple

from core.llm import call_llm
from agents.prompts import MANUS_INSTRUCTIONS, MANUS_PROMPT_TEMPLATE
from tools.base_tool import BaseTool

class ManusAgent:
    """
    核心执行智能体(基于ReAct机制)。
    通过思考-行动的循环流程按照计划执行任务步骤。
    """
    def __init__(self, tools: List[BaseTool]):
        """
        初始化ManusAgent

        参数:
            tools (List[BaseTool]): 所有可用工具实例的列表
        """
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.tools_description = self._get_tools_description()
        self.tools_list = self._get_tools_list()

    def _get_tools_description(self) -> str:
        """生成所有工具的描述字符串，用于系统提示"""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])

    def _get_tools_list(self) -> str:
        """生成包含工具名称和参数的用户提示列表"""
        return "\n".join([
            f"  - {tool.name}({tool.get_args_str()}): {tool.description}"
            for tool in self.tools
        ])

    def _find_json_block(self, text: str) -> Dict[str, Any]:
        """从LLM响应中提取第一个有效的JSON块"""
        # 使用正则表达式查找被```json ... ```包裹的JSON块
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ 警告：找到JSON代码块但解析失败。错误: {e}。原始内容: {json_str}")
                # 继续尝试解析整个文本

        # 如果未找到代码块或解析失败，尝试将整个字符串解析为JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"❌ 无法从LLM响应解析JSON: {text}")
            return None

    def run_step(self, task: str, plan: List[str], current_step_index: int, previous_steps_history: str) -> Tuple[str, bool, str]:
        """
        执行计划中的单个步骤

        参数:
            task (str): 原始顶级任务描述
            plan (List[str]): 完整计划步骤列表
            current_step_index (int): 当前要执行的步骤索引(从1开始)
            previous_steps_history (str): 所有先前步骤的执行历史记录

        返回:
            包含以下元素的元组:
            - step_history (str): 当前步骤的完整执行历史(思考+行动+观察)
            - finished (bool): 表示是否调用"finish"工具的标识
            - final_summary (str): 若调用"finish"工具则返回最终摘要
        """
        current_step = plan[current_step_index - 1]
        plan_str = "\n".join(f"{i}. {s}" for i, s in enumerate(plan, 1))

        local_history = ""
        max_loops = 10  # 防止单个步骤陷入无限循环

        for i in range(max_loops):
            print(f"\n🔄 ManusAgent思考循环 {i+1}/{max_loops}，当前步骤 {current_step_index}...")

            prompt = MANUS_PROMPT_TEMPLATE.format(
                task=task,
                plan=plan_str,
                history=previous_steps_history + local_history,
                current_step=f"{current_step_index}. {current_step}",
                tools_list=self.tools_list
            )

            # 从LLM获取下一步行动
            llm_response = call_llm(prompt, instructions=MANUS_INSTRUCTIONS.format(tools_description=self.tools_description))

            if "Error:" in llm_response:
                observation = f"LLM调用失败。详情: {llm_response}"
                local_history += f"\nObservation: {observation}"
                continue

            action_json = self._find_json_block(llm_response)

            if not action_json:
                observation = "无效操作格式。请严格使用指定JSON格式响应，包含`thought`和`action`键。"
                local_history += f"\nObservation: {observation}"
                continue

            thought = action_json.get("thought", "[未提供思考内容]")
            action = action_json.get("action", {})
            tool_name = action.get("name")
            tool_args = action.get("args", {})

            print(f"🤔 思考: {thought}")
            print(f"🎬 行动: 调用工具`{tool_name}`，参数: {tool_args}")

            local_history += f"\nThought: {thought}\nAction: {json.dumps(action_json, indent=2, ensure_ascii=False)}"

            if tool_name in self.tool_map:
                tool = self.tool_map[tool_name]
                try:
                    observation = tool.execute(**tool_args)
                    print(f"👀 观察: {observation}")
                except Exception as e:
                    observation = f"执行工具'{tool_name}'出错: {e}"
                    print(f"❌ {observation}")

                local_history += f"\nObservation: {observation}"

                if tool.name == "finish":
                    return local_history, True, tool_args.get("summary", "未提供摘要")
            else:
                observation = f"未找到工具'{tool_name}'。请从可用工具列表中选择。"
                print(f"❌ {observation}")
                local_history += f"\nObservation: {observation}"

            # 简单的启发式规则，当观察表明步骤完成时跳出循环
            # 更高级的智能体可以让LLM决定何时步骤完成
            if "successfully" in observation.lower() or "done" in observation.lower() or "complete" in observation.lower():
                print(f"✅ 观察表明步骤已完成。继续执行计划中的下一步。")
                break

        return local_history, False, ""