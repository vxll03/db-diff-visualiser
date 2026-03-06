import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import DbModel


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Project(DbModel, IdMixin):
    __tablename__ = "projects"
    __table_args__ = (Index("idx_project_name", "name"),)

    name: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    icon: Mapped[str | None] = mapped_column(String)

    snapshots = relationship(
        "Snapshot",
        back_populates="project",
    )


class Snapshot(DbModel, IdMixin):
    __tablename__ = "snapshots"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT")
    )

    # Example: "a18e39ae"
    revision_id: Mapped[str] = mapped_column(String)
    prev_revision_id: Mapped[str | None] = mapped_column(String)

    schema_data: Mapped[dict] = mapped_column(JSONB)
    diff_data: Mapped[dict | None] = mapped_column(JSONB)

    views_data: Mapped[dict | None] = mapped_column(JSONB)
    views_diff_data: Mapped[dict | None] = mapped_column(JSONB)

    functions_data: Mapped[dict | None] = mapped_column(JSONB)
    functions_diff_data: Mapped[dict | None] = mapped_column(JSONB)

    triggers_data: Mapped[dict | None] = mapped_column(JSONB)
    triggers_diff_data: Mapped[dict | None] = mapped_column(JSONB)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    project = relationship("Project", back_populates="snapshots")
