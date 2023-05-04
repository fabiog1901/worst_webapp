from typing import Any
from psycopg_pool import ConnectionPool
from pydantic import PyObject
import os

from uuid import UUID

from worst_crm.models import (
    NewAccount,
    Account,
    NewProject,
    Project,
    NewNote,
    Note,
    NewTask,
    Task,
)
from worst_crm.models import User, UserInDB, UpdatedUserInDB


DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")

# the pool starts connecting immediately.
pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


def get_fields(model) -> str:
    return ", ".join([x for x in model.__fields__.keys()])


def get_placeholders(model) -> str:
    return ("%s, " * len(tuple(model.__fields__.keys())))[:-2]


# ADMIN/USERS
USERS_COLS = get_fields(User)
USERINDB_COLS = get_fields(UserInDB)
USERINDB_PLACEHOLDERS = get_placeholders(UserInDB)


def get_all_users() -> list[User]:
    return execute_stmt(
        f"""
        select {USERS_COLS} 
        from users
        order by full_name
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


# ACCOUNTS
NEWACCOUNT_COLS = get_fields(NewAccount)
NEWACCOUNT_PLACEHOLDERS = get_placeholders(NewAccount)
ACCOUNTS_COLS = get_fields(Account)


def get_all_accounts() -> list[Account]:
    return execute_stmt(
        f"""
        select {ACCOUNTS_COLS}
        from accounts
        order by account_name
        """,
        (),
        Account,
        True,
    )


def get_account(account_id: UUID) -> Account | None:
    return execute_stmt(
        f"""
        select {ACCOUNTS_COLS} 
        from accounts 
        where account_id = %s
        """,
        (account_id,),
        Account,
    )


def create_account(new_account: NewAccount) -> Account | None:
    return execute_stmt(
        f"""
        insert into accounts ({NEWACCOUNT_COLS})
        values
        ({NEWACCOUNT_PLACEHOLDERS})
        returning {ACCOUNTS_COLS}
        """,
        tuple(new_account.dict().values()),
        Account,
    )


def update_account(account_id: UUID, account: NewAccount) -> Account | None:
    old_acc = get_account(account_id)

    if old_acc:
        old_acc = NewAccount(**old_acc.dict())
        update_data = account.dict(exclude_unset=True)
        new_acc = old_acc.copy(update=update_data)

        return execute_stmt(
            f"""
            update accounts set 
                ({NEWACCOUNT_COLS}) = ({NEWACCOUNT_PLACEHOLDERS})
            where account_id = %s
            returning {ACCOUNTS_COLS}
            """,
            (*tuple(new_acc.dict().values()), account_id),
            Account,
        )


def delete_account(account_id: UUID) -> Account | None:
    return execute_stmt(
        f"""
        delete from accounts
        where account_id = %s
        returning {ACCOUNTS_COLS}
        """,
        (account_id,),
        Account,
    )


# PROJECTS
PROJECTS_COLS = get_fields(Project)
NEWPROJECT_COLS = get_fields(NewProject)
NEWPROJECT_PLACEHOLODERS = get_placeholders(NewProject)


def get_all_projects(account_id: UUID) -> list[Project]:
    return execute_stmt(
        f"""
        select {PROJECTS_COLS}
        from projects
        where account_id = %s
        order by project_name
        """,
        (account_id,),
        Project,
        True,
    )


def get_project(account_id: UUID, project_id: UUID) -> Project | None:
    return execute_stmt(
        f"""
        select {PROJECTS_COLS}
        from projects 
        where (account_id, project_id) = (%s, %s)
        """,
        (account_id, project_id),
        Project,
    )


def create_project(account_id: UUID, new_project: NewProject) -> Project | None:
    return execute_stmt(
        f"""
        insert into projects 
            ({NEWPROJECT_COLS}, account_id)
        values
            ({NEWPROJECT_PLACEHOLODERS}, %s)
        returning {PROJECTS_COLS}
        """,
        (*tuple(new_project.dict().values()), account_id),
        Project,
    )


def update_project(
    account_id: UUID, project_id: UUID, project: NewProject
) -> Project | None:
    old_proj = get_project(account_id, project_id)

    if old_proj:
        old_proj = NewProject(**old_proj.dict())
        update_data = project.dict(exclude_unset=True)
        new_proj = old_proj.copy(update=update_data)

        return execute_stmt(
            f"""
            update projects set 
                ({NEWPROJECT_COLS}) = ({NEWPROJECT_PLACEHOLODERS})
            where (account_id, project_id) = (%s, %s)
            returning {PROJECTS_COLS}
            """,
            (*tuple(new_proj.dict().values()), account_id, project_id),
            Project,
        )


def delete_project(account_id: UUID, project_id: UUID) -> Project | None:
    return execute_stmt(
        f"""
        delete from projects
        where (account_id, project_id) = (%s, %s)
        returning {PROJECTS_COLS}
        """,
        (account_id, project_id),
        Project,
    )


# NOTES
NOTES_COLS = get_fields(Note)
NEWNOTE_COLS = get_fields(NewNote)
NEWNOTE_PLACEHOLDERS = get_placeholders(NewNote)


def get_all_notes(account_id: UUID, project_id: UUID) -> list[Note]:
    return execute_stmt(
        f"""
        select {NOTES_COLS} 
        from notes
        where (account_id, project_id) =  (%s, %s)
        order by note_id desc
        """,
        (account_id, project_id),
        Note,
        True,
    )


def get_note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:
    return execute_stmt(
        f"""
        select {NOTES_COLS}
        from notes 
        where (account_id, project_id, note_id) = (%s, %s, %s)
        """,
        (account_id, project_id, note_id),
        Note,
    )


def create_note(account_id: UUID, project_id: UUID, new_note: NewNote) -> Note | None:
    return execute_stmt(
        f"""
        insert into notes 
            ({NEWNOTE_COLS}, account_id, project_id)
        values
            ({NEWNOTE_PLACEHOLDERS}, %s, %s)
        returning {NOTES_COLS}
        """,
        (*tuple(new_note.dict().values()), account_id, project_id),
        Note,
    )


def update_note(
    account_id: UUID, project_id: UUID, note_id: int, note: NewNote
) -> Note | None:
    old_note = get_note(account_id, project_id, note_id)

    if old_note:
        old_note = NewNote(**old_note.dict())
        update_data = note.dict(exclude_unset=True)
        new_note = old_note.copy(update=update_data)

        return execute_stmt(
            f"""
            update notes set 
                ({NEWNOTE_COLS}) = ({NEWNOTE_PLACEHOLDERS})
            where (account_id, project_id, note_id) = (%s, %s, %s)
            returning {NOTES_COLS}
            """,
            (*tuple(new_note.dict().values()), account_id, project_id, note_id),
            Note,
        )


def delete_note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:
    return execute_stmt(
        f"""
        delete from notes
        where (account_id, project_id, note_id) = (%s, %s, %s)
        returning {NOTES_COLS}
        """,
        (account_id, project_id, note_id),
        Note,
    )


# TASKS
TASKS_COLS = get_fields(Task)
NEWTASK_COLS = get_fields(NewTask)
NEWTASK_PLACEHOLDERS = get_placeholders(NewTask)


def get_all_tasks(account_id: UUID, project_id: UUID) -> list[Task]:
    return execute_stmt(
        f"""
        select {TASKS_COLS}
        from tasks
        where (account_id, project_id) =  (%s, %s)
        order by task_id desc
        """,
        (account_id, project_id),
        Task,
        True,
    )


def get_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:
    return execute_stmt(
        f"""
        select {TASKS_COLS}
        from tasks 
        where (account_id, project_id, task_id) = (%s, %s, %s)
        """,
        (account_id, project_id, task_id),
        Task,
    )


def create_task(account_id: UUID, project_id: UUID, new_task: NewTask) -> Task | None:
    return execute_stmt(
        f"""
        insert into tasks 
            ({NEWTASK_COLS}, account_id, project_id)
        values
            ({NEWTASK_PLACEHOLDERS}, %s, %s)
        returning {TASKS_COLS}
        """,
        (*tuple(new_task.dict().values()), account_id, project_id),
        Task,
    )


def update_task(
    account_id: UUID, project_id: UUID, task_id: int, task: NewTask
) -> Task | None:
    old_task = get_task(account_id, project_id, task_id)

    if old_task:
        old_task = NewTask(**old_task.dict())
        update_data = task.dict(exclude_unset=True)
        new_task = old_task.copy(update=update_data)

        return execute_stmt(
            f"""
            update tasks set 
                ({NEWTASK_COLS}) = ({NEWTASK_PLACEHOLDERS})
            where (account_id, project_id, task_id) = (%s, %s, %s)
            returning {TASKS_COLS}
            """,
            (*tuple(new_task.dict().values()), account_id, project_id, task_id),
            Task,
        )


def delete_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:
    return execute_stmt(
        f"""
        delete from tasks
        where (account_id, project_id, task_id) = (%s, %s, %s)
        returning {TASKS_COLS}
        """,
        (account_id, project_id, task_id),
        Task,
    )


def execute_stmt(stmt: str, args: tuple, model: PyObject, is_list: bool = False) -> Any:
    def get_col_names():
        if not cur.description:
            raise ValueError("Couldn't fetch column names from ResultSet")

        return [desc[0] for desc in cur.description]

    with pool.connection() as conn:
        with conn.cursor() as cur:
            if is_list:
                rsl = cur.execute(stmt, args).fetchall()  # type: ignore

                col_names = get_col_names()
                return [
                    model(**{k: rs[i] for i, k in enumerate(col_names)}) for rs in rsl
                ]

            else:
                rs = cur.execute(stmt, args).fetchone()  # type: ignore

                if rs:
                    return model(**{k: rs[i] for i, k in enumerate(get_col_names())})
                else:
                    return None
