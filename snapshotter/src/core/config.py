from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitSettings(BaseSettings):
    URL: str = Field("amqp://guest:guest@rabbitmq:5672/")
    MIGRATION_TASK_QUEUE: str = "migration_tasks"
    TASK_RESULT_QUEUE: str = "task_results"

    model_config = SettingsConfigDict(env_prefix="RABBIT__", extra="ignore")


class ApplicationSettings(BaseSettings):
    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)

    PG_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@postgres:5432/postgres"
    )
    SHARED_MIGRATIONS_DIR: Path = Field(default=Path("/app/migrations_storage"))

    ALEMBIC_INI_PATH: str = Field(default="/app/alembic.ini")
    ALEMBIC_VERSIONS_DIRNAME: str = Field(default="alembic/versions")

    model_config = SettingsConfigDict(env_file=None, extra="ignore")


settings = ApplicationSettings()
