from fastapi import APIRouter, Security, BackgroundTasks
from worst_crm import db
from worst_crm.models import Status
import worst_crm.dependencies as dep
from typing import Annotated
from worst_crm.models import User
import inspect

NAME = __name__.split(".", 2)[-1]

router = APIRouter(prefix="/status", tags=[NAME])


# ACCOUNT
@router.get(
    "/account",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)
async def get_all_account_status() -> list[Status]:
    return db.get_all_account_status()


@router.post("/account")
async def create_account_status(
    status: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Status | None:
    x = db.create_account_status(status)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.delete("/account")
async def delete_account_status(
    status: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Status | None:
    x = db.delete_account_status(status)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


# PROJECT
@router.get(
    "/project",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)
async def get_all_project_status() -> list[Status]:
    return db.get_all_project_status()


@router.post("/project")
async def create_project_status(
    status: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Status | None:
    x = db.create_project_status(status)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.delete("/project")
async def delete_project_status(
    status: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Status | None:
    x = db.delete_project_status(status)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


# TASK
@router.get(
    "/task",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)
async def get_all_task_status() -> list[Status]:
    return db.get_all_task_status()


@router.post("/task")
async def create_task_status(
    status: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Status | None:
    x = db.create_task_status(status)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.delete("/task")
async def delete_task_status(
    status: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Status | None:
    x = db.delete_task_status(status)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x
