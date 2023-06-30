from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import (
    UserInDB,
    Account,
    Project,
    Task,
)
import worst_crm.db as db
import worst_crm.dependencies as dep
import pytest
import httpx
import random
from uuid import UUID

client = TestClient(app)


def get_random_name(prefix: str = "ACC-") -> str:
    return prefix + str(random.randint(1, 100000)).zfill(6)


# UTILITY FUNCTIONS
# def get_account(account_id: UUID, token) -> Account | None:
#     r = client.get(
#         f"/accounts/{account_id}", headers={"Authorization": f"Bearer {token}"}
#     )

#     assert r.status_code == 200
#     if r.json():
#         return Account(**r.json())
#     return None


# def create_account(token) -> Account:
#     r = client.post("/accounts", headers={"Authorization": f"Bearer {token}"})

#     assert r.status_code == 200
#     return Account(**r.json())


# def update_account(account_id: UUID, token) -> Account:
#     r = client.put(
#         f"/accounts/{account_id}",
#         headers={"Authorization": f"Bearer {token}"},
#         json={
#             "name": "ACC-00001",
#             "text": "some dummy text updated",
#             "status": random.choice(["NEW", "OPPORTUNITY", "POC"]),
#             "owned_by": "dummyadmin",
#             "tags": [random.choice(["t1", "t2", "t3"])],
#             "data": {"k": "v", "kk": "vv"},
#         },
#     )
#     assert r.status_code == 200
#     return Account(**r.json())


# def delete_account(account_id: UUID, token) -> Account | None:
#     r = client.delete(
#         f"/accounts/{account_id}", headers={"Authorization": f"Bearer {token}"}
#     )

#     assert r.status_code == 200
#     if r.json():
#         return Account(**r.json())
#     return None


# PROJECT
def get_project(account_id: UUID, project_id: UUID, token: str) -> Project | None:
    r = client.get(
        f"/projects/{account_id}/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    if r.json():
        return Project(**r.json())
    return None


def create_project(account_id: UUID, token: str) -> Project:
    r = client.post(
        f"/projects/{account_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    return Project(**r.json())


def update_project(account_id: UUID, project_id: UUID, token: str) -> Project:
    r = client.put(
        f"/projects/{account_id}/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "PROJ-00001",
            "text": "dummy project descr UPDATED",
            "status": "ON HOLD",
            "tags": [random.choice(["p1111", "p2222", "p2222"])],
        },
    )
    assert r.status_code == 200
    return Project(**r.json())


def delete_project(account_id: UUID, project_id: UUID, token: str) -> Project | None:
    r = client.delete(
        f"/projects/{account_id}/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    if r.json():
        return Project(**r.json())
    return None


# TASK
def get_task(
    account_id: UUID, project_id: UUID, task_id: int, token: str
) -> Task | None:
    r = client.get(
        f"/tasks/{account_id}/{project_id}/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    if r.json():
        return Task(**r.json())
    return None


def create_task(account_id: UUID, project_id: UUID, token: str) -> Task:
    r = client.post(
        f"/tasks/{account_id}/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    return Task(**r.json())


def update_task(account_id: UUID, project_id: UUID, task_id: int, token: str) -> Task:
    r = client.put(
        f"/tasks/{account_id}/{project_id}/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "TASK-000001",
            "text": "dummy Task descr UPDATED",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": [random.choice(["t1", "t2", "t3"])],
        },
    )
    assert r.status_code == 200
    return Task(**r.json())


def delete_task(
    account_id: UUID, project_id: UUID, task_id: int, token: str
) -> Task | None:
    r = client.delete(
        f"/tasks/{account_id}/{project_id}/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    if r.json():
        return Task(**r.json())
    return None


# # NOTES
# def get_note(
#     account_id: UUID, project_id: UUID, note_id: int, token: str
# ) -> Note | None:
#     r = client.get(
#         f"/notes/{account_id}/{project_id}/{note_id}",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert r.status_code == 200
#     if r.json():
#         return Note(**r.json())
#     return None


# def create_note(account_id: UUID, project_id: UUID, token: str) -> NewNote:
#     r = client.post(
#         f"/notes/{account_id}/{project_id}",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert r.status_code == 200
#     return NewNote(**r.json())


# def update_note(account_id: UUID, project_id: UUID, note_id: int, token: str) -> Note:
#     r = client.put(
#         f"/notes/{account_id}/{project_id}/{note_id}",
#         headers={"Authorization": f"Bearer {token}"},
#         json={
#             "name": "NOTE-000001",
#             "text": "dummy Note descr UPDATED",
#             "tags": [random.choice(["n1", "n2", "n3"])],
#         },
#     )
#     assert r.status_code == 200
#     return Note(**r.json())


# def delete_note(
#     account_id: UUID, project_id: UUID, note_id: int, token: str
# ) -> Note | None:
#     r = client.delete(
#         f"/notes/{account_id}/{project_id}/{note_id}",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert r.status_code == 200
#     if r.json():
#         return Note(**r.json())
#     return None


# PYTEST FIXTURES
@pytest.fixture
def login(username: str = "dummyadmin", password: str = "dummyadmin") -> str:
    r = client.post("/login", data={"username": username, "password": password})

    assert r.status_code == 200

    return r.json()["access_token"]


@pytest.fixture(scope="session")
def setup_test():
    db.load_schema("storage/worst_crm.ddl.sql")

    assert db.create_user(
        UserInDB(
            user_id="dummyadmin",
            is_disabled=False,
            scopes=["rw", "admin"],
            hashed_password=dep.get_password_hash("dummyadmin"),
        )
    )


# GENERAL
def test_healthcheck():
    r = client.get("/healthcheck")
    assert r.status_code == 200
    assert r.json() == {}


def s3_upload(presigned_put_url: str, filename: str):
    try:
        with open(filename, "rb") as f:
            txt = f.read()

        r = httpx.put(presigned_put_url, data=txt)  # type: ignore

        assert r.status_code == 200

    except FileNotFoundError:
        print(f"Couldn't find {filename}.")


def s3_download(presigned_get_url: str, filename: str):
    try:
        with open(filename, "wb") as f:
            with httpx.stream("GET", presigned_get_url) as r:
                assert r.status_code == 200

                for data in r.iter_bytes():
                    f.write(data)

    except FileNotFoundError:
        print(f"Couldn't find {filename}.")
