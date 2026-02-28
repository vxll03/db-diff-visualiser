import abc
import json
import uuid
from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError

from src.core.config import settings


class BaseSnapshotWorker(abc.ABC):
    def __init__(self, work_dir: Path):
        self._work_dir = work_dir
        self.shared_dir = settings.SHARED_MIGRATIONS_DIR

    def process(self, project_name: str, target_revision: str):
        task_id = uuid.uuid4().hex[:8]
        temp_db_name = f"task_{project_name}_{task_id}"

        base_url_obj = make_url(settings.PG_URL)
        temp_db_url = base_url_obj.set(database=temp_db_name).render_as_string(
            hide_password=False
        )

        admin_engine = create_engine(
            base_url_obj.set(database="postgres"), isolation_level="AUTOCOMMIT"
        )

        try:
            with admin_engine.connect() as conn:
                conn.execute(text(f'CREATE DATABASE "{temp_db_name}"'))

            rev_id, prev_rev_id = self._perform_snapshot(
                db_url=temp_db_url,
                project_name=project_name,
                target_revision=target_revision,
            )

            return (rev_id, prev_rev_id)

        except Exception as e:
            logger.exception(f"Error processing {project_name}: {e}")
        finally:
            self._cleanup_db(admin_engine, temp_db_name)

    def _cleanup_db(self, admin_engine, db_name: str):
        try:
            with admin_engine.connect() as conn:
                conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE)'))
            logger.debug(f"Temporary DB: {db_name} deleted")
        except OperationalError:
            pass
        except Exception as e:
            logger.error(f"Error deleting DB {db_name}: {e}")
        finally:
            admin_engine.dispose()

    def _save_json(self, data, path: Path):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"File saved: {path.name}")

    @abc.abstractmethod
    def _perform_snapshot(
        self, db_url: str, project_name: str, target_revision: str
    ) -> tuple[str, str | None]:
        pass
