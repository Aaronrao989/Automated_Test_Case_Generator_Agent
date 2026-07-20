"""Centralized application configuration.

Values come from environment variables (or an optional ``.env`` for local
development). Only settings the running application actually uses are declared.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Query params that appear in copy-paste Supabase URLs but that libpq/psycopg2
# does not accept as connection options.
_UNSUPPORTED_DB_PARAMS = {"pgbouncer"}

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Database -------------------------------------------------------
    database_url: str = Field(default="sqlite:///./dev.db", alias="DATABASE_URL")

    # --- LLM ------------------------------------------------------------
    llm_provider: Literal["groq"] = Field(default="groq", alias="LLM_PROVIDER")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_MODEL")
    llm_batch_size: int = Field(default=3, alias="LLM_BATCH_SIZE")

    # --- CORS -----------------------------------------------------------
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    # --- Uploads / analysis limits -------------------------------------
    upload_dir: str = Field(default="/tmp/uploads", alias="UPLOAD_DIR")
    max_file_size: int = Field(default=15 * 1024 * 1024, alias="MAX_FILE_SIZE")
    max_files_to_analyze: int = Field(default=15, alias="MAX_FILES_TO_ANALYZE")
    max_functions_to_analyze: int = Field(default=10, alias="MAX_FUNCTIONS_TO_ANALYZE")

    # --- Environment ----------------------------------------------------
    environment: Literal["development", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def has_groq_key(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.startswith("gsk_"))

    @property
    def cors_origin_list(self) -> List[str]:
        # Strip whitespace and any trailing slash so exact-match works.
        return [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Render/Heroku hand out legacy "postgres://" URLs SQLAlchemy rejects.
        if value.startswith("postgres://"):
            value = value.replace("postgres://", "postgresql://", 1)
        # Drop query params psycopg2 can't parse (e.g. Supabase's ?pgbouncer=true).
        parts = urlsplit(value)
        if parts.query:
            kept = [(k, v) for k, v in parse_qsl(parts.query) if k not in _UNSUPPORTED_DB_PARAMS]
            value = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept), parts.fragment))
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
