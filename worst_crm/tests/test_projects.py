from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Project
from worst_crm.tests.test_accounts import create_account, delete_account
from uuid import UUID
from worst_crm.tests.utils import login, setup_test

client = TestClient(app)


# CREATE
def test_get_projects_non_auth():
    r = client.get("/projects/12345")

    assert r.status_code == 401


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
        f"/projects/{account_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_prpj1"
        }""",
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


def test_crud_project(login, setup_test):
    token = login

    # CREATE
    acc = create_account(token)

    proj = create_project(acc.account_id, token)

    # READ
    r = client.get(
        f"/projects/{proj.account_id}/{proj.project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert proj == Project(**r.json())

    # READ ALL
    r = client.get(
        f"/projects/{proj.account_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    l: list[Project] = [Project(**x) for x in r.json()]

    assert len(l) > 0

    # UPDATE
    r = client.put(
        f"/projects/{proj.account_id}/{proj.project_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_proj1",
            "text": "dummy project descr UPDATED",
            "status": "NEW",
            "attachments" : ["gino", "pino", "lino"],
            "owned_by": "dummyadmin",
            "tags": ["p1111", "p2222", "p2222"]
        }""",
    )

    assert r.status_code == 200

    upd_proj = Project(**r.json())

    assert upd_proj == get_project(proj.account_id, proj.project_id, token)

    # DELETE
    del_proj = delete_project(proj.account_id, proj.project_id, token)

    assert del_proj == upd_proj

    # a read returns null
    assert get_project(proj.account_id, proj.project_id, token) is None

    # a second delete return null
    assert delete_project(proj.account_id, proj.project_id, token) is None

    # finally, delete account
    assert delete_account(proj.account_id, token)
