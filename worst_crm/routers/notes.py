from fastapi import APIRouter, Depends, Security
from typing import Annotated
from uuid import UUID
from worst_crm import db
from worst_crm.models import Note, NewNote, NoteInDB, User
import json
import worst_crm.dependencies as dep

router = APIRouter(
    prefix="/notes",
    dependencies=[Depends(dep.get_current_user)],
    tags=["notes"],
)


@router.get("/{account_id}/{project_id}")
async def get_all_notes(account_id: UUID, project_id: UUID) -> list[Note]:
    return db.get_all_notes(account_id, project_id)


@router.get("/{account_id}/{project_id}/{note_id}")
async def get_note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:
    return db.get_note(account_id, project_id, note_id)


@router.post(
    "/{account_id}/{project_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def create_note(
    account_id: UUID,
    project_id: UUID,
    note: NewNote,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Note | None:
    note_in_db = NoteInDB(
        **note.dict(exclude={"data"}),
        data=json.dumps(note.data),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    return db.create_note(account_id, project_id, note_in_db)


@router.put(
    "/{account_id}/{project_id}/{note_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def update_note(
    account_id: UUID,
    project_id: UUID,
    note_id: int,
    note: NewNote,
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> Note | None:
    note_in_db = NoteInDB(
        **note.dict(exclude={"data"}),
        data=json.dumps(note.data),
        created_by=current_user.user_id,
        updated_by=current_user.user_id
    )

    return db.update_note(account_id, project_id, note_id, note_in_db)


@router.delete(
    "/{account_id}/{project_id}/{note_id}",
    dependencies=[Security(dep.get_current_user, scopes=["rw"])],
)
async def delete_note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:
    return db.delete_note(account_id, project_id, note_id)
