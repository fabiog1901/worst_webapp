from pydantic import BaseModel
from uuid import UUID
import datetime as dt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []


class CommonUser(BaseModel):
    full_name: str | None = None
    email: str | None = None
    is_disabled: bool | None = None
    scopes: list[str] | None = None
    
    
class User(CommonUser):
    user_id: str
    

class UpdatedUser(CommonUser):
    password: str | None = None


class UpdatedUserInDB(CommonUser):
    hashed_password: str | None = None


class NewUser(User):
    password: str


class UserInDB(User):
    hashed_password: str


class NewAccount(BaseModel):
    account_name: str
    description: str | None = None
    tags: list[str] | None = None


class Account(NewAccount):
    account_id: UUID
    created_at: dt.datetime
    updated_at: dt.datetime


class NewProject(BaseModel):
    project_name: str
    description: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class Project(NewProject):
    account_id: UUID
    project_id: UUID
    created_at: dt.datetime
    updated_at: dt.datetime


class NewNote(BaseModel):
    note_name: str
    content: str | None = None
    tags: list[str] | None = None


class Note(NewNote):
    account_id: UUID
    project_id: UUID
    note_id: int
    updated_at: dt.datetime


class NewTask(BaseModel):
    task_name: str
    content: str | None = None
    task_status: str
    tags: list[str] | None = None


class Task(NewTask):
    account_id: UUID
    project_id: UUID
    task_id: int
    updated_at: dt.datetime
