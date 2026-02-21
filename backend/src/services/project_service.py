from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Project, Snapshot
from src.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ProjectRepository(db)

    async def create_project(self, name: str):
        await self.repo.create_project(name)

    async def create_snapshot(
        self,
        rev_id: str,
        project_id: int,
        schema: dict,
        prev_rev_id: str | None = None,
        diff: dict | None = None,
    ):
        await self.repo.create_snapshot(
            rev_id=rev_id,
            project_id=project_id,
            schema=schema,
            prev_rev_id=prev_rev_id,
            diff=diff,
        )

    async def get_projects(self) -> Sequence[Project]:
        return await self.repo.get_projects()

    async def get_project_by_name(self, name: str) -> Project | None:
        return await self.repo.get_project_by(name=name)

    async def get_project_by_id(self, id: int) -> Project | None:
        return await self.repo.get_project_by(id=id)

    async def get_snapshots_by_project(self, project_id: int) -> Sequence[Snapshot]:
        return await self.repo.get_snapshots_by_project(project_id=project_id)
