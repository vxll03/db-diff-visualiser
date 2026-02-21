import datetime as dt

from pydantic import BaseModel, ConfigDict

from src.utils.enums import RabbitTaskStatus


class BaseOrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MigrationUploadResponseSchema(BaseModel):
    status: RabbitTaskStatus
    project: str
    file: str
    revision: str


class ProjectResponseSchema(BaseOrmModel):
    id: int
    name: str
    created_at: dt.datetime

class SnapshotResponseSchema(BaseOrmModel):
    id: int
    project_id: int
    created_at: dt.datetime
    revision_id: str
    prev_revision_id: str | None
    schema_data: dict
    diff_data: dict | None
