from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL

PROJECT_DIR = Path(__file__).parent.parent.parent


class OpenAIConfig(BaseModel):
    api_key: str = ""


class Database(BaseModel):
    hostname: str = "postgres"
    username: str = "postgres"
    password: SecretStr
    port: int = 5432
    name: str = "postgres"
    default_db: str = "postgres"


class Settings(BaseSettings):
    open_ai_config: OpenAIConfig
    database: Database

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_database_uri(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.database.username,
            password=self.database.password.get_secret_value(),
            host=self.database.hostname,
            port=self.database.port,
            database=self.database.name,
        )

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_sync_database_uri(self) -> URL:
        return URL.create(
            drivername="postgresql",
            username=self.database.username,
            password=self.database.password.get_secret_value(),
            host=self.database.hostname,
            port=self.database.port,
            database=self.database.name,
        )

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_sync_default_database_uri(self) -> URL:
        return URL.create(
            drivername="postgresql",
            username=self.database.username,
            password=self.database.password.get_secret_value(),
            host=self.database.hostname,
            port=self.database.port,
            database=self.database.default_db,
        )

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_DIR}/.env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
