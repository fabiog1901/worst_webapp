from fastapi import APIRouter, Depends, Security
from uuid import UUID

from worst_crm import db
import worst_crm.dependencies as dep
from worst_crm.models import Account, NewAccount

router = APIRouter(
    prefix="/accounts",
    dependencies=[Depends(dep.get_current_active_user)],
    tags=["accounts"],
)


@router.get("")
async def get_all_accounts() -> list[Account]:
    return db.get_all_accounts()


@router.get("/{account_id}")
async def get_account(account_id: UUID) -> Account | None:
    return db.get_account(account_id)


@router.post("", dependencies=[Security(dep.get_current_active_user, scopes=["rw"])])
async def create_account(account: NewAccount) -> Account | None:
    if account.tags:
        account.tags = sorted(list(set(account.tags)))
    return db.create_account(account)


@router.put(
    "/{account_id}", dependencies=[Security(dep.get_current_active_user, scopes=["rw"])]
)
async def update_account(account_id: UUID, account: NewAccount) -> Account | None:
    if account.tags:
        account.tags = sorted(list(set(account.tags)))

    return db.update_account(account_id, account)


@router.delete(
    "/{account_id}", dependencies=[Security(dep.get_current_active_user, scopes=["rw"])]
)
async def delete_account(account_id: UUID) -> Account | None:
    return db.delete_account(account_id)
