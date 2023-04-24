from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
import datetime as dt
from fastapi.security import OAuth2PasswordRequestForm
from worst_crm.routers import accounts, projects, notes, tasks, admin

from worst_crm.dependencies import Token, authenticate_user, create_access_token

app = FastAPI(
    title='WorstCRM API',
    docs_url="/api"
    )

ACCESS_TOKEN_EXPIRE_MINUTES = 480


@app.post("/login", response_model=Token, tags=['auth'])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(accounts.router)
app.include_router(projects.router)
app.include_router(notes.router)
app.include_router(tasks.router)
app.include_router(admin.router)
