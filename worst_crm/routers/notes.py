from fastapi import APIRouter, Depends, Security
from uuid import UUID

from worst_crm import db
import worst_crm.dependencies as dep
from worst_crm.models import NewNote, Note

router = APIRouter(
    prefix="/notes",
    dependencies=[Depends(dep.get_current_active_user)],
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
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def create_Note(account_id: UUID, project_id: UUID, note: NewNote) -> Note | None:
    return db.create_note(account_id, project_id, note)


@router.put(
    "/{account_id}/{project_id}/{note_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def update_Note(
    account_id: UUID, project_id: UUID, note_id: int, note: NewNote
) -> Note | None:
    return db.update_note(account_id, project_id, note_id, note)


@router.delete(
    "/{account_id}/{project_id}/{note_id}",
    dependencies=[Security(dep.get_current_active_user, scopes=["rw"])],
)
async def delete_Note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:
    return db.delete_note(account_id, project_id, note_id)
