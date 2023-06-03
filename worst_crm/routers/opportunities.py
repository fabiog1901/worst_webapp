from fastapi import APIRouter, Depends, Security
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID
from worst_crm import db
from worst_crm.models import (
    Opportunity,
    NewOpportunity,
    OpportunityFilters,
    OpportunityInDB,
    OpportunityOverview,
    OpportunityOverviewWithAccountName,
    UpdatedOpportunity,
    User,
)
import worst_crm.dependencies as dep

router = APIRouter(
    prefix='/opportunities',
    dependencies=[Depends(dep.get_current_user)],
    tags=['opportunities'],
)


# CRUD
@router.get('')
async def get_all_opportunities(
    opportunity_filters: OpportunityFilters | None = None,
) -> list[OpportunityOverviewWithAccountName]:

    return db.get_all_opportunities(opportunity_filters)


@router.get('/{account_id}')
async def get_all_opportunitys_for_account_id(
    account_id: UUID,
) -> list[OpportunityOverview]:
    return db.get_all_opportunities_for_account_id(account_id)


@router.get('/{account_id}/{opportunity_id}')
async def get_opportunity(account_id: UUID, opportunity_id: UUID) -> Opportunity | None:
    return db.get_opportunity(account_id, opportunity_id)


@router.post(
    '/{account_id}', dependencies=[Security(dep.get_current_user, scopes=['rw'])]
)
async def create_opportunity(
    account_id: UUID,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> NewOpportunity | None:
    opportunity_in_db = OpportunityInDB(
        created_by=current_user.user_id, updated_by=current_user.user_id
    )

    return db.create_opportunity(account_id, opportunity_in_db)


@router.put(
    '/{account_id}/{opportunity_id}',
    dependencies=[Security(dep.get_current_user, scopes=['rw'])],
)
async def update_opportunity(
    account_id: UUID,
    opportunity_id: UUID,
    opportunity: UpdatedOpportunity,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Opportunity | None:
    opportunity_in_db = OpportunityInDB(
        **opportunity.dict(exclude_unset=True), updated_by=current_user.user_id
    )

    return db.update_opportunity(account_id, opportunity_id, opportunity_in_db)


@router.delete(
    '/{account_id}/{opportunity_id}',
    dependencies=[Security(dep.get_current_user, scopes=['rw'])],
)
async def delete_opportunity(
    account_id: UUID, opportunity_id: UUID
) -> Opportunity | None:
    return db.delete_opportunity(account_id, opportunity_id)


# Attachements
@router.get(
    '/{account_id}/{opportunity_id}/presigned-get-url/{filename}',
    name='Get pre-signed URL for downloading an attachment',
)
async def get_presigned_get_url(account_id: UUID, opportunity_id: UUID, filename: str):
    s3_object_name = str(account_id) + '/' + str(opportunity_id) + '/' + filename
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    '/{account_id}/{opportunity_id}/presigned-put-url/{filename}',
    dependencies=[Security(dep.get_current_user, scopes=['rw'])],
    name='Get pre-signed URL for uploading an attachment',
)
async def get_presigned_put_url(account_id: UUID, opportunity_id: UUID, filename: str):
    s3_object_name = str(account_id) + '/' + str(opportunity_id) + '/' + filename
    db.add_opportunity_attachment(account_id, opportunity_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    '/{account_id}/{opportunity_id}/attachments/{filename}',
    dependencies=[Security(dep.get_current_user, scopes=['rw'])],
)
async def delete_attachement(account_id: UUID, opportunity_id: UUID, filename: str):
    s3_object_name = str(account_id) + '/' + str(opportunity_id) + '/' + filename
    db.remove_opportunity_attachment(account_id, opportunity_id, filename)
    dep.s3_remove_object(s3_object_name)
