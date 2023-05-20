from fastapi import APIRouter, Depends, Security, Query
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID
from backend import db
import datetime as dt
from backend.models import (
    Project,
    NewProject,
    ProjectFilters,
    ProjectInDB,
    ProjectOverview,
    ProjectOverviewWithAccountName,
    UpdatedProject,
    User,
)
import json
import backend.dependencies as dep

router = APIRouter(
    prefix="/projects",
    dependencies=[Depends(dep.get_current_user)],
    tags=["projects"],
)


# CRUD
@router.get("")
async def get_all_projects(
    name: Annotated[list[str], Query()] = [],
    owned_by: Annotated[list[str], Query()] = [],
    due_date_from: dt.date | None = None,
    due_date_to: dt.date | None = None,
    status: Annotated[list[str], Query()] = [],
    tags: Annotated[list[str], Query()] = [],
    attachments: Annotated[list[str], Query()] = [],
    created_at_from: dt.date | None = None,
    created_at_to: dt.date | None = None,
    created_by: Annotated[list[str], Query()] = [],
    updated_at_from: dt.date | None = None,
    updated_at_to: dt.date | None = None,
    updated_by: Annotated[list[str], Query()] = [],
) -> list[ProjectOverviewWithAccountName]:
    # TODO possibly using elasticsearch for text/data columns?

    project_filters = ProjectFilters()

    if name:
        project_filters.name = name
    if owned_by:
        project_filters.owned_by = owned_by
    if due_date_from:
        project_filters.due_date_from = due_date_from
    if due_date_to:
        project_filters.due_date_to = due_date_to
    if status:
        project_filters.status = status
    if tags:
        project_filters.tags = tags
    if attachments:
        project_filters.attachments = attachments
    if created_at_from:
        project_filters.created_at_from = created_at_from
    if created_at_to:
        project_filters.created_at_to = created_at_to
    if created_by:
        project_filters.created_by = created_by
    if updated_at_from:
        project_filters.updated_at_from = updated_at_from
    if updated_at_to:
        project_filters.updated_at_to = updated_at_to
    if updated_by:
        project_filters.updated_by = updated_by

    return db.get_all_projects(project_filters)


@router.get("/{account_id}")
async def get_all_projects_for_account_id(
    account_id: UUID,
) -> list[ProjectOverview]:
    return db.get_all_projects_for_account_id(account_id)


@router.get("/{account_id}/{project_id}")
async def get_project(account_id: UUID, project_id: UUID) -> Project | None:
    return db.get_project(account_id, project_id)


@router.post(
    "/{account_id}", dependencies=[Security(dep.get_current_user, scopes=["rw"])]
)
async def create_project(
    account_id: UUID,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> NewProject | None:
    project_in_db = ProjectInDB(
        created_by=current_user.user_id, updated_by=current_user.user_id
    )  # type: ignore

    return db.create_project(account_id, project_in_db)


@router.put(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_project(
    account_id: UUID,
    project_id: UUID,
    project: UpdatedProject,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Project | None:
    project_in_db = ProjectInDB(
        **project.dict(exclude_unset=True, exclude={"data"}),
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


# Attachements
@router.get(
    "/{account_id}/{project_id}/presigned-get-url/{filename}",
    name="Get pre-signed URL for downloading an attachment",
)
async def get_presigned_get_url(account_id: UUID, project_id: UUID, filename: str):
    s3_object_name = str(account_id) + "/" + str(project_id) + "/" + filename
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/{account_id}/{project_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    name="Get pre-signed URL for uploading an attachment",
)
async def get_presigned_put_url(account_id: UUID, project_id: UUID, filename: str):
    s3_object_name = str(account_id) + "/" + str(project_id) + "/" + filename
    db.add_project_attachment(account_id, project_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/{account_id}/{project_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement(account_id: UUID, project_id: UUID, filename: str):
    s3_object_name = str(account_id) + "/" + str(project_id) + "/" + filename
    db.remove_project_attachment(account_id, project_id, filename)
    dep.s3_remove_object(s3_object_name)
