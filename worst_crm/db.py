from psycopg_pool import ConnectionPool
from pydantic import PyObject
from typing import Any
from uuid import UUID
import datetime as dt
import os

from worst_crm.models import (
    NewAccount,
    Account,
    AccountFilters,
    AccountInDB,
    AccountOverview,
    NewOpportunity,
    NewOpportunityNote,
    NewProjectNote,
    Opportunity,
    OpportunityFilters,
    OpportunityInDB,
    OpportunityNote,
    OpportunityOverview,
    OpportunityOverviewWithAccountName,
    NewTask,
    ProjectNote,
    Task,
    TaskFilters,
    TaskInDB,
    TaskOverview,
    TaskOverviewWithProjectName,
    NewAccountNote,
    AccountNote,
    NoteFilters,
    NoteInDB,
    NoteOverview,
    NoteOverviewWithProjectName,
    NewProject,
    Project,
    ProjectFilters,
    ProjectInDB,
    ProjectOverview,
    ProjectOverviewWithAccountName,
    ProjectOverviewWithOpportunityName,
    Status,
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


def create_account(account_in_db: AccountInDB) -> NewAccount:
    return execute_stmt(
        f"""
        INSERT INTO accounts 
            ({ACCOUNT_IN_DB_COLS})
        VALUES
            ({ACCOUNT_IN_DB_PLACEHOLDERS})
        RETURNING account_id
        """,
        tuple(account_in_db.dict().values()),
        NewAccount,
    )


def update_account(account_id: UUID, account: AccountInDB) -> Account | None:
    old_acc = get_account(account_id)

    if old_acc:
        old_acc = AccountInDB(**old_acc.dict())
        update_data = account.dict(exclude_unset=True)
        new_acc = old_acc.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE accounts SET 
                ({ACCOUNT_IN_DB_COLS}) = ({ACCOUNT_IN_DB_PLACEHOLDERS})
            WHERE account_id = %s
            RETURNING {ACCOUNTS_COLS}
            """,
            (*tuple(new_acc.dict().values()), account_id),
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


# OPPORTUNITIES
OPPORTUNITY_IN_DB_COLS = get_fields(ProjectInDB)
OPPORTUNITY_IN_DB_PLACEHOLDERS = get_placeholders(ProjectInDB)
OPPORTUNITY_OVERVIEW_COLS = get_fields(ProjectOverview)
OPPORTUNITIES_COLS = get_fields(Project)


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
        SELECT {fully_qualified}, opportunities.name AS opportunity_name
        FROM projects JOIN opportunities
            ON projects.opportunity_id = opportunities.opportunity_id
        {where_clause}
        ORDER BY opportunity_name, projects.name
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


def create_opportunity(
    account_id: UUID, opportunity_in_db: OpportunityInDB
) -> NewOpportunity | None:
    return execute_stmt(
        f"""
        INSERT INTO opportunities 
            ({OPPORTUNITY_IN_DB_COLS}, account_id)
        VALUES
            ({OPPORTUNITY_IN_DB_PLACEHOLDERS}, %s)
        RETURNING account_id, opportunity_id
        """,
        (*tuple(opportunity_in_db.dict().values()), account_id),
        NewProject,
    )


def update_opportunity(
    account_id: UUID, opportunity_id: UUID, opportunity_in_db: OpportunityInDB
) -> Opportunity | None:
    old_opp = get_opportunity(account_id, opportunity_id)

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
            (*tuple(new_opp.dict().values()), account_id, opportunity_id),
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
        Project,
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
        FROM accounts a 
            JOIN opportunities o 
                ON a.account_id = o.account_id 
            JOIN projects p 
                ON (o.account_id, o.opportunity_id) = (p.account_id, p.opportunity_id)
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
        FROM projects p JOIN opportunities o
            ON (o.account_id, o.opportunity_id) = (p.account_id, p.opportunity_id) 
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


def create_project(
    account_id: UUID, opportunity_id: UUID, project_in_db: ProjectInDB
) -> NewProject | None:
    return execute_stmt(
        f"""
        INSERT INTO projects 
            ({PROJECT_IN_DB_COLS}, account_id, opportunity_id)
        VALUES
            ({PROJECT_IN_DB_PLACEHOLDERS}, %s, %s)
        RETURNING account_id, opportunity_id, project_id
        """,
        (*tuple(project_in_db.dict().values()), account_id, opportunity_id),
        NewProject,
    )


def update_project(
    account_id: UUID, project_id: UUID, opportunity_id: UUID, project_in_db: ProjectInDB
) -> Project | None:
    old_proj = get_project(account_id, opportunity_id, project_id)

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
            (*tuple(new_proj.dict().values()), account_id, opportunity_id, project_id),
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
        FROM tasks t JOIN projects p
            ON (t.account_id, t.project_id) = (p.account_id, p.project_id)
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


def create_task(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, task_in_db: TaskInDB
) -> NewTask | None:
    return execute_stmt(
        f"""
        INSERT INTO tasks 
            ({TASK_IN_DB_COLS}, account_id, opportunity_id, project_id)
        VALUES
            ({TASK_IN_DB_PLACEHOLDERS}, %s, %s, %s)
        RETURNING account_id, project_id, task_id
        """,
        (*tuple(task_in_db.dict().values()), account_id, opportunity_id, project_id),
        NewTask,
    )


def update_task(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    task_id: UUID,
    task_in_db: TaskInDB,
) -> Task | None:
    old_task = get_task(account_id, opportunity_id, project_id, task_id)

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
                account_id,
                opportunity_id,
                project_id,
                task_id,
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
NOTE_IN_DB_COLS = get_fields(NoteInDB)
NOTE_IN_DB_PLACEHOLDERS = get_placeholders(NoteInDB)
NOTE_OVERVIEW_COLS = get_fields(NoteOverview)
ACCOUNT_NOTES_COLS = get_fields(AccountNote)
OPPORTUNITY_NOTES_COLS = get_fields(OpportunityNote)
PROJECT_NOTES_COLS = get_fields(ProjectNote)


# def get_all_notes(
#     account_id: UUID, note_filters: NoteFilters
# ) -> list[NoteOverviewWithProjectName]:
#     where_clause, bind_params = __get_where_clause(
#         note_filters, table_name="notes", include_where=False
#     )

#     fully_qualified = ", ".join([f"notes.{x}" for x in NoteOverview.__fields__.keys()])

#     return execute_stmt(
#         f"""
#         SELECT {fully_qualified}, projects.name AS project_name
#         FROM notes JOIN projects
#             ON notes.project_id = projects.project_id
#         WHERE notes.account_id = %s
#         {' AND ' if where_clause else ''} {where_clause}
#         ORDER BY project_name, note_id DESC
#         """,
#         (account_id,) + bind_params,
#         NoteOverviewWithProjectName,
#         True,
#     )


# def get_all_notes_for_project_id(
#     account_id: UUID, project_id: UUID
# ) -> list[NoteOverview]:
#     return execute_stmt(
#         f"""
#         SELECT {NOTE_OVERVIEW_COLS}
#         FROM notes
#         WHERE (account_id, project_id) =  (%s, %s)
#         ORDER BY note_id DESC
#         """,
#         (account_id, project_id),
#         NoteOverview,
#         True,
#     )

# ACCOUNT_NOTES
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


def create_account_note(
    account_id: UUID, note_in_db: NoteInDB
) -> NewAccountNote | None:
    return execute_stmt(
        f"""
        INSERT INTO account_notes 
            ({NOTE_IN_DB_COLS}, account_id)
        VALUES
            ({NOTE_IN_DB_PLACEHOLDERS}, %s)
        RETURNING account_id, note_id
        """,
        (*tuple(note_in_db.dict().values()), account_id),
        NewAccountNote,
    )


def update_account_note(
    account_id: UUID, note_id: UUID, note_in_db: NoteInDB
) -> AccountNote | None:
    old_note = get_account_note(account_id, note_id)

    if old_note:
        old_note = NoteInDB(**old_note.dict())
        update_data = note_in_db.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE account_notes SET 
                ({NOTE_IN_DB_COLS}) = ({NOTE_IN_DB_PLACEHOLDERS})
            WHERE (account_id, note_id) = (%s, %s)
            RETURNING {ACCOUNT_NOTES_COLS}
            """,
            (*tuple(new_note.dict().values()), account_id, note_id),
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


def create_opportunity_note(
    account_id: UUID, opportunity_id: UUID, note_in_db: NoteInDB
) -> NewOpportunityNote | None:
    return execute_stmt(
        f"""
        INSERT INTO opportunity_notes 
            ({NOTE_IN_DB_COLS}, account_id, opportunity_id)
        VALUES
            ({NOTE_IN_DB_PLACEHOLDERS}, %s, %s)
        RETURNING account_id, opportunity_id, note_id
        """,
        (*tuple(note_in_db.dict().values()), account_id, opportunity_id),
        NewOpportunityNote,
    )


def update_opportunity_note(
    account_id: UUID, opportunity_id: UUID, note_id: UUID, note_in_db: NoteInDB
) -> OpportunityNote | None:
    old_note = get_opportunity_note(account_id, opportunity_id, note_id)

    if old_note:
        old_note = NoteInDB(**old_note.dict())
        update_data = note_in_db.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE opportunity_notes SET 
                ({NOTE_IN_DB_COLS}) = ({NOTE_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, note_id) = (%s, %s, %s)
            RETURNING {OPPORTUNITY_NOTES_COLS}
            """,
            (*tuple(new_note.dict().values()), account_id, opportunity_id, note_id),
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


def create_project_note(
    account_id: UUID, opportunity_id: UUID, project_id: UUID, note_in_db: NoteInDB
) -> NewProjectNote | None:
    return execute_stmt(
        f"""
        INSERT INTO project_notes 
            ({NOTE_IN_DB_COLS}, account_id, opportunity_id, project_id)
        VALUES
            ({NOTE_IN_DB_PLACEHOLDERS}, %s, %s, %s)
        RETURNING account_id, opportunity_id, note_id
        """,
        (*tuple(note_in_db.dict().values()), account_id, opportunity_id, project_id),
        NewProjectNote,
    )


def update_project_note(
    account_id: UUID,
    opportunity_id: UUID,
    project_id: UUID,
    note_id: UUID,
    note_in_db: NoteInDB,
) -> ProjectNote | None:
    old_note = get_project_note(account_id, opportunity_id, project_id, note_id)

    if old_note:
        old_note = NoteInDB(**old_note.dict())
        update_data = note_in_db.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE project_notes SET 
                ({NOTE_IN_DB_COLS}) = ({NOTE_IN_DB_PLACEHOLDERS})
            WHERE (account_id, opportunity_id, project_id, note_id) = (%s, %s, %s, %s)
            RETURNING {PROJECT_NOTES_COLS}
            """,
            (
                *tuple(new_note.dict().values()),
                account_id,
                opportunity_id,
                project_id,
                note_id,
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


# ==============================================================================================
def execute_stmt(
    stmt: str,
    args: tuple = (),
    model: PyObject = Any,
    is_list: bool = False,
    returning_rs: bool = True,
) -> Any:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt, args)  # type: ignore

            if not returning_rs:
                return

            if not cur.description:
                raise ValueError("Could not fetch column names from ResultSet")
            col_names = [desc[0] for desc in cur.description]

            if is_list:
                rsl = cur.fetchall()
                return [
                    model(**{k: rs[i] for i, k in enumerate(col_names)}) for rs in rsl
                ]
            else:
                rs = cur.fetchone()
                if rs:
                    return model(**{k: rs[i] for i, k in enumerate(col_names)})
                else:
                    return None
