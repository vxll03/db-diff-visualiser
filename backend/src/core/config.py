from pathlib import Path

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=5432, ge=1, le=65535)
    USER: str = Field(default="postgres")
    PASS: SecretStr = Field(...)
    NAME: str = Field(...)
    ECHO: bool = Field(default=False)

    @computed_field(return_type=str)
    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"

    @computed_field(return_type=str)
    @property
    def SYNC_DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"

    model_config = SettingsConfigDict(env_prefix="DB__", extra="ignore")


class RabbitSettings(BaseSettings):
    URL: str = Field("amqp://guest:guest@rabbitmq:5672/")
    MIGRATION_TASK_QUEUE: str = "migration_tasks"
    TASK_RESULT_QUEUE: str = "task_results"

    model_config = SettingsConfigDict(env_prefix="RABBIT__", extra="ignore")


class ApplicationSettings(BaseSettings):
    SHARED_MIGRATIONS_DIR: Path = Field(default=Path("/app/migrations_storage"))
    CORS_ORIGINS: list[str] = Field(default=["localhost:*"])

    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_nested_delimiter='__',
        case_sensitive=False,
        env_file_encoding='utf-8',
    )

settings = ApplicationSettings()
