import random
from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import (
    Project,
    ProjectOverview,
    ProjectOverviewWithAccountName,
    ProjectOverviewWithOpportunityName,
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


def test_get_projects_non_auth():
    r = client.get("/projects")

    assert r.status_code == 401


def test_create_project(login):
    r = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "PROJ-1",
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
    x = Project(**r.json())
    assert isinstance(x, Project)


def test_load_projects(login):
    for _ in range(20):
        r = client.post(
            "/projects",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "name": "PROJ-" + str(random.randint(10000, 99999)),
                "account_id": ACCOUNT_ID,
                "opportunity_id": OPPORTUNITY_ID,
                "text": fake.text(),
                "status": "NEW",
                "due_date": fake.date(),
                "owned_by": "dummyadmin",
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_project(login):
    r = client.put(
        f"/projects",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "OPP-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "project_id": PROJECT_ID,
            "text": "Updated proj text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = Project(**r.json())

    # fetch stored account
    r = client.get(
        f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert Project(**r.json()) == x
    assert x.text == "Updated proj text"


def test_get_all_projects(login):
    r = client.get(
        "/projects/",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[ProjectOverviewWithAccountName] = [
        ProjectOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_get_all_projects_with_filters(login):
    r = client.get(
        "/projects/",
        headers={"Authorization": f"Bearer {login}"},
        params={"name": ["PROJ-1"]},
    )
    assert r.status_code == 200
    l: list[ProjectOverviewWithAccountName] = [
        ProjectOverviewWithAccountName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_get_all_projects_for_account_id(login):
    r = client.get(
        f"/projects/{ACCOUNT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[ProjectOverviewWithOpportunityName] = [
        ProjectOverviewWithOpportunityName(**x) for x in r.json()
    ]
    assert len(l) >= 20


def test_get_all_projects_for_opportunity_id(login):
    r = client.get(
        f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200
    l: list[ProjectOverview] = [ProjectOverview(**x) for x in r.json()]
    assert len(l) >= 20


def test_attachment_upload_and_download(login):
    for filename in ["1MB with spaces.txt", "ss.png"]:
        # uploading
        r = client.get(
            f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/presigned-put-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_upload(r.text, f".testdata/{filename}")

        # Downloading
        r = client.get(
            f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/presigned-get-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

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
            f"projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        # deleting attachment twice
        r = client.delete(
            f"projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200


def test_delete_project(login):
    r = client.get(
        f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = Project(**r.json())

    r = client.delete(
        f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == Project(**r.json())

    # a get returns null
    r = client.get(
        f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/projects/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate account for other tests
    test_create_project(login)
