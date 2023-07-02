from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import ProjectNote, ProjectNoteOverview
from worst_crm.tests import utils
from worst_crm.tests.utils import login
import hashlib
import validators
from faker import Faker
import random

fake = Faker()

client = TestClient(app)


ACCOUNT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
OPPORTUNITY_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
PROJECT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
NOTE_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def test_get_project_notes_non_auth():
    r = client.get(f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}")

    assert r.status_code == 401


def test_create_project_note(login):
    r = client.post(
        "/notes/project",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "NOTE-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "project_id": OPPORTUNITY_ID,
            "note_id": NOTE_ID,
            "text": "Initial text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )

    assert r.status_code == 200
    x = ProjectNote(**r.json())
    assert isinstance(x, ProjectNote)


def test_load_project_notes(login):
    for _ in range(20):
        r = client.post(
            "/notes/project",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "name": "NOTE-" + str(random.randint(0000, 9999)),
                "account_id": ACCOUNT_ID,
                "opportunity_id": OPPORTUNITY_ID,
                "project_id": OPPORTUNITY_ID,
                "text": fake.text(),
                "status": "NEW",
                "owned_by": "dummyadmin",
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_project_note(login):
    r = client.put(
        f"/notes/project",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "NOTE-1",
            "account_id": ACCOUNT_ID,
            "opportunity_id": OPPORTUNITY_ID,
            "project_id": OPPORTUNITY_ID,
            "note_id": NOTE_ID,
            "text": "Updated project_note text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = ProjectNote(**r.json())

    # fetch stored project
    r = client.get(
        f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert ProjectNote(**r.json()) == x
    assert x.text == "Updated project_note text"


def test_get_all_project_notes(login):
    r = client.get(
        f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[ProjectNoteOverview] = [ProjectNoteOverview(**x) for x in r.json()]
    assert len(l) >= 20


def test_attachment_upload_and_download(login):
    for filename in ["1MB with spaces.txt"]:
        # uploading
        r = client.get(
            f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}/presigned-put-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_upload(r.text, f".testdata/{filename}")

        # Downloading
        r = client.get(
            f"notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}/presigned-get-url/{filename}",
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
            f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        # deleting attachment twice
        r = client.delete(
            f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200


def test_delete_project_note(login):
    r = client.get(
        f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = ProjectNote(**r.json())

    r = client.delete(
        f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == ProjectNote(**r.json())

    # a get returns null
    r = client.get(
        f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/notes/project/{ACCOUNT_ID}/{OPPORTUNITY_ID}/{PROJECT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate project for other tests
    test_create_project_note(login)
