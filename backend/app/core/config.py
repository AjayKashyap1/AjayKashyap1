from functools import lru_cache
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "QC Intel"
    environment: str = "production"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    backend_cors_origins: list[AnyHttpUrl] | list[str] = []
    openai_api_key: str | None = None

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()
