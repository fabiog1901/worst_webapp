from fastapi import APIRouter, Security, BackgroundTasks
from worst_crm import db
import worst_crm.dependencies as dep
from typing import Annotated
from worst_crm.models import User, ModelName, Model, ModelInDB, UpdatedModel
import inspect

NAME = __name__.split(".", 2)[-1]

router = APIRouter(prefix="/models", tags=[NAME])


@router.get(
    "{name}",
    dependencies=[Security(dep.get_current_user, scopes=["admin"])],
)
async def get_model(name: ModelName) -> Model | None:
    return db.get_model(name)


@router.put("")
async def update_model(
    model: UpdatedModel,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["admin"])],
    bg_task: BackgroundTasks,
) -> Model | None:
    model_in_db = ModelInDB(
        **model.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    x = db.update_model(model_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x
