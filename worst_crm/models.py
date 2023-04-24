
from pydantic import BaseModel
from uuid import UUID
import datetime as dt

class User(BaseModel):
    username: str
    full_name: str | None = None
    email: str | None = None
    is_disabled: bool | None = None
    scopes: list[str] | None = None
    password: str | None = None

class UserInDB(User):
    hashed_password: str
    
class NewAccount(BaseModel):
    account_name: str
    description: str | None = None
    tags: list[str] | None = None

class Account(NewAccount):
    account_id: UUID
    

class NewProject(BaseModel):
    project_name: str
    description: str | None = None
    status: str | None = None
    tags: list[str] | None = None
    
class Project(NewProject):
    account_id: UUID
    project_id: UUID


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
    
    