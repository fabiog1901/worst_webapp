import random
from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import (
    Task,
    TaskOverview,
    TaskOverviewWithProjectName,
)
from worst_crm.tests import utils
from worst_crm.tests.utils import login
import hashlib
import validators
from faker import Faker

fake = Faker()

client = TestClient(app)


ACCOUNT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
OPPORTUNITY_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
PROJECT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
TASK_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def test_get_tasks_non_auth():
    r = client.get(f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}")

    assert r.status_code == 401


def test_create_task(login):
    r = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "TASK-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "project_id": PROJECT_ID,
            "task_id": TASK_ID,
            "text": "Initial text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )

    assert r.status_code == 200
    x = Task(**r.json())
    assert isinstance(x, Task)


def test_load_tasks(login):
    for _ in range(20):
        r = client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "name": "TASK-" + str(random.randint(0000, 9999)),
                "account_id": ACCOUNT_ID,
                "opportunity_id": OPPORTUNITY_ID,
                "project_id": PROJECT_ID,
                "text": "Initial text",
                "status": "NEW",
                "owned_by": "dummyadmin",
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_task(login):
    r = client.put(
        f"/tasks",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "TASK-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "project_id": PROJECT_ID,
            "task_id": TASK_ID,
            "text": "Updated task text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = Task(**r.json())

    # fetch stored account
    r = client.get(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert Task(**r.json()) == x
    assert x.text == "Updated task text"


def test_get_all_tasks_for_project_id(login):
    r = client.get(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[TaskOverview] = [TaskOverview(**x) for x in r.json()]
    assert len(l) >= 20


def test_get_all_tasks_for_opportunity_id(login):
    r = client.get(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[TaskOverviewWithProjectName] = [
        TaskOverviewWithProjectName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_attachment_upload_and_download(login):
    for filename in ["1MB with spaces.txt"]:
        # uploading
        r = client.get(
            f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}/presigned-put-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_upload(r.text, f".testdata/{filename}")

        # Downloading
        r = client.get(
            f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}/presigned-get-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )
        print(r.text)
        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_download(r.text, f".testdata/.{filename}")

        # comparing for equality
        with open(f".testdata/{filename}", "rb") as f:
            digest1 = hashlib.file_digest(f, "sha256")

        with open(f".testdata/.{filename}", "rb") as f:
            digest2 = hashlib.file_digest(f, "sha256")  # type: ignore

        assert digest1.hexdigest() == digest2.hexdigest()

        # deleting attachment
        r = client.delete(
            f"tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        # deleting attachment twice
        r = client.delete(
            f"tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200


def test_delete_task(login):
    r = client.get(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = Task(**r.json())

    r = client.delete(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == Task(**r.json())

    # a get returns null
    r = client.get(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/tasks/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{TASK_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate account for other tests
    test_create_task(login)
