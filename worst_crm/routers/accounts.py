from fastapi import APIRouter, Depends, Security
from fastapi.responses import HTMLResponse
from typing import Annotated
from uuid import UUID
from worst_crm import db
from worst_crm.models import (
    Account,
    NewAccount,
    UpdatedAccount,
    AccountInDB,
    AccountInfo,
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
@router.get("")
async def get_all_accounts() -> list[AccountInfo]:
    return db.get_all_accounts()


@router.get("/{account_id}")
async def get_account(account_id: UUID) -> Account | None:
    return db.get_account(account_id)


@router.post("", dependencies=[Security(dep.get_current_user, scopes=["rw"])])
async def create_account(
    new_account: NewAccount,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Account | None:
    acc_in_db = AccountInDB(
        **new_account.dict(),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

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
        **updated_account.dict(exclude={"data"}),
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
