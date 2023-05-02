from fastapi import APIRouter, Depends, Security
from uuid import UUID

from worst_crm import db
import worst_crm.dependencies as dep
from worst_crm.models import NewProject, Project

router = APIRouter(
    prefix="/projects",
    dependencies=[Depends(dep.get_current_active_user)],
    tags=["projects"],
)


@router.get("/{account_id}")
async def get_all_projects(account_id: UUID) -> list[Project]:
    return db.get_all_projects(account_id)


@router.get("/{account_id}/{project_id}")
async def get_project(account_id: UUID, project_id: UUID) -> Project | None:
    return db.get_project(account_id, project_id)


@router.post(
    "/{account_id}", dependencies=[Security(dep.get_current_active_user, scopes=["rw"])]
)
async def create_Project(account_id: UUID, project: NewProject) -> Project | None:
    return db.create_project(account_id, project)


@router.put(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def update_Project(
    account_id: UUID, project_id: UUID, project: NewProject
) -> Project | None:
    return db.update_project(account_id, project_id, project)


@router.delete(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def delete_Project(account_id: UUID, project_id: UUID) -> Project | None:
    return db.delete_project(account_id, project_id)
