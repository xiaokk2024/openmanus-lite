import os
import toml
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists.
# This is useful for keeping API keys out of version control.
load_dotenv()

# --- Configuration Class ---
class Config:
    def __init__(self, config_path="config.toml"):
        """Loads configuration from a TOML file and environment variables."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        # Load the TOML configuration file
        with open(config_path, 'r', encoding='utf-8') as f:
            toml_config = toml.load(f)

        # --- LLM Configuration ---
        llm_config = toml_config.get("llm", {})
        # Prioritize environment variable for API key for better security
        self.LLM_API_KEY = os.getenv("LLM_API_KEY", llm_config.get("api_key"))
        self.LLM_BASE_URL = llm_config.get("base_url")
        self.LLM_MODEL = llm_config.get("model")
        self.LLM_MAX_TOKENS = llm_config.get("max_tokens", 4096)
        self.LLM_TEMPERATURE = llm_config.get("temperature", 0.1)

        # --- Workspace Configuration ---
        self.WORKSPACE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workspace")

    def check_config(self):
        """Checks if essential configurations are set."""
        if not self.LLM_API_KEY:
            print("❌ Error: LLM API key is not configured.")
            print("Please set it in config.toml or as an LLM_API_KEY environment variable.")
            return False
        if not self.LLM_BASE_URL:
            print("❌ Error: LLM base_url is not configured in config.toml.")
            return False
        if not self.LLM_MODEL:
            print("❌ Error: LLM model is not configured in config.toml.")
            return False

        # Ensure the workspace directory exists
        if not os.path.exists(self.WORKSPACE_PATH):
            print(f"📂 Workspace directory not found, creating it at: {self.WORKSPACE_PATH}")
            os.makedirs(self.WORKSPACE_PATH)

        return True

# Create a global config instance to be used throughout the application
try:
    AppConfig = Config()
except FileNotFoundError as e:
    print(f"❌ {e}")
    AppConfig = None

