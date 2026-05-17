from pathlib import Path
from functools import lru_cache
from typing import Optional, Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


# ==========================================================
# LOAD .ENV
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ==========================================================
# SETTINGS
# ==========================================================

class Settings(BaseSettings):
    """
    Centralized application settings.
    """

    # ------------------------------------------------------
    # MODEL CONFIG
    # ------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ------------------------------------------------------
    # DATABASE
    # ------------------------------------------------------

    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL"
    )

    # ------------------------------------------------------
    # REDIS
    # ------------------------------------------------------

    redis_url: str = Field(
        default="redis://redis:6379/0",
        alias="REDIS_URL"
    )

    # ------------------------------------------------------
    # CELERY
    # ------------------------------------------------------

    celery_broker_url: str = Field(
        default="redis://redis:6379/0",
        alias="CELERY_BROKER_URL"
    )

    celery_result_backend: str = Field(
        default="redis://redis:6379/0",
        alias="CELERY_RESULT_BACKEND"
    )

    # ------------------------------------------------------
    # LLM PROVIDER
    # ------------------------------------------------------

    llm_provider: Literal[
        "groq",
        "openai"
    ] = Field(
        default="groq",
        alias="LLM_PROVIDER"
    )

    # ------------------------------------------------------
    # OPENAI
    # ------------------------------------------------------

    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY"
    )

    openai_model: str = Field(
        default="gpt-4o-mini",
        alias="OPENAI_MODEL"
    )

    # ------------------------------------------------------
    # GROQ
    # ------------------------------------------------------

    groq_api_key: Optional[str] = Field(
        default=None,
        alias="GROQ_API_KEY"
    )

    groq_model: str = Field(
        default="llama-3.1-8b-instant",
        alias="GROQ_MODEL"
    )

    # ------------------------------------------------------
    # LANGSMITH
    # ------------------------------------------------------

    langsmith_api_key: Optional[str] = Field(
        default=None,
        alias="LANGSMITH_API_KEY"
    )

    langsmith_project: str = Field(
        default="test-case-generator",
        alias="LANGSMITH_PROJECT"
    )

    # ------------------------------------------------------
    # DOCKER
    # ------------------------------------------------------

    docker_sandbox_image: str = Field(
        default="python:3.11-slim",
        alias="DOCKER_SANDBOX_IMAGE"
    )

    # ------------------------------------------------------
    # FILE UPLOADS
    # ------------------------------------------------------

    upload_dir: str = Field(
        default="/tmp/uploads",
        alias="UPLOAD_DIR"
    )

    max_file_size: int = Field(
        default=104857600,
        alias="MAX_FILE_SIZE"
    )

    # ------------------------------------------------------
    # VALIDATION HELPERS
    # ------------------------------------------------------

    @property
    def has_groq_key(self) -> bool:

        return bool(
            self.groq_api_key
            and self.groq_api_key.startswith("gsk_")
        )

    @property
    def has_openai_key(self) -> bool:

        return bool(
            self.openai_api_key
            and self.openai_api_key.startswith("sk-")
        )


# ==========================================================
# SETTINGS SINGLETON
# ==========================================================

@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()