import openai
from config import AppConfig

# --- Initialize OpenAI Client ---
# This block now dynamically configures the client based on the loaded config.
def get_llm_client():
    """Initializes and returns the OpenAI client based on global configuration."""
    if not AppConfig or not AppConfig.check_config():
        print("❌ LLM Client cannot be initialized due to missing configuration.")
        return None

    try:
        client = openai.OpenAI(
            base_url=AppConfig.LLM_BASE_URL,
            api_key=AppConfig.LLM_API_KEY,
        )
        print("✅ LLM Client initialized successfully.")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return None

# Initialize the client when the module is imported
client = get_llm_client()

def call_llm(prompt: str, instructions: str = "You are a helpful assistant.") -> str:
    """
    A general-purpose function to call the Large Language Model (LLM).
    It now uses the globally configured client and parameters.
    """
    if not client:
        error_msg = "LLM client is not initialized. Please check your configuration."
        print(f"❌ {error_msg}")
        return f"Error: {error_msg}"

    print("\n" + "="*50)
    print(f"🤖 Calling LLM (Model: {AppConfig.LLM_MODEL})...")
    print(f"System Instructions (truncated): {instructions[:150]}...")
    print(f"User Prompt (truncated): {prompt[:200]}...")
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
        print("✅ LLM Response:")
        print(content)
        print("*"*50 + "\n")

        return content.strip() if content else "Error: LLM returned an empty response."

    except openai.APIError as e:
        error_message = f"OpenAI API Error: {e}"
        print(f"❌ {error_message}")
        return f"Error: {error_message}"
    except Exception as e:
        error_message = f"An unexpected error occurred while calling the LLM: {e}"
        print(f"❌ {error_message}")
        return f"Error: {error_message}"
