# -*- coding: utf-8 -*-
from core.llm import call_llm
from agents.prompts import PLANNING_INSTRUCTIONS

class PlanningAgent:
    """
    计划智能体。
    负责接收用户任务并创建可执行的步骤序列。
    """
    def create_plan(self, task: str) -> str:
        """
        根据用户任务生成执行计划

        参数:
            task (str): 用户定义的任务描述

        返回:
            str: 由LLM生成的计划字符串，每行表示一个步骤
        """
        print("🤔 PlanningAgent正在规划任务执行方案...")

        # 构建计划提示
        prompt = f"这是我的任务需求: '{task}'\n\n请为我创建一个详细的分步骤计划。"

        # 调用LLM生成计划
        plan_str = call_llm(prompt, instructions=PLANNING_INSTRUCTIONS)

        return plan_str