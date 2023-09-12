from enum import Enum
from pydantic import create_model, BaseModel, EmailStr, Field
from pydantic.fields import FieldInfo
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
                SELECT skema 
                FROM models
                WHERE name = %s""",
                (to_snake_case(model_name),),
            )

            rs = cur.fetchone()

            if rs:
                return rs[0]

    return {}


def build_model_tuple(d: dict[str, dict[str, dict]]) -> dict:
    def get_type(x):
        return {"string": str, "integer": int, "null": None}[x]

    def get_fieldinfo(meta: dict):
        fi = FieldInfo()
        if meta.get("default", None):
            fi.default = meta["default"]
        fi.metadata = fi._collect_metadata(meta)
        return fi

    fields = {}
    for k, v in d.get("properties", {}).items():
        if v.get("anyOf", None):
            fields[k] = (
                get_type(v["anyOf"][0]["type"]) | get_type(v["anyOf"][1]["type"]),
                get_fieldinfo(v),
            )
        else:
            fields[k] = (get_type(v["type"]), get_fieldinfo(v))

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


# MODELS


class ModelName(str, Enum):
    account = "account"
    artifact = "artifact"
    contact = "contact"
    opportunity = "opportunity"
    project = "project"
    task = "task"


class PydanticModel(BaseModel):
    properties: dict
    required: list[str] | None = None
    title: str | None = None
    type: str | None = None


class UpdatedModel(BaseModel):
    name: ModelName
    skema: PydanticModel


class ModelInDB(UpdatedModel, CommonInDB):
    pass


class Model(DBComputed, ModelInDB):
    pass


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
