from fastapi import Security, BackgroundTasks
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

NAME = "contacts"

router = dep.get_api_router(NAME)


# CRUD
@router.get(
    "",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_contacts() -> list[ContactWithAccountName]:
    return db.get_all_contacts()


@router.get(
    "/{account_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_all_contacts_for_account_id(
    account_id: UUID,
) -> list[Contact]:
    return db.get_all_contacts_for_account_id(account_id)


@router.get(
    "/{account_id}/{contact_id}",
    dependencies=[Security(dep.get_current_user)],
)
async def get_contact(
    account_id: UUID,
    contact_id: UUID,
) -> Contact | None:
    return db.get_contact(account_id, contact_id)


@router.post(
    "",
    description="`contact_id` will be generated if not provided by client.",
)
async def create_contact(
    contact: UpdatedContact,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Contact | None:
    contact_in_db = ContactInDB(
        **contact.model_dump(exclude_unset=True),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    if not contact_in_db.contact_id:
        contact_in_db.contact_id = uuid4()
        
    con = db.create_contact(contact_in_db)
    
    if con:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "create_contact",
            con.model_dump_json()
        )
        
    return con


@router.put(
    "",
)
async def update_contact(
    contact: UpdatedContact,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Contact | None:
    contact_in_db = ContactInDB(
        **contact.model_dump(exclude_unset=True), updated_by=current_user.user_id
    )

    con = db.update_contact(contact_in_db)
    
    if con:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "update_contact",
            con.model_dump_json()
        )
        
    return con


@router.delete(
    "/{account_id}/{contact_id}",
)
async def delete_contact(
    account_id: UUID,
    contact_id: UUID,
    current_user: Annotated[User, Security(dep.get_current_user, scopes=["rw"])],
    bg_task: BackgroundTasks,
) -> Contact | None:
    
    con = db.delete_contact(account_id, contact_id)
    
    if con:
        bg_task.add_task(
            db.log_event,
            NAME,
            current_user.user_id,
            "delete_contact",
            con.model_dump_json()
        )
        
    return con
