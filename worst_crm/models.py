from pydantic import Json, create_model, BaseModel, Field, EmailStr
from typing import Any
from uuid import UUID
import datetime as dt

# utility functions

# this dict will come from the database
# accounts = {
#     "ticker": (str | None, None),
#     "industry": (str | None, Field(min_length=3, max_length=20)),
# }


def update_account(d):
    pass


def update_model(name: str, base, dict_def: dict):
    fields = {}
    for field_name, value in dict_def.items():
        if isinstance(value, tuple):
            fields[field_name] = value
        elif isinstance(value, dict):
            fields[field_name] = (
                update_model(f"{name}_{field_name}", base, value),
                ...,
            )
        else:
            raise ValueError(f"Field {field_name}:{value} has invalid syntax")
    return create_model(name, __base__=base, **fields)


def update_filter_model(name: str, base, dict_def: dict):
    fields = {}
    for field_name, value in dict_def.items():
        if isinstance(value, tuple):
            fields[field_name] = (list[value[0]], value[1])  # type: ignore
        elif isinstance(value, dict):
            fields[field_name] = (
                update_filter_model(f"{name}_{field_name}", base, value),
                ...,
            )
        else:
            raise ValueError(f"Field {field_name}:{value} has invalid syntax")
    return create_model(name, __base__=base, **fields)


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
# Account = update_model("Account", Account, accounts)  # type: ignore
# AccountOverview = update_model("AccountOverview", AccountOverview, accounts)  # type: ignore
# UpdatedAccount = update_model("UpdatedAccount", UpdatedAccount, accounts)  # type: ignore
# AccountFilters = update_filter_model("AccountFilters", AccountFilters, accounts)  # type: ignore


# CONTACT
class UpdatedContact(BaseModel):
    account_id: UUID
    contact_id: UUID | None = None
    fname: str | None = Field(default="", max_length=50)
    lname: str | None = Field(default="", max_length=50)
    role_title: str | None = Field(default="", max_length=50)
    email: EmailStr | None = None
    telephone_number: str | None = Field(default="", max_length=20)
    business_card: str | None = Field(default="", max_length=500)
    tags: set[str] | None = None


class ContactInDB(UpdatedContact, CommonInDB):
    pass


class Contact(DBComputed, ContactInDB):
    pass


class ContactWithAccountName(Contact):
    account_name: str | None = None


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


# Opportunity = dict_model("Opportunity", Opportunity, accounts)  # type: ignore
# OpportunityOverview = dict_model("OpportunityOverview", OpportunityOverview, accounts)  # type: ignore
# OpportunityOverviewWithAccountName = dict_model("OpportunityOverviewWithAccountName", OpportunityOverviewWithAccountName, accounts)  # type: ignore
# UpdatedOpportunity = dict_model("UpdatedOpportunity", UpdatedOpportunity, accounts)  # type: ignore
# OpportunityFilters = filter_model("OpportunityFilters", OpportunityFilters, accounts)  # type: ignore


# ARTIFACT_SCHEMA
class UpdatedArtifactSchema(Name):
    artifact_schema_id: UUID | None = None
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
    artifact_schema_id: UUID
    schema_definition: dict | None = None
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


# Artifact = dict_model("Artifact", Artifact, accounts)  # type: ignore
# ArtifactOverview = dict_model("ArtifactOverview", ArtifactOverview, accounts)  # type: ignore
# ArtifactOverviewWithAccountName = dict_model("ArtifactOverviewWithAccountName", ArtifactOverviewWithAccountName, accounts)  # type: ignore
# ArtifactOverviewWithOpportunityName = dict_model("ArtifactOverviewWithOpportunityName", ArtifactOverviewWithOpportunityName, accounts)  # type: ignore
# UpdatedArtifact = dict_model("UpdatedArtifact", UpdatedArtifact, accounts)  # type: ignore
# ArtifactFilters = filter_model("ArtifactFilters", ProjectFilters, accounts)  # type: ignore


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


# Project = dict_model("Project", Project, accounts)  # type: ignore
# ProjectOverview = dict_model("ProjectOverview", ProjectOverview, accounts)  # type: ignore
# ProjectOverviewWithAccountName = dict_model("ProjectOverviewWithAccountName", ProjectOverviewWithAccountName, accounts)  # type: ignore
# ProjectOverviewWithOpportunityName = dict_model("ProjectOverviewWithOpportunityName", ProjectOverviewWithOpportunityName, accounts)  # type: ignore
# UpdatedProject = dict_model("UpdatedProject", UpdatedProject, accounts)  # type: ignore
# ProjectFilters = filter_model("ProjectFilters", ProjectFilters, accounts)  # type: ignore


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
