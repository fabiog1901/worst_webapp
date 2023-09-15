from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Annotated
from worst_crm import db
from worst_crm import service as svc
from worst_crm.api_router import APIRouter
from worst_crm.models import (
    UserInDB,
    Token,
    User,
    UpdatedUserInDB,
    pyd_models,
)
from worst_crm.routers.admin import admin
import os
import threading
import time
import worst_crm.dependencies as dep


JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY_SECONDS", 1800))

app = FastAPI(
    title="WorstCRM API",
    version="0.1.0",
    docs_url="/api",
    openapi_url="/worst_crm.openapi.json",
)


app.mount("/static", StaticFiles(directory="webapp/dist"), name="static")

# origins = [
#     "http://localhost",
#     "http://localhost:8000" "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get(
    "/",
)
async def home() -> FileResponse:
    return FileResponse("webapp/dist/index.html")


@app.get("/healthcheck")
async def healthcheck() -> dict:
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
            status_code=status.HTTP_401_UNAUTHORIZED,
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = dep.create_access_token(
        data={"sub": user.user_id, "scopes": user.scopes},
        expire_seconds=JWT_EXPIRY_SECONDS,
    )

    return Token(access_token=access_token, token_type="bearer")


# add routers dynamically
for k, v in pyd_models.items():
    router = APIRouter(
        model_name=k,
        default_model=v["default"],
        overview_model=v["overview"],
        update_model=v["update"],
    )

    app.include_router(router)

# ADMIN
app.include_router(admin.router)


# uvicorn server is started and configured to reload
# if file 'watch.txt' changes.
# Thus, whenever the app wants to instruct uvicorn to reboot itself,
# it just has to touch that file.
# To make sure that every instance of the app reboots,
# the app updates a db entry that is periodically fetched by
# every instance. If the value is different than the initial value,
# the app touches file watch.txt which will cause uvicorn to reload the app.

# store initial value at startup
watch_epoch = db.get_watch()


def watch_it(watch_epoch: int):
    while True:
        if db.get_watch() > watch_epoch:
            Path("watch.txt").touch()

        time.sleep(15)


# periodically check if a restart is needed
threading.Thread(target=watch_it, args=(watch_epoch,), daemon=True).start()


# from psycopg_pool import ConnectionPool

# DB_URL = os.getenv("DB_URL")

# if not DB_URL:
#     raise EnvironmentError("DB_URL env variable not found!")


# # the pool starts connecting immediately.
# pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


# def get_pool():
#     return pool
