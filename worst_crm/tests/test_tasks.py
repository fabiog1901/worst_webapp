from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Task
from worst_crm.tests.test_accounts import create_account, delete_account
from worst_crm.tests.test_projects import create_project, delete_project
from uuid import UUID
from worst_crm.tests.utils import login, setup_test, s3_download, s3_upload
import hashlib
import validators

client = TestClient(app)


# CREATE
def test_get_tasks_non_auth():
    r = client.get("/tasks/dfads/asdgfads")

    assert r.status_code == 401


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
        content="""
        {
            "name": "dummy_task1"
        }""",
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


def test_crud_task(login, setup_test):
    token = login

    # CREATE
    acc = create_account(token)
    proj = create_project(acc.account_id, token)
    task = create_task(proj.account_id, proj.project_id, token)

    # READ
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}/{task.task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert task == Task(**r.json())

    # READ ALL
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    l: list[Task] = [Task(**x) for x in r.json()]

    assert len(l) > 0

    # UPDATE
    r = client.put(
        f"/tasks/{task.account_id}/{proj.project_id}/{task.task_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_proj1",
            "description": "dummy Task descr UPDATED",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["p1111", "p2222", "p2222"]
        }""",
    )

    assert r.status_code == 200

    upd_task = Task(**r.json())

    assert upd_task == get_task(task.account_id, task.project_id, task.task_id, token)

    # DELETE
    del_task = delete_task(task.account_id, task.project_id, task.task_id, token)

    assert del_task == upd_task

    # a read returns null
    assert get_task(task.account_id, task.project_id, task.task_id, token) is None

    # a second delete return null
    assert delete_task(task.account_id, task.project_id, task.task_id, token) is None

    # finally, delete account
    assert delete_project(task.account_id, task.project_id, token)
    assert delete_account(task.account_id, token)


def test_attachment_upload_and_download(login, setup_test):
    token = login

    acc = create_account(token)
    proj = create_project(acc.account_id, token)
    task = create_task(proj.account_id, proj.project_id, token)

    filename = "1MB with spaces.txt"

    # uploading
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}/{task.task_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    assert validators.url(r.text)  # type: ignore

    s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}/{task.task_id}/presigned-get-url/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    assert validators.url(r.text)  # type: ignore

    s3_download(r.text, f".testdata/.{filename}")

    # comparing for equality
    with open(f".testdata/{filename}", "rb") as f:
        digest1 = hashlib.file_digest(f, "sha256")

    with open(f".testdata/.{filename}", "rb") as f:
        digest2 = hashlib.file_digest(f, "sha256")

    assert digest1.hexdigest() == digest2.hexdigest()

    # deleting
    r = client.delete(
        f"tasks/{task.account_id}/{task.project_id}/{task.task_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200
