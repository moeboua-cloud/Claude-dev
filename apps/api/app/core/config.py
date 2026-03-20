"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Agentic IAM Platform"
    app_version: str = "0.1.0"
    environment: Literal["local", "development", "staging", "production"] = "local"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Database
    database_url: str = "postgresql+asyncpg://iam_user:iam_pass@localhost:5432/agentic_iam"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth / JWT
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # LLM Provider
    llm_provider: Literal["openai", "anthropic", "mock"] = "mock"
    llm_model: str = "gpt-4"
    llm_api_key: str = ""
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # Action execution mode
    action_mode: Literal["read_only", "simulation", "approval_required", "execution"] = "simulation"

    # Connector mode
    connector_mode: Literal["mock", "live"] = "mock"

    model_config = {"env_prefix": "IAM_", "env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
