from fastapi import Security, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import (
    Project,
    ProjectFilters,
    ProjectInDB,
    ProjectOverview,
    ProjectOverviewWithAccountName,
    ProjectOverviewWithOpportunityName,
    UpdatedProject,
    User,
)
import worst_crm.dependencies as dep

NAME = "projects"

router = dep.get_api_router(NAME)


@router.get(
    "",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_projects(
    project_filters: ProjectFilters | None = None,
) -> list[ProjectOverviewWithAccountName]:
    return db.get_all_projects(project_filters)


@router.get(
    "/{account_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_projects_for_account_id(
    account_id: UUID,
    project_filters: ProjectFilters | None = None,
) -> list[ProjectOverviewWithOpportunityName]:
    return db.get_all_projects_for_account_id(account_id, project_filters)


@router.get(
    "/{account_id}/{opportunity_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_projects_for_opportunity_id(
    account_id: UUID,
    opportunity_id: UUID,
) -> list[ProjectOverview]:
    return db.get_all_projects_for_opportunity_id(account_id, opportunity_id)


@router.get(
    "/{account_id}/{opportunity_id}/{project_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_project(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
) -> Project | None:
    return db.get_project(account_id, opportunity_id, project_id)


@router.post(
    "",
    description="`project_id` will be generated if not provided by client.",
)
async def create_project(
    proj: UpdatedProject,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Project | None:
    project_in_db = ProjectInDB(
        **proj.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not project_in_db.project_id:
        project_in_db.project_id = uuid4()

    pro = db.create_project(project_in_db)
    
    if pro:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "create_project",
            pro.model_dump_json()
        )
        
    return pro


@router.put(
    "",
)
async def update_project(
    project: UpdatedProject,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task = BackgroundTasks,
) -> Project | None:
    project_in_db = ProjectInDB(
        **project.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    pro = db.update_project(project_in_db)
    
    if pro:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "update_project",
            pro.model_dump_json()
        )
        
    return pro


@router.delete(
    "/{account_id}/{opportunity_id}/{project_id}",
)
async def delete_project(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Project | None:
    
    pro = db.delete_project(account_id, opportunity_id, project_id)
    
    if pro:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "delete_project",
            pro.model_dump_json()
        )
    
    return pro


# Attachements
@router.get(
    "/{account_id}/{opportunity_id}/{project_id}/presigned-get-url/{filename}",
    name="Get pre-signed URL for downloading an attachment",
    dependencies=[Security(dep.get_current_user)],
)
async def get_presigned_get_url(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    filename: str,
):
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + filename
    )
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/{account_id}/{opportunity_id}/{project_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    name="Get pre-signed URL for uploading an attachment",
)
async def get_presigned_put_url(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    filename: str,
):
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + filename
    )
    db.add_project_attachment(account_id, opportunity_id, project_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/{account_id}/{opportunity_id}/{project_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    filename: str,
):
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + filename
    )
    db.remove_project_attachment(account_id, opportunity_id, project_id, filename)
    dep.s3_remove_object(s3_object_name)
