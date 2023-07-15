from fastapi import HTTPException, Security, status, BackgroundTasks
from typing import Annotated
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import (
    Artifact,
    ArtifactFilters,
    ArtifactInDB,
    ArtifactOverview,
    ArtifactOverviewWithAccountName,
    ArtifactOverviewWithOpportunityName,
    UpdatedArtifact,
    User,
)
import worst_crm.dependencies as dep
from worst_crm.models import build_model_tuple, extend_model
from pydantic import BaseModel, ValidationError
import inspect

NAME = __name__.split(".")[-1]

router = dep.get_api_router(NAME)


def sanitize(
    artifact_schema_id: str,
    payload: dict,
) -> dict:
    artifact_schema = db.get_artifact_schema(artifact_schema_id)

    if artifact_schema:
        model: type[BaseModel] = extend_model(
            artifact_schema_id,
            BaseModel,
            build_model_tuple(artifact_schema.artifact_schema),
        )

        try:
            model.model_validate(payload)

            return model(**payload).model_dump()

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"artifact schema '{artifact_schema_id}' not found.",
        )


@router.get(
    "",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_artifacts(
    artifact_filters: ArtifactFilters | None = None,
) -> list[ArtifactOverviewWithAccountName]:
    return db.get_all_artifacts(artifact_filters)


@router.get(
    "/{account_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_artifacts_for_account_id(
    account_id: UUID,
    artifact_filters: ArtifactFilters | None = None,
) -> list[ArtifactOverviewWithOpportunityName]:
    return db.get_all_artifacts_for_account_id(account_id, artifact_filters)


@router.get(
    "/{account_id}/{opportunity_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_artifacts_for_opportunity_id(
    account_id: UUID,
    opportunity_id: UUID,
) -> list[ArtifactOverview]:
    return db.get_all_artifacts_for_opportunity_id(account_id, opportunity_id)


@router.get(
    "/{account_id}/{opportunity_id}/{artifact_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_artifact(
    account_id: UUID,
    opportunity_id: UUID,
    artifact_id: UUID,
) -> Artifact | None:
    return db.get_artifact(account_id, opportunity_id, artifact_id)


@router.post(
    "",
    description="`artifact_id` will be generated if not provided by client.",
)
async def create_artifact(
    artifact: UpdatedArtifact,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Artifact | None:
    artifact_in_db = ArtifactInDB(
        **artifact.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id,
    )

    if not artifact_in_db.artifact_id:
        artifact_in_db.artifact_id = uuid4()

    artifact_in_db.payload = sanitize(
        artifact_in_db.artifact_schema_id, artifact_in_db.payload
    )

    x = db.create_artifact(artifact_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_json_schema(),
        )

    return x


@router.put(
    "",
)
async def update_artifact(
    artifact: UpdatedArtifact,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Artifact | None:
    artifact_in_db = ArtifactInDB(
        **artifact.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    artifact_in_db.payload = sanitize(
        artifact_in_db.artifact_schema_id, artifact_in_db.payload
    )

    x = db.update_artifact(artifact_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_json_schema(),
        )

    return x


@router.delete(
    "/{account_id}/{opportunity_id}/{artifact_id}",
)
async def delete_artifact(
    account_id: UUID,
    opportunity_id: UUID,
    artifact_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Artifact | None:
    x = db.delete_artifact(account_id, opportunity_id, artifact_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x
