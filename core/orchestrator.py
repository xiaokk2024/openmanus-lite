import logging
from agents.planning_agent import PlanningAgent
from agents.manus_agent import ManusAgent
from tools.file_tools import ReadFileTool, WriteFileTool, ListFilesTool
from tools.shell_tool import ShellTool
from tools.python_tool import PythonTool
from tools.finish_tool import FinishTool

class Orchestrator:
    """
    主任务编排器。
    它接收一个初始任务，协调 PlanningAgent 和 ManusAgent，
    并驱动整个工作流程直至完成。
    """
    def __init__(self, task: str):
        """
        初始化编排器。

        参数:
            task (str): 用户定义的初始任务。
        """
        self.task = task
        self.planning_agent = PlanningAgent()

        # 为执行智能体初始化所有可用工具
        self.tools = [
            ReadFileTool(),
            WriteFileTool(),
            ListFilesTool(),
            ShellTool(),
            PythonTool(),
            FinishTool()
        ]
        self.manus_agent = ManusAgent(self.tools)

    def _parse_plan(self, plan_str: str) -> list[str]:
        """一个简单的解析器，用于将 LLM 的计划字符串转换为步骤列表。"""
        if not plan_str or "错误:" in plan_str:
            return []

        steps = []
        for line in plan_str.split('\n'):
            line = line.strip()
            # 这个正则表达式查找以数字后跟点或括号，或以连字符开头的行。
            # 例如 "1. ", "1) ", "- "
            if line and (line[0].isdigit() or line.startswith('-')):
                # 清理前缀以获取实际的步骤描述
                step_description = ".".join(line.split('.')[1:]).strip()
                if not step_description: # 处理像 "- 步骤" 这样的情况
                    step_description = " ".join(line.split(' ')[1:]).strip()
                if step_description:
                    steps.append(step_description)

        # 如果解析失败，则将整个字符串视为单步计划
        return steps if steps else [plan_str]

    def run(self):
        """
        启动并执行整个任务工作流程。
        """
        logging.info("="*50)
        logging.info(f"🎬 开始新任务: {self.task}")
        logging.info("="*50 + "\n")

        # 1. 规划阶段
        logging.info("\n" + "-"*20 + " 阶段 1: 任务规划 " + "-"*20)
        plan_str = self.planning_agent.create_plan(self.task)
        plan = self._parse_plan(plan_str)

        if not plan:
            logging.error("❌ 规划失败。无法生成有效计划。正在终止。")
            return "错误：规划失败。"

        logging.info("✅ 任务规划完成。计划如下:")
        for i, step in enumerate(plan, 1):
            logging.info(f"  - 步骤 {i}: {step}")
        logging.info("-" * 50 + "\n")

        # 2. 执行阶段
        logging.info("\n" + "-"*20 + " 阶段 2: 计划执行 " + "-"*20)

        full_history = ""
        for i, step_description in enumerate(plan, 1):
            logging.info(f"\n▶️ 正在执行步骤 {i}/{len(plan)}: {step_description}")
            logging.info("-" * 40)

            # 调用 ManusAgent 来执行单个步骤。
            # 它返回该步骤的思考/操作历史记录，以及一个指示任务是否完成的标志。
            step_history, finished, final_summary = self.manus_agent.run_step(
                task=self.task,
                plan=plan,
                current_step_index=i,
                previous_steps_history=full_history
            )

            # 将已完成步骤的历史记录附加到完整历史记录中，以便在下一步骤中作为上下文。
            full_history += step_history + "\n\n"

            # 如果智能体调用了 FinishTool，则提前结束流程。
            if finished:
                logging.info("\n" + "="*50)
                logging.info(f"✅ 代理已提前完成任务！")
                logging.info(f"最终总结: {final_summary}")
                logging.info("="*50 + "\n")
                return final_summary

        # 如果代理在没有调用 FinishTool 的情况下完成了所有步骤，则会执行到这部分。
        # 这可能表示计划有缺陷，但我们可以将完整的历史记录作为结果返回。
        logging.info("\n" + "="*50)
        logging.info("🏁 所有计划步骤均已执行。")
        logging.info("未调用 'finish' 工具，这可能表示计划不完整。")
        logging.info("将返回完整的执行历史记录作为结果。")
        logging.info("="*50 + "\n")
        return full_history
