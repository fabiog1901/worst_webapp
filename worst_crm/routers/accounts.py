from typing import Annotated
from fastapi import APIRouter, Depends, Security, Request, Query
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID
import datetime as dt
from worst_crm import db
from worst_crm.models import (
    NewAccount,
    Account,
    UpdatedAccount,
    AccountInDB,
    AccountOverview,
    AccountFilters,
    User,
)
import json
import worst_crm.dependencies as dep

router = APIRouter(
    prefix="/accounts",
    dependencies=[Depends(dep.get_current_user)],
    tags=["accounts"],
)


# CRUD
# TODO missing data and text
@router.get("")
async def get_all_accounts(
    name: Annotated[list[str], Query()] = [],
    owned_by: Annotated[list[str], Query()] = [],
    due_date_from: dt.date | None = None,
    due_date_to: dt.date | None = None,
    status: Annotated[list[str], Query()] = [],
    tags: Annotated[list[str], Query()] = [],
    attachments: Annotated[list[str], Query()] = [],
    created_at_from: dt.date | None = None,
    created_at_to: dt.date | None = None,
    created_by: Annotated[list[str], Query()] = [],
    updated_at_from: dt.date | None = None,
    updated_at_to: dt.date | None = None,
    updated_by: Annotated[list[str], Query()] = [],
) -> list[AccountOverview]:
    # TODO possibly using elasticsearch for text/data columns?

    account_filters = AccountFilters()

    if name:
        account_filters.name = name
    if owned_by:
        account_filters.owned_by = owned_by
    if due_date_from:
        account_filters.due_date_from = due_date_from
    if due_date_to:
        account_filters.due_date_to = due_date_to
    if status:
        account_filters.status = status
    if tags:
        account_filters.tags = tags
    if attachments:
        account_filters.attachments = attachments
    if created_at_from:
        account_filters.created_at_from = created_at_from
    if created_at_to:
        account_filters.created_at_to = created_at_to
    if created_by:
        account_filters.created_by = created_by
    if updated_at_from:
        account_filters.updated_at_from = updated_at_from
    if updated_at_to:
        account_filters.updated_at_to = updated_at_to
    if updated_by:
        account_filters.updated_by = updated_by

    return db.get_all_accounts(account_filters)


@router.get("/{account_id}")
async def get_account(account_id: UUID) -> Account | None:
    return db.get_account(account_id)


@router.post("", dependencies=[Security(dep.get_current_user, scopes=["rw"])])
async def create_account(
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> NewAccount | None:
    acc_in_db = AccountInDB(
        created_by=current_user.user_id, updated_by=current_user.user_id
    )  # type: ignore

    return db.create_account(acc_in_db)


@router.put(
    "/{account_id}", dependencies=[Security(dep.get_current_user, scopes=["rw"])]
)
async def update_account(
    account_id: UUID,
    updated_account: UpdatedAccount,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Account | None:
    acc_in_db = AccountInDB(
        **updated_account.dict(exclude_unset=True, exclude={"data"}),
        data=json.dumps(updated_account.data),
        updated_by=current_user.user_id
    )
    return db.update_account(account_id, acc_in_db)


@router.delete(
    "/{account_id}", dependencies=[Security(dep.get_current_user, scopes=["rw"])]
)
async def delete_account(account_id: UUID) -> Account | None:
    return db.delete_account(account_id)


# Attachements
@router.get(
    "/{account_id}/presigned-get-url/{filename}",
    name="Get pre-signed URL for downloading an attachment",
)
async def get_presigned_get_url(account_id: UUID, filename: str):
    s3_object_name = str(account_id) + "/" + filename
    data = dep.get_presigned_get_url(s3_object_name)
    return HTMLResponse(content=data)


@router.get(
    "/{account_id}/presigned-put-url/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    name="Get pre-signed URL for uploading an attachment",
)
async def get_presigned_put_url(account_id: UUID, filename: str):
    s3_object_name = str(account_id) + "/" + filename
    db.add_account_attachment(account_id, filename)
    data = dep.get_presigned_put_url(s3_object_name)
    return HTMLResponse(content=data)


@router.delete(
    "/{account_id}/attachments/{filename}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_attachement(account_id: UUID, filename: str):
    s3_object_name = str(account_id) + "/" + filename
    db.remove_account_attachment(account_id, filename)
    dep.s3_remove_object(s3_object_name)
