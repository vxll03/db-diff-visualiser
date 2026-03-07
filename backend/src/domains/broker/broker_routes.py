from fastapi import APIRouter, UploadFile

from src.dependencies import FileServiceDep, RabbitServiceDep
from src.domains.project.api_schemas import (
    MigrationUploadResponseSchema,
)
from src.utils.enums import RabbitTaskStatus

router = APIRouter()


@router.post(
    "/upload/{project_id}",
    response_model=MigrationUploadResponseSchema,
    status_code=201,
)
async def upload_migrations(
    files: list[UploadFile],
    rabbit_srv: RabbitServiceDep,
    migration_srv: FileServiceDep,
    project_id: int,
):
    prepared_data = await migration_srv.prepare_files(
        project_id=project_id, files=files
    )

    await rabbit_srv.publish_tasks(tasks=prepared_data)

    return {
        "status": RabbitTaskStatus.ACCEPTED,
        "processed_count": len(prepared_data),
        "details": [
            {
                "file": d["file"],
                "revision": d["revision"],
                "down_revision": d["down_revision"],
            }
            for d in prepared_data
        ],
    }
