from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Project, Snapshot


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, name: str) -> None:
        project = Project(name=name)
        self.db.add(project)
        await self.db.commit()

    async def create_snapshot(
        self,
        rev_id: str,
        project_id: int,
        schema: dict,
        prev_rev_id: str | None = None,
        diff: dict | None = None,
    ) -> None:
        snap = Snapshot(
            project_id=project_id,
            revision_id=rev_id,
            prev_revision_id=prev_rev_id,
            schema_data=schema,
            diff_data=diff,
        )
        self.db.add(snap)
        await self.db.commit()

    async def get_project(self, name: str) -> Project | None:
        stmt = select(Project).where(Project.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_projects(self):
        stmt = select(Project)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_project_by(self, **kwargs) -> Project | None:
        """Get Project instance from db by any fields. \n
        If project count > 1 returns first \n
        If project count == 0 returns None
        """
        stmt = select(Project).filter_by(**kwargs)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_snapshots_by_project(self, project_id: int) -> Sequence[Snapshot]:
        stmt = select(Snapshot).where(Snapshot.project_id == project_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_snapshot_by(self, **kwargs) -> Snapshot | None:
        """Get Snapshot instance from db by any fields. \n
        If Snapshot count > 1 returns first \n
        If Snapshot count == 0 returns None
        """
        stmt = select(Snapshot).filter_by(**kwargs)
        result = await self.db.execute(stmt)
        return result.scalars().first()
