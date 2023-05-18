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
class Name(BaseModel):
    name: str | None = Field(min_length=2, max_length=50)


class Basic1(Name):
    owned_by: str | None = None
    status: str | None = None
    due_date: dt.date | None = None


class Basic2(BaseModel):
    data: dict | None = None
    tags: set[str] | None = None


class Basic2InDB(BaseModel):
    data: Any | None = None
    tags: list[str] | None = None


class Text(BaseModel):
    text: str | None = Field(max_length=1000000)


class CommonInDB(BaseModel):
    created_by: str | None = None
    updated_by: str | None = None


class DBComputed(BaseModel):
    created_at: dt.datetime
    updated_at: dt.datetime


class BasicFilters(BaseModel):
    name: list[str] | None = None
    owned_by: list[str] | None = None
    due_date_from: dt.date | None = None
    due_date_to: dt.date | None = None
    status: list[str] | None = None
    tags: list[str] | None = None
    attachments: list[str] | None = None
    created_at_from: dt.date | None = None
    created_at_to: dt.date | None = None
    created_by: list[str] | None = None
    updated_at_from: dt.date | None = None
    updated_at_to: dt.date | None = None
    updated_by: list[str] | None = None


# STATUS
class Status(BaseModel):
    name: str = Field(min_length=3, max_length=20)


# ACCOUNT
class UpdatedAccount(Basic1, Text, Basic2):
    pass


class AccountInDB(Basic1, Text, Basic2InDB, CommonInDB):
    pass


class Account(DBComputed, AccountInDB):
    account_id: UUID
    attachments: list[str]


# TODO should add tags
# model similar to account, minus data, text, tags, attachments
class AccountOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID


class AccountFilters(BasicFilters):
    pass


# PROJECT
class UpdatedProject(Basic1, Text, Basic2):
    pass


class ProjectInDB(Basic1, Text, Basic2InDB, CommonInDB):
    pass


class Project(DBComputed, ProjectInDB):
    account_id: UUID
    project_id: UUID
    attachments: list[str]


class ProjectOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID
    project_id: UUID


# includes account_name
class ProjectOverviewWithAccountName(ProjectOverview):
    account_name: str | None = None


class ProjectFilters(BasicFilters):
    pass


# TASK
class UpdatedTask(Basic1, Text, Basic2):
    pass


class TaskInDB(Basic1, Text, Basic2InDB, CommonInDB):
    pass


class Task(DBComputed, TaskInDB):
    account_id: UUID
    project_id: UUID
    task_id: int
    attachments: list[str]


class TaskOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID
    project_id: UUID
    task_id: int


class TaskOverviewWithProjectName(TaskOverview):
    project_name: str | None = None


class TaskFilters(BasicFilters):
    pass


# NOTES
class UpdatedNote(Name, Text, Basic2):
    pass


class NoteInDB(Name, Text, Basic2InDB, CommonInDB):
    pass


class Note(DBComputed, NoteInDB):
    account_id: UUID
    project_id: UUID
    note_id: int
    attachments: list[str]


class NoteOverview(Name, CommonInDB, DBComputed):
    account_id: UUID
    project_id: UUID
    note_id: int


class NoteOverviewWithProjectName(NoteOverview):
    project_name: str | None = None


class NoteFilters(BaseModel):
    name: list[str] | None = None
    tags: list[str] | None = None
    attachments: list[str] | None = None
    created_at_from: dt.date | None = None
    created_at_to: dt.date | None = None
    created_by: list[str] | None = None
    updated_at_from: dt.date | None = None
    updated_at_to: dt.date | None = None
    updated_by: list[str] | None = None
