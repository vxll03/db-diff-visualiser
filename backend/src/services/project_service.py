from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Project, Snapshot
from src.repositories.project_repository import ProjectRepository
from src.schemas.api_schemas import LatestSnapshotsResponseSchema, ProjectUpdateSchema


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = ProjectRepository(db)

    async def create_project(self, name: str, icon: str | None = None) -> Project:
        return await self._repo.create_project(name=name, icon=icon)

    async def update_project(
        self, project_id: int, schema: ProjectUpdateSchema
    ) -> Project:
        project = await self._repo.update_project(
            id=project_id, **schema.model_dump(exclude_unset=True)
        )
        if not project:
            raise HTTPException(404, "Project ont found")
        return project

    async def delete_project(self, project_id):
        await self._repo.delete_project(id=project_id)

    async def create_snapshot(
        self,
        rev_id: str,
        project_id: int,
        schema: dict,
        prev_rev_id: str | None = None,
        diff: dict | None = None,
    ):
        await self._repo.create_snapshot(
            rev_id=rev_id,
            project_id=project_id,
            schema=schema,
            prev_rev_id=prev_rev_id,
            diff=diff,
        )

    async def get_projects_with_stats(self):
        projects = await self._repo.get_projects_with_stats()
        return [
            {
                **project_obj.__dict__,
                "snapshots_count": snap_count,
                "tables_count": t_count,
                "views_count": v_count,
                "triggers_count": tr_count,
                "mat_views_count": mv_count,
            }
            for project_obj, snap_count, t_count, v_count, tr_count, mv_count in projects
        ]

    async def get_project_by_name(self, name: str) -> Project | None:
        return await self._repo.get_project_by(name=name)

    async def get_project_by_id(self, id: int) -> Project | None:
        return await self._repo.get_project_by(id=id)

    async def get_snapshots_by_project(self, project_id: int) -> Sequence[Snapshot]:
        return await self._repo.get_snapshots_by_project(project_id=project_id)

    async def get_snapshot_by(self, **kwargs) -> Snapshot | None:
        return await self._repo.get_snapshot_by(**kwargs)

    async def get_latest_snapshots(self, limit: int = 10):
        snapshots = await self._repo.get_latest_snapshots(limit=limit)
        return [
            LatestSnapshotsResponseSchema(
                id=s.id,
                revision_id=s.revision_id,
                project_id=s.project_id,
                project_name=s.project.name,
                created_at=s.created_at,
            )
            for s in snapshots
        ]

    async def get_snapshot_count_by_date(self):
        return await self._repo.get_snapshot_count_by_date()
