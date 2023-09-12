from psycopg_pool import ConnectionPool
from psycopg.types.array import ListDumper
from psycopg.types.json import Jsonb, JsonbDumper
from typing import Any
from uuid import UUID
import os

from worst_crm.models import (
    Account,
    AccountFilters,
    AccountInDB,
    AccountOverview,
    Contact,
    ContactInDB,
    ContactWithAccountName,
    Model,
    ModelInDB,
    Status,
)
from worst_crm.models import User, UserInDB, UpdatedUserInDB


DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise EnvironmentError("DB_URL env variable not found!")


# the pool starts connecting immediately.
pool = ConnectionPool(DB_URL, kwargs={"autocommit": True})


def log_event(obj: str, username: str, action: str, details: str):
    execute_stmt(
        """UPSERT INTO 
            events (object, ts, username, action, details) 
        VALUES 
            (%s, now(), %s, %s, %s)
        """,
        (obj, username, action, details),
        returning_rs=False,
    )


def get_watch() -> int:
    return execute_stmt(
        "SELECT ts::INT8 FROM WATCH AS OF SYSTEM TIME follower_read_timestamp() LIMIT 1",
    )[0]


def update_watch() -> None:
    # just refresh the entry to update column 'ts'
    execute_stmt("UPDATE watch SET id=1 WHERE true", returning_rs=False)


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


def create_account_status(status: str) -> Status | None:
    return execute_stmt(
        "INSERT INTO account_status(name) VALUES (%s) RETURNING name",
        (status,),
        model=Status,
    )


def delete_account_status(status: str) -> Status | None:
    return execute_stmt(
        "DELETE FROM account_status WHERE name = %s RETURNING name",
        (status,),
        model=Status,
    )


def get_all_project_status() -> list[Status]:
    return execute_stmt("SELECT name FROM project_status", model=Status, is_list=True)


def create_project_status(status: str) -> Status | None:
    return execute_stmt(
        "INSERT INTO project_status(name) VALUES (%s) RETURNING name",
        (status,),
        model=Status,
    )


def delete_project_status(status: str) -> Status | None:
    return execute_stmt(
        "DELETE FROM project_status WHERE name = %s RETURNING name",
        (status,),
        model=Status,
    )


def get_all_task_status() -> list[Status]:
    return execute_stmt("SELECT name FROM task_status", model=Status, is_list=True)


def create_task_status(status: str) -> Status | None:
    return execute_stmt(
        "INSERT INTO task_status(name) VALUES (%s) RETURNING name",
        (status,),
        model=Status,
    )


def delete_task_status(status: str) -> Status | None:
    return execute_stmt(
        "DELETE FROM task_status WHERE name = %s RETURNING name",
        (status,),
        model=Status,
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
    print("===================================================")
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
        tuple(user.model_dump().values()),
        User,
    )


def increase_failed_attempt_count(user_id: str) -> UserInDB | None:
    return execute_stmt(
        f"""update users set
            failed_attempts = failed_attempts + 1 
        where user_id = %s
        returning {USERINDB_COLS}""",
        (user_id,),
        UserInDB,
    )


def reset_failed_attempt_count(user_id: str):
    execute_stmt(
        "UPDATE users SET failed_attempts = 0 WHERE user_id = %s",
        (user_id,),
        returning_rs=False,
    )


def update_user(user_id: str, user: UpdatedUserInDB) -> User | None:
    old_uid = get_user_with_hash(user_id)

    if old_uid:
        update_data = user.model_dump(exclude_unset=True)

        new_uid = old_uid.model_copy(update=update_data)

        return execute_stmt(
            f"""
            update users set 
            ({USERINDB_COLS}) = 
                ({USERINDB_PLACEHOLDERS})
            where user_id  = %s
            returning {USERS_COLS}
            """,
            (*tuple(new_uid.model_dump().values()), user_id),
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


# ADMIN/MODELS


# ACCOUNTS
MODEL_IN_DB_COLS = get_fields(ModelInDB)
MODEL_IN_DB_PLACEHOLDERS = get_placeholders(ModelInDB)
MODEL_COLS = get_fields(Model)


def get_type(json_data_type: str) -> str:
    """
    Maps a python type to a column data type
    """
    return {
        "string": "STRING",
        "integer": "INT8",
        "datetime": "TIMESTAMPTZ",
        "date": "DATE",
    }[json_data_type]


def get_model(name: str) -> Model:
    return execute_stmt(
        f"""
        SELECT {MODEL_COLS} 
        FROM models
        WHERE name = %s""",
        (name,),
        Model,
    )


def update_model(model_in_db: ModelInDB) -> Model | None:
    def get_table_name(name: str) -> str:
        return {
            "account": "accounts",
            "opportunity": "opportunities",
            "artifact": "artifacts",
            "project": "projects",
            "task": "tasks",
            "account_note": "account_notes",
            "opportunity_note": "opportunity_notes",
            "project_note": "project_notes",
            "contact": "contacts",
        }[name]

    old_model = get_model(model_in_db.name)

    additions: dict[str, str] = {}
    removals: list[str] = []

    for k in old_model.skema.properties.keys():
        if k not in model_in_db.skema.properties.keys():
            removals.append(k)

    for k, v in model_in_db.skema.properties.items():
        if k not in old_model.skema.properties.keys():
            additions[k] = v["type"]

    # drop column stmts have to be executed in their own transaction
    for x in removals:
        execute_stmt(
            f"""SET sql_safe_updates = false;
            ALTER TABLE {get_table_name(model_in_db.name)} DROP COLUMN {x};
            SET sql_safe_updates = true;
            """,
            returning_rs=False,
        )

    for x, y in additions.items():
        execute_stmt(
            f"ALTER TABLE {get_table_name(model_in_db.name)} ADD COLUMN {x} {get_type(y)};",
            returning_rs=False,
        )

    new_model = execute_stmt(
        f"""
        UPDATE models SET
            ({MODEL_IN_DB_COLS}) = ({MODEL_IN_DB_PLACEHOLDERS})
        WHERE name = %s 
        RETURNING {MODEL_COLS}""",
        (*tuple(model_in_db.model_dump().values()), model_in_db.name),
        Model,
    )

    # trigger async App restart
    update_watch()

    return new_model


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
        tuple(account_in_db.model_dump().values()),
        Account,
    )


def update_account(account_in_db: AccountInDB) -> Account | None:
    if account_in_db.account_id:
        old_acc = get_account(account_in_db.account_id)
    else:
        return None

    if old_acc:
        old_acc = AccountInDB(**old_acc.model_dump())
        update_data = account_in_db.model_dump(exclude_unset=True)
        new_acc = old_acc.model_copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE accounts SET 
                ({ACCOUNT_IN_DB_COLS}) = ({ACCOUNT_IN_DB_PLACEHOLDERS})
            WHERE account_id = %s
            RETURNING {ACCOUNTS_COLS}
            """,
            (*tuple(new_acc.model_dump().values()), account_in_db.account_id),
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
    fully_qualified = ", ".join([f"contacts.{x}" for x in Contact.model_fields.keys()])

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
        tuple(contact_in_db.model_dump().values()),
        Contact,
    )


def update_contact(contact_in_db: ContactInDB) -> Contact | None:
    if contact_in_db.contact_id:
        old_contact = get_contact(contact_in_db.account_id, contact_in_db.contact_id)
    else:
        return None

    if old_contact:
        old_contact = ContactInDB(**old_contact.model_dump())
        update_data = contact_in_db.model_dump(exclude_unset=True)
        new_contact = old_contact.model_copy(update=update_data)

        return execute_stmt(
            f"""
            UPDATE contacts SET 
                ({CONTACT_IN_DB_COLS}) = ({CONTACT_IN_DB_PLACEHOLDERS})
            WHERE (account_id, contact_id) = (%s, %s)
            RETURNING {CONTACT_COLS}
            """,
            (
                *tuple(new_contact.model_dump().values()),
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


class DictJsonbDumper(JsonbDumper):
    def dump(self, obj):
        return super().dump(Jsonb(obj))


# ==============================================================================================
def execute_stmt(
    stmt: str,
    args: tuple = (),
    model: Any = None,
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

                    if model:
                        return [
                            model(**{k: rs[i] for i, k in enumerate(col_names)})
                            for rs in rsl
                        ]
                    else:
                        return rsl
                else:
                    rs = cur.fetchone()
                    if rs:
                        if model:
                            return model(**{k: rs[i] for i, k in enumerate(col_names)})
                        else:
                            return rs
                    else:
                        return None
            except Exception as e:
                # TODO correctly handle error such as PK violations
                print(e)
                return None
