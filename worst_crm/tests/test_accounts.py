from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Account
from worst_crm.tests.utils import login, setup_test, s3_download, s3_upload
from uuid import UUID
import validators
import hashlib

client = TestClient(app)


# CREATE
def test_get_accounts_non_auth():
    r = client.get("/accounts")

    assert r.status_code == 401


def create_account(token: str) -> Account:
    r = client.post(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1"
        }""",
    )

    assert r.status_code == 200

    return Account(**r.json())


def delete_account(
    account_id: UUID,
    token: str,
):
    r = client.delete(
        f"/accounts/{account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200

    return Account(**r.json())


def test_crud_account(login, setup_test):
    token = login

    # CREATE
    acc = create_account(token)

    # READ
    r = client.get(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert acc == Account(**r.json())

    # READ ALL
    r = client.get(
        "/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )

    l: list[Account] = [Account(**x) for x in r.json()]

    assert len(l) > 0

    # UPDATE
    r = client.put(
        f"/accounts/{acc.account_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_acc1",
            "text": "some dummy text updated",
            "status": "NEW",
            "owned_by": "dummyadmin",
            "tags": ["t1", "t2", "t5555"],
            "data": {"k": "v", "kk": "vv"}
        }""",
    )

    upd_acc = Account(**r.json())

    r = client.get(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert upd_acc == Account(**r.json())

    # DELETE
    del_acc = delete_account(acc.account_id, token)

    assert del_acc == upd_acc

    # a read returns null
    r = client.get(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200
    assert r.json() is None

    # a second delete return null
    r = client.delete(
        f"/accounts/{acc.account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert r.status_code == 200
    assert r.json() is None


def test_attachment_upload_and_download(login, setup_test):
    token = login

    acc = create_account(token)

    filename = "1MB with spaces.txt"

    # uploading
    r = client.get(
        f"/accounts/{acc.account_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    assert validators.url(r.text)  # type: ignore

    s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/accounts/{acc.account_id}/presigned-get-url/{filename}",
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

    filename = "ss.png"

    # uploading
    r = client.get(
        f"/accounts/{acc.account_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    assert validators.url(r.text)  # type: ignore

    s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/accounts/{acc.account_id}/presigned-get-url/{filename}",
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
        f"accounts/{acc.account_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    # deleting twice
    r = client.delete(
        f"accounts/{acc.account_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200
