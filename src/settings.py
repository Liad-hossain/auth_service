import multiprocessing
from urllib.parse import quote_plus

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    base_url: str = "http://localhost:8000"

    # Application
    app_name: str = "copilot"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    worker_count: int = multiprocessing.cpu_count() * 2 + 1
    reload: bool = False

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "copilot"
    MASTER_DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/copilot?sslmode=disable"
    )

    @property
    def database_url(self) -> AnyUrl:
        return AnyUrl.build(
            scheme="postgresql",
            username=self.db_user,
            password=quote_plus(self.db_password),
            host=self.db_host,
            port=self.db_port,
            path=self.db_name,
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "password"
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{quote_plus(self.redis_password)}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # JWT Security
    authentication_secret_key: str
    authentication_algorithm: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 1


settings = Settings()
