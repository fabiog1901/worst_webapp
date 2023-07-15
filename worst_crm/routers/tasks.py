from fastapi import Security, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import (
    Task,
    TaskFilters,
    UpdatedTask,
    TaskInDB,
    TaskOverview,
    TaskOverviewWithProjectName,
    User,
)
import worst_crm.dependencies as dep
import inspect

NAME = __name__.split(".")[-1]

router = dep.get_api_router(NAME)


@router.get(
    "/{account_id}/{opportunity_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_tasks_for_opportunity_id(
    account_id: UUID,
    opportunity_id: UUID,
    task_filters: TaskFilters | None = None,
) -> list[TaskOverviewWithProjectName]:
    return db.get_all_tasks_for_opportunity_id(account_id, opportunity_id, task_filters)


@router.get(
    "/{account_id}/{opportunity_id}/{project_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_tasks_for_project_id(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
) -> list[TaskOverview]:
    return db.get_all_tasks_for_project_id(account_id, opportunity_id, project_id)


@router.get(
    "/{account_id}/{opportunity_id}/{project_id}/{task_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_task(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
) -> Task | None:
    return db.get_task(account_id, opportunity_id, project_id, task_id)


@router.post(
    "",
    description="`task_id` will be generated if not provided by client.",
)
async def create_task(
    task: UpdatedTask,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Task | None:
    task_in_db = TaskInDB(
        **task.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not task_in_db.task_id:
        task_in_db.task_id = uuid4()

    x = db.create_task(task_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.put(
    "",
)
async def update_task(
    task: UpdatedTask,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Task | None:
    task_in_db = TaskInDB(**task.model_dump(), updated_by=current_user.user_id)

    x = db.update_task(task_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/{account_id}/{opportunity_id}/{project_id}/{task_id}",
)
async def delete_task(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Task | None:
    x = db.delete_task(account_id, opportunity_id, project_id, task_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


# Attachments
@router.get(
    "/{account_id}/{opportunity_id}/{project_id}/{task_id}/presigned-get-url/{filename}",
    name="Get pre-signed URL for downloading an attachment",
    dependencies=[Security(dep.get_current_user)],
)
async def get_presigned_get_url(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    filename: str,
):
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + str(task_id)
        + "/"
        + filename
    )
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/{account_id}/{opportunity_id}/{project_id}/{task_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    name="Get pre-signed URL for uploading an attachment",
)
async def get_presigned_put_url(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    filename: str,
):
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + str(task_id)
        + "/"
        + filename
    )
    db.add_task_attachment(account_id, opportunity_id, project_id, task_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/{account_id}/{opportunity_id}/{project_id}/{task_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    filename: str,
):
    s3_object_name = (
        str(account_id)
        + "/"
        + str(opportunity_id)
        + "/"
        + str(project_id)
        + "/"
        + str(task_id)
        + "/"
        + filename
    )
    db.remove_task_attachment(account_id, opportunity_id, project_id, task_id, filename)
    dep.s3_remove_object(s3_object_name)
