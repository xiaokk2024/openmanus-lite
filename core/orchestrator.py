from agents.planning_agent import PlanningAgent
from agents.manus_agent import ManusAgent
from tools.file_tools import ReadFileTool, WriteFileTool, ListFilesTool
from tools.shell_tool import ShellTool
from tools.python_tool import PythonTool
from tools.finish_tool import FinishTool

class Orchestrator:
    """
    The main task orchestrator.
    It receives an initial task, coordinates the PlanningAgent and ManusAgent,
    and drives the entire workflow to completion.
    """
    def __init__(self, task: str):
        """
        Initializes the Orchestrator.

        Args:
            task (str): The initial user-defined task.
        """
        self.task = task
        self.planning_agent = PlanningAgent()

        # Initialize all available tools for the execution agent
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
        """A simple parser to convert the LLM's plan string into a list of steps."""
        if not plan_str or "Error:" in plan_str:
            return []

        steps = []
        for line in plan_str.split('\n'):
            line = line.strip()
            # This regex looks for lines starting with a number followed by a dot or parenthesis, or a hyphen.
            # e.g., "1. ", "1) ", "- "
            if line and (line[0].isdigit() or line.startswith('-')):
                # Clean up the prefix to get the actual step description
                step_description = ".".join(line.split('.')[1:]).strip()
                if not step_description: # Handle cases like "- step"
                    step_description = " ".join(line.split(' ')[1:]).strip()
                if step_description:
                    steps.append(step_description)

        # If parsing fails, treat the whole string as a single-step plan
        return steps if steps else [plan_str]

    def run(self):
        """
        Starts and executes the entire task workflow.
        """
        print("="*50)
        print(f"🎬 Starting new task: {self.task}")
        print("="*50 + "\n")

        # 1. Planning Phase
        print("\n" + "-"*20 + " Phase 1: Task Planning " + "-"*20)
        plan_str = self.planning_agent.create_plan(self.task)
        plan = self._parse_plan(plan_str)

        if not plan:
            print("❌ Planning failed. Could not generate a valid plan. Terminating.")
            return "Error: Planning failed."

        print("✅ Task planning complete. The plan is as follows:")
        for i, step in enumerate(plan, 1):
            print(f"  - Step {i}: {step}")
        print("-" * 50 + "\n")

        # 2. Execution Phase
        print("\n" + "-"*20 + " Phase 2: Plan Execution " + "-"*20)

        full_history = ""
        for i, step_description in enumerate(plan, 1):
            print(f"\n▶️ Executing Step {i}/{len(plan)}: {step_description}")
            print("-" * 40)

            # Call ManusAgent to execute a single step.
            # It returns the history of thoughts/actions for the step, and a flag indicating if the task is finished.
            step_history, finished, final_summary = self.manus_agent.run_step(
                task=self.task,
                plan=plan,
                current_step_index=i,
                previous_steps_history=full_history
            )

            # Append the history of the completed step to the full history for context in the next step.
            full_history += step_history + "\n\n"

            # If the agent called the FinishTool, end the process early.
            if finished:
                print("\n" + "="*50)
                print(f"✅ Task finished early by agent!")
                print(f"Final Summary: {final_summary}")
                print("="*50 + "\n")
                return final_summary

        # This part is reached if the agent completes all steps without calling the FinishTool.
        # This might indicate a flawed plan, but we can return the full history as the result.
        print("\n" + "="*50)
        print("🏁 All plan steps have been executed.")
        print("The 'finish' tool was not called, which might indicate an incomplete plan.")
        print("Returning the full execution history as the result.")
        print("="*50 + "\n")
        return full_history
