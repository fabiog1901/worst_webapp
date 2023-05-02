from fastapi import APIRouter, Security, HTTPException, status

from worst_crm import db
from worst_crm import dependencies as dep
from worst_crm.models import NewUser, User, UserInDB, UpdatedUser, UpdatedUserInDB

router_admin = APIRouter(
    prefix="/admin",
    dependencies=[Security(dep.get_current_active_user, scopes=["admin"])],
)

router_users = APIRouter(
    prefix="/users",
    tags=["admin/users"],
)


@router_users.get("")
async def get_all_users() -> list[User]:
    return db.get_all_users()


@router_users.get("/{user_id}")
async def get_user(user_id: str) -> User | None:
    return db.get_user(user_id)


@router_users.post("")
async def create_user(new_user: NewUser) -> User | None:
        
    uid = UserInDB(
        **new_user.dict(), hashed_password=dep.get_password_hash(new_user.password)
    )

    return db.create_user(uid)


@router_users.put("/{user_id}")
async def update_user(user_id: str, user: UpdatedUser) -> User | None:
    updated_uid = UpdatedUserInDB(**user.dict())

    if user.password:
        updated_uid.hashed_password = dep.get_password_hash(user.password)

    return db.update_user(user_id, updated_uid)


@router_users.delete("/{user_id}")
async def delete_user(user_id: str) -> User | None:
    return db.delete_user(user_id)


router_admin.include_router(router_users)
