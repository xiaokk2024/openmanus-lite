# OpenManus-Lite

这是一个 `OpenManus` 项目的轻量级复刻版本，旨在保留其核心的“规划-执行-总结”自主代理流程，同时简化项目结构，移除复杂的沙盒机制，并使用 Conda 进行环境管理。

这个精简版项目非常适合用于学习和理解自主代理（Autonomous Agent）的基本工作原理。

## 核心架构

`OpenManus-Lite` 的工作流包含三个核心阶段：

1.  **规划 (Planning):** `PlanningAgent` 接收用户的初始任务，并将其分解为一个清晰、可执行的步骤列表（Plan）。
2.  **执行 (Execution):** `ManusAgent` 遵循 ReAct (Reason+Act) 模式，逐一执行计划中的步骤。
3.  **总结 (Finishing):** 当所有计划步骤都完成后，代理会调用 `FinishTool`，输出最终的成果并结束任务。

## ⚠️ 安全警告

与原版 `OpenManus` 不同，此 Lite 版本**没有沙盒环境**。这意味着 `ShellTool` 和 `PythonTool` 会直接在您的本地机器上执行命令和代码。请确保您完全了解代理将要执行的任务，并只在可信的环境中运行此项目。

## 安装

1.  **克隆项目:**
    ```bash
    git clone <your-repo-url>
    cd openmanus-lite
    ```

2.  **创建 Conda 环境:**
    确保您已安装 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 Anaconda。然后运行以下命令来创建并激活环境：
    ```bash
    conda env create -f environment.yml
    conda activate openmanus-lite
    ```

3.  **配置 LLM:**
    打开 `config.toml` 文件，根据您的LLM提供商填入 `model`, `base_url`, 和 `api_key` 等信息。
    ```toml
    # openmanus-lite/config.toml
    [llm]
    model = "your-model-name"
    base_url = "your-api-endpoint-url"
    api_key = "your-secret-api-key" # 强烈建议使用环境变量
    # ...
    ```
    为了安全起见，您可以将`api_key`留空，然后在项目根目录创建一个 `.env` 文件，写入 `LLM_API_KEY="your-secret-api-key"`。程序会优先使用环境变量中的密钥。

## 如何使用

1.  **确保环境已激活:**
    ```bash
    conda activate openmanus-lite
    ```

2.  **定义任务并运行:**
    打开 `main.py` 文件，修改 `task` 变量，然后从终端运行：
    ```bash
    python main.py
    ```

3.  **观察输出:**
    代理的思考过程、行动和最终结果将会实时打印在控制台中。
