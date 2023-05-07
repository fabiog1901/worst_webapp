from fastapi import APIRouter, Depends, Security
from typing import Annotated
from uuid import UUID
from worst_crm import db
from worst_crm.models import Project, NewProject, ProjectInDB, User
import json
import worst_crm.dependencies as dep

router = APIRouter(
    prefix="/projects",
    dependencies=[Depends(dep.get_current_user)],
    tags=["projects"],
)


@router.get("/{account_id}")
async def get_all_projects(account_id: UUID) -> list[Project]:
    return db.get_all_projects(account_id)


@router.get("/{account_id}/{project_id}")
async def get_project(account_id: UUID, project_id: UUID) -> Project | None:
    return db.get_project(account_id, project_id)


@router.post(
    "/{account_id}", dependencies=[Security(dep.get_current_user, scopes=["rw"])]
)
async def create_project(
    account_id: UUID,
    project: NewProject,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Project | None:
    project_in_db = ProjectInDB(
        **project.dict(exclude={"data"}),
        data=json.dumps(project.data),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    return db.create_project(account_id, project_in_db)


@router.put(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_project(
    account_id: UUID,
    project_id: UUID,
    project: NewProject,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Project | None:
    project_in_db = ProjectInDB(
        **project.dict(exclude={"data"}),
        data=json.dumps(project.data),
        updated_by=current_user.user_id
    )

    return db.update_project(account_id, project_id, project_in_db)


@router.delete(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_project(account_id: UUID, project_id: UUID) -> Project | None:
    return db.delete_project(account_id, project_id)
