from functools import lru_cache
from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://seekerlab:seekerlab@localhost:5432/seekerlab"
    dev_auth_enabled: bool = False
    dev_builder_token: str = ""
    dev_tester_token: str = ""
    cors_origins: list[str] = []

    @model_validator(mode="after")
    def validate_dev_auth(self) -> Self:
        if self.dev_auth_enabled:
            if self.app_env == "production":
                raise ValueError("Development authentication cannot run in production")
            if min(len(self.dev_builder_token), len(self.dev_tester_token)) < 32:
                raise ValueError("Run scripts/bootstrap.py to create development tokens")
            if self.dev_builder_token == self.dev_tester_token:
                raise ValueError("Builder and tester tokens must be different")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
