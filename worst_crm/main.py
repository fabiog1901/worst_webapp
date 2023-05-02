from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from worst_crm.models import UserInDB, Token
from worst_crm.routers import accounts, projects, notes, tasks, admin
import os
import worst_crm.dependencies as dep

app = FastAPI(
    title="WorstCRM API", docs_url="/api", openapi_url="/worst_crm.openapi.json"
)

ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 1800))


@app.get("/healthcheck")
async def healthcheck():
    return {}


@app.post("/login", tags=["auth"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user: UserInDB | None = dep.authenticate_user(
        form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
app.include_router(admin.router_admin)
