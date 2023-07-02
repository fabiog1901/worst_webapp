from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import AccountNote, AccountNoteOverview
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


def test_get_account_notes_non_auth():
    r = client.get(f"/notes/account/{ACCOUNT_ID}")

    assert r.status_code == 401


def test_create_account_note(login):
    r = client.post(
        "/notes/account",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "NOTE-1",
            "account_id": ACCOUNT_ID,
            "note_id": NOTE_ID,
            "text": "Initial text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )

    assert r.status_code == 200
    x = AccountNote(**r.json())
    assert isinstance(x, AccountNote)


def test_load_account_notes(login):
    for _ in range(20):
        r = client.post(
            "/notes/account",
            headers={"Authorization": f"Bearer {login}"},
            json={
                "name": "NOTE-" + str(random.randint(0000, 9999)),
                "account_id": ACCOUNT_ID,
                "text": fake.text(),
                "status": "NEW",
                "owned_by": "dummyadmin",
                "tags": ["t1", "t2", "t1"],
            },
        )

        assert r.status_code == 200


def test_update_account_note(login):
    r = client.put(
        f"/notes/account",
        headers={"Authorization": f"Bearer {login}"},
        json={
            "name": "NOTE-1",
            "account_id": ACCOUNT_ID,
            "note_id": NOTE_ID,
            "text": "Updated account_note text",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t1"],
        },
    )
    assert r.status_code == 200
    x = AccountNote(**r.json())

    # fetch stored account
    r = client.get(
        f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert AccountNote(**r.json()) == x
    assert x.text == "Updated account_note text"


def test_get_all_account_notes(login):
    r = client.get(
        f"/notes/account/{ACCOUNT_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.status_code == 200

    l: list[AccountNoteOverview] = [AccountNoteOverview(**x) for x in r.json()]
    assert len(l) >= 20


def test_attachment_upload_and_download(login):
    for filename in ["1MB with spaces.txt"]:
        # uploading
        r = client.get(
            f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}/presigned-put-url/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        assert validators.url(r.text)  # type: ignore

        utils.s3_upload(r.text, f".testdata/{filename}")

        # Downloading
        r = client.get(
            f"notes/account/{ACCOUNT_ID}/{NOTE_ID}/presigned-get-url/{filename}",
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
            f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200

        # deleting attachment twice
        r = client.delete(
            f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}/attachments/{filename}",
            headers={"Authorization": f"Bearer {login}"},
        )

        assert r.status_code == 200


def test_delete_account_note(login):
    r = client.get(
        f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    acc = AccountNote(**r.json())

    r = client.delete(
        f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )

    assert r.status_code == 200
    assert acc == AccountNote(**r.json())

    # a get returns null
    r = client.get(
        f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/notes/account/{ACCOUNT_ID}/{NOTE_ID}",
        headers={"Authorization": f"Bearer {login}"},
    )
    assert r.json() is None

    # recreate account for other tests
    test_create_account_note(login)
