from fastapi import APIRouter, Depends, Security
from fastapi.responses import HTMLResponse
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

router = APIRouter(
    prefix="/artifacts",
    dependencies=[Depends(dep.get_current_user)],
    tags=["artifacts"],
)


# CRUD
@router.get("")
async def get_all_artifacts(
    artifact_filters: ArtifactFilters | None = None,
) -> list[ArtifactOverviewWithAccountName]:
    return db.get_all_artifacts(artifact_filters)


@router.get("/{account_id}")
async def get_all_artifacts_for_account_id(
    account_id: UUID,
    artifact_filters: ArtifactFilters | None = None,
) -> list[ArtifactOverviewWithOpportunityName]:
    return db.get_all_artifacts_for_account_id(account_id, artifact_filters)


@router.get("/{account_id}/{opportunity_id}")
async def get_all_artifacts_for_opportunity_id(
    account_id: UUID, opportunity_id: UUID
) -> list[ArtifactOverview]:
    return db.get_all_artifacts_for_opportunity_id(account_id, opportunity_id)


@router.get("/{account_id}/{opportunity_id}/{artifact_id}")
async def get_artifact(
    account_id: UUID, opportunity_id: UUID, artifact_id: UUID
) -> Artifact | None:
    return db.get_artifact(account_id, opportunity_id, artifact_id)


@router.post(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    description="`opportunity_id` will be generated if not provided by client.",
)
async def create_artifact(
    artifact: UpdatedArtifact,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Artifact | None:
    artifact_in_db = ArtifactInDB(
        **artifact.dict(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not artifact_in_db.artifact_id:
        artifact_in_db.artifact_id = uuid4()

    return db.create_artifact(artifact_in_db)


@router.put(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_artifact(
    artifact: UpdatedArtifact,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Artifact | None:
    artifact_in_db = ArtifactInDB(
        **artifact.dict(exclude_unset=True), updated_by=current_user.user_id
    )

    return db.update_artifact(artifact_in_db)


@router.delete(
    "/{account_id}/{opportunity_id}/{artifact_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_artifact(
    account_id: UUID, opportunity_id: UUID, artifact_id: UUID
) -> Artifact | None:
    return db.delete_artifact(account_id, opportunity_id, artifact_id)
