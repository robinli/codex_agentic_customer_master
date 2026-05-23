from functools import lru_cache
import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./app.db"
    openai_api_key: str | None = None
    agent_model: str = "gpt-5.4-mini"
    agent_reasoning_effort: str = "medium"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    demo_users_json: str = json.dumps(
        [
            {
                "id": "00000000-0000-0000-0000-000000000010",
                "email": "admin@example.com",
                "name": "Admin User",
                "roles": ["admin"],
                "password": "admin1234",
            },
            {
                "id": "00000000-0000-0000-0000-000000000002",
                "email": "approver@example.com",
                "name": "Approver User",
                "roles": ["approver"],
                "password": "approver1234",
            },
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "email": "editor@example.com",
                "name": "Editor User",
                "roles": ["editor"],
                "password": "editor1234",
            },
            {
                "id": "00000000-0000-0000-0000-000000000003",
                "email": "viewer@example.com",
                "name": "Viewer User",
                "roles": ["viewer"],
                "password": "viewer1234",
            },
        ]
    )
    cors_origins: List[str] = ["http://localhost:3000"]
    default_page_size: int = 20
    max_page_size: int = 100

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
