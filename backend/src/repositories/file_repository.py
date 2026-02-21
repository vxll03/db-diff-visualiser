from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Project, Snapshot


class FileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, name: str):
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
    ):
        snap = Snapshot(
            project_id=project_id,
            revision_id=rev_id,
            prev_revision_id=prev_rev_id,
            schema_data=schema,
            diff_data=diff,
        )
        self.db.add(snap)
        await self.db.commit()

    async def get_project(self, name: str):
        stmt = select(Project).where(Project.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
