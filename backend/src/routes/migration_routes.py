from fastapi import APIRouter, Query, UploadFile

from dependencies import FileServiceDep, ProjectServiceDep, RabbitServiceDep
from src.schemas.api_schemas import (
    MigrationUploadResponseSchema,
    ProjectResponseSchema,
    SnapshotResponseSchema,
)
from src.utils.enums import RabbitTaskStatus

router = APIRouter()


@router.post(
    "/migrations/upload_new",
    response_model=MigrationUploadResponseSchema,
    status_code=201,
)
async def upload_migrations(
    file: UploadFile,
    rabbit_srv: RabbitServiceDep,
    migration_srv: FileServiceDep,
    project_name: str = Query(...),
):
    revision = await migration_srv.prepare_file(project_name=project_name, file=file)
    await rabbit_srv.publish_task(project_name=project_name, revision=revision)

    return {
        "status": RabbitTaskStatus.ACCEPTED,
        "project": project_name,
        "file": file.filename,
        "revision": revision,
    }


@router.get("/projects", response_model=list[ProjectResponseSchema])
async def get_project_list(srv: ProjectServiceDep):
    return await srv.get_projects()


@router.get("/snapshots/{project_id}", response_model=list[SnapshotResponseSchema])
async def get_project_snapshots(project_id: int, srv: ProjectServiceDep):
    return await srv.get_snapshots_by_project(project_id=project_id)
