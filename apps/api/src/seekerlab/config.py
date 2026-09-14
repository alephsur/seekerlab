from functools import lru_cache
from typing import Literal, Self
from urllib.parse import urlparse

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
    siws_domain: str = "localhost:8000"
    siws_uri: str = "http://localhost:8000"
    siws_statement: str = "Sign in to SeekerLab. This request does not authorize a payment."
    siws_chain_id: Literal["solana:devnet"] = "solana:devnet"
    siws_challenge_ttl_seconds: int = 300
    session_access_ttl_seconds: int = 900
    session_refresh_ttl_seconds: int = 2592000

    @model_validator(mode="after")
    def validate_dev_auth(self) -> Self:
        if self.dev_auth_enabled:
            if self.app_env == "production":
                raise ValueError("Development authentication cannot run in production")
            if min(len(self.dev_builder_token), len(self.dev_tester_token)) < 32:
                raise ValueError("Run scripts/bootstrap.py to create development tokens")
            if self.dev_builder_token == self.dev_tester_token:
                raise ValueError("Builder and tester tokens must be different")
        parsed_uri = urlparse(self.siws_uri)
        if (
            parsed_uri.netloc != self.siws_domain
            or parsed_uri.scheme not in {"http", "https"}
            or parsed_uri.username is not None
            or parsed_uri.password is not None
        ):
            raise ValueError("SIWS_DOMAIN must match the authority in SIWS_URI")
        if (
            not 1 <= len(self.siws_domain) <= 255
            or not 1 <= len(self.siws_uri) <= 512
            or not 1 <= len(self.siws_statement) <= 255
            or any(character in value for value in (
                self.siws_domain, self.siws_uri, self.siws_statement
            ) for character in "\r\n")
        ):
            raise ValueError("SIWS fields contain invalid characters or exceed their limits")
        if self.app_env == "production" and parsed_uri.scheme != "https":
            raise ValueError("SIWS_URI must use HTTPS in production")
        if not 60 <= self.siws_challenge_ttl_seconds <= 600:
            raise ValueError("SIWS challenge lifetime must be between 60 and 600 seconds")
        if not 300 <= self.session_access_ttl_seconds <= 3600:
            raise ValueError("Session access lifetime must be between 300 and 3600 seconds")
        if not 86400 <= self.session_refresh_ttl_seconds <= 7776000:
            raise ValueError("Session refresh lifetime must be between 1 and 90 days")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
