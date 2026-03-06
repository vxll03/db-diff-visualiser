from fastapi import APIRouter, Query

from src.dependencies import ProjectServiceDep
from src.domains.project.api_schemas import (
    LatestSnapshotsResponseSchema,
    SnapshotByDateResponseSchema,
    SnapshotResponseSchema,
    SnapshotTitleResponseSchema,
)

router = APIRouter()

@router.get("/latest", response_model=list[LatestSnapshotsResponseSchema])
async def get_latest_snapshot(
    srv: ProjectServiceDep, limit: int = Query(default=10, ge=1, le=20)
):
    return await srv.get_latest_snapshots(limit=limit)

@router.get("/count_by_date", response_model=list[SnapshotByDateResponseSchema])
async def get_snapshot_count_by_date(srv: ProjectServiceDep):
    return await srv.get_snapshot_count_by_date()

@router.get("/{project_id}", response_model=list[SnapshotTitleResponseSchema])
async def get_project_snapshots(project_id: int, srv: ProjectServiceDep):
    return await srv.get_snapshots_by_project(project_id=project_id)


@router.get("/{project_id}/{revision_id}", response_model=SnapshotResponseSchema)
async def get_project_snapshot(
    project_id: int, revision_id: int, srv: ProjectServiceDep
):
    return await srv.get_snapshot_by(project_id=project_id, id=revision_id)
