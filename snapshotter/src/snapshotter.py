import asyncio
import json
import shutil
import uuid
from enum import Enum
from pathlib import Path

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from alembic.config import Config
from alembic.script import ScriptDirectory
from loguru import logger
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError

from alembic import command
from src.core.config import settings
from src.diff import SchemaDiff


class SnapshotWorker:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.shared_dir = settings.SHARED_MIGRATIONS_DIR
        self.alembic_versions_dir = self.work_dir / settings.ALEMBIC_VERSIONS_DIRNAME
        self.connection = None

    async def run(self):
        self.connection = await aio_pika.connect_robust(settings.rabbit.URL)
        async with self.connection:
            channel = await self.connection.channel()
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(
                settings.rabbit.MIGRATION_TASK_QUEUE, durable=True
            )
            logger.info("Worker started...")

            await queue.consume(self._process_task)
            await asyncio.Future()

    async def _process_task(self, message: AbstractIncomingMessage):
        async with message.process():
            data = json.loads(message.body.decode())
            project_name = data.get("project")
            if not project_name:
                logger.error("Project name not found in task payload")
                return

            target_revision = data.get("target_revision", "head")

            task_id = uuid.uuid4().hex[:8]
            temp_db_name = f"task_{project_name}_{task_id}"

            base_url_obj = make_url(settings.PG_URL)
            temp_db_url = base_url_obj.set(database=temp_db_name).render_as_string(
                hide_password=False
            )

            logger.info(f"Task started for: {project_name} in: {temp_db_name}")

            self._prepare_task_migrations(project_name)

            admin_engine = create_engine(
                base_url_obj.set(database="postgres"), isolation_level="AUTOCOMMIT"
            )

            try:
                with admin_engine.connect() as conn:
                    conn.execute(text(f'CREATE DATABASE "{temp_db_name}"'))

                rev_id, prev_rev_id = self._get_snapshot(
                    db_url=temp_db_url,
                    project_name=project_name,
                    target_revision=target_revision,
                )

                await self._send_result_signal(
                    project_name=project_name,
                    revision_id=rev_id,
                    prev_revision_id=prev_rev_id,
                )

                logger.info(f"Snapshot completed for: {project_name} ({rev_id})")
            except Exception as e:
                logger.exception(f"Error processing {project_name}: {e}")
            finally:
                try:
                    with admin_engine.connect() as conn:
                        conn.execute(
                            text(
                                f'DROP DATABASE IF EXISTS "{temp_db_name}" WITH (FORCE)'
                            )
                        )
                    logger.debug(f"Temporary DB: {temp_db_name} deleted")
                except OperationalError:
                    pass
                except Exception as e:
                    logger.error(
                        f"Error while deleting DB {temp_db_name} occurred: {e}"
                    )
                admin_engine.dispose()

    async def _send_result_signal(
        self, project_name: str, revision_id: str, prev_revision_id: str | None
    ):
        if not self.connection:
            return

        payload = {
            "project": project_name,
            "revision_id": revision_id,
            "prev_revision_id": prev_revision_id,
        }

        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="task_results",
            )

    def _prepare_task_migrations(self, project_name: str):
        project_dir = self.shared_dir / project_name / "input"

        if not project_dir.exists():
            raise Exception("Migrations not found")

        for f in self.alembic_versions_dir.glob("*.py"):
            f.unlink()

        for file in project_dir.glob("*.py"):
            shutil.copy(file, self.alembic_versions_dir)

    def _get_snapshot(self, db_url: str, project_name: str, target_revision: str):
        cfg = Config(settings.ALEMBIC_INI_PATH)
        cfg.set_main_option("sqlalchemy.url", db_url)

        script = ScriptDirectory.from_config(cfg)

        if target_revision == "head":
            head_rev = script.get_current_head()
            if not head_rev:
                raise Exception("No migrations found")
            script_obj = script.get_revision(head_rev)
        else:
            script_obj = script.get_revision(target_revision)

        if not script_obj:
            raise Exception(f"Revision {target_revision} not found")

        current_rev = script_obj.revision
        down_rev = script_obj.down_revision

        if isinstance(down_rev, tuple):
            down_rev = down_rev[0]

        project_output_dir = self.shared_dir / project_name / "output"
        project_output_dir.mkdir(parents=True, exist_ok=True)

        if down_rev:
            logger.info(f"Incremental migration: {down_rev} -> {current_rev}")

            command.upgrade(cfg, down_rev)
            old_schema = self._capture_schema(db_url)

            command.upgrade(cfg, current_rev)
            new_schema = self._capture_schema(db_url)

            diff_engine = SchemaDiff(old_schema, new_schema)
            diff_result = diff_engine.compare()
            self._save_json(diff_result, project_output_dir / f"{current_rev}_diff.json")
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

    def _save_json(self, data, path: Path):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"File saved: {path.name}")
