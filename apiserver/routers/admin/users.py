from fastapi import APIRouter, Security, BackgroundTasks

from apiserver import db
from apiserver import dependencies as dep
from apiserver.models import NewUser, User, UserInDB, UpdatedUser, UpdatedUserInDB
from typing import Annotated
import inspect
import datetime as dt

NAME = __name__.split(".", 2)[-1]

router = APIRouter(
    prefix="/users",
    tags=[NAME],
)


@router.get(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)
async def get_all_users() -> list[User]:
    return db.get_all_users()


@router.get(
    "/{user_id}",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)
async def get_user(user_id: str) -> User | None:
    return db.get_user(user_id)


@router.post("")
async def create_user(
    new_user: NewUser,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> User | None:
    uid = UserInDB(
        **new_user.model_dump(),
        hashed_password=dep.get_password_hash(new_user.password)
    )

    x = db.create_user(uid)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            dt.datetime.utcnow(),
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(exclude="hashed_password"),  # type: ignore
        )

    return x


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user: UpdatedUser,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> User | None:
    updated_uid = UpdatedUserInDB(**user.model_dump())

    if user.password:
        updated_uid.hashed_password = dep.get_password_hash(user.password)

    x = db.update_user(user_id, updated_uid)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            dt.datetime.utcnow(),
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(exclude="hashed_password"),  # type: ignore
        )

    return x


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> User | None:
    x = db.delete_user(user_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            dt.datetime.utcnow(),
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(exclude="hashed_password"),  # type: ignore
        )

    return x
