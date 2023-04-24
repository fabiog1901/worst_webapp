from fastapi import APIRouter, Depends, Security
from uuid import UUID

from worst_crm import db
from worst_crm.dependencies import get_current_active_user
from worst_crm.models import NewProject, Project

router = APIRouter(
    prefix="/projects",
    # dependencies=[Depends(get_current_active_user)],
    tags=['projects'],
)



@router.get("/{account_id}")
async def get_all_projects(account_id: UUID) -> list[Project]:

    return db.get_all_projects(account_id)


@router.get("/{account_id}/{project_id}")
async def get_project(account_id: UUID, project_id: UUID) -> Project | None:

    return db.get_project(account_id, project_id)


# , dependencies=[Security(get_current_active_user, scopes=["rw"])])
@router.post("/{account_id}")
async def create_Project(account_id: UUID, new_project: NewProject) -> Project | None:

    return db.create_project(account_id, new_project)


# , dependencies=[Security(get_current_active_user, scopes=["rw"])])
@router.put("/{account_id}/{project_id}")
async def update_Project(account_id: UUID, project_id: UUID, project: NewProject) -> Project | None:

    return db.update_project(account_id, project_id, project)


# , dependencies=[Security(get_current_active_user, scopes=["rw"])])
@router.delete("/{account_id}/{project_id}")
async def delete_Project(account_id: UUID, project_id: UUID) -> Project | None:

    return db.delete_project(account_id, project_id)
