from collections import defaultdict
from datetime import timedelta
from typing import Sequence

from sqlalchemy import Interval, cast, delete, func, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domains.project.models import Project, Snapshot


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, name: str, icon: str | None = None) -> Project:
        project = Project(name=name, icon=icon)
        self.db.add(project)
        await self.db.flush()
        await self.db.commit()
        return project

    async def update_project(self, id, **kwargs) -> Project | None:
        stmt = (
            update(Project).values(**kwargs).where(Project.id == id).returning(Project)
        )
        query = await self.db.execute(stmt)
        await self.db.commit()
        return query.scalar_one_or_none()

    async def delete_project(self, id: int):
        stmt = delete(Project).where(Project.id == id)
        await self.db.execute(stmt)
        await self.db.commit()

    async def create_snapshot(
        self,
        rev_id: str,
        project_id: int,
        schema: dict,
        views,
        functions,
        triggers,
        views_diff,
        functions_diff,
        triggers_diff,
        prev_rev_id: str | None = None,
        diff: dict | None = None,
    ) -> None:
        snap = Snapshot(
            project_id=project_id,
            revision_id=rev_id,
            prev_revision_id=prev_rev_id,
            schema_data=schema,
            diff_data=diff,
            views_data=views,
            views_diff_data=views_diff,
            functions_data=functions,
            functions_diff_data=functions_diff,
            triggers_data=triggers,
            triggers_diff_data=triggers_diff,
        )
        self.db.add(snap)
        await self.db.commit()

    async def get_projects_with_stats(self):
        def json_len_fallback(column, key: str, label: str):
            return func.coalesce(func.jsonb_array_length(column[key]), 0).label(label)

        stmt = (
            select(
                Project,
                func.count(Snapshot.id)
                .over(partition_by=Project.id)
                .label("snapshots_count"),
                json_len_fallback(Snapshot.schema_data, "tables", "tables_count"),
                json_len_fallback(Snapshot.views_data, "views", "views_count"),
                json_len_fallback(
                    Snapshot.views_data, "materialized_views", "mat_views_count"
                ),
                json_len_fallback(Snapshot.triggers_data, "triggers", "triggers_count"),
                json_len_fallback(
                    Snapshot.functions_data, "functions", "functions_count"
                ),
            )
            .outerjoin(Snapshot, Project.id == Snapshot.project_id)
            .distinct(Project.id)
            .order_by(Project.id, Snapshot.id.desc().nulls_last())
        )

        result = await self.db.execute(stmt)
        return result.all()

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
        snapshots = result.scalars().all()
        if not snapshots:
            return []

        children_map = defaultdict(list)
        for s in snapshots:
            children_map[s.prev_revision_id].append(s)

        known_rev_ids = {s.revision_id for s in snapshots}
        roots = [s for s in snapshots if s.prev_revision_id not in known_rev_ids]

        roots.sort(key=lambda x: x.created_at)

        sorted_snapshots = []
        visited = set()

        def traverse(node: Snapshot):
            if node.revision_id in visited:
                return
            sorted_snapshots.append(node)
            visited.add(node.revision_id)

            children = sorted(
                children_map.get(node.revision_id, []), key=lambda x: x.created_at
            )
            for child in children:
                traverse(child)

        for root in roots:
            traverse(root)

        return sorted_snapshots

    async def get_snapshot_by(self, **kwargs) -> Snapshot | None:
        """Get Snapshot instance from db by any fields. \n
        If Snapshot count > 1 returns first \n
        If Snapshot count == 0 returns None
        """
        stmt = select(Snapshot).filter_by(**kwargs)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_latest_snapshots(self, limit: int = 10):
        stmt = (
            select(Snapshot)
            .options(joinedload(Snapshot.project))
            .order_by(Snapshot.id.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_snapshot_count_by_date(self):
        range_stmt = select(
            func.min(Snapshot.created_at), func.max(Snapshot.created_at)
        )

        range_res = await self.db.execute(range_stmt)
        min_date, max_date = range_res.fetchone() or (None, None)

        if not min_date or not max_date:
            return []

        delta = max_date - min_date
        if delta > timedelta(days=365):
            interval_type = "month"
        elif delta > timedelta(days=30):
            interval_type = "week"
        else:
            interval_type = "day"

        series = func.generate_series(
            func.date_trunc(interval_type, min_date),
            func.date_trunc(interval_type, max_date),
            cast(literal(f"1 {interval_type}"), Interval),
        ).column_valued("period")

        date_grid = select(series).cte("date_grid")

        stmt = (
            select(date_grid.c.period, func.count(Snapshot.id).label("count"))
            .select_from(date_grid)
            .outerjoin(
                Snapshot,
                (
                    func.date_trunc(interval_type, Snapshot.created_at)
                    == date_grid.c.period
                ),
            )
            .group_by(date_grid.c.period)
            .order_by(date_grid.c.period.asc())
        )

        result = await self.db.execute(stmt)

        return [{"date": r.period.date(), "count": r.count} for r in result.all()]
