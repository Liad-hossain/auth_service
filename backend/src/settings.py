from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "copilot"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    worker_count: int = 1
    reload: bool = False

    # Database (optional - uncomment if needed)
    # database_url: str = "sqlite:///./app.db"

    # Security (optional - uncomment if needed)
    # secret_key: str = "your-secret-key"
    # access_token_expire_minutes: int = 30


settings = Settings()
