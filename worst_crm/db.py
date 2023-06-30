from psycopg_pool import ConnectionPool
from psycopg.types.array import ListDumper
from psycopg.types.json import JsonbDumper
from pydantic import PyObject
from typing import Any
from uuid import UUID
import datetime as dt
import os

from worst_crm.models import (
    Account,
    AccountFilters,
    AccountInDB,
    AccountNote,
    AccountNoteInDB,
    AccountNoteOverview,
    AccountOverview,
    Artifact,
    ArtifactFilters,
    ArtifactInDB,
    ArtifactOverview,
    ArtifactOverviewWithAccountName,
    ArtifactOverviewWithOpportunityName,
    ArtifactSchema,
    ArtifactSchemaInDB,
    Contact,
    ContactInDB,
    ContactWithAccountName,
    NoteFilters,
    Opportunity,
    OpportunityFilters,
    OpportunityInDB,
    OpportunityNote,
    OpportunityNoteInDB,
    OpportunityNoteOverview,
    OpportunityOverview,
    OpportunityOverviewWithAccountName,
    Project,
    ProjectFilters,
    ProjectInDB,
    ProjectNote,
    ProjectNoteInDB,
    ProjectNoteOverview,
    ProjectOverview,
    ProjectOverviewWithAccountName,
    ProjectOverviewWithOpportunityName,
    Status,
    Task,
    TaskFilters,
    TaskInDB,
    TaskOverview,
    TaskOverviewWithProjectName,
)
from worst_crm.models import User, UserInDB, UpdatedUserInDB


DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")


# the pool starts connecting immediately.
pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


def load_schema(ddl_filename):
    with open(ddl_filename) as f:
        execute_stmt(f.read(), returning_rs=False)


def get_fields(model) -> str:
    return ", ".join([x for x in model.__fields__.keys()])


def get_placeholders(model) -> str:
    return ("%s, " * len(tuple(model.__fields__.keys())))[:-2]


# STATUS
def get_all_account_status() -> list[Status]:
    return execute_stmt("SELECT name FROM account_status", model=Status, is_list=True)


def create_account_status(status: str):
    execute_stmt(
        "UPSERT INTO account_status(name) VALUES (%s)", (status,), returning_rs=False
    )


def delete_account_status(status: str):
    execute_stmt(
        "DELETE FROM account_status WHERE name = %s", (status,), returning_rs=False
    )


def get_all_project_status() -> list[Status]:
    return execute_stmt("SELECT name FROM project_status", model=Status, is_list=True)


def create_project_status(status: str):
    execute_stmt(
        "UPSERT INTO project_status(name) VALUES (%s)", (status,), returning_rs=False
    )


def delete_project_status(status: str):
    execute_stmt(
        "DELETE FROM project_status WHERE name = %s", (status,), returning_rs=False
    )


def get_all_task_status() -> list[Status]:
    return execute_stmt("SELECT name FROM task_status", model=Status, is_list=True)


def create_task_status(status: str):
    execute_stmt(
        "UPSERT INTO task_status(name) VALUES (%s)", (status,), returning_rs=False
    )


def delete_task_status(status: str):
    execute_stmt(
        "DELETE FROM task_status WHERE name = %s", (status,), returning_rs=False
    )


# ADMIN/USERS
USERS_COLS = get_fields(User)
USERINDB_COLS = get_fields(UserInDB)
USERINDB_PLACEHOLDERS = get_placeholders(UserInDB)


def get_all_users() -> list[User]:
    return execute_stmt(
        f"""
        SELECT {USERS_COLS} 
        FROM users
        ORDER BY full_name
        """,
        (),
        User,
        True,
    )


def get_user_with_hash(user_id: str) -> UserInDB | None:
    return execute_stmt(
        f"""
        select {USERINDB_COLS}
        from users 
        where user_id = %s
        """,
        (user_id,),
        UserInDB,
    )


def get_user(user_id: str) -> User | None:
    return execute_stmt(
        f"""
        select {USERS_COLS}
        from users 
        where user_id = %s
        """,
        (user_id,),
        User,
    )


def create_user(user: UserInDB) -> User | None:
    return execute_stmt(
        f"""
        insert into users 
            ({USERINDB_COLS})
        values
            ({USERINDB_PLACEHOLDERS})
        returning {USERS_COLS}
        """,
        tuple(user.dict().values()),
        User,
    )


def increase_failed_attempt_count(user_id: str) -> UserInDB | None:
    return execute_stmt(
        f"""update users set
            failed_attempts = failed_attempts +1 
        where user_id = %s
        returning {USERINDB_COLS}""",
        (user_id,),
        UserInDB,
    )


def update_user(user_id: str, user: UpdatedUserInDB) -> User | None:
    old_uid = get_user_with_hash(user_id)

    if old_uid:
        update_data = user.dict(exclude_unset=True)

        new_uid = old_uid.copy(update=update_data)

        return execute_stmt(
            f"""
            update users set 
            ({USERINDB_COLS}) = 
                ({USERINDB_PLACEHOLDERS})
            where user_id  = %s
            returning {USERS_COLS}
            """,
            (*tuple(new_uid.dict().values()), user_id),
            User,
        )


def delete_user(user_id: str) -> User | None:
    return execute_stmt(
        f"""
        delete from users
        where user_id = %s
        returning {USERS_COLS}
        """,
        (user_id,),
        User,
    )


def __get_where_clause(
    filters, table_name: str, include_where: bool = True
) -> tuple[str, tuple]:
    where: list[str] = []
    bind_params: list[Any] = []

    if not filters:
        return ("", ())

    filters_iter = iter(filters)

    for k, v in filters_iter:
        if v:
            # handling special case 'tags'
            if k == "tags":
                where.append(f"{table_name}.{k} @> %s")
                bind_params.append(v)
            elif k[-5:] == "_from":
                where.append(f"{table_name}.{k[:-5]} >= %s")
                bind_params.append(v)
            elif k[-3:] == "_to":
                where.append(f"{table_name}.{k[:-3]} <= %s")
                bind_params.append(v)
            else:
                where.append(f'{table_name}.{k} IN ({ ("%s, " * len(v))[:-2] })')
                bind_params += v

    where_clause: str = ""
    if where and include_where:
        where_clause = "WHERE "

    for x in where:
        where_clause += x + " AND "

    return (where_clause[:-4], tuple(bind_params))


# ACCOUNTS
ACCOUNT_IN_DB_COLS = get_fields(AccountInDB)
ACCOUNT_IN_DB_PLACEHOLDERS = get_placeholders(AccountInDB)
ACCOUNT_OVERVIEW_COLS = get_fields(AccountOverview)
ACCOUNTS_COLS = get_fields(Account)


def add_model_accounts(d):
    pass


def get_all_accounts(account_filters: AccountFilters | None) -> list[AccountOverview]:
    where_clause, bind_params = __get_where_clause(account_filters, "accounts")
    return execute_stmt(
        f"""
        SELECT {ACCOUNT_OVERVIEW_COLS}
        FROM accounts
        {where_clause} 
        ORDER BY name
        """,
        bind_params,
        AccountOverview,
        True,
    )


def get_account(account_id: UUID) -> Account | None:
    return execute_stmt(
        f"""
        SELECT {ACCOUNTS_COLS} 
        FROM accounts 
        WHERE account_id = %s
        """,
        (account_id,),
        Account,
    )


def create_account(account_in_db: AccountInDB) -> Account | None:
    return execute_stmt(
        f"""
        INSERT INTO accounts 
            ({ACCOUNT_IN_DB_COLS})
        VALUES
            ({ACCOUNT_IN_DB_PLACEHOLDERS})
        RETURNING {ACCOUNTS_COLS}
        """,
        tuple(account_in_db.dict().values()),
        Account,
    )


def update_account(account_in_db: AccountInDB) -> Account | None:
    if account_in_db.account_id:
        old_acc = get_account(account_in_db.account_id)
    else:
        return None

    if old_acc:
        old_acc = AccountInDB(**old_acc.dict())
        update_data = account_in_db.dict(exclude_unset=True)
        new_acc = old_acc.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE accounts SET 
                ({ACCOUNT_IN_DB_COLS}) = ({ACCOUNT_IN_DB_PLACEHOLDERS})
            WHERE account_id = %s
            RETURNING {ACCOUNTS_COLS}
            """,
            (*tuple(new_acc.dict().values()), account_in_db.account_id),
            Account,
        )


def delete_account(account_id: UUID) -> Account | None:
    return execute_stmt(
        f"""
        DELETE FROM accounts
        WHERE account_id = %s
        RETURNING {ACCOUNTS_COLS}
        """,
        (account_id,),
        Account,
    )


def add_account_attachment(account_id: UUID, s3_object_name: str) -> None:
    return execute_stmt(
        """
        UPDATE accounts SET
            attachments = array_append(attachments, %s)
        WHERE account_id = %s
        """,
        (s3_object_name, account_id),
        returning_rs=False,
    )


def remove_account_attachment(account_id: UUID, s3_object_name: str) -> None:
    return execute_stmt(
        """
        UPDATE accounts SET
            attachments = array_remove(attachments, %s)
        WHERE account_id = %s
        """,
        (s3_object_name, account_id),
        returning_rs=False,
    )


# CONTACTS
CONTACT_IN_DB_COLS = get_fields(ContactInDB)
CONTACT_IN_DB_PLACEHOLDERS = get_placeholders(ContactInDB)
CONTACT_OVERVIEW_COLS = get_fields(Contact)
CONTACT_COLS = get_fields(Contact)


def get_all_contacts() -> list[ContactWithAccountName]:
    fully_qualified = ", ".join([f"contacts.{x}" for x in Contact.__fields__.keys()])

    return execute_stmt(
        f"""
        SELECT {fully_qualified}, accounts.name AS account_name
        FROM accounts JOIN contacts
            ON accounts.account_id = contacts.account_id
        ORDER BY account_name, contacts.fname
        """,
        (),
        ContactWithAccountName,
        True,
    )


def get_all_contacts_for_account_id(account_id: UUID) -> list[Contact]:
    return execute_stmt(
        f"""
        SELECT {CONTACT_COLS}
        FROM contacts
        WHERE account_id = %s
        ORDER BY fname
        """,
        (account_id,),
        Contact,
        True,
    )


def get_contact(account_id: UUID, contact_id: UUID) -> Contact | None:
    return execute_stmt(
        f"""
        SELECT {CONTACT_COLS}
        FROM contacts 
        WHERE (account_id, contact_id) = (%s, %s)
        """,
        (account_id, contact_id),
        Contact,
    )


def create_contact(contact_in_db: ContactInDB) -> Contact | None:
    return execute_stmt(
        f"""
        INSERT INTO contacts 
            ({CONTACT_IN_DB_COLS})
        VALUES
            ({CONTACT_IN_DB_PLACEHOLDERS})
        RETURNING {CONTACT_COLS}
        """,
        tuple(contact_in_db.dict().values()),
        Contact,
    )


def update_contact(contact_in_db: ContactInDB) -> Contact | None:
    if contact_in_db.contact_id:
        old_contact = get_contact(contact_in_db.account_id, contact_in_db.contact_id)
    else:
        return None

    if old_contact:
        old_contact = ContactInDB(**old_contact.dict())
        update_data = contact_in_db.dict(exclude_unset=True)
        new_contact = old_contact.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE contacts SET 
                ({CONTACT_IN_DB_COLS}) = ({CONTACT_IN_DB_PLACEHOLDERS})
            WHERE (account_id, contact_id) = (%s, %s)
            RETURNING {CONTACT_COLS}
            """,
            (
                *tuple(new_contact.dict().values()),
                contact_in_db.account_id,
                contact_in_db.contact_id,
            ),
            Contact,
        )


def delete_contact(account_id: UUID, contact_id: UUID) -> Contact | None:
    return execute_stmt(
        f"""
        DELETE FROM contacts
        WHERE (account_id, contact_id) = (%s, %s)
        RETURNING {CONTACT_COLS}
        """,
        (account_id, contact_id),
        Contact,
    )


# OPPORTUNITIES
OPPORTUNITY_IN_DB_COLS = get_fields(OpportunityInDB)
OPPORTUNITY_IN_DB_PLACEHOLDERS = get_placeholders(OpportunityInDB)
OPPORTUNITY_OVERVIEW_COLS = get_fields(OpportunityOverview)
OPPORTUNITIES_COLS = get_fields(Opportunity)


def get_all_opportunities(
    opportunity_filters: OpportunityFilters | None,
) -> list[OpportunityOverviewWithAccountName]:
    where_clause, bind_params = __get_where_clause(
        opportunity_filters, table_name="opportunities"
    )

    fully_qualified = ", ".join(
        [f"opportunities.{x}" for x in OpportunityOverview.__fields__.keys()]
    )

    return execute_stmt(
        f"""
        SELECT {fully_qualified}, accounts.name AS account_name
        FROM accounts JOIN opportunities
            ON accounts.account_id = opportunities.account_id
        {where_clause}
        ORDER BY account_name, opportunities.name
        """,
        bind_params,
        OpportunityOverviewWithAccountName,
        True,
    )


def get_all_opportunities_for_account_id(account_id: UUID) -> list[OpportunityOverview]:
    return execute_stmt(
        f"""
        SELECT {OPPORTUNITY_OVERVIEW_COLS}
        FROM opportunities
        WHERE account_id = %s
        ORDER BY name
        """,
        (account_id,),
        OpportunityOverview,
        True,
    )


def get_opportunity(account_id: UUID, opportunity_id: UUID) -> Opportunity | None:
    return execute_stmt(
        f"""
        SELECT {OPPORTUNITIES_COLS}
        FROM opportunities 
        WHERE (account_id, opportunity_id) = (%s, %s)
        """,
        (account_id, opportunity_id),
        Opportunity,
    )


def create_opportunity(opportunity_in_db: OpportunityInDB) -> Opportunity | None:
    return execute_stmt(
        f"""
        INSERT INTO opportunities 
            ({OPPORTUNITY_IN_DB_COLS})
        VALUES
            ({OPPORTUNITY_IN_DB_PLACEHOLDERS})
        RETURNING {OPPORTUNITIES_COLS}
        """,
        tuple(opportunity_in_db.dict().values()),
        Opportunity,
    )


def update_opportunity(opportunity_in_db: OpportunityInDB) -> Opportunity | None:
    if opportunity_in_db.opportunity_id:
        old_opp = get_opportunity(
            opportunity_in_db.account_id, opportunity_in_db.opportunity_id
        )
    else:
        return None

    if old_opp:
        old_opp = OpportunityInDB(**old_opp.dict())
        update_data = opportunity_in_db.dict(exclude_unset=True)
        new_opp = old_opp.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE opportunities SET 
                ({OPPORTUNITY_IN_DB_COLS}) = ({OPPORTUNITY_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id) = (%s, %s)
            RETURNING {OPPORTUNITIES_COLS}
            """,
            (
                *tuple(new_opp.dict().values()),
                opportunity_in_db.account_id,
                opportunity_in_db.opportunity_id,
            ),
            Opportunity,
        )


def delete_opportunity(account_id: UUID, opportunity_id: UUID) -> Opportunity | None:
    return execute_stmt(
        f"""
        DELETE FROM opportunities
        WHERE (account_id, opportunity_id) = (%s, %s)
        RETURNING {OPPORTUNITIES_COLS}
        """,
        (account_id, opportunity_id),
        Opportunity,
    )


def add_opportunity_attachment(
    account_id: UUID, opportunity_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE opportunities SET
            attachments = array_append(attachments, %s)
        WHERE (account_id, opportunity_id) = (%s, %s)
        """,
        (s3_object_name, account_id, opportunity_id),
        returning_rs=False,
    )


def remove_opportunity_attachment(
    account_id: UUID, opportunity_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE opportunities SET
            attachments = array_remove(attachments, %s)
        WHERE (account_id, opportunity_id) = (%s, %s)
        """,
        (s3_object_name, account_id, opportunity_id),
        returning_rs=False,
    )


# ARTIFACT_SCHEMA
ARTIFACT_SCHEMA_IN_DB_COLS = get_fields(ArtifactSchemaInDB)
ARTIFACT_SCHEMA_IN_DB_PLACEHOLDERS = get_placeholders(ArtifactSchemaInDB)
ARTIFACT_SCHEMAS_COLS = get_fields(ArtifactSchema)


def get_all_artifact_schemas() -> list[ArtifactSchema]:
    return execute_stmt(
        f"""
        SELECT {ARTIFACT_SCHEMAS_COLS}
        FROM artifact_schemas
        ORDER BY name
        """,
        (),
        ArtifactSchema,
        True,
    )


def get_artifact_schema(artifact_schema_id: UUID) -> ArtifactSchema | None:
    return execute_stmt(
        f"""
        SELECT {ARTIFACT_SCHEMAS_COLS}
        FROM artifact_schemas 
        WHERE artifact_schema_id = %s
        """,
        (artifact_schema_id,),
        ArtifactSchema,
    )


def create_artifact_schema(
    artifact_schema_in_db: ArtifactSchemaInDB,
) -> ArtifactSchema | None:
    return execute_stmt(
        f"""
        INSERT INTO artifact_schemas 
            ({ARTIFACT_SCHEMA_IN_DB_COLS})
        VALUES
            ({ARTIFACT_SCHEMA_IN_DB_PLACEHOLDERS})
        RETURNING {ARTIFACT_SCHEMAS_COLS}
        """,
        tuple(artifact_schema_in_db.dict().values()),
        ArtifactSchema,
    )


def update_artifact_schema(
    artifact_schema_in_db: ArtifactSchemaInDB,
) -> ArtifactSchema | None:
    if artifact_schema_in_db.artifact_schema_id:
        old_art = get_artifact_schema(artifact_schema_in_db.artifact_schema_id)
    else:
        return None

    if old_art:
        old_art = ArtifactSchemaInDB(**old_art.dict())
        update_data = artifact_schema_in_db.dict(exclude_unset=True)
        new_art = old_art.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE artifact_schemas SET 
                ({ARTIFACT_SCHEMA_IN_DB_COLS}) = ({ARTIFACT_SCHEMA_IN_DB_PLACEHOLDERS})
            WHERE artifact_schema_id = %s
            RETURNING {ARTIFACT_SCHEMAS_COLS}
            """,
            (
                *tuple(new_art.dict().values()),
                new_art.artifact_schema_id,
            ),
            ArtifactSchema,
        )


def delete_artifact_schema(artifact_schema_id: UUID) -> ArtifactSchema | None:
    return execute_stmt(
        f"""
        DELETE FROM artifact_schemas
        WHERE artifact_schema_id = %s
        RETURNING {ARTIFACT_SCHEMAS_COLS}
        """,
        (artifact_schema_id,),
        ArtifactSchema,
    )


# ARTIFACTS
ARTIFACT_IN_DB_COLS = get_fields(ArtifactInDB)
ARTIFACT_IN_DB_PLACEHOLDERS = get_placeholders(ArtifactInDB)
ARTIFACT_OVERVIEW_COLS = get_fields(ArtifactOverview)
ARTIFACTS_COLS = get_fields(Artifact)


def get_all_artifacts(
    artifact_filters: ArtifactFilters | None,
) -> list[ArtifactOverviewWithAccountName]:
    where_clause, bind_params = __get_where_clause(
        artifact_filters, table_name="artifacts", include_where=False
    )

    fully_qualified = ", ".join(
        [f"artifacts.{x}" for x in ArtifactOverview.__fields__.keys()]
    )

    return execute_stmt(
        f"""
        SELECT
            {fully_qualified}, 
            accounts.name as account_name, 
            opportunities.name AS opportunity_name
        FROM accounts 
            JOIN opportunities 
                ON accounts.account_id = opportunities.account_id 
            JOIN artifacts 
                ON (opportunities.account_id, opportunities.opportunity_id) = (artifacts.account_id, artifacts.opportunity_id)
        {where_clause}
        ORDER BY account_name, opportunity_name, artifacts.name
        """,
        bind_params,
        ArtifactOverviewWithAccountName,
        True,
    )


def get_all_artifacts_for_account_id(
    account_id: UUID,
    artifact_filters: ArtifactFilters | None,
) -> list[ArtifactOverviewWithOpportunityName]:
    where_clause, bind_params = __get_where_clause(
        artifact_filters, table_name="artifacts", include_where=False
    )

    fully_qualified = ", ".join(
        [f"artifacts.{x}" for x in ArtifactOverview.__fields__.keys()]
    )

    return execute_stmt(
        f"""
        SELECT {fully_qualified}, opportunities.name AS opportunity_name
        FROM artifacts JOIN opportunities 
            ON (opportunities.account_id, opportunities.opportunity_id) = (artifacts.account_id, artifacts.opportunity_id) 
        WHERE account_id = %s {' AND ' if where_clause else ''} {where_clause}
        ORDER BY opportunity_name, artifacts.name
        """,
        (account_id,) + bind_params,
        ArtifactOverviewWithOpportunityName,
        True,
    )


def get_all_artifacts_for_opportunity_id(
    account_id: UUID, opportunity_id: UUID
) -> list[ArtifactOverview]:
    return execute_stmt(
        f"""
        SELECT {ARTIFACT_OVERVIEW_COLS}
        FROM artifacts
        WHERE (account_id, opportunity_id) = (%s, %s)
        ORDER BY name
        """,
        (account_id, opportunity_id),
        ArtifactOverview,
        True,
    )


def get_artifact(
    account_id: UUID, opportunity_id: UUID, artifact_id: UUID
) -> Artifact | None:
    return execute_stmt(
        f"""
        SELECT {ARTIFACTS_COLS}
        FROM artifacts 
        WHERE (account_id, opportunity_id, artifact_id) = (%s, %s, %s)
        """,
        (account_id, opportunity_id, artifact_id),
        Artifact,
    )


def create_artifact(artifact_in_db: ArtifactInDB) -> Artifact | None:
    return execute_stmt(
        f"""
        INSERT INTO artifacts 
            ({ARTIFACT_IN_DB_COLS})
        VALUES
            ({ARTIFACT_IN_DB_PLACEHOLDERS})
        RETURNING {ARTIFACTS_COLS}
        """,
        tuple(artifact_in_db.dict().values()),
        Artifact,
    )


def update_artifact(artifact_in_db: ArtifactInDB) -> Artifact | None:
    if artifact_in_db.artifact_id:
        old_proj = get_artifact(
            artifact_in_db.account_id,
            artifact_in_db.opportunity_id,
            artifact_in_db.artifact_id,
        )
    else:
        return None

    if old_proj:
        old_proj = ArtifactInDB(**old_proj.dict())
        update_data = artifact_in_db.dict(exclude_unset=True)
        new_proj = old_proj.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE artifacts SET 
                ({ARTIFACT_IN_DB_COLS}) = ({ARTIFACT_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, artifact_id) = (%s, %s, %s)
            RETURNING {ARTIFACTS_COLS}
            """,
            (
                *tuple(new_proj.dict().values()),
                artifact_in_db.account_id,
                artifact_in_db.opportunity_id,
                artifact_in_db.artifact_id,
            ),
            Artifact,
        )


def delete_artifact(
    account_id: UUID, opportunity_id: UUID, artifact_id: UUID
) -> Artifact | None:
    return execute_stmt(
        f"""
        DELETE FROM artifacts
        WHERE (account_id, opportunity_id, artifact_id) = (%s, %s, %s)
        RETURNING {ARTIFACTS_COLS}
        """,
        (account_id, opportunity_id, artifact_id),
        Artifact,
    )


# PROJECTS
PROJECT_IN_DB_COLS = get_fields(ProjectInDB)
PROJECT_IN_DB_PLACEHOLDERS = get_placeholders(ProjectInDB)
PROJECT_OVERVIEW_COLS = get_fields(ProjectOverview)
PROJECTS_COLS = get_fields(Project)


def get_all_projects(
    project_filters: ProjectFilters | None,
) -> list[ProjectOverviewWithAccountName]:
    where_clause, bind_params = __get_where_clause(
        project_filters, table_name="projects", include_where=False
    )

    fully_qualified = ", ".join(
        [f"projects.{x}" for x in ProjectOverview.__fields__.keys()]
    )

    return execute_stmt(
        f"""
        SELECT
            {fully_qualified}, 
            accounts.name as account_name, 
            opportunities.name AS opportunity_name
        FROM accounts
            JOIN opportunities
                ON accounts.account_id = opportunities.account_id 
            JOIN projects  
                ON (opportunities.account_id, opportunities.opportunity_id) = (projects.account_id, projects.opportunity_id)
        {where_clause}
        ORDER BY account_name, opportunity_name, projects.name
        """,
        bind_params,
        ProjectOverviewWithAccountName,
        True,
    )


def get_all_projects_for_account_id(
    account_id: UUID,
    project_filters: ProjectFilters | None,
) -> list[ProjectOverviewWithOpportunityName]:
    where_clause, bind_params = __get_where_clause(
        project_filters, table_name="projects", include_where=False
    )

    fully_qualified = ", ".join(
        [f"projects.{x}" for x in ProjectOverview.__fields__.keys()]
    )

    return execute_stmt(
        f"""
        SELECT {fully_qualified}, opportunities.name AS opportunity_name
        FROM projects JOIN opportunities 
            ON (opportunities.account_id, opportunities.opportunity_id) = (projects.account_id, projects.opportunity_id) 
        WHERE account_id = %s {' AND ' if where_clause else ''} {where_clause}
        ORDER BY opportunity_name, projects.name
        """,
        (account_id,) + bind_params,
        ProjectOverviewWithOpportunityName,
        True,
    )


def get_all_projects_for_opportunity_id(
    account_id: UUID, opportunity_id: UUID
) -> list[ProjectOverview]:
    return execute_stmt(
        f"""
        SELECT {PROJECT_OVERVIEW_COLS}
        FROM projects
        WHERE (account_id, opportunity_id) = (%s, %s)
        ORDER BY name
        """,
        (account_id, opportunity_id),
        ProjectOverview,
        True,
    )


def get_project(
    account_id: UUID, opportunity_id: UUID, project_id: UUID
) -> Project | None:
    return execute_stmt(
        f"""
        SELECT {PROJECTS_COLS}
        FROM projects 
        WHERE (account_id, opportunity_id, project_id) = (%s, %s, %s)
        """,
        (account_id, opportunity_id, project_id),
        Project,
    )


def create_project(project_in_db: ProjectInDB) -> Project | None:
    return execute_stmt(
        f"""
        INSERT INTO projects 
            ({PROJECT_IN_DB_COLS})
        VALUES
            ({PROJECT_IN_DB_PLACEHOLDERS})
        RETURNING {PROJECTS_COLS}
        """,
        tuple(project_in_db.dict().values()),
        Project,
    )


def update_project(project_in_db: ProjectInDB) -> Project | None:
    if project_in_db.project_id:
        old_proj = get_project(
            project_in_db.account_id,
            project_in_db.opportunity_id,
            project_in_db.project_id,
        )
    else:
        return None

    if old_proj:
        old_proj = ProjectInDB(**old_proj.dict())
        update_data = project_in_db.dict(exclude_unset=True)
        new_proj = old_proj.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE projects SET 
                ({PROJECT_IN_DB_COLS}) = ({PROJECT_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, project_id) = (%s, %s, %s)
            RETURNING {PROJECTS_COLS}
            """,
            (
                *tuple(new_proj.dict().values()),
                project_in_db.account_id,
                project_in_db.opportunity_id,
                project_in_db.project_id,
            ),
            Project,
        )


def delete_project(
    account_id: UUID, opportunity_id: UUID, project_id: UUID
) -> Project | None:
    return execute_stmt(
        f"""
        DELETE FROM projects
        WHERE (account_id, opportunity_id, project_id) = (%s, %s, %s)
        RETURNING {PROJECTS_COLS}
        """,
        (account_id, opportunity_id, project_id),
        Project,
    )


def add_project_attachment(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE projects SET
            attachments = array_append(attachments, %s)
        WHERE (account_id, opportunity_id, project_id) = (%s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, project_id),
        returning_rs=False,
    )


def remove_project_attachment(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE projects SET
            attachments = array_remove(attachments, %s)
        WHERE (account_id, opportunity_id, project_id) = (%s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, project_id),
        returning_rs=False,
    )


# TASKS
TASK_IN_DB_COLS = get_fields(TaskInDB)
TASK_IN_DB_PLACEHOLDERS = get_placeholders(TaskInDB)
TASK_OVERVIEW_COLS = get_fields(TaskOverview)
TASKS_COLS = get_fields(Task)


def get_all_tasks_for_opportunity_id(
    account_id: UUID, opportunity_id: UUID, task_filters: TaskFilters | None = None
) -> list[TaskOverviewWithProjectName]:
    where_clause, bind_params = __get_where_clause(
        task_filters, table_name="tasks", include_where=False
    )

    fully_qualified = ", ".join([f"tasks.{x}" for x in TaskOverview.__fields__.keys()])

    return execute_stmt(
        f"""
        SELECT {fully_qualified}, projects.name AS project_name
        FROM tasks JOIN projects
            ON (tasks.account_id, tasks.project_id) = (projects.account_id, projects.project_id)
        WHERE tasks.account_id = %s
        {' AND ' if where_clause else ''} {where_clause}
        ORDER BY project_name, task_id DESC
        """,
        (account_id,) + bind_params,
        TaskOverviewWithProjectName,
        True,
    )


def get_all_tasks_for_project_id(
    account_id: UUID, opportunity_id: UUID, project_id: UUID
) -> list[TaskOverview]:
    return execute_stmt(
        f"""
        SELECT {TASK_OVERVIEW_COLS}
        FROM tasks
        WHERE (account_id, opportunity_id, project_id) =  (%s, %s, %s)
        ORDER BY task_id DESC
        """,
        (account_id, opportunity_id, project_id),
        TaskOverview,
        True,
    )


def get_task(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, task_id: UUID
) -> Task | None:
    return execute_stmt(
        f"""
        SELECT {TASKS_COLS}
        FROM tasks 
        WHERE (account_id, opportunity_id, project_id, task_id) = (%s, %s, %s, %s)
        """,
        (account_id, opportunity_id, project_id, task_id),
        Task,
    )


def create_task(task_in_db: TaskInDB) -> Task | None:
    return execute_stmt(
        f"""
        INSERT INTO tasks 
            ({TASK_IN_DB_COLS})
        VALUES
            ({TASK_IN_DB_PLACEHOLDERS})
        RETURNING {TASKS_COLS}
        """,
        tuple(task_in_db.dict().values()),
        Task,
    )


def update_task(task_in_db: TaskInDB) -> Task | None:
    if task_in_db.task_id:
        old_task = get_task(
            task_in_db.account_id,
            task_in_db.opportunity_id,
            task_in_db.project_id,
            task_in_db.task_id,
        )
    else:
        return None

    if old_task:
        old_task = TaskInDB(**old_task.dict())
        update_data = task_in_db.dict(exclude_unset=True)
        new_task = old_task.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE tasks SET 
                ({TASK_IN_DB_COLS}) = ({TASK_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, project_id, task_id) = (%s, %s, %s, %s)
            RETURNING {TASKS_COLS}
            """,
            (
                *tuple(new_task.dict().values()),
                task_in_db.account_id,
                task_in_db.opportunity_id,
                task_in_db.project_id,
                task_in_db.task_id,
            ),
            Task,
        )


def delete_task(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, task_id: UUID
) -> Task | None:
    return execute_stmt(
        f"""
        DELETE FROM tasks
        WHERE (account_id, opportunity_id, project_id, task_id) = (%s, %s, %s, %s)
        RETURNING {TASKS_COLS}
        """,
        (account_id, opportunity_id, project_id, task_id),
        Task,
    )


def add_task_attachment(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    s3_object_name: str,
) -> None:
    return execute_stmt(
        """
        UPDATE tasks SET
            attachments = array_append(attachments, %s)
        WHERE (account_id, opportunity_id, project_id, task_id) = (%s, %s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, project_id, task_id),
        returning_rs=False,
    )


def remove_task_attachment(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    s3_object_name: str,
) -> None:
    return execute_stmt(
        """
        UPDATE tasks SET
            attachments = array_remove(attachments, %s)
        WHERE (account_id, opportunity_id, project_id, task_id) = (%s, %s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, project_id, task_id),
        returning_rs=False,
    )


# NOTES
ACC_NOTE_IN_DB_COLS = get_fields(AccountNoteInDB)
OPP_NOTE_IN_DB_COLS = get_fields(OpportunityNoteInDB)
PROJ_NOTE_IN_DB_COLS = get_fields(ProjectNoteInDB)
ACC_NOTE_IN_DB_PLACEHOLDERS = get_placeholders(AccountNoteInDB)
OPP_NOTE_IN_DB_PLACEHOLDERS = get_placeholders(OpportunityNoteInDB)
PROJ_NOTE_IN_DB_PLACEHOLDERS = get_placeholders(ProjectNoteInDB)
ACCOUNT_NOTES_COLS = get_fields(AccountNote)
OPPORTUNITY_NOTES_COLS = get_fields(OpportunityNote)
PROJECT_NOTES_COLS = get_fields(ProjectNote)


# ACCOUNT_NOTES
def get_all_account_notes(
    account_id: UUID, note_filters: NoteFilters | None = None
) -> list[AccountNoteOverview]:
    where_clause, bind_params = __get_where_clause(
        note_filters, table_name="account_notes", include_where=False
    )

    return execute_stmt(
        f"""
        SELECT {ACCOUNT_NOTES_COLS}
        FROM account_notes
        WHERE account_id = %s
        {' AND ' if where_clause else ''} {where_clause}
        ORDER BY name
        """,
        (account_id,) + bind_params,
        AccountNoteOverview,
        True,
    )


def get_account_note(account_id: UUID, note_id: UUID) -> AccountNote | None:
    return execute_stmt(
        f"""
        SELECT {ACCOUNT_NOTES_COLS}
        FROM account_notes 
        WHERE (account_id, note_id) = (%s, %s)
        """,
        (account_id, note_id),
        AccountNote,
    )


def create_account_note(note_in_db: AccountNoteInDB) -> AccountNote | None:
    return execute_stmt(
        f"""
        INSERT INTO account_notes 
            ({ACC_NOTE_IN_DB_COLS})
        VALUES
            ({ACC_NOTE_IN_DB_PLACEHOLDERS})
        RETURNING {ACCOUNT_NOTES_COLS}
        """,
        tuple(note_in_db.dict().values()),
        AccountNote,
    )


def update_account_note(note_in_db: AccountNoteInDB) -> AccountNote | None:
    if note_in_db.note_id:
        old_note = get_account_note(note_in_db.account_id, note_in_db.note_id)
    else:
        return None

    if old_note:
        old_note = AccountNoteInDB(**old_note.dict())
        update_data = note_in_db.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE account_notes SET 
                ({ACC_NOTE_IN_DB_COLS}) = ({ACC_NOTE_IN_DB_PLACEHOLDERS})
            WHERE (account_id, note_id) = (%s, %s)
            RETURNING {ACCOUNT_NOTES_COLS}
            """,
            (
                *tuple(new_note.dict().values()),
                note_in_db.account_id,
                note_in_db.note_id,
            ),
            AccountNote,
        )


def delete_account_note(account_id: UUID, note_id: UUID) -> AccountNote | None:
    return execute_stmt(
        f"""
        DELETE FROM account_notes
        WHERE (account_id, note_id) = (%s, %s)
        RETURNING {ACCOUNT_NOTES_COLS}
        """,
        (account_id, note_id),
        AccountNote,
    )


def add_account_note_attachment(
    account_id: UUID, note_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE account_notes SET
            attachments = array_append(attachments, %s)
        WHERE (account_id, note_id) = (%s, %s)
        """,
        (s3_object_name, account_id, note_id),
        returning_rs=False,
    )


def remove_account_note_attachment(
    account_id: UUID, note_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE account_notes SET
            attachments = array_remove(attachments, %s)
        WHERE (account_id, note_id) = (%s, %s)
        """,
        (s3_object_name, account_id, note_id),
        returning_rs=False,
    )


# OPPORTUNITY_NOTE
def get_all_opportunity_notes(
    account_id: UUID, opportunity_id: UUID, note_filters: NoteFilters | None = None
) -> list[OpportunityNoteOverview]:
    where_clause, bind_params = __get_where_clause(
        note_filters, table_name="account_notes", include_where=False
    )

    return execute_stmt(
        f"""
        SELECT {OPPORTUNITY_NOTES_COLS}
        FROM opportunity_notes
        WHERE (account_id, opportunity_id) = (%s, %s)
        {' AND ' if where_clause else ''} {where_clause}
        ORDER BY name
        """,
        (account_id, opportunity_id) + bind_params,
        OpportunityNoteOverview,
        True,
    )


def get_opportunity_note(
    account_id: UUID, opportunity_id: UUID, note_id: UUID
) -> OpportunityNote | None:
    return execute_stmt(
        f"""
        SELECT {OPPORTUNITY_NOTES_COLS}
        FROM opportunity_notes 
        WHERE (account_id, opportunity_id, note_id) = (%s, $s, %s)
        """,
        (account_id, opportunity_id, note_id),
        OpportunityNote,
    )


def create_opportunity_note(note_in_db: OpportunityNoteInDB) -> OpportunityNote | None:
    return execute_stmt(
        f"""
        INSERT INTO opportunity_notes 
            ({OPP_NOTE_IN_DB_COLS})
        VALUES
            ({OPP_NOTE_IN_DB_PLACEHOLDERS})
        RETURNING {OPPORTUNITY_NOTES_COLS}
        """,
        tuple(note_in_db.dict().values()),
        OpportunityNote,
    )


def update_opportunity_note(note_in_db: OpportunityNoteInDB) -> OpportunityNote | None:
    if note_in_db.note_id:
        old_note = get_opportunity_note(
            note_in_db.account_id, note_in_db.opportunity_id, note_in_db.note_id
        )
    else:
        return None

    if old_note:
        old_note = OpportunityNoteInDB(**old_note.dict())
        update_data = note_in_db.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE opportunity_notes SET 
                ({OPP_NOTE_IN_DB_COLS}) = ({OPP_NOTE_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, note_id) = (%s, %s, %s)
            RETURNING {OPPORTUNITY_NOTES_COLS}
            """,
            (
                *tuple(new_note.dict().values()),
                note_in_db.account_id,
                note_in_db.opportunity_id,
                note_in_db.note_id,
            ),
            OpportunityNote,
        )


def delete_opportunity_note(
    account_id: UUID, opportunity_id: UUID, note_id: UUID
) -> OpportunityNote | None:
    return execute_stmt(
        f"""
        DELETE FROM opportunity_notes
        WHERE (account_id, opportunity_id, note_id) = (%s, %s, %s)
        RETURNING {OPPORTUNITY_NOTES_COLS}
        """,
        (account_id, opportunity_id, note_id),
        OpportunityNote,
    )


def add_opportunity_note_attachment(
    account_id: UUID, opportunity_id: UUID, note_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE opportunity_notes SET
            attachments = array_append(attachments, %s)
        WHERE (account_id, opportunity_id, note_id) = (%s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, note_id),
        returning_rs=False,
    )


def remove_opportunity_note_attachment(
    account_id: UUID, opportunity_id: UUID, note_id: UUID, s3_object_name: str
) -> None:
    return execute_stmt(
        """
        UPDATE opportunity_notes SET
            attachments = array_remove(attachments, %s)
        WHERE (account_id, opportunity_id, note_id) = (%s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, note_id),
        returning_rs=False,
    )


# PROJECT_NOTE
def get_all_project_notes(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_filters: NoteFilters | None = None,
) -> list[ProjectNoteOverview]:
    where_clause, bind_params = __get_where_clause(
        note_filters, table_name="account_notes", include_where=False
    )

    return execute_stmt(
        f"""
        SELECT {PROJECT_NOTES_COLS}
        FROM project_notes
        WHERE (account_id, opportunity_id, project_id) = (%s, %s, %s)
        {' AND ' if where_clause else ''} {where_clause}
        ORDER BY name
        """,
        (account_id, opportunity_id, project_id) + bind_params,
        ProjectNoteOverview,
        True,
    )


def get_project_note(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, note_id: UUID
) -> ProjectNote | None:
    return execute_stmt(
        f"""
        SELECT {PROJECT_NOTES_COLS}
        FROM project_notes 
        WHERE (account_id, opportunity_id, project_id, note_id) = (%s, $s, %s, %s)
        """,
        (account_id, opportunity_id, project_id, note_id),
        ProjectNote,
    )


def create_project_note(note_in_db: ProjectNoteInDB) -> ProjectNote | None:
    return execute_stmt(
        f"""
        INSERT INTO project_notes 
            ({PROJ_NOTE_IN_DB_COLS})
        VALUES
            ({PROJ_NOTE_IN_DB_PLACEHOLDERS})
        RETURNING {PROJECT_NOTES_COLS}
        """,
        tuple(note_in_db.dict().values()),
        ProjectNote,
    )


def update_project_note(note_in_db: ProjectNoteInDB) -> ProjectNote | None:
    if note_in_db.note_id:
        old_note = get_project_note(
            note_in_db.account_id,
            note_in_db.opportunity_id,
            note_in_db.project_id,
            note_in_db.note_id,
        )
    else:
        return None

    if old_note:
        old_note = ProjectNoteInDB(**old_note.dict())
        update_data = note_in_db.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE project_notes SET 
                ({PROJ_NOTE_IN_DB_COLS}) = ({PROJ_NOTE_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, project_id, note_id) = (%s, %s, %s, %s)
            RETURNING {PROJECT_NOTES_COLS}
            """,
            (
                *tuple(new_note.dict().values()),
                note_in_db.account_id,
                note_in_db.opportunity_id,
                note_in_db.project_id,
                note_in_db.note_id,
            ),
            ProjectNote,
        )


def delete_project_note(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, note_id: UUID
) -> ProjectNote | None:
    return execute_stmt(
        f"""
        DELETE FROM project_notes
        WHERE (account_id, opportunity_id, project_id, note_id) = (%s, %s, %s, %s)
        RETURNING {PROJECT_NOTES_COLS}
        """,
        (account_id, opportunity_id, project_id, note_id),
        ProjectNote,
    )


def add_project_note_attachment(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    s3_object_name: str,
) -> None:
    return execute_stmt(
        """
        UPDATE project_notes SET
            attachments = array_append(attachments, %s)
        WHERE (account_id, opportunity_id, project_id, note_id) = (%s, %s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, project_id, note_id),
        returning_rs=False,
    )


def remove_project_note_attachment(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    s3_object_name: str,
) -> None:
    return execute_stmt(
        """
        UPDATE project_notes SET
            attachments = array_remove(attachments, %s)
        WHERE (account_id, opportunity_id, project_id, note_id) = (%s, %s, %s, %s)
        """,
        (s3_object_name, account_id, opportunity_id, project_id, note_id),
        returning_rs=False,
    )


from psycopg.types.json import Jsonb, JsonbDumper


class DictJsonbDumper(JsonbDumper):
    def dump(self, obj):
        return super().dump(Jsonb(obj))


# ==============================================================================================
def execute_stmt(
    stmt: str,
    args: tuple = (),
    model: PyObject = Any,
    is_list: bool = False,
    returning_rs: bool = True,
) -> Any:
    with pool.connection() as conn:
        # convert a set to a psycopg list
        conn.adapters.register_dumper(set, ListDumper)
        conn.adapters.register_dumper(dict, DictJsonbDumper)

        with conn.cursor() as cur:
            try:
                cur.execute(stmt, args)  # type: ignore

                if not returning_rs:
                    return

                if not cur.description:
                    raise ValueError("Could not fetch column names from ResultSet")
                col_names = [desc[0] for desc in cur.description]

                if is_list:
                    rsl = cur.fetchall()
                    for x in rsl:
                        print(x)
                    return [
                        model(**{k: rs[i] for i, k in enumerate(col_names)})
                        for rs in rsl
                    ]
                else:
                    rs = cur.fetchone()
                    if rs:
                        return model(**{k: rs[i] for i, k in enumerate(col_names)})
                    else:
                        return None
            except Exception as e:
                # TODO correctly handle error such as PK violations
                print(e)
                return None
