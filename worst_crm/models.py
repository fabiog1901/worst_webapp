from pydantic import create_model, BaseModel, Field, EmailStr
from uuid import UUID
import datetime as dt
import os
import psycopg
import re

#############################
#  LOAD MODELS DYNAMICALLY  #
#############################

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")


def fetch_model_definition(model_name: str) -> dict[str, dict]:
    def to_snake_case(string):
        return re.sub(r"(.)([A-Z])", r"\1_\2", str(string)).lower()

    with psycopg.connect(DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT model_def 
                FROM models
                WHERE name = %s""",
                (to_snake_case(model_name),),
            )

            rs = cur.fetchone()

            if rs:
                return rs[0]

    return {}


def build_model_tuple(d: dict[str, dict]) -> dict:
    fields = {}
    for k, v in d.items():
        if v.get("alt_type", None):
            if v.get("default_value", None):
                if isinstance(v["default_value"], dict):
                    f = Field()
                    for kk, vv in v["default_value"].items():
                        setattr(f, kk, vv)
                    # fields[k] = (str | None, None)
                    fields[k] = (eval(v["type"]) | eval(v["alt_type"]), f)
                else:
                    fields[k] = (
                        eval(v["type"]) | eval(v["alt_type"]),
                        eval(v["default_value"]),
                    )

            else:
                if isinstance(v["default_value"], dict):
                    f = Field()
                    for kk, vv in v["default_value"].items():
                        setattr(f, kk, vv)
                    fields[k] = eval(v["type"]) | eval(v["alt_type"])
                else:
                    fields[k] = eval(v["type"]) | eval(v["alt_type"])
        else:
            if v.get("default_value", None):
                if isinstance(v["default_value"], dict):
                    f = Field()
                    for kk, vv in v["default_value"].items():
                        setattr(f, kk, vv)
                    fields[k] = (eval(v["type"]), f)
                else:
                    fields[k] = (eval(v["type"]), eval(v["default_value"]))

            else:
                if isinstance(v["default_value"], dict):
                    f = Field()
                    for kk, vv in v["default_value"].items():
                        setattr(f, kk, vv)
                    fields[k] = eval(v["type"])
                else:
                    fields[k] = eval(v["type"])

    return fields


def extend_model(name: str, base: type, dict_def: dict):
    fields = {}
    for field_name, value in dict_def.items():
        if isinstance(value, tuple):
            fields[field_name] = value
        elif isinstance(value, dict):
            fields[field_name] = (
                extend_model(f"{name}_{field_name}", base, value),
                ...,
            )
        else:
            raise ValueError(f"Field {field_name}:{value} has invalid syntax")
    return create_model(name, __base__=base, **fields)


def extend_filter_model(name: str, base, dict_def: dict):
    fields = {}
    for field_name, value in dict_def.items():
        if isinstance(value, tuple):
            fields[field_name] = (list[value[0]], value[1])  # type: ignore
        elif isinstance(value, dict):
            fields[field_name] = (
                extend_filter_model(f"{name}_{field_name}", base, value),
                ...,
            )
        else:
            raise ValueError(f"Field {field_name}:{value} has invalid syntax")
    return create_model(name, __base__=base, **fields)


def update_model(parent_class: type, base_class: type):
    d = fetch_model_definition(parent_class.__name__)
    f = build_model_tuple(d)
    return extend_model(base_class.__name__, base_class, f)


def update_filter_model(parent_class: type, base_class: type):
    d = fetch_model_definition(parent_class.__name__)
    f = build_model_tuple(d)
    return extend_model(base_class.__name__, base_class, f)


###################
#  ADMIN OBJECTS  #
###################
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


###################
#  MODEL OBJECTS  #
###################


# COMMON
class Name(BaseModel):
    name: str | None = Field(default="", max_length=50)


class Basic1(Name):
    owned_by: str | None = None
    status: str | None = None
    due_date: dt.date | None = None
    tags: set[str] | None = None


class Text(BaseModel):
    text: str | None = Field(default="", max_length=1000000)


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
class UpdatedAccount(Basic1, Text):
    account_id: UUID | None = None


class AccountInDB(UpdatedAccount, CommonInDB):
    pass


class Account(DBComputed, AccountInDB):
    attachments: list[str]


class AccountOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID


class AccountFilters(BasicFilters):
    pass


# extending the Model dynamically
# if I don't previously declare Account as a class, here Account will be a variable
# and a variable gives problem elsewhere where it is imported
Account = update_model(Account, Account)
AccountOverview = update_model(Account, AccountOverview)
UpdatedAccount = update_model(Account, UpdatedAccount)
AccountInDB = update_model(Account, UpdatedAccount)
AccountFilters = update_filter_model(Account, AccountFilters)


# CONTACT
class UpdatedContact(BaseModel):
    account_id: UUID
    contact_id: UUID | None = None
    fname: str | None = Field(default="", max_length=50)
    lname: str | None = Field(default="", max_length=50)
    role_title: str | None = Field(default="", max_length=50)
    email: EmailStr | None = None
    telephone_number: str | None = Field(default="", max_length=30)
    business_card: str | None = Field(default="", max_length=500)
    tags: set[str] | None = None


class ContactInDB(UpdatedContact, CommonInDB):
    pass


class Contact(DBComputed, ContactInDB):
    pass


class ContactWithAccountName(Contact):
    account_name: str | None = None


Contact = update_model(Contact, Contact)
UpdatedContact = update_model(Contact, UpdatedContact)


# OPPORTUNITY
class UpdatedOpportunity(Basic1, Text):
    account_id: UUID
    opportunity_id: UUID | None = None


class OpportunityInDB(UpdatedOpportunity, CommonInDB):
    pass


class Opportunity(DBComputed, OpportunityInDB):
    attachments: list[str]


class OpportunityOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID
    opportunity_id: UUID


class OpportunityOverviewWithAccountName(OpportunityOverview):
    account_name: str | None = None


class OpportunityFilters(BasicFilters):
    pass


Opportunity = update_model(Opportunity, Opportunity)
OpportunityOverview = update_model(Opportunity, OpportunityOverview)
OpportunityOverviewWithAccountName = update_model(
    Opportunity, OpportunityOverviewWithAccountName
)
UpdatedOpportunity = update_model(Opportunity, UpdatedOpportunity)
OpportunityFilters = update_filter_model(Opportunity, OpportunityFilters)


# ARTIFACT_SCHEMA
class UpdatedArtifactSchema(BaseModel):
    artifact_schema_id: str
    artifact_schema: dict | None = None


class ArtifactSchemaInDB(UpdatedArtifactSchema, CommonInDB):
    pass


class ArtifactSchema(DBComputed, ArtifactSchemaInDB):
    pass


# ARTIFACT
class UpdatedArtifact(Name):
    account_id: UUID
    opportunity_id: UUID
    artifact_id: UUID | None = None
    artifact_schema_id: str
    artifact_schema: dict | None = None
    tags: set[str] | None = None


class ArtifactInDB(UpdatedArtifact, CommonInDB):
    pass


class Artifact(DBComputed, ArtifactInDB):
    pass


class ArtifactOverview(Name, CommonInDB, DBComputed):
    account_id: UUID
    opportunity_id: UUID
    artifact_id: UUID
    tags: set[str] | None = None


class ArtifactOverviewWithOpportunityName(ArtifactOverview):
    opportunity_name: str | None = None


class ArtifactOverviewWithAccountName(ArtifactOverviewWithOpportunityName):
    account_name: str | None = None


class ArtifactFilters(BasicFilters):
    pass


Artifact = update_model(Artifact, Artifact)
ArtifactOverview = update_model(Artifact, ArtifactOverview)
ArtifactOverviewWithAccountName = update_model(
    Artifact, ArtifactOverviewWithAccountName
)
ArtifactOverviewWithOpportunityName = update_model(
    Artifact, ArtifactOverviewWithOpportunityName
)
UpdatedArtifact = update_model(Artifact, UpdatedArtifact)
ArtifactFilters = update_filter_model(Artifact, ArtifactFilters)


# PROJECT
class UpdatedProject(Basic1, Text):
    account_id: UUID
    opportunity_id: UUID
    project_id: UUID | None = None


class ProjectInDB(UpdatedProject, CommonInDB):
    pass


class Project(DBComputed, ProjectInDB):
    attachments: list[str]


class ProjectOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID
    opportunity_id: UUID
    project_id: UUID


class ProjectOverviewWithOpportunityName(ProjectOverview):
    opportunity_name: str | None = None


class ProjectOverviewWithAccountName(ProjectOverviewWithOpportunityName):
    account_name: str | None = None


class ProjectFilters(BasicFilters):
    pass


Project = update_model(Project, Project)
ProjectOverview = update_model(Project, ProjectOverview)
ProjectOverviewWithAccountName = update_model(Project, ProjectOverviewWithAccountName)
ProjectOverviewWithOpportunityName = update_model(
    Project, ProjectOverviewWithOpportunityName
)
UpdatedProject = update_model(Project, UpdatedProject)
ProjectFilters = update_filter_model(Project, ProjectFilters)


# TASK
class UpdatedTask(Basic1, Text):
    account_id: UUID
    opportunity_id: UUID
    project_id: UUID
    task_id: UUID | None = None


class TaskInDB(UpdatedTask, CommonInDB):
    pass


class Task(DBComputed, TaskInDB):
    attachments: list[str]


class TaskOverview(Basic1, CommonInDB, DBComputed):
    account_id: UUID
    opportunity_id: UUID
    project_id: UUID
    task_id: UUID


class TaskOverviewWithProjectName(TaskOverview):
    project_name: str | None = None


class TaskFilters(BasicFilters):
    pass


Task = update_model(Task, Task)
TaskOverview = update_model(Task, TaskOverview)
TaskOverviewWithProjectName = update_model(Task, TaskOverviewWithProjectName)
UpdatedTask = update_model(Task, UpdatedTask)
TaskFilters = update_filter_model(Task, TaskFilters)


# NOTES
class UpdatedAccountNote(Name, Text):
    account_id: UUID
    note_id: UUID | None = None
    tags: set[str] | None = None


class UpdatedOpportunityNote(UpdatedAccountNote):
    opportunity_id: UUID


class UpdatedProjectNote(UpdatedOpportunityNote):
    project_id: UUID


class AccountNoteInDB(UpdatedAccountNote, CommonInDB):
    pass


class OpportunityNoteInDB(UpdatedOpportunityNote, CommonInDB):
    pass


class ProjectNoteInDB(UpdatedProjectNote, CommonInDB):
    pass


class AccountNote(DBComputed, AccountNoteInDB):
    attachments: list[str]


class OpportunityNote(DBComputed, OpportunityNoteInDB):
    attachments: list[str]


class ProjectNote(DBComputed, ProjectNoteInDB):
    attachments: list[str]


class AccountNoteOverview(Name, CommonInDB, DBComputed):
    account_id: UUID
    note_id: UUID


class OpportunityNoteOverview(AccountNoteOverview):
    opportunity_id: UUID


class ProjectNoteOverview(OpportunityNoteOverview):
    project_id: UUID


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
