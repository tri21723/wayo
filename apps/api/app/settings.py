from functools import lru_cache
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import AnyHttpUrl, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WAYO_",
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
        hide_input_in_errors=True,
    )

    database_url: str | None = Field(default=None, repr=False)
    supabase_url: AnyHttpUrl | None = None
    environment: Literal["local", "staging", "production"] = "local"
    admin_user_ids: list[UUID] = Field(default_factory=list)
    provider_timeout_seconds: float = Field(default=10, ge=1, le=30)
    provider_max_calls: int = Field(default=10, ge=1, le=100)
    providers_enabled: list[Literal["routing", "weather", "llm"]] = Field(default_factory=list)
    routing_base_url: AnyHttpUrl | None = None
    weather_base_url: AnyHttpUrl | None = None
    llm_api_key: SecretStr | None = Field(default=None, repr=False)
    llm_model: str | None = Field(default=None, min_length=1, max_length=100)
    llm_max_output_tokens: int = Field(default=512, ge=64, le=4096)

    @model_validator(mode="after")
    def deployment_settings(self):
        if self.environment != "local":
            if not self.database_url or not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Deployment requires PostgreSQL.")
            from sqlalchemy.engine import make_url

            if make_url(self.database_url).query.get("sslmode") not in (
                "require",
                "verify-ca",
                "verify-full",
            ):
                raise ValueError("Deployment requires database TLS.")
            if not self.supabase_url or self.supabase_url.scheme != "https":
                raise ValueError("Deployment requires HTTPS Supabase Auth.")
            for url in (self.routing_base_url, self.weather_base_url):
                if url is not None and url.scheme != "https":
                    raise ValueError("Deployment provider URLs must use HTTPS.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
