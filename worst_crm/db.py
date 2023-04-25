from typing import Any
from psycopg_pool import ConnectionPool
from psycopg import Cursor

from uuid import UUID
from pydantic import BaseModel

from worst_crm.models import NewAccount, Account, NewProject, Project, NewNote, Note, NewTask, Task
from worst_crm.models import User, UserInDB


dburl = 'postgres://root@localhost:26257/worst_crm?sslmode=disable'

# the pool starts connecting immediately.
pool = ConnectionPool(dburl, kwargs={'autocommit': True})

# ADMIN
def get_user(username: str) -> UserInDB | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select username, full_name, email, hashed_password, is_disabled, scopes 
                from users 
                where username = %s
                """,
                (username, ))

            rs = cur.fetchone()

            if rs is not None:

                return UserInDB(
                    username=rs[0],
                    full_name=rs[1],
                    email=rs[2],
                    hashed_password=rs[3],
                    is_disabled=rs[4],
                    scopes=rs[5]
                )

    return None


def create_user(user: UserInDB) -> bool:
    if user.username not in fake_users_db:
        fake_users_db[user.username] = user
        return True
    return False


def update_user(user: UserInDB) -> bool:
    if user.username in fake_users_db:
        fake_users_db[user.username] = user
        return True
    return False


def delete_user(username: str) -> bool:
    if username in fake_users_db:
        del fake_users_db[username]
        return True
    return False


# ACCOUNTS
ACCOUNTS_COLS = "account_id, account_name, created_at, updated_at, description, tags"
def get_all_accounts() -> list[Account]:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select {ACCOUNTS_COLS}
                from accounts
                order by account_name
                """,
                ())

            return ret_obj(Account, cur, True) # type: ignore
        
            rs = cur.fetchall()
            
            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
            
                return [Account(**{k: r[i] for i, k in enumerate(col_names) }) for r in rs]

    return []


def get_account(account_id: UUID) -> Account | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select {ACCOUNTS_COLS} 
                from accounts 
                where account_id = %s
                """,
                (account_id, ))

            return ret_obj(Account, cur) 
        
            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Account(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def create_account(new_account: NewAccount) -> Account | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into accounts (account_name, description, tags)
                values
                (%s, %s, %s)
                returning account_id, account_name, description, tags
                """,
                (new_account.account_name, new_account.description, new_account.tags)
            )

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Account(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def update_account(account_id: UUID, account: NewAccount) -> Account | None:

    old_acc = get_account(account_id)

    if old_acc:

        update_data = account.dict(exclude_unset=True)

        new_acc = old_acc.copy(update=update_data)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update accounts set 
                    account_name = %s,
                    description  = %s,
                    tags = %s
                    where account_id  = %s
                    returning account_id, account_name, description, tags
                    """,
                    (new_acc.account_name, new_acc.description, new_acc.tags, account_id))

                rs = cur.fetchone()

                if cur.description and rs:
                    col_names = [desc[0] for desc in cur.description]
                    return Account(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def delete_account(account_id: UUID) -> Account | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                delete from accounts
                where account_id = %s
                returning account_id, account_name, description, tags
                """,
                (account_id, ))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Account(**{k: rs[i] for i, k in enumerate(col_names)})

    return None

# PROJECTS
def get_all_projects(account_id: UUID) -> list[Project]:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select account_id, description, project_id, project_name, status, tags
                from projects
                where account_id = %s
                order by project_name
                """,
                (account_id, ))

            rs = cur.fetchall()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return [Project(**{k: r[i] for i, k in enumerate(col_names)}) for r in rs]

    return []


def get_project(account_id: UUID, project_id: UUID) -> Project | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select account_id, description, project_id, project_name, status, tags
                from projects 
                where (account_id, project_id) = (%s, %s)
                """,
                (account_id, project_id))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Project(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def create_project(account_id: UUID, new_project: NewProject) -> Project | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into projects (account_id, project_name, description, status, tags)
                values
                (%s, %s, %s, %s, %s)
                returning account_id, description, project_id, project_name, status, tags
                """,
                (account_id, new_project.project_name,
                 new_project.description, new_project.status, new_project.tags)
            )

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Project(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def update_project(account_id: UUID, project_id: UUID, project: NewProject) -> Project | None:

    old_proj = get_project(account_id, project_id)

    if old_proj:

        update_data = project.dict(exclude_unset=True)

        new_proj = old_proj.copy(update=update_data)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update projects set 
                    project_name = %s,
                    description  = %s,
                    status = %s,
                    tags = %s
                    where (account_id, project_id) = (%s, %s)
                    returning account_id, description, project_id, project_name, status, tags
                    """,
                    (new_proj.project_name, new_proj.description, new_proj.status, new_proj.tags, account_id,
                     project_id))

                rs = cur.fetchone()

                if cur.description and rs:
                    col_names = [desc[0] for desc in cur.description]
                    return Project(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def delete_project(account_id: UUID, project_id: UUID) -> Project | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                delete from projects
                where (account_id, project_id) = (%s, %s)
                returning account_id, description, project_id, project_name, status, tags
                """,
                (account_id, project_id))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Project(**{k: rs[i] for i, k in enumerate(col_names)})

    return None

# NOTES
def get_all_notes(account_id: UUID, project_id: UUID) -> list[Note]:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select account_id, content, note_id, note_name, project_id, tags, updated_at
                from notes
                where (account_id, project_id) =  (%s, %s)
                order by note_id desc
                """,
                (account_id, project_id))

            rs = cur.fetchall()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return [Note(**{k: r[i] for i, k in enumerate(col_names)}) for r in rs]

    return []


def get_note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select account_id, content, note_id, note_name, project_id, tags, updated_at
                from notes 
                where (account_id, project_id, note_id) = (%s, %s, %s)
                """,
                (account_id, project_id, note_id))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Note(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def create_note(account_id: UUID, project_id: UUID, new_note: NewNote) -> Note | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into notes (account_id, project_id, note_name, content, tags)
                values
                (%s, %s, %s, %s, %s)
                returning account_id, content, note_id, note_name, project_id, tags, updated_at
                """,
                (account_id, project_id, new_note.note_name,
                 new_note.content, new_note.tags)
            )

            rs = cur.fetchone()

            print(rs)
            
            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Note(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def update_note(account_id: UUID, project_id: UUID, note_id: int, note: NewNote) -> Note | None:

    old_note = get_note(account_id, project_id, note_id)

    if old_note:

        update_data = note.dict(exclude_unset=True)

        new_note = old_note.copy(update=update_data)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    update notes set 
                    note_name = %s,
                    content  = %s,
                    tags = %s
                    where (account_id, project_id, note_id) = (%s, %s, %s)
                    returning account_id, content, note_id, note_name, project_id, tags, updated_at
                    """,
                    (new_note.note_name, new_note.content, new_note.tags, account_id, project_id,
                     note_id))

                rs = cur.fetchone()

                if cur.description and rs:
                    col_names = [desc[0] for desc in cur.description]
                    return Note(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def delete_note(account_id: UUID, project_id: UUID, note_id: int) -> Note | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                delete from notes
                where (account_id, project_id, note_id) = (%s, %s, %s)
                returning account_id, content, note_id, note_name, project_id, tags, updated_at
                """,
                (account_id, project_id, note_id))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Note(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


# TASKS
TASKS_COLS = "account_id, content, project_id, tags, task_id, task_name, task_status, updated_at"
def get_all_tasks(account_id: UUID, project_id: UUID) -> list[Task]:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select {TASKS_COLS}
                from tasks
                where (account_id, project_id) =  (%s, %s)
                order by task_id desc
                """,
                (account_id, project_id))

            rs = cur.fetchall()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return [Task(**{k: r[i] for i, k in enumerate(col_names)}) for r in rs]

    return []


def get_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select {TASKS_COLS}
                from tasks 
                where (account_id, project_id, task_id) = (%s, %s, %s)
                """,
                (account_id, project_id, task_id))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Task(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def create_task(account_id: UUID, project_id: UUID, new_task: NewTask) -> Task | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                insert into tasks (account_id, project_id, task_name, content, task_status, tags)
                values
                (%s, %s, %s, %s, %s, %s)
                returning {TASKS_COLS}
                """,
                (account_id, project_id, new_task.task_name, new_task.content,
                 new_task.task_status, new_task.tags)
            )

            rs = cur.fetchone()

            print(rs)
            
            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Task(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def update_task(account_id: UUID, project_id: UUID, task_id: int, task: NewTask) -> Task | None:

    old_task = get_task(account_id, project_id, task_id)

    if old_task:

        update_data = task.dict(exclude_unset=True)

        new_task = old_task.copy(update=update_data)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    update tasks set 
                    task_name = %s,
                    task_status = %s,
                    content  = %s,
                    tags = %s
                    where (account_id, project_id, task_id) = (%s, %s, %s)
                    returning {TASKS_COLS}
                    """,
                    (new_task.task_name, new_task.task_status, new_task.content, new_task.tags, account_id, project_id,
                     task_id))

                rs = cur.fetchone()

                if cur.description and rs:
                    col_names = [desc[0] for desc in cur.description]
                    return Task(**{k: rs[i] for i, k in enumerate(col_names)})

    return None


def delete_task(account_id: UUID, project_id: UUID, task_id: int) -> Task | None:

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                delete from tasks
                where (account_id, project_id, task_id) = (%s, %s, %s)
                returning {TASKS_COLS}
                """,
                (account_id, project_id, task_id))

            rs = cur.fetchone()

            if cur.description and rs:
                col_names = [desc[0] for desc in cur.description]
                return Task(**{k: rs[i] for i, k in enumerate(col_names)})

    return None

def ret_obj(obj, cur: Cursor, is_list: bool = False) -> Any:

    if is_list:
        rs = cur.fetchall()
        
        if cur.description and rs:
            col_names = [desc[0] for desc in cur.description]
            
            return [obj(**{k: r[i] for i, k in enumerate(col_names)}) for r in rs]

        return []
    
    rs = cur.fetchone()

    if cur.description and rs:
        col_names = [desc[0] for desc in cur.description]
        
        return obj(**{k: rs[i] for i, k in enumerate(col_names)})

    return None 