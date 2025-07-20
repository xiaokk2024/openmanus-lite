import sys
from core.orchestrator import Orchestrator
from config import AppConfig # Import the global config instance

def main():
    """
    The main entry point of the application.
    """
    # 1. Check if the configuration was loaded successfully
    if not AppConfig:
        print("❌ Fatal Error: Could not load configuration. Exiting.")
        sys.exit(1)

    # The check is now handled inside the get_llm_client function,
    # but we can do an initial check here for a clearer exit message.
    if not AppConfig.check_config():
        sys.exit(1)

    # ==========================================================================
    # Define the task you want the agent to accomplish here
    # ==========================================================================
    # Example Task 1: Simple file operation
    # task = "Create a file named 'hello.txt' in the workspace, write 'Hello, OpenManus-Lite!' into it, and then verify its content."

    # Example Task 2: Using shell commands and file I/O
    task = "做一个黄伟文经典作品展的网站"

    # Example Task 3: Using the Python tool for calculations
    # task = "Use Python to calculate the result of 123 multiplied by 456, and write the final answer into a file named 'calculation_result.txt'."
    # ==========================================================================

    # 2. Initialize and run the orchestrator
    print(f"🚀 Starting agent to accomplish task: {task}")
    orchestrator = Orchestrator(task=task)
    final_result = orchestrator.run()

    # 3. Print the final result
    print("\n\n" + "#"*20 + " Task Final Result " + "#"*20)
    print(final_result if final_result else "The task did not return a definitive final result.")
    print("#"*58)


if __name__ == "__main__":
    main()
