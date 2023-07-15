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

NAME = "artifact-schemas"

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

    art = db.create_artifact_schema(artifact_in_db)

    if art:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "create_artifact_schema",
            art.model_json_schema(),
        )

    return art


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

    art = db.update_artifact_schema(artifact_in_db)

    if art:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "update_artifact_schema",
            art.model_json_schema(),
        )

    return art


@router.delete(
    "/{artifact_schema_id}",
)
async def delete_artifact_schema(
    artifact_schema_id: str,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> ArtifactSchema | None:
    art = db.delete_artifact_schema(artifact_schema_id)
    if art:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "delete_artifact_schema",
            art.model_dump_json(),
        )

    return art
