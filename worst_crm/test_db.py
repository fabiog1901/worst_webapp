import json
from . import db
from . import dependencies as dep
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
from worst_crm.models import NewUser, User, UserInDB, UpdatedUser, UpdatedUserInDB


def test_user_create():
    d = """{
            "user_id": "testuser1",
            "full_name": "testuser1",
            "email": "testuser1@test.com",
            "is_disabled": false,
            "password": "testuser1",
            "scopes": [
                "admin",
                "rw"
            ]
        }"""

    nu = NewUser(**json.loads(d))

    uid = UserInDB(**nu.dict(), hashed_password=dep.get_password_hash(nu.password))

    u = db.create_user(uid)

    assert u == User(**nu.dict())

    user = db.get_user("testuser1")

    assert user == User(**nu.dict())


def test_user_update():
    user = db.get_user("testuser1")

    u = UpdatedUserInDB(
        hashed_password=dep.get_password_hash("testuser123"),
        full_name="Test User 1 Updated",
    )

    user = db.update_user("testuser1", u)

    assert user
    assert user.full_name == "Test User 1 Updated"

    uid = db.get_user_with_hash("testuser1")

    assert uid
    assert dep.verify_password("testuser123", uid.hashed_password)
    assert uid.full_name == "Test User 1 Updated"


def test_user_get_all():
    users = db.get_all_users()

    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], User)


def test_user_delete():
    user = db.get_user("testuser1")

    assert user

    deleted_user = db.delete_user(user.user_id)

    assert user == deleted_user

    user = db.get_user("testuser1")

    assert user is None


# ACCOUNTS


def test_account():
    new_acc = NewAccount(
        account_name="testaccount1", description="testdescr", tags=["test1", "test2"]
    )

    acc = db.create_account(new_acc)

    assert acc

    check = db.get_account(acc.account_id)

    assert check

    check = NewAccount(**check.dict())

    assert new_acc == check

    # list all
    acc_list = db.get_all_accounts()

    assert acc_list
    assert isinstance(acc_list, list)
    assert len(acc_list) > 0

    # update
    up_acc = NewAccount(account_name="updated acc name", description="updated desc")

    updated_acc = db.update_account(acc.account_id, up_acc)

    assert updated_acc
    assert updated_acc == db.get_account(acc.account_id)

    assert updated_acc.account_name == up_acc.account_name

    # delete
    del_acc = db.delete_account(acc.account_id)

    assert del_acc

    assert db.get_account(acc.account_id) is None


# # PROJECTS

# def get_all_projects():


# def get_project():


# def create_project():


# def update_project():


# def delete_project():


# # NOTES

# def get_all_notes():


# def get_note():


# def create_note():


# def update_note():


# def delete_note():


# # TASKS

# def get_all_tasks():


# def get_task():


# def create_task():


# def update_task():


# def delete_task():
