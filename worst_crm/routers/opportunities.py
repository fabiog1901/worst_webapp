from fastapi import Security, BackgroundTasks
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import (
    Opportunity,
    OpportunityFilters,
    OpportunityInDB,
    OpportunityOverview,
    OpportunityOverviewWithAccountName,
    UpdatedOpportunity,
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
async def get_all_opportunities(
    opportunity_filters: OpportunityFilters | None = None,
) -> list[OpportunityOverviewWithAccountName]:
    return db.get_all_opportunities(opportunity_filters)


@router.get(
    "/{account_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_opportunities_for_account_id(
    account_id: UUID,
) -> list[OpportunityOverview]:
    return db.get_all_opportunities_for_account_id(account_id)


@router.get(
    "/{account_id}/{opportunity_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_opportunity(account_id: UUID, opportunity_id: UUID) -> Opportunity | None:
    return db.get_opportunity(account_id, opportunity_id)


@router.post(
    "",
    description="`opportunity_id` will be generated if not provided by client.",
)
async def create_opportunity(
    opp: UpdatedOpportunity,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Opportunity | None:
    opportunity_in_db = OpportunityInDB(
        **opp.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not opportunity_in_db.opportunity_id:
        opportunity_in_db.opportunity_id = uuid4()

    x = db.create_opportunity(opportunity_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            inspect.currentframe().f_code.co_name,
            x.model_dump_json(),
        )

    return x


@router.put(
    "",
)
async def update_opportunity(
    opportunity: UpdatedOpportunity,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Opportunity | None:
    opportunity_in_db = OpportunityInDB(
        **opportunity.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    x = db.update_opportunity(opportunity_in_db)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "update_opportunity",
            x.model_dump_json(),
        )

    return x


@router.delete(
    "/{account_id}/{opportunity_id}",
)
async def delete_opportunity(
    account_id: UUID,
    opportunity_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Opportunity | None:
    x = db.delete_opportunity(account_id, opportunity_id)

    if x:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "delete_opportunity",
            x.model_dump_json(),
        )

    return x


# Attachements
@router.get(
    "/{account_id}/{opportunity_id}/presigned-get-url/{filename}",
    name="Get pre-signed URL for downloading an attachment",
    dependencies=[Security(dep.get_current_user)],
)
async def get_presigned_get_url(
    account_id: UUID,
    opportunity_id: UUID,
    filename: str,
):
    s3_object_name = str(account_id) + "/" + str(opportunity_id) + "/" + filename
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/{account_id}/{opportunity_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    name="Get pre-signed URL for uploading an attachment",
)
async def get_presigned_put_url(
    account_id: UUID,
    opportunity_id: UUID,
    filename: str,
):
    s3_object_name = str(account_id) + "/" + str(opportunity_id) + "/" + filename
    db.add_opportunity_attachment(account_id, opportunity_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/{account_id}/{opportunity_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement(
    account_id: UUID,
    opportunity_id: UUID,
    filename: str,
):
    s3_object_name = str(account_id) + "/" + str(opportunity_id) + "/" + filename
    db.remove_opportunity_attachment(account_id, opportunity_id, filename)
    dep.s3_remove_object(s3_object_name)
