from fastapi import APIRouter, Depends, Security
from typing import Annotated
from uuid import UUID, uuid4
from worst_crm import db
from worst_crm.models import (
    Contact,
    ContactInDB,
    ContactWithAccountName,
    UpdatedContact,
    User,
)
import worst_crm.dependencies as dep

router = APIRouter(
    prefix="/contacts",
    dependencies=[Depends(dep.get_current_user)],
    tags=["contacts"],
)


# CRUD
@router.get("")
async def get_all_contacts() -> list[ContactWithAccountName]:
    return db.get_all_contacts()


@router.get("/{account_id}")
async def get_all_contacts_for_account_id(
    account_id: UUID,
) -> list[Contact]:
    return db.get_all_contacts_for_account_id(account_id)


@router.get("/{account_id}/{contact_id}")
async def get_contact(account_id: UUID, contact_id: UUID) -> Contact | None:
    return db.get_contact(account_id, contact_id)


@router.post(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
    description="`contact_id` will be generated if not provided by client.",
)
async def create_contact(
    contact: UpdatedContact,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Contact | None:
    contact_in_db = ContactInDB(
        **contact.dict(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not contact_in_db.contact_id:
        contact_in_db.contact_id = uuid4()

    return db.create_contact(contact_in_db)


@router.put(
    "",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_contact(
    contact: UpdatedContact,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Contact | None:
    contact_in_db = ContactInDB(
        **contact.dict(exclude_unset=True), updated_by=current_user.user_id
    )

    return db.update_contact(contact_in_db)


@router.delete(
    "/{account_id}/{contact_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_contact(account_id: UUID, contact_id: UUID) -> Contact | None:
    return db.delete_contact(account_id, contact_id)
