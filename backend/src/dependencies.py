from typing import Annotated

from fastapi import Depends

from src.core.database import DatabaseDep
from src.domains.broker.services.file_service import FileService
from src.domains.broker.services.rabbit_service import RabbitService
from src.domains.project.services.project_service import ProjectService


def get_rabbit_service() -> RabbitService:
    return RabbitService()


RabbitServiceDep = Annotated[RabbitService, Depends(get_rabbit_service)]


def get_project_service(db: DatabaseDep) -> ProjectService:
    return ProjectService(db=db)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


def get_file_service(project_srv: ProjectServiceDep) -> FileService:
    return FileService(project_srv=project_srv)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
