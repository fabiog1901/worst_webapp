from fastapi.testclient import TestClient
from worst_crm.main import app
from worst_crm.models import Note
from worst_crm.tests.test_accounts import create_account, delete_account
from worst_crm.tests.test_projects import create_project, delete_project
from uuid import UUID
from worst_crm.tests.utils import login, setup_test, s3_download, s3_upload
import hashlib
import validators

client = TestClient(app)


# CREATE
def test_get_notes_non_auth():
    r = client.get("/notes/12345/12345")

    assert r.status_code == 401


def get_note(
    account_id: UUID, project_id: UUID, note_id: int, token: str
) -> Note | None:
    r = client.get(
        f"/notes/{account_id}/{project_id}/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    if r.json():
        return Note(**r.json())
    return None


def create_note(account_id: UUID, project_id: UUID, token: str) -> Note:
    r = client.post(
        f"/notes/{account_id}/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_note1",
            "text": "dummy Note descr",
            "status": "NEW",
            "tags": ["p1", "p2", "p2"],
            "data": {"key-note": "val-note"}
        }""",
    )

    assert r.status_code == 200

    return Note(**r.json())


def delete_note(
    account_id: UUID, project_id: UUID, note_id: int, token: str
) -> Note | None:
    r = client.delete(
        f"/notes/{account_id}/{project_id}/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    if r.json():
        return Note(**r.json())
    return None


def test_crud_note(login, setup_test):
    token = login

    # CREATE
    acc = create_account(token)

    proj = create_project(acc.account_id, token)

    note = create_note(proj.account_id, proj.project_id, token)

    # READ
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}/{note.note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert note == Note(**r.json())

    # READ ALL
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    l: list[Note] = [Note(**x) for x in r.json()]

    assert len(l) > 0

    # UPDATE
    r = client.put(
        f"/notes/{note.account_id}/{proj.project_id}/{note.note_id}",
        headers={"Authorization": f"Bearer {token}"},
        content="""
        {
            "name": "dummy_proj1",
            "description": "dummy Note descr UPDATED",
            "status": "NEW",
            "tags": ["p1111", "p2222", "p2222"]
        }""",
    )

    assert r.status_code == 200

    upd_note = Note(**r.json())

    assert upd_note == get_note(note.account_id, note.project_id, note.note_id, token)

    # DELETE
    del_note = delete_note(note.account_id, note.project_id, note.note_id, token)

    assert del_note == upd_note

    # a read returns null
    assert get_note(note.account_id, note.project_id, note.note_id, token) is None

    # a second delete return null
    assert delete_note(note.account_id, note.project_id, note.note_id, token) is None

    # finally, delete account
    assert delete_project(note.account_id, note.project_id, token)
    assert delete_account(note.account_id, token)


def test_attachment_upload_and_download(login, setup_test):
    token = login

    acc = create_account(token)
    proj = create_project(acc.account_id, token)
    note = create_note(proj.account_id, proj.project_id, token)

    filename = "1MB with spaces.txt"

    # uploading
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}/{note.note_id}/presigned-put-url/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200

    assert validators.url(r.text)  # type: ignore

    s3_upload(r.text, f".testdata/{filename}")

    # Downloading
    r = client.get(
        f"/notes/{note.account_id}/{note.project_id}/{note.note_id}/presigned-get-url/{filename}",
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
        f"notes/{note.account_id}/{note.project_id}/{note.note_id}/attachments/{filename}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200
