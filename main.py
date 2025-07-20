import sys
from core.orchestrator import Orchestrator
from config import AppConfig

def main():
    """
    应用程序的主入口函数。
    """
    # 1. 检查配置是否成功加载
    if not AppConfig:
        print("❌ 致命错误：无法加载配置。程序退出。")
        sys.exit(1)

    # 检查大模型配置
    if not AppConfig.check_config():
        sys.exit(1)

    # ==========================================================================
    # 在此定义希望代理完成的任务
    # ==========================================================================
    # 示例任务 1：简单文件操作
    # task = "在工作区创建一个名为'hello.txt'的文件，写入'Hello, OpenManus-Lite!'"

    # 示例任务 2：使用Python工具进行计算
    task = "使用Python计算123乘以456的结果，并将最终答案写入名为'calculation_result.txt'的文件"
    # ==========================================================================

    # 2. 初始化并运行编排器
    print(f"🚀 智能体开始任务：{task}")
    orchestrator = Orchestrator(task=task)
    final_result = orchestrator.run()

    # 3. 打印最终结果
    print("\n\n" + "#"*20 + " 任务最终结果 " + "#"*20)
    print(final_result if final_result else "任务未返回明确的最终结果")
    print("#"*58)


if __name__ == "__main__":
    main()