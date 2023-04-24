from fastapi import APIRouter, Depends, Security
from uuid import UUID

from worst_crm import db
from worst_crm.dependencies import get_current_active_user
from worst_crm.models import Account, NewAccount

router = APIRouter(
    prefix="/accounts",
    # dependencies=[Depends(get_current_active_user)],
    tags=['accounts'],
)


@router.get("")
async def get_all_accounts() -> list[Account]:

    return db.get_all_accounts()


@router.get("/{account_id}")
async def get_account(account_id: UUID) -> Account | None:

    return db.get_account(account_id)


# , dependencies=[Security(get_current_active_user, scopes=["rw"])])
@router.post("")
async def create_account(new_account: NewAccount) -> Account | None:

    return db.create_account(new_account)


# , dependencies=[Security(get_current_active_user, scopes=["rw"])])
@router.put("/{account_id}")
async def update_account(account_id: UUID, account: NewAccount) -> Account | None:

    return db.update_account(account_id, account)


# , dependencies=[Security(get_current_active_user, scopes=["rw"])])
@router.delete("/{account_id}")
async def delete_account(account_id: UUID) -> Account | None:

    return db.delete_account(account_id)
