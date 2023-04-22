from fastapi import APIRouter, Depends
from pydantic import BaseModel

from worst_crm.dependencies import get_current_active_user

router = APIRouter(
    prefix="/notes",
    dependencies=[Depends(get_current_active_user)],
    tags=['notes'],
)



class Note(BaseModel):
    name: str
    description: str | None = None


@router.post("/")
async def create_note(note: Note):
    return {"key": "you inserted it!!"}

@router.get("/{note_id}")
async def get_item(note_id: int):
    return {0: "mona",
            1: "cula"}.get(note_id, "n/a")
    
@router.delete("/{note_id}")
async def delete_note(note_id: int):
    return {"item deleted": True,
            "note_id": note_id}
    
