from pydantic import BaseModel, Field, EmailStr, Json
from uuid import UUID
import datetime as dt
from typing import Any


# ADMIN OBJECTS
class Token(BaseModel):
    access_token: str
    token_type: str


class CommonUser(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    is_disabled: bool | None = None
    scopes: list[str] | None = None


class User(CommonUser):
    user_id: str


class UpdatedUser(CommonUser):
    password: str | None = None


class UpdatedUserInDB(CommonUser):
    hashed_password: str | None = None


class NewUser(User):
    password: str = Field(min_length=8, max_length=50)


class UserInDB(User):
    hashed_password: str
    failed_attempts: int = 0


# DATA OBJECTS

class CommonAccount(BaseModel):
    name: str
    owned_by: str | None = None
    description: str | None = None
    status: str | None = None
    
    
class NewAccount(CommonAccount):
    data: dict | None = None
    tags: set[str] | None = None
    

class AccountInDB(CommonAccount):
    created_by: str
    updated_by: str
    data: Any | None = None
    tags: list[str] | None = None


class Account(AccountInDB):
    account_id: UUID
    created_at: dt.datetime
    updated_at: dt.datetime


class NewProject(BaseModel):
    name: str
    owned_by: str | None = None
    description: str | None = None
    status: str | None = None
    data: Json | None = None
    tags: list[str] | None = None


class Project(NewProject):
    account_id: UUID
    project_id: UUID
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str


class NewTask(BaseModel):
    name: str
    owned_by: str | None = None
    description: str | None = None
    status: str | None = None
    data: Json | None = None
    tags: list[str] | None = None


class Task(NewTask):
    account_id: UUID
    project_id: UUID
    task_id: int
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str


class NewNote(BaseModel):
    name: str
    content: str | None = None
    data: Json | None = None
    tags: list[str] | None = None


class Note(NewNote):
    account_id: UUID
    project_id: UUID
    note_id: int
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str
