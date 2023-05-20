import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Task, NewTask, TaskOverviewWithProjectName, TaskOverview
from backend.tests import utils
from backend.tests.utils import login, setup_test
import hashlib
import validators

client = TestClient(app)

new_task: NewTask
task: Task


# CREATE
def test_get_tasks_non_auth():
    r = client.get("/tasks/123456")

    assert r.status_code == 401


def test_create_task(login, setup_test):
    acc = utils.create_account(login)
    proj = utils.create_project(acc.account_id, login)

    global new_task

    new_task = utils.create_task(proj.account_id, proj.project_id, login)

    assert isinstance(new_task, NewTask)


def test_update_task(login, setup_test):
    global task
    global new_task

    upd_task = utils.update_task(
        new_task.account_id, new_task.project_id, new_task.task_id, login
    )

    assert isinstance(upd_task, Task)
    assert upd_task == utils.get_task(
        new_task.account_id, new_task.project_id, new_task.task_id, login
    )

    task = upd_task


def test_read_all_tasks_for_account_id(login, setup_test):
    for _ in range(20):
        time.sleep(1)
        utils.create_task(task.account_id, task.project_id, login)

    r = client.get(
        f"/tasks/{task.account_id}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[TaskOverviewWithProjectName] = [
        TaskOverviewWithProjectName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_read_all_tasks_for_account_id_with_filters(login, setup_test):
    r = client.get(
        f"/tasks/{task.account_id}",
        headers={"Authorization": f"Bearer {login}"},
        params={"status": ["NEW"]},
    )
    assert r.status_code == 200
    l: list[TaskOverviewWithProjectName] = [
        TaskOverviewWithProjectName(**x) for x in r.json()
    ]
    assert len(l) == 1


def test_read_all_tasks_for_project_id(login, setup_test):
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[TaskOverview] = [TaskOverview(**x) for x in r.json()]
    assert len(l) >= 1


def test_attachment_upload_and_download(login, setup_test):
    global task

    filename = "1MB with spaces.txt"

    # uploading
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}/{task.task_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    assert validators.url(r.text)  # type: ignore
    utils.s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/tasks/{task.account_id}/{task.project_id}/{task.task_id}/presigned-get-url/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    assert validators.url(r.text)  # type: ignore
    utils.s3_download(r.text, f".testdata/.{filename}")

    # comparing for equality
    with open(f".testdata/{filename}", "rb") as f:
        digest1 = hashlib.file_digest(f, "sha256")

    with open(f".testdata/.{filename}", "rb") as f:
        digest2 = hashlib.file_digest(f, "sha256")

    assert digest1.hexdigest() == digest2.hexdigest()

    # deleting
    r = client.delete(
        f"tasks/{task.account_id}/{task.project_id}/{task.task_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    task_with_attachments = utils.get_task(
        task.account_id, task.project_id, task.task_id, login
    )

    if task_with_attachments:
        task = task_with_attachments


def test_delete_task(login, setup_test):
    del_task = utils.delete_task(task.account_id, task.project_id, task.task_id, login)

    assert del_task == task

    # a read returns null
    assert utils.get_task(task.account_id, task.project_id, task.task_id, login) is None

    # a second delete return null
    assert (
        utils.delete_task(task.account_id, task.project_id, task.task_id, login) is None
    )

    # finally, delete account
    assert utils.delete_project(task.account_id, task.project_id, login)
    assert utils.delete_account(task.account_id, login)
