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

# COMMON
class Basic(BaseModel):
    name: str
    owned_by: str | None = None
    text: str | None = None
    status: str | None = None


class Basic2(BaseModel):
    data: dict | None = None
    tags: set[str] | None = None


class Basic2InDB(BaseModel):
    data: Any | None = None
    tags: list[str] | None = None


class CommonInDB(BaseModel):
    created_by: str
    updated_by: str


class DBComputed(BaseModel):
    created_at: dt.datetime
    updated_at: dt.datetime


# ACCOUNT
class AccountInDB(Basic, Basic2InDB, CommonInDB):
    pass


class NewAccount(Basic, Basic2):
    pass


class Account(DBComputed, AccountInDB):
    account_id: UUID


# PROJECT
class ProjectInDB(Basic, Basic2InDB, CommonInDB):
    pass


class NewProject(Basic, Basic2):
    pass


class Project(DBComputed, ProjectInDB):
    account_id: UUID
    project_id: UUID


# TASK
class TaskInDB(Basic, Basic2InDB, CommonInDB):
    pass


class NewTask(Basic, Basic2):
    pass


class Task(DBComputed, TaskInDB):
    account_id: UUID
    project_id: UUID
    task_id: int


# NOTES
class NoteInDB(Basic, Basic2InDB, CommonInDB):
    pass


class NewNote(Basic, Basic2):
    pass


class Note(DBComputed, NoteInDB):
    account_id: UUID
    project_id: UUID
    note_id: int
