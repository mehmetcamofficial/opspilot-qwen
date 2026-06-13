from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "OpsPilot Backend"
    APP_ENV: str = "dev"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    QWEN_API_BASE: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    QWEN_API_KEY: str = "replace_me"
    QWEN_MODEL: str = "qwen-plus"

    USE_MOCK_LLM: bool = True
    FALLBACK_TO_MOCK_ON_ERROR: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
