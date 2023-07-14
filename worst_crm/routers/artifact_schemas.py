from fastapi import APIRouter, Depends, Security
from typing import Annotated
from worst_crm import db
from worst_crm.models import (
    ArtifactSchema,
    ArtifactSchemaInDB,
    UpdatedArtifactSchema,
    User,
)
import worst_crm.dependencies as dep

router = APIRouter(
    prefix="/artifact-schemas",
    dependencies=[Depends(dep.get_current_user)],
    tags=["artifact-schemas"],
)


# CRUD
@router.get("")
async def get_all_artifacts() -> list[ArtifactSchema]:
    return db.get_all_artifact_schemas()


@router.get("/{artifact_schema_id}")
async def get_artifact_schema(artifact_schema_id: str) -> ArtifactSchema | None:
    return db.get_artifact_schema(artifact_schema_id)


@router.post(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def create_artifact_schema(
    artifact_schema: UpdatedArtifactSchema,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> ArtifactSchema | None:
    artifact_in_db = ArtifactSchemaInDB(
        **artifact_schema.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    return db.create_artifact_schema(artifact_in_db)


@router.put(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_artifact_schema(
    artifact: UpdatedArtifactSchema,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> ArtifactSchema | None:
    artifact_in_db = ArtifactSchemaInDB(
        **artifact.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    return db.update_artifact_schema(artifact_in_db)


@router.delete(
    "/{artifact_schema_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_artifact_schema(artifact_schema_id: str) -> ArtifactSchema | None:
    return db.delete_artifact_schema(artifact_schema_id)
