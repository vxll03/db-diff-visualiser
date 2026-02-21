import json
import os
import re
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile
from loguru import logger

from src.core.config import settings
from src.schemas.rabbit_schemas import IncomingMessageSchema
from src.services.project_service import ProjectService


class FileService:
    def __init__(self, project_srv: ProjectService):
        self.project_srv = project_srv

    async def prepare_file(self, project_name: str, file: UploadFile):
        if not file.filename:
            raise HTTPException(422, "filename not found")

        if not await self.project_srv.get_project_by_name(project_name):
            await self.project_srv.create_project(project_name)

        project_dir = settings.SHARED_MIGRATIONS_DIR / project_name / "input"
        project_dir.mkdir(parents=True, exist_ok=True)

        file_path = project_dir / file.filename

        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            raise HTTPException(500, "Could not save migration file") from e

        revision = self._extract_revision(file_path)

        return revision

    def _extract_revision(self, file_path: Path) -> str:
        try:
            content = file_path.read_text()
            match = re.search(r"revision\s*[:=]\s*['\"]([^'\"]+)['\"]", content)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"Failed to parse revision from {file_path}: {e}")
        raise HTTPException(422, 'Invalid migration file (revision not found)')


    async def process_schema(self, message: IncomingMessageSchema):
        project = await self.project_srv.get_project_by_name(message.project)
        if not project:
            logger.error(f'Project not found by name: {message.project}')
            return

        project_dir = settings.SHARED_MIGRATIONS_DIR / project.name / "output"
        schema = project_dir / f'{message.revision_id}_schema.json'
        diff = project_dir / f'{message.revision_id}_diff.json'

        schema_data, diff_data = None, None
        with open(schema, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
        if diff.exists():
            with open(diff, 'r', encoding='utf-8') as f:
                diff_data = json.load(f)

        await self.project_srv.create_snapshot(
            project_id=project.id,
            rev_id=message.revision_id,
            prev_rev_id=message.prev_revision_id,
            schema=schema_data,
            diff=diff_data,
        )

        os.remove(schema)
        if diff.exists():
            os.remove(diff)
