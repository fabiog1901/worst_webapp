from fastapi import APIRouter, Depends, Security
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID
from worst_crm import db
from worst_crm.models import Task, NewTask, UpdatedTask, TaskInDB, User
import json
import worst_crm.dependencies as dep

router = APIRouter(
    prefix="/tasks",
    dependencies=[Depends(dep.get_current_user)],
    tags=["tasks"],
)

# CRUD
@router.get("/{account_id}/{project_id}")
async def get_all_tasks(account_id: UUID, project_id: UUID) -> list[Task]:
    return db.get_all_tasks(account_id, project_id)


@router.get("/{account_id}/{project_id}/{task_id}")
async def get_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:
    return db.get_task(account_id, project_id, task_id)


@router.post(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def create_task(
    account_id: UUID,
    project_id: UUID,
    task: NewTask,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Task | None:
    task_in_db = TaskInDB(
        **task.dict(), created_by=current_user.user_id, updated_by=current_user.user_id
    )

    return db.create_task(account_id, project_id, task_in_db)


@router.put(
    "/{account_id}/{project_id}/{task_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_task(
    account_id: UUID,
    project_id: UUID,
    task_id: int,
    task: UpdatedTask,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Task | None:
    task_in_db = TaskInDB(
        **task.dict(exclude={"data"}),
        data=json.dumps(task.data),
        updated_by=current_user.user_id
    )

    return db.update_task(account_id, project_id, task_id, task_in_db)


@router.delete(
    "/{account_id}/{project_id}/{task_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:
    return db.delete_task(account_id, project_id, task_id)


# Attachments
@router.get(
    "/{account_id}/{project_id}/{task_id}/presigned-get-url/{filename}",
    name="Get pre-signed URL for downloading an attachment",
)
async def get_presigned_get_url(
    account_id: UUID, project_id: UUID, task_id: int, filename: str
):
    s3_object_name = (
        str(account_id) + "/" + str(project_id) + "/" + str(task_id) + "/" + filename
    )
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/{account_id}/{project_id}/{task_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    name="Get pre-signed URL for uploading an attachment",
)
async def get_presigned_put_url(
    account_id: UUID, project_id: UUID, task_id: int, filename: str
):
    s3_object_name = (
        str(account_id) + "/" + str(project_id) + "/" + str(task_id) + "/" + filename
    )
    db.add_task_attachment(account_id, project_id, task_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/{account_id}/{project_id}/{task_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement(
    account_id: UUID, project_id: UUID, task_id: int, filename: str
):
    s3_object_name = (
        str(account_id) + "/" + str(project_id) + "/" + str(task_id) + "/" + filename
    )
    db.remove_task_attachment(account_id, project_id, task_id, filename)
    dep.s3_remove_object(s3_object_name)
