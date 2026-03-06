import datetime as dt

from pydantic import BaseModel, ConfigDict

from src.utils.enums import RabbitTaskStatus


class BaseOrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MigrationUploadDetailSchema(BaseModel):
    file: str
    revision: str
    down_revision: str | None

class MigrationUploadResponseSchema(BaseModel):
    status: RabbitTaskStatus
    processed_count: int
    details: list[MigrationUploadDetailSchema]


# region Projects
class ProjectCreateSchema(BaseModel):
    name: str
    icon: str | None

class ProjectUpdateSchema(BaseModel):
    name: str | None = None
    icon: str | None = None


class ProjectResponseSchema(BaseOrmModel):
    id: int
    name: str
    icon: str | None
    created_at: dt.datetime


class ProjectStatsResponseSchema(BaseOrmModel):
    id: int
    name: str
    icon: str | None
    created_at: dt.datetime
    snapshots_count: int
    tables_count: int
    views_count: int
    triggers_count: int
    mat_views_count: int
    functions_count: int

# endregion


# region Snapshots
class SnapshotResponseSchema(BaseOrmModel):
    id: int
    project_id: int
    created_at: dt.datetime
    revision_id: str
    prev_revision_id: str | None
    schema_data: dict
    diff_data: dict | None
    views_data: dict | None
    views_diff_data: dict | None
    functions_data: dict | None
    functions_diff_data: dict | None
    triggers_data: dict | None
    triggers_diff_data: dict | None

class SnapshotTitleResponseSchema(BaseOrmModel):
    id: int
    revision_id: str
    prev_revision_id: str | None
    created_at: dt.datetime


class LatestSnapshotsResponseSchema(BaseOrmModel):
    id: int
    revision_id: str
    project_id: int
    project_name: str
    created_at: dt.datetime


class SnapshotByDateResponseSchema(BaseOrmModel):
    date: dt.date
    count: int


# endregion
