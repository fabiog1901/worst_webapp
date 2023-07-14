from fastapi import APIRouter

from worst_crm import db
from worst_crm import dependencies as dep
from worst_crm.models import NewUser, User, UserInDB, UpdatedUser, UpdatedUserInDB

router = APIRouter(
    prefix="/users",
    tags=["admin/users"],
)


@router.get("")
async def get_all_users() -> list[User]:
    return db.get_all_users()


@router.get("/{user_id}")
async def get_user(user_id: str) -> User | None:
    return db.get_user(user_id)


@router.post("")
async def create_user(new_user: NewUser) -> User | None:
    uid = UserInDB(
        **new_user.model_dump(),
        hashed_password=dep.get_password_hash(new_user.password)
    )

    return db.create_user(uid)


@router.put("/{user_id}")
async def update_user(user_id: str, user: UpdatedUser) -> User | None:
    updated_uid = UpdatedUserInDB(**user.model_dump())

    if user.password:
        updated_uid.hashed_password = dep.get_password_hash(user.password)

    return db.update_user(user_id, updated_uid)


@router.delete("/{user_id}")
async def delete_user(user_id: str) -> User | None:
    return db.delete_user(user_id)
