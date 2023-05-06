from worst_crm import db
from fastapi import FastAPI, Depends, HTTPException, Query, status
import fastapi
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from worst_crm.models import UserInDB, Token, User, UpdatedUserInDB
from worst_crm.routers import accounts, projects, notes, tasks, admin, status
import os
import worst_crm.dependencies as dep

app = FastAPI(
    title="WorstCRM API", docs_url="/api", openapi_url="/worst_crm.openapi.json"
)

ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 1800))


@app.get("/healthcheck")
async def healthcheck():
    return {}


@app.get("/me", dependencies=[Depends(dep.get_current_user)])
async def get_user_me(
    current_user: Annotated[User, Depends(dep.get_current_user)]
) -> User | None:
    return current_user


@app.put("/update-password", dependencies=[Depends(dep.get_current_user)])
async def update_password(
    old_password: str,
    new_password: Annotated[str, Query(min_length=8, max_length=50)],
    current_user: Annotated[User, Depends(dep.get_current_user)],
) -> bool:
    user = db.get_user_with_hash(current_user.user_id)
    if not user or not dep.verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.update_user(
        current_user.user_id,
        UpdatedUserInDB(hashed_password=dep.get_password_hash(new_password)),
    )

    return bool(user)


@app.post("/login", tags=["auth"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user: UserInDB | None = dep.authenticate_user(
        form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = dep.create_access_token(
        data={"sub": user.user_id, "scopes": user.scopes},
        expire_seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
    )

    return Token(access_token=access_token, token_type="bearer")


app.include_router(accounts.router)
app.include_router(projects.router)
app.include_router(notes.router)
app.include_router(tasks.router)
app.include_router(status.router)
app.include_router(admin.router_admin)
