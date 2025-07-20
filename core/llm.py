import openai
from config import AppConfig

# --- 初始化 OpenAI 客户端 ---
# 此代码块现在根据加载的配置动态配置客户端。
def get_llm_client():
    """根据全局配置初始化并返回 OpenAI 客户端。"""
    if not AppConfig or not AppConfig.check_config():
        print("❌ 由于缺少配置，无法初始化 LLM 客户端。")
        return None

    try:
        client = openai.OpenAI(
            base_url=AppConfig.LLM_BASE_URL,
            api_key=AppConfig.LLM_API_KEY,
        )
        print("✅ LLM 客户端初始化成功。")
        return client
    except Exception as e:
        print(f"❌ 初始化 OpenAI 客户端失败：{e}")
        return None

# 导入模块时初始化客户端
client = get_llm_client()

def call_llm(prompt: str, instructions: str = "你是一个乐于助人的助手。") -> str:
    """
    一个调用大型语言模型 (LLM) 的通用函数。
    它现在使用全局配置的客户端和参数。
    """
    if not client:
        error_msg = "LLM 客户端未初始化。请检查您的配置。"
        print(f"❌ {error_msg}")
        return f"错误：{error_msg}"

    print("\n" + "="*50)
    print(f"🤖 正在调用 LLM (模型: {AppConfig.LLM_MODEL})...")
    print(f"系统指令 (截断): {instructions[:150]}...")
    print(f"用户提示 (截断): {prompt[:200]}...")
    print("="*50 + "\n")

    try:
        response = client.chat.completions.create(
            model=AppConfig.LLM_MODEL,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
            ],
            max_tokens=AppConfig.LLM_MAX_TOKENS,
            temperature=AppConfig.LLM_TEMPERATURE,
        )
        content = response.choices[0].message.content

        print("\n" + "*"*50)
        print("✅ LLM 响应:")
        print(content)
        print("*"*50 + "\n")

        return content.strip() if content else "错误：LLM 返回了空响应。"

    except openai.APIError as e:
        error_message = f"OpenAI API 错误：{e}"
        print(f"❌ {error_message}")
        return f"错误：{error_message}"
    except Exception as e:
        error_message = f"调用 LLM 时发生意外错误：{e}"
        print(f"❌ {error_message}")
        return f"错误：{error_message}"
