from fastapi import APIRouter, Security

from worst_crm.dependencies import get_current_active_user, User, UserInDB, get_password_hash

router = APIRouter(
    prefix="/admin",
    dependencies=[Security(get_current_active_user, scopes=["admin"])],
    tags=['admin'],
)


@router.get("/users/{username}")
async def get_user(username: str):
    return {0: "mona",
            1: "cula"}.get(username, "n/a")
    
    
    

@router.post("/users")
async def create_user(user: User):
    
    hashedpwd = get_password_hash(user.password)

    return {"key": "new user created!"}


@router.put("/users/{username}")
async def update_user(username: int):
    return {"item deleted": True,
            "note_id": username}
    
@router.delete("/users/{username}")
async def delete_user(username: int):
    return {"item deleted": True,
            "note_id": username}
    