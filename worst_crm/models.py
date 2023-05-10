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
    name: str = Field(min_length=2, max_length=50)


class Basic1(Basic):
    owned_by: str | None = None
    text: str | None = None
    attachments: list[str] | None = None
    status: str | None = None
    due_date: dt.date | None = None


class Basic2(BaseModel):
    data: dict | None = None
    tags: set[str] | None = None


class Basic2InDB(BaseModel):
    data: Any | None = None
    tags: list[str] | None = None


class CommonInDB(BaseModel):
    created_by: str | None = None
    updated_by: str | None = None


class DBComputed(BaseModel):
    created_at: dt.datetime
    updated_at: dt.datetime


# ACCOUNT
class NewAccount(Basic):
    pass


class UpdatedAccount(NewAccount, Basic1, Basic2):
    pass


class AccountInDB(NewAccount, Basic1, Basic2InDB, CommonInDB):
    pass


class Account(DBComputed, AccountInDB):
    account_id: UUID


# PROJECT
class NewProject(Basic):
    pass


class UpdatedProject(NewProject, Basic1, Basic2):
    pass


class ProjectInDB(NewProject, Basic1, Basic2InDB, CommonInDB):
    pass


class Project(DBComputed, ProjectInDB):
    account_id: UUID
    project_id: UUID


# TASK
class NewTask(Basic):
    pass


class UpdatedTask(NewTask, Basic1, Basic2):
    pass


class TaskInDB(NewTask, Basic1, Basic2InDB, CommonInDB):
    pass


class Task(DBComputed, TaskInDB):
    account_id: UUID
    project_id: UUID
    task_id: int


# NOTES
class NewNote(Basic):
    pass


class UpdatedNote(NewNote, Basic2):
    text: str | None = None
    attachments: list[str] | None = None


class NoteInDB(NewNote, Basic2InDB, CommonInDB):
    pass


class Note(DBComputed, NoteInDB):
    account_id: UUID
    project_id: UUID
    note_id: int


# STATUS
class Status(BaseModel):
    name: str = Field(min_length=3, max_length=20)
