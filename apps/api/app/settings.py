from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WAYO_",
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
    )

    database_url: str | None = Field(default=None, repr=False)
    supabase_url: AnyHttpUrl | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
