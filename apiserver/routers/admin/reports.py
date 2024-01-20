from fastapi import APIRouter, Security, BackgroundTasks, Body
from typing import Annotated
from apiserver.models import User, Report
import inspect
import apiserver.dependencies as dep
import apiserver.service as svc
import datetime as dt
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

NAME = __name__.split(".", 2)[-1]

router = APIRouter(
    prefix="/reports",
    tags=[NAME],
    dependencies=[Security(dep.get_current_user, scopes=["worst_read"])],
)


@router.get("")
async def get_all_reports() -> dict[str, Report] | None:
    return JSONResponse(jsonable_encoder(svc.get_all_reports()))


@router.get("/{name}")
async def get_report(name: str) -> Report | None:
    return svc.get_report(name)


@router.post(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["worst_admin"])],
)
async def create_report(
    name: Annotated[str, Body()],
    sql_stmt: Annotated[str, Body()],
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_admin"])
    ],
    bg_task: BackgroundTasks,
) -> Report | None:
    x = svc.create_report(name, sql_stmt, current_user)

    if x:
        bg_task.add_task(
            svc.log_event,
            NAME,
            dt.datetime.utcnow(),
            current_user,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.put(
    "/{name}",
    dependencies=[Security(dep.get_current_user, scopes=["worst_admin"])],
)
async def update_report(
    name: str,
    sql_stmt: Annotated[str, Body()],
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_admin"])
    ],
    bg_task: BackgroundTasks,
) -> Report | None:
    x = svc.update_report(name, sql_stmt, current_user)

    if x:
        bg_task.add_task(
            svc.log_event,
            NAME,
            dt.datetime.utcnow(),
            current_user,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/{name}",
    dependencies=[Security(dep.get_current_user, scopes=["worst_admin"])],
)
async def delete_report(
    name: str,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_admin"])
    ],
    bg_task: BackgroundTasks,
) -> Report | None:
    x = svc.delete_report(name)

    if x:
        bg_task.add_task(
            svc.log_event,
            NAME,
            dt.datetime.utcnow(),
            current_user,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x
