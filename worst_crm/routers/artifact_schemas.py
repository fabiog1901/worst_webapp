from fastapi import Security, BackgroundTasks
from typing import Annotated
from worst_crm import db
from worst_crm.models import (
    ArtifactSchema,
    ArtifactSchemaInDB,
    UpdatedArtifactSchema,
    User,
)
import worst_crm.dependencies as dep
import inspect

NAME = __name__.split(".")[-1]

router = dep.get_api_router(NAME)


@router.get(
    "",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_artifacts() -> list[ArtifactSchema]:
    return db.get_all_artifact_schemas()


@router.get(
    "/{artifact_schema_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_artifact_schema(artifact_schema_id: str) -> ArtifactSchema | None:
    return db.get_artifact_schema(artifact_schema_id)


@router.post(
    "",
)
async def create_artifact_schema(
    artifact_schema: UpdatedArtifactSchema,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ArtifactSchema | None:
    artifact_in_db = ArtifactSchemaInDB(
        **artifact_schema.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    x = db.create_artifact_schema(artifact_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.put(
    "",
)
async def update_artifact_schema(
    artifact: UpdatedArtifactSchema,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ArtifactSchema | None:
    artifact_in_db = ArtifactSchemaInDB(
        **artifact.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    x = db.update_artifact_schema(artifact_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/{artifact_schema_id}",
)
async def delete_artifact_schema(
    artifact_schema_id: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ArtifactSchema | None:
    x = db.delete_artifact_schema(artifact_schema_id)
    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,  # type: ignore
            x.model_dump_json(),
        )

    return x
