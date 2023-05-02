from fastapi import APIRouter, Depends, Security
from uuid import UUID

from worst_crm import db
import worst_crm.dependencies as dep
from worst_crm.models import NewTask, Task

router = APIRouter(
    prefix="/tasks",
    dependencies=[Depends(dep.get_current_active_user)],
    tags=["tasks"],
)


@router.get("/{account_id}/{project_id}")
async def get_all_tasks(account_id: UUID, project_id: UUID) -> list[Task]:
    return db.get_all_tasks(account_id, project_id)


@router.get("/{account_id}/{project_id}/{task_id}")
async def get_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:
    return db.get_task(account_id, project_id, task_id)


@router.post(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def create_Task(account_id: UUID, project_id: UUID, task: NewTask) -> Task | None:
    return db.create_task(account_id, project_id, task)


@router.put(
    "/{account_id}/{project_id}/{task_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def update_Task(
    account_id: UUID, project_id: UUID, task_id: int, task: NewTask
) -> Task | None:
    return db.update_task(account_id, project_id, task_id, task)


@router.delete(
    "/{account_id}/{project_id}/{task_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def delete_Task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:
    return db.delete_task(account_id, project_id, task_id)
