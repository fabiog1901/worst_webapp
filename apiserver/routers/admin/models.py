from fastapi import APIRouter, Security, BackgroundTasks
from typing import Annotated
from apiserver.models import User, Model, ModelUpdate
import inspect
import apiserver.dependencies as dep
import apiserver.service as svc
import datetime as dt

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


NAME = __name__.split(".", 2)[-1]

router = APIRouter(prefix="/models", tags=[NAME])


@router.get(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["worst_read"])],
)
async def get_all_models() -> dict[str, Model] | None:
    return JSONResponse(jsonable_encoder(svc.get_all_models()))


@router.get(
    "/{name}",
    dependencies=[Security(dep.get_current_user, scopes=["worst_read"])],
)
async def get_model(name: str) -> Model | None:
    return svc.get_model(name)


@router.post(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["worst_admin"])],
)
async def create_model(
    model: ModelUpdate,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_admin"])
    ],
    bg_task: BackgroundTasks,
) -> Model | None:
    x = svc.create_model(model, current_user)

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
    "",
    dependencies=[Security(dep.get_current_user, scopes=["worst_admin"])],
)
async def update_model(
    model: ModelUpdate,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_admin"])
    ],
    bg_task: BackgroundTasks,
) -> Model | None:
    x = svc.update_model(model, current_user)

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
async def delete_model(
    name: str,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_admin"])
    ],
    bg_task: BackgroundTasks,
) -> Model | None:
    x = svc.delete_model(name)

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
