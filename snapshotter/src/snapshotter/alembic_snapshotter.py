import shutil
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from loguru import logger
from sqlalchemy import create_engine, inspect

from alembic import command
from src.core.config import settings
from src.diff_checker import SchemaDiff
from src.snapshotter.base_snapshotter import BaseSnapshotWorker


class AlembicSnapshotter(BaseSnapshotWorker):
    def __init__(self, work_dir: Path):
        super().__init__(work_dir)
        self.alembic_versions_dir = self._work_dir / settings.ALEMBIC_VERSIONS_DIRNAME

    def _perform_snapshot(
        self, db_url: str, project_name: str, target_revision: str
    ) -> tuple[str, str | None]:
        self._prepare_task_migrations(project_name)
        return self._get_snapshot(db_url, project_name, target_revision)

    def _prepare_task_migrations(self, project_name: str):
        project_dir = self.shared_dir / project_name / "input"
        if not project_dir.exists():
            raise Exception("Migrations not found")

        for f in self.alembic_versions_dir.glob("*.py"):
            f.unlink()

        for file in project_dir.glob("*.py"):
            shutil.copy(file, self.alembic_versions_dir)

    def _get_snapshot(
        self, db_url: str, project_name: str, target_revision: str
    ) -> tuple[str, str | None]:
        cfg = Config(settings.ALEMBIC_INI_PATH)
        cfg.set_main_option("sqlalchemy.url", db_url)
        script = ScriptDirectory.from_config(cfg)

        script_obj = script.get_revision(
            script.get_current_head() if target_revision == "head" else target_revision
        )
        if not script_obj:
            raise Exception(f"Revision {target_revision} not found")

        current_rev = script_obj.revision
        down_rev = (
            script_obj.down_revision[0]
            if isinstance(script_obj.down_revision, (tuple, list))
            else script_obj.down_revision
        )

        project_output_dir = self.shared_dir / project_name / "output"
        project_output_dir.mkdir(parents=True, exist_ok=True)

        if down_rev:
            logger.info(f"Incremental migration: {down_rev} -> {current_rev}")
            command.upgrade(cfg, down_rev)
            old_schema = self._capture_schema(db_url)
            command.upgrade(cfg, current_rev)
            new_schema = self._capture_schema(db_url)

            diff_engine = SchemaDiff(old_schema, new_schema)
            self._save_json(
                diff_engine.compare(), project_output_dir / f"{current_rev}_diff.json"
            )
        else:
            logger.info(f"Base migration: {current_rev}")
            command.upgrade(cfg, current_rev)
            new_schema = self._capture_schema(db_url)

        self._save_json(new_schema, project_output_dir / f"{current_rev}_schema.json")
        return current_rev, down_rev

    def _capture_schema(self, db_url: str):
        engine = create_engine(db_url)
        inspector = inspect(engine)
        snapshot = {"tables": []}

        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append(
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": str(col["default"]) if col.get("default") else None,
                    }
                )
            snapshot["tables"].append(
                {
                    "name": table_name,
                    "columns": columns,
                    "primary_key": inspector.get_pk_constraint(table_name).get(
                        "constrained_columns", []
                    ),
                    "foreign_keys": [
                        {
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"],
                        }
                        for fk in inspector.get_foreign_keys(table_name)
                    ],
                }
            )
        return snapshot
