import json
import re
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile
from loguru import logger

from src.core.config import settings
from src.domains.project.services.project_service import ProjectService
from src.domains.broker.rabbit_schemas import IncomingMessageSchema


class FileService:
    def __init__(self, project_srv: ProjectService):
        self.project_srv = project_srv

    async def prepare_files(
        self, project_id: int, files: list[UploadFile]
    ) -> list[dict]:
        if not files:
            raise HTTPException(422, "No files provided")

        project = await self.project_srv.get_project_by_id(project_id)
        if not project:
            raise HTTPException(404, "Project not found")

        project_dir = settings.SHARED_MIGRATIONS_DIR / project.name / "input"
        project_dir.mkdir(parents=True, exist_ok=True)

        processed_files = []

        for file in files:
            if not file.filename:
                continue

            file_path = project_dir / file.filename
            try:
                with file_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                logger.error(f"Failed to save file {file.filename}: {e}")
                raise HTTPException(500, f"Could not save file {file.filename}") from e

            revision, down_revision = self._extract_revisions(file_path)
            processed_files.append(
                {
                    "file": file.filename,
                    "revision": revision,
                    "down_revision": down_revision,
                    "project_name": project.name,
                }
            )

        return processed_files

    def _extract_revisions(self, file_path: Path) -> tuple[str, str | None]:
        try:
            content = file_path.read_text()
            rev_match = re.search(
                r"revision\s*(?::\s*[^=]+)?\s*=\s*['\"]([^'\"]+)['\"]", content
            )
            down_rev_match = re.search(
                r"down_revision\s*(?::\s*[^=]+)?\s*=\s*['\"]([^'\"]+)['\"]|down_revision\s*=\s*None",
                content,
            )

            if not rev_match:
                raise HTTPException(
                    422, f"Invalid migration file {file_path.name} (revision not found)"
                )

            revision = rev_match.group(1)
            down_revision = (
                down_rev_match.group(1)
                if down_rev_match and down_rev_match.group(1)
                else None
            )

            return revision, down_revision
        except Exception as e:
            logger.error(f"Failed to parse revisions from {file_path}: {e}")
            raise HTTPException(422, "Error parsing migration file")

    async def process_schema(self, message: IncomingMessageSchema):
        project = await self.project_srv.get_project_by_name(message.project)
        if not project:
            logger.error(f"Project not found by name: {message.project}")
            return

        out_dir = settings.SHARED_MIGRATIONS_DIR / project.name / "output"
        rev = message.revision_id

        schema_data = self._load_and_clean(out_dir / f"{rev}_schema.json")
        if not schema_data:
            return

        views_data = self._load_and_clean(out_dir / f"{rev}_views.json")
        funcs_data = self._load_and_clean(out_dir / f"{rev}_functions.json")
        triggers_data = self._load_and_clean(out_dir / f"{rev}_triggers.json")

        schema_diff = self._load_and_clean(out_dir / f"{rev}_diff.json")
        views_diff = self._load_and_clean(out_dir / f"{rev}_views_diff.json")
        funcs_diff = self._load_and_clean(out_dir / f"{rev}_functions_diff.json")
        triggers_diff = self._load_and_clean(out_dir / f"{rev}_triggers_diff.json")

        await self.project_srv.create_snapshot(
            project_id=project.id,
            rev_id=rev,
            prev_rev_id=message.prev_revision_id,
            schema=schema_data,
            views=views_data,
            functions=funcs_data,
            triggers=triggers_data,
            diff=schema_diff,
            views_diff=views_diff,
            functions_diff=funcs_diff,
            triggers_diff=triggers_diff,
        )

    def _load_and_clean(self, filepath: Path) -> dict | None:
        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            filepath.unlink()
            return data
        except Exception as e:
            logger.error(f"Failed to process file {filepath.name}: {e}")
            return None
