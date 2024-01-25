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

router = APIRouter(
    prefix=f"/{NAME}",
    tags=[NAME],
)


@router.get(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["worst_models_read"])],
    description="Required permission: `worst_models_read`",
)
async def get_all_models() -> dict[str, Model] | None:
    return JSONResponse(jsonable_encoder(svc.get_all_models()))


@router.get(
    "/{name}",
    dependencies=[Security(dep.get_current_user, scopes=["worst_models_read"])],
    description="Required permission: `worst_models_read`",
)
async def get_model(name: str) -> Model | None:
    return svc.get_model(name)


@router.post(
    "",
    description="Required permission: `worst_models_create`",
)
async def create_model(
    model: ModelUpdate,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_models_create"])
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
    description="Required permission: `worst_models_update`",
)
async def update_model(
    model: ModelUpdate,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_models_update"])
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
    description="Required permission: `worst_models_delete`",
)
async def delete_model(
    name: str,
    current_user: Annotated[
        User, Security(dep.get_current_user, scopes=["worst_models_delete"])
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
