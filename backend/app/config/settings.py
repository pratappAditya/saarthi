import os
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

config_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/app/app") and os.path.abspath(config_dir).startswith("/app"):
    project_root = "/app"
else:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(config_dir)))
env_path = os.path.join(project_root, ".env")

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    APP_NAME: str = "Saarthi"
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "none" if os.getenv("ENVIRONMENT", "development").lower() in ("staging", "production") else "mock")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "" if os.getenv("ENVIRONMENT", "development").lower() in ("staging", "production") else "mock-model")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    ALLOW_DEMO_FALLBACK: bool = False
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    MODEL_TEMPERATURE: float = 0.7
    MODEL_MAX_TOKENS: int = 512
    OLLAMA_THINK: bool = False
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    FEATURE_BILLING: bool = False
    PAYMENT_PROVIDER: str = "none"
    API_BASE_URL: str = ""
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH",
        os.path.join(os.getenv("SAARTHI_DATA_DIR", os.path.join(project_root, "data")), "database", "saarthi.db")
    )
    DATABASE_URL: str = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URI", ""))
    SAARTHI_DATA_DIR: str = os.getenv("SAARTHI_DATA_DIR", os.path.join(project_root, "data"))
    TRUSTED_PATHS: str = ""
    ALLOWED_ROOTS: list[str] = [project_root]
    VENDOR_ADMIN_KEY: str = os.getenv("VENDOR_ADMIN_KEY", os.getenv("ADMIN_SECRET_KEY", ""))
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "")
    # Tool System settings
    TOOL_ENABLED: bool = True
    TOOL_ROOT_PATH: str = project_root
    max_tool_iterations: int = 8
    MAX_TOOL_ITERATIONS: int = 8
    MAX_TOOL_OUTPUT_CHARS: int = 12000
    TERMINAL_TIMEOUT_SECONDS: int = 30
    TOOL_EXECUTION_TIMEOUT: float = 30.0
    MAX_AGENT_ITERATIONS: int = 6

    # Context & Prompt Optimization Settings
    MAX_HISTORY_MESSAGES: int = 8
    MAX_HISTORY_CHARS: int = 6000
    MAX_MEMORY_RESULTS: int = 5
    MAX_MEMORY_CONTEXT_CHARS: int = 3000
    MAX_TOOL_DESCRIPTION_CHARS: int = 2000
    COMPACT_SYSTEM_PROMPT: bool = True

    # Multi-Provider AI Model Settings
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    GLM_API_KEY: str = ""
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    KIMI_API_KEY: str = ""
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    MINIMAX_API_KEY: str = ""
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    LLAMA_API_KEY: str = ""
    LLAMA_BASE_URL: str = ""
    MODEL_TIMEOUT_SECONDS: float = 30.0
    MODEL_MAX_RETRIES: int = 2
    MODEL_PREFER_LOCAL: bool = True
    MODEL_FALLBACK_ORDER: list[str] = ["ollama", "groq", "deepseek", "qwen", "openrouter"]

    # MCP (Model Context Protocol) Settings
    MCP_ENABLED: bool = True
    MCP_DISCOVERY_TIMEOUT: float = 10.0
    MCP_TOOL_EXECUTION_TIMEOUT: float = 30.0
    MCP_ALLOW_STDIO_TRANSPORT: bool = True
    MCP_ALLOW_HTTP_TRANSPORT: bool = True
    MCP_TIER_C_AUTO_APPROVE: bool = False

    @model_validator(mode="after")
    def parse_trusted_paths(self) -> 'Settings':
        # Expand any environment variables in TRUSTED_PATHS (e.g. %USERPROFILE%)
        # and parse it as a list of roots if provided.
        trusted = self.TRUSTED_PATHS or os.getenv("TRUSTED_PATHS", "")
        if trusted:
            roots = []
            for p in trusted.split(";"):
                p = p.strip()
                if p:
                    # Replace newlines if formatted across lines
                    p = p.replace("\n", "").replace("\r", "")
                    expanded = os.path.expandvars(p)
                    roots.append(expanded)
            self.ALLOWED_ROOTS = roots
        return self

    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8", extra="ignore")

# Initialize global settings
settings = Settings()

