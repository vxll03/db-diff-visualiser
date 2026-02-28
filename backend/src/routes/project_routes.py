from fastapi import APIRouter

from src.dependencies import ProjectServiceDep
from src.schemas.api_schemas import (
    ProjectCreateSchema,
    ProjectResponseSchema,
    ProjectStatsResponseSchema,
    ProjectUpdateSchema,
)

router = APIRouter()


@router.get("", response_model=list[ProjectStatsResponseSchema])
async def get_project_list_w_stats(srv: ProjectServiceDep):
    return await srv.get_projects_with_stats()


@router.post("", status_code=201, response_model=ProjectResponseSchema)
async def create_project(srv: ProjectServiceDep, schema: ProjectCreateSchema):
    return await srv.create_project(name=schema.name, icon=schema.icon)


@router.patch("/{project_id}", response_model=ProjectResponseSchema)
async def update_project(
    srv: ProjectServiceDep, project_id: int, schema: ProjectUpdateSchema
):
    return await srv.update_project(project_id=project_id, schema=schema)


@router.delete("/{project_id}", status_code=204)
async def delete_project(srv: ProjectServiceDep, project_id: int):
    await srv.delete_project(project_id=project_id)
